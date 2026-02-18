#!/usr/bin/env python
"""
argv[1]: texto a sintetizar
argv[2]: ruta de salida (opcional, default out/output.wav)
stdout: ruta del archivo generado
"""
import sys
import torch
import soundfile as sf
from pathlib import Path
from qwentts import Qwen3TTSModel

MODEL_DIR = "./models/Qwen3-TTS-12Hz-0.6B-CustomVoice"
text = sys.argv[1]
output_path = sys.argv[2] if len(sys.argv) > 2 else "out/output.wav"

Path("out").mkdir(exist_ok=True)
model = Qwen3TTSModel.from_pretrained(MODEL_DIR, device_map="cpu", dtype=torch.float32)
wavs, sr = model.generate(custom_voice={
    "text": text,
    "language": "Spanish",
    "speaker": "Ona_Anna",
    "instruct": "Tono natural, cercano",
})
sf.write(output_path, wavs[0], sr)
print(output_path)
