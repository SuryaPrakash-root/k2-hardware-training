import json
import itertools
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


SEARCH_DIR = Path(__file__).parent.parent.parent / "models" / "hyperparameter_search"
SEARCH_DIR.mkdir(parents=True, exist_ok=True)


def generate_param_grid(search_space: dict) -> list[dict]:
    keys = search_space.keys()
    values = search_space.values()
    combinations = list(itertools.product(*values))
    return [dict(zip(keys, combo)) for combo in combinations]


def create_search_config(search_space: dict, max_trials: int = 10) -> dict:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    search_id = f"search_{timestamp}"
    
    param_grid = generate_param_grid(search_space)
    
    if len(param_grid) > max_trials:
        import random
        param_grid = random.sample(param_grid, max_trials)
    
    search_config = {
        "id": search_id,
        "timestamp": datetime.now().isoformat(),
        "search_space": search_space,
        "param_grid": param_grid,
        "total_trials": len(param_grid),
        "completed_trials": 0,
        "results": [],
        "status": "pending",
        "best_result": None,
    }
    
    config_file = SEARCH_DIR / f"{search_id}.json"
    with open(config_file, "w") as f:
        json.dump(search_config, f, indent=2)
    
    return search_config


def update_search_result(search_id: str, trial_index: int, result: dict):
    config_file = SEARCH_DIR / f"{search_id}.json"
    if not config_file.exists():
        return None
    
    with open(config_file, "r") as f:
        search_config = json.load(f)
    
    result["trial_index"] = trial_index
    result["timestamp"] = datetime.now().isoformat()
    search_config["results"].append(result)
    search_config["completed_trials"] = len(search_config["results"])
    
    if search_config["best_result"] is None or result.get("loss", float("inf")) < search_config["best_result"].get("loss", float("inf")):
        search_config["best_result"] = result
    
    if search_config["completed_trials"] >= search_config["total_trials"]:
        search_config["status"] = "completed"
    else:
        search_config["status"] = "running"
    
    with open(config_file, "w") as f:
        json.dump(search_config, f, indent=2)
    
    return search_config


def get_search_status(search_id: str) -> dict:
    config_file = SEARCH_DIR / f"{search_id}.json"
    if not config_file.exists():
        return None
    
    with open(config_file, "r") as f:
        return json.load(f)


def list_searches() -> list[dict]:
    searches = []
    for f in SEARCH_DIR.glob("search_*.json"):
        try:
            with open(f, "r") as fh:
                search = json.load(fh)
                searches.append({
                    "id": search["id"],
                    "timestamp": search["timestamp"],
                    "status": search["status"],
                    "total_trials": search["total_trials"],
                    "completed_trials": search["completed_trials"],
                    "best_loss": search.get("best_result", {}).get("loss"),
                })
        except (json.JSONDecodeError, IOError):
            pass
    
    return sorted(searches, key=lambda x: x["timestamp"], reverse=True)


DEFAULT_SEARCH_SPACE = {
    "learning_rate": [1e-5, 2e-5, 5e-5],
    "lora_rank": [4, 8, 16],
    "epochs": [2, 3, 5],
    "batch_size": [2, 4],
}
