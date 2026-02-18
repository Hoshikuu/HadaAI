import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

MODEL_DIR = "./models/Qwen3-4B-Instruct-2507"

bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

tok = AutoTokenizer.from_pretrained(MODEL_DIR, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    device_map="cuda:0",
    quantization_config=bnb,
)

messages = [
    {"role": "system", "content": "Eres una waifu cariñosa y juguetona. Hablas español."},
    {"role": "user", "content": "Preséntate en 2 frases."},
]

prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tok(prompt, return_tensors="pt").to(model.device)

out = model.generate(
    **inputs,
    max_new_tokens=120,
    do_sample=True,
    temperature=0.8,
    top_p=0.9,
)
print(tok.decode(out[0], skip_special_tokens=True))
