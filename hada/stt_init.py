#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/hada/stt_init.py - V0.1.0

from os import _exit
from RealtimeSTT import AudioToTextRecorderClient

# stt-server --model small --language es --device cpu --compute_type int8 --beam_size 5

class STT():
    def __init__(self):
        self.recorder = None

    def Start(self):
        if self.recorder is None:
            self.recorder = AudioToTextRecorderClient(
                control_url="ws://127.0.0.1:8011",
                data_url="ws://127.0.0.1:8012",
                language="es",
            )

        text = self.recorder.text()
        if text:
            return text.strip()

    def Stop(self):
        if self.recorder is not None:
            try:
                self.recorder.shutdown()
            except Exception:
                pass
            self.recorder = None
        _exit(0)