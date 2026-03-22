#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/hada/stt_init.py - V0.1.4

from asyncio import sleep
from RealtimeSTT import AudioToTextRecorderClient
from winpty import PtyProcess

class Stt():
    """Speach to text class

    Methods\n
    |    -> StartStt()\n
    |    -> StopStt()\n
    |    -> Play()\n
    """
    def __init__(self, EXECUTE = True):
        self.EXECUTE = EXECUTE
        self.recorder = None

    async def StartStt(self):
        """Starts the stt server in a PTY
        """
        # Crea el cmd para poder ejecutar el servidor
        proc = PtyProcess.spawn(['cmd.exe'])

        # Espera el tiempo necesario para que cmd se termine de ejecutar
        print("STT will execute in 3 seconds...")
        await sleep(3)

        # Una vez que el cmd este listo, ejecuta el comando para ejecutar el stt
        proc.write("stt-server --model small --language es --device cpu --compute_type int8 --beam_size 5\r\n")

        # Espera 8 segundos para que se termine de cargar el Stt
        print("STT is loading...")
        await sleep(8)
        print("STT is ON")

        # Mantiene la terminal viva hasta que se apague
        while self.EXECUTE and proc.isalive():
            await sleep(5)

        # Desconectamos el cliente antes de cerrar el servidor para evitar mensajes de error
        if self.recorder is not None:
            try:
                self.recorder.shutdown()
            except Exception:
                pass
            self.recorder = None

        # Esperamos 1 segundo y cerramos el servidor
        await sleep(1)
        proc.close()
        print("STT is OFF")

    def Play(self):
        """The Stt client to connect to the stt server

        Returns:
            str: Return the processed stt text
        """
        # Conexion al servidor stt
        if self.recorder is None:
            self.recorder = AudioToTextRecorderClient(
                control_url="ws://127.0.0.1:8011",
                data_url="ws://127.0.0.1:8012",
                language="es",
            )
        
        # Esto es bloqueante se queda esperando hasta conseguir un texto
        try:
            text = self.recorder.text()
            if text: # Si detecta texto devuelve el texto
                return text.strip()
            return None # Cualquier otra cosa devuelve None
        except Exception:
            return None

    def StopStt(self):
        """Para el servidor Stt
        """
        self.EXECUTE = False