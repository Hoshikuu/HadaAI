import torch
from qwen_asr import Qwen3ASRModel

MODEL_DIR = r"./models/Qwen3-ASR-0.6B"  # o "Qwen/Qwen3-ASR-0.6B"

model = Qwen3ASRModel.from_pretrained(
    MODEL_DIR,
    device_map="cpu",
    dtype=torch.float32,
)

# Puedes pasar ruta local (según el README soporta path/URL/base64/(np,sr))
result = model.transcribe(audio=["test.wav"])
print(result)
