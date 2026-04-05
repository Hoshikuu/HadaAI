# HADA AI

Small silly AI, will be your companion for now, it's a fun model i created for fun, not for serious use, i just want to try to create something new

Please read [index](_index.md) for full walkthrough of the repo

Small local LLM
- Qwen3.5 9B
- Quantized to 4bits medium -> 4Q_K_M

Runned and executed with llama.cpp
- Build B8263

Minimum Requirements
- Python >= 3.11 (have not tried with lower versions)
- GPU with CUDA at least 6GB VRAM
- CPU with 8Gb RAM

## For now this code doesn't download the models yet, i will work on that, also doesn't downloads the voices neither the piper or llama.cpp

```
├── 📁 .venv
├── 📁 hada
│   ├── 📁 mem
│   │   └── 📝 _index.md
│   ├── 📁 models
│   │   ├── 📄 HadaAI-.gguf
│   │   ├── 📄 HadaAI-agg.gguf
│   │   ├── 📄 mmproj-.gguf
│   │   ├── 📄 mmproj-agg.gguf
│   │   └── 📝 _index.md
│   ├── 📁 piper
│   ├── 📁 prompts
│   │   ├── 📁 others
│   │   │   └── 📝 _index.md
│   │   ├── 📁 system
│   │   │   ├── 📝 _index.md
│   │   │   ├── 📄 hadaV1.txt
│   │   │   ├── 📄 hadaV2.txt
│   │   │   ├── 📄 hadaV3.txt
│   │   │   ├── 📄 hadaV4.txt
│   │   │   ├── 📄 hadaV5.txt
│   │   │   ├── 📄 hadaV6.1.txt
│   │   │   ├── 📄 hadaV6.2.txt
│   │   │   └── 📄 hadaV6.3.txt
│   │   └── 📝 _index.md
│   ├── 📁 voices
│   │   ├── 📄 es_ES-sharvard-medium.onnx
│   │   ├── ⚙️ es_ES-sharvard-medium.onnx.json
│   │   └── 📝 _index.md
│   ├── 🐍 __init__.py
│   ├── 📝 _index.md
│   ├── 🐍 hada_init.py
│   ├── 🐍 mem_init.py
│   ├── 🐍 stt_init.py
│   ├── 🌐 tts_dev_panel.html
│   └── 🐍 tts_init.py
├── 📁 llama.cpp
├── 📁 TasksTool
│   ├── 📁 templates
│   │   └── 🌐 index.html
│   ├── ⚙️ .gitignore
│   ├── 📄 LICENSE
│   ├── 📝 README.md
│   ├── 🐍 main.py
│   └── 📄 requirements.txt
├── ⚙️ .gitignore
├── 📄 LICENSE
├── 📝 README.md
├── 📝 _index.md
├── 🐍 main.py
└── 📄 requirements.txt
```