"""
Hada - Entry point
Modos:
  python main.py          → chat de texto puro
  python main.py --voice  → ASR (mic) + TTS (audio out)
  python main.py --image path/img.png  → turno con visión
"""
import argparse
import uuid
from pipeline import run_turn
import budget

SESSION_ID = str(uuid.uuid4())[:8]
history = []

def print_budget():
    remaining = budget.remaining()
    mode = budget.budget_mode()
    print(f"  [Budget: {remaining:,} tokens restantes | modo: {mode}]")

def text_loop(image_path: str = None):
    print("Hada lista. Escribe 'exit' para salir, 'budget' para ver tokens.\n")
    while True:
        try:
            user_input = input("Tu: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        if user_input.lower() == "budget":
            print_budget()
            continue

        response = run_turn(
            user_text=user_input,
            history=history,
            session_id=SESSION_ID,
            image_path=image_path,
        )
        image_path = None  # VL solo en el primer turno con imagen

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

        print(f"Hada: {response}\n")

def voice_loop():
    from asr import transcribe
    from tts import speak
    import sounddevice as sd
    import soundfile as sf
    import numpy as np

    FS = 16000
    DUR = 5
    print("Modo voz activo. Ctrl+C para salir.\n")

    while True:
        try:
            input("[ Pulsa Enter para hablar... ]")
            print("Grabando...")
            audio = sd.rec(int(DUR * FS), samplerate=FS, channels=1, dtype="float32")
            sd.wait()
            sf.write("tmp_input.wav", audio, FS)

            user_text = transcribe("tmp_input.wav")
            if not user_text:
                print("No entendí nada, repite.")
                continue
            print(f"Tu: {user_text}")

            response = run_turn(
                user_text=user_text,
                history=history,
                session_id=SESSION_ID,
            )
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": response})

            print(f"Hada: {response}")
            audio_path = speak(response)

            data, sr = sf.read(audio_path)
            sd.play(data, sr)
            sd.wait()

        except KeyboardInterrupt:
            print("\nHasta luego.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice", action="store_true", help="Modo voz (ASR + TTS)")
    parser.add_argument("--image", type=str, default=None, help="Ruta a imagen para VL")
    args = parser.parse_args()

    print_budget()
    if args.voice:
        voice_loop()
    else:
        text_loop(image_path=args.image)
