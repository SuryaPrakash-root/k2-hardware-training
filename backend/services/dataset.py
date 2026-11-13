import json
import uuid
from pathlib import Path
from datetime import datetime


DATASET_DIR = Path(__file__).parent.parent.parent / "data"
DATASET_DIR.mkdir(exist_ok=True)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def create_qa_pairs(chunks: list[str], source_name: str) -> list[dict]:
    examples = []
    for i, chunk in enumerate(chunks):
        if len(chunk) < 50:
            continue
        question = f"Explain the following concept from {source_name}:\n\n{chunk[:200]}..."
        answer = chunk
        examples.append({
            "text": f"User: {question}\nAssistant: {answer}"
        })
    return examples


def save_dataset(examples: list[dict], dataset_name: str) -> str:
    import re
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r'[^\w\-_]', '_', dataset_name)[:50]
    filename = f"{safe_name}_{timestamp}.jsonl"
    filepath = DATASET_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    return str(filepath)


def merge_datasets(dataset_files: list[str], output_name: str = "hardware_knowledge_base") -> str:
    all_examples = []
    for file_path in dataset_files:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    all_examples.append(json.loads(line))

    output_path = DATASET_DIR / f"{output_name}.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for example in all_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    return str(output_path)


def list_datasets() -> list[dict]:
    datasets = []
    for f in DATASET_DIR.glob("*.jsonl"):
        with open(f, "r", encoding="utf-8") as fh:
            count = sum(1 for _ in fh)
        datasets.append({
            "name": f.stem,
            "path": str(f),
            "examples": count,
            "created": datetime.fromtimestamp(f.stat().st_ctime).isoformat()
        })
    return datasets
