import torch
import soundfile as sf
from pathlib import Path
from qwentts import Qwen3TTSModel

MODEL_DIR = r"./models/Qwen3-TTS-12Hz-0.6B-CustomVoice"
OUTPUT_PATH = "out/output.wav"

_model = None

def _load():
    global _model
    if _model is None:
        _model = Qwen3TTSModel.from_pretrained(
            MODEL_DIR,
            device_map="cpu",
            dtype=torch.float32,
        )

def speak(text: str, speaker: str = "Ona_Anna", instruction: str = "Tono natural, cercano") -> str:
    _load()
    Path("out").mkdir(exist_ok=True)
    wavs, sr = _model.generate(
        custom_voice={
            "text": text,
            "language": "Spanish",
            "speaker": speaker,
            "instruct": instruction,
        }
    )
    sf.write(OUTPUT_PATH, wavs[0], sr)
    return OUTPUT_PATH
