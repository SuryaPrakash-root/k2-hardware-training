import subprocess
import os
import re
import json
from pathlib import Path
from datetime import datetime


IS_DOCKER = os.path.exists("/.dockerenv")

if IS_DOCKER:
    TRAINING_DIR = Path("/app/training")
    PYTHON_BIN = "python3"
else:
    TRAINING_DIR = Path(__file__).parent.parent.parent
    PYTHON_BIN = str(TRAINING_DIR / "venv" / "bin" / "python")

LOG_DIR = Path("/app/logs") if IS_DOCKER else TRAINING_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

training_state = {
    "status": "idle",
    "progress": 0,
    "epoch": 0,
    "total_epochs": 3,
    "loss": 0.0,
    "step": 0,
    "total_steps": 99,
    "log": [],
    "start_time": None,
    "end_time": None,
    "error": None,
}


def get_training_state() -> dict:
    return training_state.copy()


def start_training(config: dict) -> dict:
    global training_state

    if training_state["status"] == "training":
        return {"error": "Training already in progress"}

    training_state.update({
        "status": "training",
        "progress": 0,
        "epoch": 0,
        "total_epochs": config.get("epochs", 3),
        "loss": 0.0,
        "step": 0,
        "total_steps": 0,
        "log": [],
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "error": None,
    })

    import threading
    thread = threading.Thread(target=_run_training, args=(config,), daemon=True)
    thread.start()

    return {"message": "Training started", "status": "training"}


def _parse_line(line: str, config: dict):
    global training_state
    
    if not line:
        return
    
    json_match = re.search(r"\{[^}]+\}", line)
    if json_match:
        try:
            data = json.loads(json_match.group())
            if 'loss' in data:
                training_state["loss"] = float(data['loss'])
            if 'epoch' in data:
                training_state["epoch"] = float(data['epoch'])
            if 'train_runtime' in data:
                training_state["status"] = "completed"
                training_state["progress"] = 100
            return
        except (json.JSONDecodeError, ValueError):
            pass
    
    progress_match = re.search(r"(\d+)%\|[^|]*\|\s*(\d+)/(\d+)", line)
    if progress_match:
        try:
            training_state["progress"] = int(progress_match.group(1))
            training_state["step"] = int(progress_match.group(2))
            training_state["total_steps"] = int(progress_match.group(3))
        except ValueError:
            pass


def _run_training(config: dict):
    global training_state

    try:
        cmd = [
            PYTHON_BIN,
            str(TRAINING_DIR / "train_lora.py"),
        ]

        log_file = LOG_DIR / f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(TRAINING_DIR),
        )

        with open(log_file, "w") as f:
            for line in iter(process.stdout.readline, ""):
                if not line:
                    break
                f.write(line)
                f.flush()
                training_state["log"].append(line.strip())
                _parse_line(line, config)

        process.wait()
        
        if training_state["status"] == "training":
            training_state["status"] = "completed"
            training_state["progress"] = 100
        training_state["end_time"] = datetime.now().isoformat()

    except Exception as e:
        training_state["status"] = "error"
        training_state["error"] = str(e)
        training_state["end_time"] = datetime.now().isoformat()


def stop_training() -> dict:
    global training_state
    if training_state["status"] == "training":
        training_state["status"] = "stopped"
        training_state["end_time"] = datetime.now().isoformat()
        return {"message": "Training stop requested"}
    return {"error": "No training in progress"}
