import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

MODEL_DIR = r"./models/Qwen3-TTS-12Hz-0.6B-CustomVoice"

model = Qwen3TTSModel.from_pretrained(MODEL_DIR, device_map="cpu", dtype=torch.float32)

wavs, sr = model.generate_custom_voice(
    text="¡Uff, hola! Un poquitín distraída, pero lista para brillar. ¿Qué travesura tienes en mente hoy?",
    language="Spanish",
    speaker="Ono_Anna",
    instruct="Tono dulce",
)

sf.write("out.wav", wavs[0], sr)
print("Generado out.wav", sr)
