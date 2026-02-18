import re

EMOJI_PATTERN = re.compile(
    "[\U0001F300-\U0001FFFF"
    "\U00002600-\U000027BF"
    "\U0001F900-\U0001F9FF]+",
    flags=re.UNICODE
)

HARD_TASK_KEYWORDS = [
    r"\bplan\s+(paso|detallado|completo)\b",
    r"\banali[sz]a\b",
    r"\bdebug\b",
    r"\brefactori[sz]a\b",
    r"\bexplica\s+(en\s+detalle|todo)\b",
    r"\barchitectura\b",
    r"\boptimi[sz]a\b",
    r"\bcrea?\s+un\s+(sistema|módulo|clase|función)\b",
    r"\b(haz|genera|escribe)\s+un\s+(script|programa|código)\b",
]

def _has_emoji(text: str) -> bool:
    return bool(EMOJI_PATTERN.search(text))

def _user_used_emoji(user_text: str) -> bool:
    return bool(EMOJI_PATTERN.search(user_text))

def _count_sentences(text: str) -> int:
    return len(re.findall(r'[.!?…]+', text))

def _has_question(text: str) -> bool:
    return '¿' in text or text.strip().endswith('?')

def _is_very_long(text: str, max_words: int = 80) -> bool:
    return len(text.split()) > max_words

def _is_hard_task(user_text: str) -> bool:
    for pattern in HARD_TASK_KEYWORDS:
        if re.search(pattern, user_text, re.IGNORECASE):
            return True
    return False

def risk_score(draft: str, user_text: str, vl_used: bool = False) -> dict:
    """
    Devuelve {"score": int, "flags": [str]}
    score: 0-100
    """
    flags = []
    score = 0

    # Emoji sin permiso
    if _has_emoji(draft) and not _user_used_emoji(user_text):
        flags.append("EMOJI_NOT_ALLOWED")
        score += 30

    # Pregunta innecesaria
    if _has_question(draft):
        flags.append("UNWANTED_QUESTION")
        score += 25

    # Demasiado larga para "humana breve"
    if _is_very_long(draft):
        flags.append("TOO_LONG")
        score += 20

    # Menciona "pantalla/veo/imagen" sin VL activo
    if not vl_used and re.search(r'\b(veo|pantalla|imagen|captura|screenshot)\b', draft, re.IGNORECASE):
        flags.append("HALLUCINATION_VISUAL")
        score += 40

    # Habla de sí misma como IA/asistente
    if re.search(r'\b(como IA|soy una IA|como asistente|modelo de lenguaje)\b', draft, re.IGNORECASE):
        flags.append("AI_TALK")
        score += 35

    return {"score": min(score, 100), "flags": flags}

def classify_task(user_text: str) -> str:
    """Devuelve 'hard' o 'normal'"""
    return "hard" if _is_hard_task(user_text) else "normal"
