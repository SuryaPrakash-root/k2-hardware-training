import os
import sys
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.parser import extract_text, PARSERS
from services.url_parser import parse_url, is_youtube_url
from services.dataset import (
    chunk_text,
    create_qa_pairs,
    save_dataset,
    list_datasets,
    merge_datasets,
    DATASET_DIR,
)
from services.dataset_manager import (
    list_datasets as list_datasets_manager,
    get_dataset,
    update_dataset,
    add_example,
    delete_example,
    delete_dataset,
    merge_datasets as merge_datasets_manager,
    export_dataset,
)
from services.training_history import (
    save_training_run,
    list_training_runs,
    get_training_run,
    delete_training_run,
    compare_runs,
)
from services.hyperparameter_search import (
    create_search_config,
    get_search_status,
    list_searches,
    DEFAULT_SEARCH_SPACE,
)
from services.trainer import (
    start_training,
    stop_training,
    get_training_state,
)
from services.inference import generate_response, load_model
from services import rag
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield

app = FastAPI(title="K2 Training API", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


class TrainConfig(BaseModel):
    epochs: int = 3
    learning_rate: float = 2e-5
    batch_size: int = 2
    lora_rank: int = 8
    max_length: int = 256


class ChatRequest(BaseModel):
    prompt: str
    max_tokens: int = 4096


class UrlRequest(BaseModel):
    url: str


class ExampleRequest(BaseModel):
    question: str
    answer: str


class UpdateDatasetRequest(BaseModel):
    examples: List[dict]


class MergeRequest(BaseModel):
    names: List[str]
    output_name: Optional[str] = None


class CompareRequest(BaseModel):
    run_ids: List[str]


class AdvancedTrainConfig(BaseModel):
    epochs: int = 3
    learning_rate: float = 2e-5
    batch_size: int = 2
    lora_rank: int = 8
    max_length: int = 256
    qlora: bool = False
    cosine: bool = True
    multiturn: bool = False
    filter_data: bool = True
    dataset: str = "data/hardware_knowledge_base.jsonl"


class HyperparameterSearchRequest(BaseModel):
    search_space: Optional[Dict[str, List[Any]]] = None
    max_trials: int = 10


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "3.0.0", "supported_formats": list(PARSERS.keys())}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in PARSERS:
        raise HTTPException(400, f"Unsupported file type: {ext}. Supported: {list(PARSERS.keys())}")

    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        text = extract_text(str(file_path))
    except Exception as e:
        raise HTTPException(500, f"Failed to parse file: {str(e)}")

    chunks = chunk_text(text)
    examples = create_qa_pairs(chunks, file.filename)
    dataset_path = save_dataset(examples, Path(file.filename).stem)

    # RAG: auto-index chunks into the vector store
    rag_result = rag.index_chunks(chunks, source=file.filename)

    return {
        "filename": file.filename,
        "size": len(content),
        "text_length": len(text),
        "chunks": len(chunks),
        "examples": len(examples),
        "dataset_path": dataset_path,
        "preview": text[:1000],
        "rag_indexed": rag_result.get("indexed", 0),
    }


@app.post("/api/upload/batch")
async def upload_batch(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in PARSERS:
            results.append({"filename": file.filename, "error": f"Unsupported file type: {ext}"})
            continue

        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        try:
            text = extract_text(str(file_path))
            chunks = chunk_text(text)
            examples = create_qa_pairs(chunks, file.filename)
            dataset_path = save_dataset(examples, Path(file.filename).stem)
            rag_result = rag.index_chunks(chunks, source=file.filename)
            results.append({
                "filename": file.filename,
                "status": "success",
                "text_length": len(text),
                "examples": len(examples),
                "dataset_path": dataset_path,
                "rag_indexed": rag_result.get("indexed", 0),
            })
        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})

    return {"results": results, "total": len(files), "successful": sum(1 for r in results if r.get("status") == "success")}


