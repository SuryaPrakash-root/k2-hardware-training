import json
from pathlib import Path
from datetime import datetime


HISTORY_DIR = Path(__file__).parent.parent.parent / "models" / "training_history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def save_training_run(config: dict, metrics: dict, dataset_info: dict) -> dict:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"run_{timestamp}"
    
    run_data = {
        "id": run_id,
        "timestamp": datetime.now().isoformat(),
        "config": config,
        "metrics": metrics,
        "dataset": dataset_info,
        "status": "completed",
    }
    
    run_file = HISTORY_DIR / f"{run_id}.json"
    with open(run_file, "w", encoding="utf-8") as f:
        json.dump(run_data, f, indent=2)
    
    return run_data


def list_training_runs() -> list[dict]:
    runs = []
    for f in HISTORY_DIR.glob("run_*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                run = json.load(fh)
                runs.append(run)
        except (json.JSONDecodeError, IOError):
            pass
    
    return sorted(runs, key=lambda x: x.get("timestamp", ""), reverse=True)


def get_training_run(run_id: str) -> dict:
    run_file = HISTORY_DIR / f"{run_id}.json"
    if not run_file.exists():
        return None
    
    with open(run_file, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_training_run(run_id: str) -> dict:
    run_file = HISTORY_DIR / f"{run_id}.json"
    if run_file.exists():
        run_file.unlink()
        return {"deleted": True, "run_id": run_id}
    return {"deleted": False, "error": "Run not found"}


def compare_runs(run_ids: list[str]) -> list[dict]:
    runs = []
    for run_id in run_ids:
        run = get_training_run(run_id)
        if run:
            runs.append(run)
    return runs
