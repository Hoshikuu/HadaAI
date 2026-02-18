from pathlib import Path
from json import dumps, loads
from datetime import datetime, timezone

MEMORY_PATH = Path("mem/memory.hada")

def _ensure():
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not MEMORY_PATH.exists():
        MEMORY_PATH.write_text(dumps({}))

def load() -> dict:
    _ensure()
    return loads(MEMORY_PATH.read_text(encoding="utf-8"))

def save(data: dict):
    _ensure()
    MEMORY_PATH.write_text(dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def append_turn(user_text: str, hada_text: str):
    """Guarda el turno en raw para compresión posterior con summary.py."""
    mem = load()
    turns = mem.get("_raw_turns", [])
    turns.append({
        "ts": datetime.now(timezone.utc).isoformat(),
        "user": user_text,
        "hada": hada_text,
    })
    # Conserva solo los últimos 50 turnos raw (el resto ya fue comprimido)
    mem["_raw_turns"] = turns[-50:]
    save(mem)

def get_compressed_context(mem: dict) -> str:
    """Devuelve solo el contexto comprimido (sin _raw_turns) como string."""
    clean = {k: v for k, v in mem.items() if k != "_raw_turns"}
    return dumps(clean, ensure_ascii=False) if clean else ""
