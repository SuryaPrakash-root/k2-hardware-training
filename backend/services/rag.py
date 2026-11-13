"""
RAG (Retrieval-Augmented Generation) service for K2 Training Platform.

Architecture:
  Document upload → chunking → embedding (sentence-transformers) → FAISS index
  User query → embed query → similarity search (top-k) → context prompt → LLM answer

Components:
  - Embedding model : sentence-transformers/all-MiniLM-L6-v2 (384-dim vectors)
  - Vector store    : FAISS IndexFlatIP (inner-product = cosine on normalized vectors)
  - Persistence     : rag_index/index.faiss (vectors) + rag_index/index.json (metadata)
"""

import json
import threading
from pathlib import Path
from datetime import datetime

RAG_DIR = Path(__file__).parent.parent.parent / "rag_index"
RAG_DIR.mkdir(exist_ok=True)

INDEX_FILE = RAG_DIR / "index.faiss"
META_FILE = RAG_DIR / "index.json"

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_lock = threading.Lock()
_embedder = None          # SentenceTransformer instance (lazy-loaded)
_index = None             # faiss.Index instance
_metadata = []            # [{"text": ..., "source": ..., "chunk_id": ...}] parallel to index rows


# ---------------------------------------------------------------- embeddings

def _get_embedder():
    """Lazy-load the embedding model (only on first use)."""
    global _embedder
    if _embedder is None:
        # inference.py sets HF_HUB_OFFLINE=1 for the local LLM — clear it so the
        # embedding model can be fetched from the hub if not cached yet.
        import os
        os.environ.pop("HF_HUB_OFFLINE", None)
        os.environ.pop("TRANSFORMERS_OFFLINE", None)

        from sentence_transformers import SentenceTransformer
        print(f"[RAG] Loading embedding model: {EMBED_MODEL}")
        _embedder = SentenceTransformer(EMBED_MODEL)
        print("[RAG] Embedding model ready")
    return _embedder


def embed_texts(texts: list[str]) -> "object":
    """Return an (N, 384) float32 matrix of normalized embeddings."""
    import numpy as np
    model = _get_embedder()
    vectors = model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,   # L2-normalize → dot product == cosine similarity
        show_progress_bar=False,
    )
    return np.asarray(vectors, dtype="float32")


# ------------------------------------------------------------ index handling

def _load():
    """Load index + metadata from disk into memory (idempotent)."""
    global _index, _metadata
    if _index is not None:
        return
    if INDEX_FILE.exists() and META_FILE.exists():
        import faiss
        _index = faiss.read_index(str(INDEX_FILE))
        with open(META_FILE, "r", encoding="utf-8") as f:
            _metadata = json.load(f)
        print(f"[RAG] Loaded index: {_index.ntotal} vectors")
    else:
        _index = None
        _metadata = []


def _save():
    """Persist index + metadata to disk."""
    import faiss
    if _index is not None:
        faiss.write_index(_index, str(INDEX_FILE))
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump(_metadata, f, ensure_ascii=False, indent=1)


def _ensure_index(dim: int = 384):
    """Create an empty FAISS index if none exists yet."""
    global _index
    if _index is None:
        import faiss
        _index = faiss.IndexFlatIP(dim)   # inner product on normalized vectors = cosine


# ------------------------------------------------------------------ indexing

def index_chunks(chunks: list[str], source: str) -> dict:
    """Embed document chunks and add them to the vector index.

    Called automatically by the upload endpoints after chunking.
    """
    if not chunks:
        return {"indexed": 0, "source": source}

    # skip chunks that are too small to be useful
    chunks = [c for c in chunks if c and len(c.strip()) >= 50]
    if not chunks:
        return {"indexed": 0, "source": source}

    with _lock:
        _load()
        _ensure_index()

        vectors = embed_texts(chunks)
        start_row = _index.ntotal
        _index.add(vectors)

        for i, chunk in enumerate(chunks):
            _metadata.append({
                "text": chunk,
                "source": source,
                "chunk_id": start_row + i,
                "indexed_at": datetime.now().isoformat(),
            })

        _save()
        total = _index.ntotal
        print(f"[RAG] Indexed {len(chunks)} chunks from '{source}' (total: {total})")
        return {"indexed": len(chunks), "source": source, "total_vectors": total}


def reindex_all(sources: dict[str, list[str]]) -> dict:
    """Rebuild the whole index from scratch. sources = {name: [chunks, ...]}"""
    global _index, _metadata
    with _lock:
        _index = None
        _metadata = []
        if INDEX_FILE.exists():
            INDEX_FILE.unlink()
        if META_FILE.exists():
            META_FILE.unlink()

        total = 0
        for source, chunks in sources.items():
            result = index_chunks(chunks, source)
            total += result["indexed"]
        return {"indexed": total, "sources": len(sources)}


def clear_index():
    """Delete the index completely."""
    global _index, _metadata
    with _lock:
        _index = None
        _metadata = []
        if INDEX_FILE.exists():
            INDEX_FILE.unlink()
        if META_FILE.exists():
            META_FILE.unlink()
    return {"cleared": True}


# ---------------------------------------------------------------- retrieval

def retrieve(query: str, top_k: int = 4) -> list[dict]:
    """Embed the query and return the top-k most similar chunks.

    Each result: {"text", "source", "chunk_id", "score"} (score = cosine similarity)
    """
    with _lock:
        _load()
        if _index is None or _index.ntotal == 0:
            return []

        query_vec = embed_texts([query])
        k = min(top_k, _index.ntotal)
        scores, ids = _index.search(query_vec, k)

        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0 or idx >= len(_metadata):
                continue
            meta = _metadata[idx]
            results.append({
                "text": meta["text"],
                "source": meta["source"],
                "chunk_id": int(idx),
                "score": round(float(score), 4),
            })
        return results


def status() -> dict:
    """Index statistics for the UI."""
    with _lock:
        _load()
        sources = sorted({m["source"] for m in _metadata})
        return {
            "enabled": True,
            "model": EMBED_MODEL,
            "dimensions": 384,
            "vectors": _index.ntotal if _index is not None else 0,
            "sources": sources,
            "source_count": len(sources),
            "index_file": str(INDEX_FILE),
        }


# ------------------------------------------------------------ RAG generation

RAG_PROMPT = """You are K2, a helpful AI assistant. Answer the user's question using ONLY the provided context.
If the context does not contain the answer, say you don't have enough information in the indexed documents.
Cite the source document name when you use it. Give direct, concise answers.

=== CONTEXT ===
{context}
=== END CONTEXT ===

User: {question}
Assistant:"""


def build_context(results: list[dict]) -> str:
    """Format retrieved chunks into a single context block."""
    parts = []
    for i, r in enumerate(results, 1):
        parts.append(f"[Source {i}: {r['source']} (similarity {r['score']})]\n{r['text']}")
    return "\n\n".join(parts)


def answer_with_rag(question: str, top_k: int = 4) -> dict:
    """Full RAG pipeline: retrieve → build prompt → generate → return answer + sources.

    Returns {"answer", "sources", "retrieval_count"}
    """
    from services.inference import generate_response

    results = retrieve(question, top_k=top_k)

    if not results:
        return {
            "answer": "No documents are indexed yet. Upload a document first and it will be "
                      "automatically indexed for retrieval.",
            "sources": [],
            "retrieval_count": 0,
        }

    prompt = RAG_PROMPT.format(context=build_context(results), question=question)
    answer = generate_response(prompt, max_new_tokens=1024)

    return {
        "answer": answer,
        "sources": results,
        "retrieval_count": len(results),
    }
