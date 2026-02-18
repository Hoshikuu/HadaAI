import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    BitsAndBytesConfig, StoppingCriteriaList, StopStringCriteria
)

MODEL_DIR = "./models/Qwen3-4B-Instruct-2507"
STOP_STRINGS = ["¿", "\n\n\n"]

_tok = None
_model = None

def _load():
    global _tok, _model
    if _model is None:
        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        _tok = AutoTokenizer.from_pretrained(MODEL_DIR, use_fast=True)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_DIR,
            device_map="cuda:0",
            quantization_config=bnb,
        )

def generate(messages: list, max_new_tokens: int = 80) -> str:
    _load()
    prompt = _tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = _tok(prompt, return_tensors="pt").to(_model.device)

    stopping = StoppingCriteriaList([
        StopStringCriteria(tokenizer=_tok, stop_strings=STOP_STRINGS)
    ])

    out = _model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.55,
        top_p=0.9,
        stop_strings=STOP_STRINGS,
        tokenizer=_tok,
        stopping_criteria=stopping,
        eos_token_id=_tok.eos_token_id,
        pad_token_id=_tok.eos_token_id,
    )

    new_tokens = out[0, inputs["input_ids"].shape[1]:]
    text = _tok.decode(new_tokens, skip_special_tokens=True).strip()
    # Corta si aparece "¿" suelto al final
    text = text.split("¿")[0].rstrip(" ,;")
    return text
