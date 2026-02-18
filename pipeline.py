import json
from pathlib import Path
from datetime import datetime, timezone

import budget
import validator
import memory as mem_module
from modules import run_llm, run_vl
from tools import hada_system
import cerebras_client as remote

LOG_PATH = Path("logs/escalations.jsonl")

T1 = 30
T2 = 70

FAIL_COUNT: dict = {}

def _log_escalation(entry: dict):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def run_turn(
    user_text: str,
    history: list,
    session_id: str = "default",
    image_path: str = None,
) -> str:
    mem = mem_module.load()
    mem_context = mem_module.get_compressed_context(mem)
    mode = budget.budget_mode()

    # 1. VL (solo si hay imagen)
    vl_context = ""
    vl_used = False
    if image_path:
        vl_context = run_vl(image_path)
        vl_used = True

    # 2. Construir mensajes para Qwen3-4B
    sys_content = hada_system()
    if mem_context:
        sys_content += f"\n\nMEMORIA (SOLO LECTURA):\n{mem_context}"
    if vl_context:
        sys_content += f"\n\nVISIÓN ACTUAL: {vl_context}"

    messages = [{"role": "system", "content": sys_content}]
    messages += history[-8:]
    messages.append({"role": "user", "content": user_text})

    task_type = validator.classify_task(user_text)

    # 3. Expert directo si tarea hard
    if task_type == "hard" and mode in ("full", "repair"):
        result = remote.expert(user_text, mem, history)
        if result:
            _log_escalation({
                "ts": datetime.now(timezone.utc).isoformat(),
                "session": session_id,
                "route": "expert_direct",
                "user": user_text,
                "final": result,
            })
            mem_module.append_turn(user_text, result)
            FAIL_COUNT[session_id] = 0
            return result

    # 4. Draft local (Qwen3-4B)
    draft = run_llm(messages, max_new_tokens=90)

    # 5. Validar
    result_v = validator.risk_score(draft, user_text, vl_used=vl_used)
    score = result_v["score"]
    flags = result_v["flags"]

    if score >= T1:
        FAIL_COUNT[session_id] = FAIL_COUNT.get(session_id, 0) + 1
    else:
        FAIL_COUNT[session_id] = 0

    final_text = draft
    route = "local"

    # 6. Repair
    if T1 <= score < T2 and mode in ("full", "repair"):
        repaired = remote.repair(user_text, draft, flags)
        if repaired.get("needs_expert") and mode == "full":
            expert_result = remote.expert(user_text, mem, history)
            final_text = expert_result if expert_result else repaired["final_text"]
            route = "expert_via_repair"
        else:
            final_text = repaired["final_text"]
            route = "repair"

    # 7. Expert por score alto
    elif score >= T2 and mode == "full":
        expert_result = remote.expert(user_text, mem, history)
        final_text = expert_result if expert_result else draft
        route = "expert"

    # 8. Expert por 2 fallos consecutivos
    elif FAIL_COUNT.get(session_id, 0) >= 2 and mode == "full":
        expert_result = remote.expert(user_text, mem, history)
        if expert_result:
            final_text = expert_result
            route = "expert_retry"
            FAIL_COUNT[session_id] = 0

    # 9. Log y memoria
    if route != "local":
        _log_escalation({
            "ts": datetime.now(timezone.utc).isoformat(),
            "session": session_id,
            "route": route,
            "score": score,
            "flags": flags,
            "user": user_text,
            "draft": draft,
            "final": final_text,
            "budget_remaining": budget.remaining(),
        })

    mem_module.append_turn(user_text, final_text)
    return final_text
