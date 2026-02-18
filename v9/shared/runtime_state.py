# v9/shared/runtime_state.py
import os, json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../v9
RUNTIME_DIR = os.path.join(BASE_DIR, "runtime")

def _path(filename: str) -> str:
    return os.path.join(RUNTIME_DIR, filename)

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def write_state(filename: str, data: dict) -> None:
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    payload = dict(data or {})
    payload["_updated_at"] = now_iso()
    tmp = _path(filename) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _path(filename))

def read_state(filename: str, default=None):
    try:
        with open(_path(filename), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except Exception:
        return default