@app.post("/api/parse-url")
async def parse_url_endpoint(request: UrlRequest):
    try:
        result = parse_url(request.url)
        if result['type'] == 'error':
            raise HTTPException(400, result['text'])
        
        text = result['text']
        chunks = chunk_text(text)
        examples = create_qa_pairs(chunks, result['title'])
        dataset_path = save_dataset(examples, result['title'][:50].replace(' ', '_'))

        # RAG: auto-index URL content
        rag_result = rag.index_chunks(chunks, source=result['title'][:80])

        return {
            "url": request.url,
            "title": result['title'],
            "type": result['type'],
            "text_length": len(text),
            "chunks": len(chunks),
            "examples": len(examples),
            "dataset_path": dataset_path,
            "preview": text[:1000],
            "rag_indexed": rag_result.get("indexed", 0),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to parse URL: {str(e)}")


@app.get("/api/documents")
async def list_documents():
    documents = []
    for f in UPLOAD_DIR.iterdir():
        if f.is_file():
            documents.append({
                "name": f.name,
                "size": f.stat().st_size,
                "path": str(f),
            })
    return documents


@app.get("/api/datasets")
async def get_datasets():
    return list_datasets_manager()


@app.get("/api/datasets/{name}")
async def get_dataset_detail(name: str):
    dataset = get_dataset(name)
    if not dataset:
        raise HTTPException(404, f"Dataset '{name}' not found")
    return dataset


@app.put("/api/datasets/{name}")
async def update_dataset_endpoint(name: str, request: UpdateDatasetRequest):
    result = update_dataset(name, request.examples)
    return result


@app.post("/api/datasets/{name}/add")
async def add_example_endpoint(name: str, request: ExampleRequest):
    result = add_example(name, request.question, request.answer)
    return result


@app.delete("/api/datasets/{name}/examples/{index}")
async def delete_example_endpoint(name: str, index: int):
    result = delete_example(name, index)
    if not result.get("deleted"):
        raise HTTPException(400, result.get("error", "Failed to delete"))
    return result


@app.delete("/api/datasets/{name}")
async def delete_dataset_endpoint(name: str):
    result = delete_dataset(name)
    if not result.get("deleted"):
        raise HTTPException(404, result.get("error", "Dataset not found"))
    return result


@app.post("/api/datasets/merge")
async def merge_datasets_endpoint(request: MergeRequest):
    result = merge_datasets_manager(request.names, request.output_name)
    return result


@app.get("/api/datasets/{name}/export")
async def export_dataset_endpoint(name: str, format: str = "json"):
    export_path = export_dataset(name, format)
    if not export_path:
        raise HTTPException(404, f"Dataset '{name}' not found")
    return {"path": export_path, "format": format}


@app.post("/api/train")
async def train(config: TrainConfig):
    result = start_training(config.model_dump())
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@app.post("/api/train/advanced")
async def train_advanced(config: AdvancedTrainConfig):
    import subprocess
    import threading
    
    cmd = [
        "python3",
        str(Path(__file__).parent.parent / "train_advanced.py"),
        "--epochs", str(config.epochs),
        "--lr", str(config.learning_rate),
        "--batch_size", str(config.batch_size),
        "--lora_rank", str(config.lora_rank),
        "--max_length", str(config.max_length),
        "--dataset", config.dataset,
        "--output", f"models/hardware-lora-advanced",
    ]
    
    if config.qlora:
        cmd.append("--qlora")
    if config.cosine:
        cmd.append("--cosine")
    if config.multiturn:
        cmd.append("--multiturn")
    if config.filter_data:
        cmd.append("--filter")
    
    def run_training():
        subprocess.run(cmd, cwd=str(Path(__file__).parent.parent))
    
    thread = threading.Thread(target=run_training, daemon=True)
    thread.start()
    
    return {"message": "Advanced training started", "config": config.model_dump()}


@app.post("/api/hyperparameter/search")
async def start_hyperparameter_search(request: HyperparameterSearchRequest):
    search_space = request.search_space or DEFAULT_SEARCH_SPACE
    search_config = create_search_config(search_space, request.max_trials)
    return search_config


@app.get("/api/hyperparameter/search")
async def list_hyperparameter_searches():
    return list_searches()


@app.get("/api/hyperparameter/search/{search_id}")
async def get_hyperparameter_search(search_id: str):
    status = get_search_status(search_id)
    if not status:
        raise HTTPException(404, f"Search '{search_id}' not found")
    return status


@app.post("/api/train/stop")
async def stop():
    return stop_training()


@app.get("/api/train/status")
async def training_status():
    return get_training_state()


@app.get("/api/train/history")
async def get_training_history():
    return list_training_runs()


@app.get("/api/train/history/{run_id}")
async def get_training_run_detail(run_id: str):
    run = get_training_run(run_id)
    if not run:
        raise HTTPException(404, f"Training run '{run_id}' not found")
    return run


@app.delete("/api/train/history/{run_id}")
async def delete_training_run_endpoint(run_id: str):
    result = delete_training_run(run_id)
    if not result.get("deleted"):
        raise HTTPException(404, result.get("error", "Run not found"))
    return result


@app.post("/api/train/compare")
async def compare_training_runs(request: CompareRequest):
    runs = compare_runs(request.run_ids)
    return {"runs": runs}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        response = generate_response(request.prompt, request.max_tokens)
        return {"response": response}
    except Exception as e:
        raise HTTPException(500, f"Inference error: {str(e)}")


# ---------------------------------------------------------------- RAG endpoints

class RagQueryRequest(BaseModel):
    question: str
    top_k: int = 4


@app.get("/api/rag/status")
async def rag_status():
    """Index statistics: vector count, sources, model info."""
    return rag.status()


@app.post("/api/rag/query")
async def rag_query(request: RagQueryRequest):
    """RAG pipeline: retrieve relevant chunks → generate grounded answer + sources."""
    if not request.question.strip():
        raise HTTPException(400, "Question cannot be empty")
    try:
        import asyncio
        result = await asyncio.to_thread(
            rag.answer_with_rag, request.question, request.top_k
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"RAG error: {str(e)}")


@app.post("/api/rag/reindex")
async def rag_reindex():
    """Rebuild the vector index from all uploaded documents."""
    try:
        import asyncio
        sources = {}
        for f in UPLOAD_DIR.iterdir():
            if not f.is_file():
                continue
            try:
                text = extract_text(str(f))
                chunks = [c for c in chunk_text(text) if len(c) >= 50]
                if chunks:
                    sources[f.name] = chunks
            except Exception:
                continue
        result = await asyncio.to_thread(rag.reindex_all, sources)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(500, f"Reindex error: {str(e)}")


@app.delete("/api/rag/index")
async def rag_clear():
    """Clear the vector index."""
    return rag.clear_index()


@app.websocket("/ws/train")
async def websocket_train(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            state = get_training_state()
            await websocket.send_json(state)
            if state["status"] in ("completed", "error", "stopped"):
                break
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
