#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/hada/stt_init.py - V0.1.2

from asyncio import sleep
from RealtimeSTT import AudioToTextRecorderClient
from winpty import PtyProcess

class Stt():
    def __init__(self, EXECUTE = True):
        self.EXECUTE = EXECUTE
        self.recorder = None

    async def StartStt(self):
        proc = PtyProcess.spawn(['cmd.exe'])

        print("STT will be availeble in 3 seconds...")
        await sleep(3)
        
        proc.write("stt-server --model small --language es --device cpu --compute_type int8 --beam_size 5" + "\r\n")
        
        print("STT is loading...")
        await sleep(3)

        print("STT is UP")

        while self.EXECUTE and proc.isalive():
            await sleep(5)

        proc.close()

        print("STT OFF")

    def Play(self):
        if self.recorder is None:
            self.recorder = AudioToTextRecorderClient(
                control_url="ws://127.0.0.1:8011",
                data_url="ws://127.0.0.1:8012",
                language="es",
            )

        text = self.recorder.text()
        if text:
            return text.strip()

    def StopStt(self):
        self.EXECUTE = False

    def Pause(self):
        if self.recorder is not None:
            try:
                self.recorder.shutdown()
            except Exception:
                pass
            self.recorder = None