import sys
import json
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    BitsAndBytesConfig, StoppingCriteriaList, StopStringCriteria
)

MODEL_DIR = "./models/Qwen3-4B-Instruct-2507"
STOP_STRINGS = ["¿", "\n\n\n"]

payload = json.loads(sys.stdin.read())
messages = payload["messages"]
max_new_tokens = payload.get("max_new_tokens", 90)

bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
tok = AutoTokenizer.from_pretrained(MODEL_DIR, use_fast=False)
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, device_map="cuda:0", quantization_config=bnb)

# Tokenizar directamente desde apply_chat_template (sin pasar por tok())
input_ids = tok.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt"
).to(model.device)

attention_mask = torch.ones_like(input_ids)
inputs = {"input_ids": input_ids, "attention_mask": attention_mask}

stopping = StoppingCriteriaList([StopStringCriteria(tokenizer=tok, stop_strings=STOP_STRINGS)])

out = model.generate(
    **inputs,
    max_new_tokens=max_new_tokens,
    do_sample=True,
    temperature=0.55,
    top_p=0.9,
    stop_strings=STOP_STRINGS,
    tokenizer=tok,
    stopping_criteria=stopping,
    eos_token_id=tok.eos_token_id,
    pad_token_id=tok.eos_token_id,
)

new_tokens = out[0, input_ids.shape[1]:]
text = tok.decode(new_tokens, skip_special_tokens=True).strip()
text = text.split("¿")[0].rstrip(" ,;")
print(text)
