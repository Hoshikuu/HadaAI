#!/usr/bin/env python
"""
argv[1]: ruta imagen
argv[2]: pregunta (opcional)
stdout: descripción JSON {"description": "..."}
"""
import sys
import json
import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration, BitsAndBytesConfig

MODEL_DIR = "./models/Qwen2.5-VL-3B-Instruct"
image_path = sys.argv[1]
question = sys.argv[2] if len(sys.argv) > 2 else "¿Qué ves? Responde en 1-2 frases."

bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
processor = AutoProcessor.from_pretrained(MODEL_DIR, min_pixels=256*28*28, max_pixels=512*28*28, use_fast=False)
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(MODEL_DIR, device_map="cuda:0", quantization_config=bnb)

img = Image.open(image_path).convert("RGB")
messages = [{"role": "user", "content": [{"type": "image", "image": img}, {"type": "text", "text": question}]}]
prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = processor(text=prompt, images=img, return_tensors="pt").to(model.device)

with torch.no_grad():
    out = model.generate(**inputs, max_new_tokens=80, do_sample=False)

text = processor.batch_decode(out, skip_special_tokens=True)[0].strip()
print(json.dumps({"description": text}, ensure_ascii=False))
