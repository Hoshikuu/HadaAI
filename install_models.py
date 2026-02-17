from huggingface_hub import snapshot_download, login

login()

snapshot_download("Qwen/Qwen3-4B-Instruct-2507", local_dir="./models/Qwen3-4B-Instruct-2507")
snapshot_download("Qwen/Qwen3-ASR-0.6B", local_dir="./models/Qwen/Qwen3-ASR-0.6B")
snapshot_download("Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice", local_dir="./models/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice")
snapshot_download("Qwen/Qwen2.5-VL-3B-Instruct-AWQ", local_dir="./models/Qwen/Qwen2.5-VL-3B-Instruct-AWQ")