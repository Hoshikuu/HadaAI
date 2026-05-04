from hada.new_hada_init import HADA
from hada.stt_init import STT
from hada.tts_init import speak
from hada.mem_init import Mem
from time import sleep
from RealtimeSTT import AudioToTextRecorderClient
from os import devnull
from contextlib import redirect_stdout, redirect_stderr

if __name__ == "__main__":
    
    hada = HADA()

    print("cargando hada")

    hada.start()

    while not hada.setup:
        sleep(1)

    stt = STT()

    print("cargando stt")

    stt.start()

    while not stt.setup:
        sleep(1)

    print("cargando tts")

    speak("Testeo")

    print("iniciando cliente stt")

    if stt.recorder is None:
        # SILENCIAR EL MODULO
        with open(devnull, "w") as fnull:
            with redirect_stdout(fnull), redirect_stderr(fnull):
                stt.recorder = AudioToTextRecorderClient(
                    control_url="ws://127.0.0.1:8011",
                    data_url="ws://127.0.0.1:8012",
                    language="es",
                )
    print("Recording ...")
    text = stt.play()
    print(text)

    mem = Mem()

    response = hada.ask(text, mem)

    speak(response)

    sleep(15)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        stt.stop()
        hada.stop()
