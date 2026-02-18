#!/usr/bin/env python
"""
stdin: (vacío) — ruta del wav como argumento
argv[1]: ruta al archivo .wav
stdout: texto transcrito
"""
import sys
import torch
from qwenasr import Qwen3ASRModel

MODEL_DIR = "./models/Qwen3-ASR-0.6B"
audio_path = sys.argv[1]

model = Qwen3ASRModel.from_pretrained(MODEL_DIR, device_map="cpu", dtype=torch.float32)
result = model.transcribe(audio_path)
print(result.strip())
