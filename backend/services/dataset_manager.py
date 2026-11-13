import json
from pathlib import Path
from datetime import datetime


DATASET_DIR = Path(__file__).parent.parent.parent / "data"
DATASET_DIR.mkdir(exist_ok=True)


def list_datasets() -> list[dict]:
    datasets = []
    for f in DATASET_DIR.glob("*.jsonl"):
        examples = []
        with open(f, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        examples.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        datasets.append({
            "name": f.stem,
            "path": str(f),
            "filename": f.name,
            "examples": len(examples),
            "created": datetime.fromtimestamp(f.stat().st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })
    return sorted(datasets, key=lambda x: x["modified"], reverse=True)


def get_dataset(name: str) -> dict:
    filepath = DATASET_DIR / f"{name}.jsonl"
    if not filepath.exists():
        return None
    
    examples = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    examples.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    
    return {
        "name": name,
        "path": str(filepath),
        "filename": filepath.name,
        "examples": examples,
        "count": len(examples),
        "created": datetime.fromtimestamp(filepath.stat().st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
    }


def update_dataset(name: str, examples: list[dict]) -> dict:
    filepath = DATASET_DIR / f"{name}.jsonl"
    
    with open(filepath, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    
    return {
        "name": name,
        "path": str(filepath),
        "examples": len(examples),
        "updated": datetime.now().isoformat(),
    }


def add_example(dataset_name: str, question: str, answer: str) -> dict:
    filepath = DATASET_DIR / f"{dataset_name}.jsonl"
    
    example = {"text": f"User: {question}\nAssistant: {answer}"}
    
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(example, ensure_ascii=False) + "\n")
    
    return {"added": True, "dataset": dataset_name}


def delete_example(dataset_name: str, index: int) -> dict:
    filepath = DATASET_DIR / f"{dataset_name}.jsonl"
    
    examples = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    examples.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    
    if 0 <= index < len(examples):
        examples.pop(index)
        
        with open(filepath, "w", encoding="utf-8") as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")
        
        return {"deleted": True, "dataset": dataset_name, "remaining": len(examples)}
    
    return {"deleted": False, "error": "Invalid index"}


def delete_dataset(name: str) -> dict:
    filepath = DATASET_DIR / f"{name}.jsonl"
    if filepath.exists():
        filepath.unlink()
        return {"deleted": True, "name": name}
    return {"deleted": False, "error": "Dataset not found"}


def merge_datasets(names: list[str], output_name: str = None) -> dict:
    all_examples = []
    
    for name in names:
        filepath = DATASET_DIR / f"{name}.jsonl"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            all_examples.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
    
    if not output_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"merged_{timestamp}"
    
    output_path = DATASET_DIR / f"{output_name}.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for example in all_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    
    return {
        "name": output_name,
        "path": str(output_path),
        "examples": len(all_examples),
        "merged_from": names,
    }


def export_dataset(name: str, format: str = "json") -> str:
    filepath = DATASET_DIR / f"{name}.jsonl"
    if not filepath.exists():
        return None
    
    examples = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    examples.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    
    export_path = DATASET_DIR / f"{name}_export.{format}"
    
    if format == "json":
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(examples, f, indent=2, ensure_ascii=False)
    elif format == "jsonl":
        export_path = filepath
    
    return str(export_path)
