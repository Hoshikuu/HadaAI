from pathlib import Path
from json import dumps, loads
from datetime import datetime, timezone

BUDGET_FILE = Path("mem/budget.json")
DAILY_LIMIT = 1_000_000

def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def _load() -> dict:
    if not BUDGET_FILE.exists():
        BUDGET_FILE.parent.mkdir(parents=True, exist_ok=True)
        return {"date": _today(), "spent": 0}
    data = loads(BUDGET_FILE.read_text())
    if data.get("date") != _today():
        data = {"date": _today(), "spent": 0}
    return data

def _save(data: dict):
    BUDGET_FILE.write_text(dumps(data, indent=2))

def get_spent() -> int:
    return _load()["spent"]

def add_tokens(n: int):
    data = _load()
    data["spent"] += n
    _save(data)

def remaining() -> int:
    return max(0, DAILY_LIMIT - get_spent())

def can_spend(estimated: int) -> bool:
    return remaining() >= estimated

# Umbrales de degradación
def budget_mode() -> str:
    r = remaining()
    if r > 300_000:   return "full"      # repair + expert habilitados
    if r > 100_000:   return "repair"    # solo repair
    if r > 20_000:    return "critical"  # solo repair si violación grave
    return "off"                         # solo Qwen local
