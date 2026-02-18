from pathlib import Path
import torch
from qwen_asr import Qwen3ASRModel

MODEL_DIR = r"./models/Qwen3-ASR-0.6B"
_model = None

def _load():
    global _model
    if _model is None:
        _model = Qwen3ASRModel.from_pretrained(
            MODEL_DIR,
            device_map="cpu",
            dtype=torch.float32,
        )

def transcribe(audio_path: str) -> str:
    _load()
    result = _model.transcribe(audio_path)
    return result.strip()
