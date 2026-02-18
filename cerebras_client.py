from os import getenv
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
from json import loads, dumps
from tools import hada_system
import budget

load_dotenv()
_client = None

REPAIR_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "repair_response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "final_text": {"type": "string"},
                "reason_code": {"type": "string"},
                "needs_expert": {"type": "boolean"},
            },
            "required": ["final_text", "reason_code", "needs_expert"],
            "additionalProperties": False,
        }
    }
}

def _get_client() -> Cerebras:
    global _client
    if _client is None:
        _client = Cerebras(api_key=getenv("TOKEN"))
    return _client

# ── REPAIR ──────────────────────────────────────────────────────────────────
def repair(user_text: str, draft: str, flags: list) -> dict:
    """
    Pide al 120B que corrija el draft violando reglas.
    Devuelve {"final_text": str, "reason_code": str, "needs_expert": bool}
    """
    rules = (
        "Corrige el draft. Reglas: en español, breve (1-3 frases, más solo si el tema lo exige), "
        "humano y cercano, no preguntes a menos que sea imprescindible, no uses emojis salvo que "
        "el usuario los use primero, no hables de ti como IA, no inventes hechos. "
        f"Flags de fallo: {flags}. "
        "Devuelve JSON estricto con campos: final_text, reason_code, needs_expert."
    )
    messages = [
        {"role": "system", "content": hada_system() + "\n\n" + rules},
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": f"[DRAFT A CORREGIR]: {draft}"},
    ]
    est_tokens = sum(len(m["content"].split()) * 1.3 for m in messages) + 200
    if not budget.can_spend(int(est_tokens)):
        return {"final_text": draft, "reason_code": "BUDGET_EXHAUSTED", "needs_expert": False}

    resp = _get_client().chat.completions.create(
        messages=messages,
        model="gpt-oss-120b",
        max_completion_tokens=300,
        temperature=0.6,
        top_p=0.95,
        reasoning_effort="low",
        response_format=REPAIR_SCHEMA,
    )
    budget.add_tokens(resp.usage.total_tokens)
    return loads(resp.choices[0].message.content)

# ── EXPERT ───────────────────────────────────────────────────────────────────
def expert(user_text: str, memory: dict, history: list) -> str:
    """
    El 120B responde desde cero para tareas 'hard'.
    """
    mem_str = dumps(memory, ensure_ascii=False) if memory else ""
    sys_content = hada_system()
    if mem_str:
        sys_content += f"\n\nMEMORIA (SOLO LECTURA):\n{mem_str}"

    messages = [{"role": "system", "content": sys_content}]
    messages += history[-6:]  # últimos 3 pares
    messages.append({"role": "user", "content": user_text})

    est_tokens = sum(len(m["content"].split()) * 1.3 for m in messages) + 500
    if not budget.can_spend(int(est_tokens)):
        return None  # fallback a Qwen

    resp = _get_client().chat.completions.create(
        messages=messages,
        model="gpt-oss-120b",
        max_completion_tokens=400,
        temperature=0.85,
        top_p=0.95,
        reasoning_effort="low",
    )
    budget.add_tokens(resp.usage.total_tokens)
    return resp.choices[0].message.content.strip()
