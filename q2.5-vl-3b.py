import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

MODEL_DIR = r"./models/Qwen2.5-VL-3B-Instruct-AWQ"

# Presupuesto visual conservador para 8GB
min_pixels = 256 * 28 * 28
max_pixels = 512 * 28 * 28  # sube a 1024*28*28 si te sobra VRAM

processor = AutoProcessor.from_pretrained(
    MODEL_DIR,
    min_pixels=min_pixels,
    max_pixels=max_pixels,
)
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    MODEL_DIR,
    device_map="cuda:0",
    torch_dtype=torch.float16,
)

img = Image.open("test.png").convert("RGB")

messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": img},
            {"type": "text", "text": "¿Qué ves en la pantalla? Responde breve."},
        ],
    }
]

prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = processor(text=[prompt], images=[img], return_tensors="pt").to(model.device)

with torch.no_grad():
    out = model.generate(**inputs, max_new_tokens=80, do_sample=False)

print(processor.batch_decode(out, skip_special_tokens=True)[0])
