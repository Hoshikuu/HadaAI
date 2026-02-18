import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration, BitsAndBytesConfig

MODEL_DIR = r"./models/Qwen2.5-VL-3B-Instruct"
MIN_PIXELS = 256 * 28 * 28
MAX_PIXELS = 512 * 28 * 28

_model = None
_processor = None

def _load():
    global _model, _processor
    if _model is None:
        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        _processor = AutoProcessor.from_pretrained(
            MODEL_DIR,
            min_pixels=MIN_PIXELS,
            max_pixels=MAX_PIXELS,
            use_fast=False,
        )
        _model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            MODEL_DIR,
            device_map="cuda:0",
            quantization_config=bnb,
        )

def describe_image(image_path: str, question: str = "¿Qué ves? Responde en 1-2 frases.") -> str:
    _load()
    img = Image.open(image_path).convert("RGB")
    messages = [{"role": "user", "content": [
        {"type": "image", "image": img},
        {"type": "text", "text": question},
    ]}]
    prompt = _processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = _processor(text=prompt, images=img, return_tensors="pt").to(_model.device)
    with torch.no_grad():
        out = _model.generate(**inputs, max_new_tokens=80, do_sample=False)
    return _processor.batch_decode(out, skip_special_tokens=True)[0].strip()

def unload():
    """Libera VRAM cuando no se necesita VL."""
    global _model, _processor
    import gc
    _model = None
    _processor = None
    gc.collect()
    torch.cuda.empty_cache()
