import subprocess
import json
import sys
from pathlib import Path

# Rutas a los Python de cada venv
PYTHON = {
    "asr": ".venv-asr/Scripts/python.exe",
    "vl":  ".venv-vl/Scripts/python.exe",
    "llm": ".venv-llm/Scripts/python.exe",
    "tts": ".venv-tts/Scripts/python.exe",
}

# En Windows cambia bin/python por Scripts/python.exe
# PYTHON = {
#     "asr": r".venv-asr\Scripts\python.exe",
#     ...
# }

def _python(key: str) -> str:
    p = Path(PYTHON[key])
    if not p.exists():
        raise FileNotFoundError(f"No encontrado venv para '{key}': {p}")
    return str(p)

def run_asr(audio_path: str) -> str:
    result = subprocess.run(
        [_python("asr"), "runners/asr_runner.py", audio_path],
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"ASR error:\n{result.stderr}")
    return result.stdout.strip()

def run_vl(image_path: str, question: str = "¿Qué ves? Responde en 1-2 frases.") -> str:
    result = subprocess.run(
        [_python("vl"), "runners/vl_runner.py", image_path, question],
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"VL error:\n{result.stderr}")
    return json.loads(result.stdout.strip())["description"]

def run_llm(messages: list, max_new_tokens: int = 90) -> str:
    payload = json.dumps({"messages": messages, "max_new_tokens": max_new_tokens}, ensure_ascii=False)
    result = subprocess.run(
        [_python("llm"), "runners/llm_runner.py"],
        input=payload,
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"LLM error:\n{result.stderr}")
    return result.stdout.strip()

def run_tts(text: str, output_path: str = "out/output.wav") -> str:
    result = subprocess.run(
        [_python("tts"), "runners/tts_runner.py", text, output_path],
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"TTS error:\n{result.stderr}")
    return result.stdout.strip()
