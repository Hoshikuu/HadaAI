#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/hada/stt_init.py - V0.2.1

from subprocess import Popen as proc, PIPE, STDOUT, CREATE_NEW_PROCESS_GROUP, TimeoutExpired
from threading import Thread
from signal import CTRL_BREAK_EVENT
from datetime import datetime

class STT:
    """# STT MODULE\n
    ## Initilizes the Server and the Client\n
    - start -> Starts the server\n
    - play -> Records the audio to convert to text\n
    - stop -> Stops the server and client\n
    """
    def __init__(self):
        """STT Constructor
        """
        self.proc = None
        self.recorder = None

        self.setup = False

        # La primera vez que ejecutes el STT te saldra un mensaje para tener que confiar en el repositorio
        # Esto le dice al programa que detectar para hacer el envio de un "y" para aceptar
        self.confirm_key = "(y/N)?"

        # Le dice al programa que detectar para comprobar que el STT se haya iniciado completamente
        self.start_key = "RealtimeSTT initialized"
        self.log("Init STT", "info")

    def log(self, text: str, extra: str = "unspecified"):
        """STT MODULE Logger, logs the given text

        Args:
            text (str): The text to log
            extra (str, optional): The type of the log. Defaults to "unspecified".
        """
        with open(f"logs/stt-{datetime.now().date()}.log", "a", encoding="utf-8") as f:
            lines = text.split("\n")
            for line in lines:
                # Formato del logger
                # [CATEGORIA] [TIEMPO] [TEXTO]
                if line == "":
                    continue
                f.write(f"[{extra.upper()}] [{datetime.now().time()}] {line}\n")
        if extra.upper() == "ERROR":
            print("Ha ocurrido un error inesperado, consulta el log para mas informacion")

    def start(self):
        """# Starts the STT Server\n
        ## With the next given set of args\n
        - stt-server --model small --language es --device cuda --compute_type int8 --beam_size 5
        """
        self.log("Constructing STT Args", "info")
        cmd = [
            "stt-server",
            "--model", "small",
            "--language", "es",
            "--device", "cuda",
            "--compute_type", "int8",
            "--beam_size", "5"
        ]

        self.log("Starting STT Subprocess", "info")
        # Esto usa Popen de subprocess, para abrir una nueva terminal con los comandos dados, con pipelines de I/O
        self.proc = proc(
            cmd,
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
            text=True,
            bufsize=1,
            creationflags=CREATE_NEW_PROCESS_GROUP
        )

        self.log("Executing Read Thread", "info")
        # Ejecuta en un thread aparte la lectura del Out del subproceso que acabamos de crear para monitorear su estado
        Thread(target=self.read, daemon=True).start()

    def read(self):
        """Reads the Subprocess Out
        """
        try:
            # Buffer para guardar el caracter leido
            buffer = ""

            while self.proc and self.proc.poll() is None:
                try:
                    # Leemos por caracter porque leer por linea da error si la terminal esta esperando un valor
                    char = self.proc.stdout.read(1)
                    buffer += char

                    # Cuando se llega a final de linea guardamos el buffer y lo limpiamos
                    if char == "\n":
                        self.log(buffer, "info")
                        buffer = ""

                    line = buffer.lower()

                    # Comprobamos los diferentes estados que necesitamos
                    if self.confirm_key.lower() in line:
                        buffer += "y\n"
                        self.log(buffer, "info")
                        buffer = ""
                        if not self.send("y"):
                            break

                    if self.start_key.lower() in line:
                        # Cambia esta variable para saber que ha terminado por completo la carga del STT
                        self.setup = True
                        break # Salimos del bucle porque ya no necesitamos leer mas una vez cargado entero
                except Exception as e:
                    self.log(e, "error")
                    break
        except Exception as e:
            self.log(e, "error")
            return

    def send(self, text: str):
        """Sends text to the subprocess

        Args:
            text (str): Text to send
        """
        try:
            self.log("Sending Text", "info")
            if self.proc and self.proc.poll() is None and self.proc.stdin:
                self.proc.stdin.write(text + "\n")
                self.proc.stdin.flush()
                return True
            self.log("Maybe subprocess is not active?? How did you get here??", "warning")
            return False
        except Exception as e:
            self.log(e, "error")
            return False

    def play(self):
        """Executes the client for catching the voice and convert it to text

        Returns:
            str: Return the text heard
        """
        try:
            self.log("Recording audio ...", "info")
            if self.recorder is None:
                print("Recorder not initilized - Watch AudioToTextRecorderClient")
                self.log("No recorder found", "warning")
                return None

            text = self.recorder.text()
            if text is not None:
                self.log(f"Audio detected - {text.strip()}", "info")
                return text.strip()
            return None
        except Exception as e:
            self.log(e, "error")
            return None

    def stop(self):
        self.log("Issued STT stop", "info")
        if not self.proc or self.proc.poll() is not None:
            return

        if self.recorder is not None:
            try:
                self.recorder.shutdown()
                self.log("Recorder stop", "info")
            except Exception as e:
                self.log(e, "error")
            self.recorder = None

        try:
            self.log("Sending stop command in server", "info")
            self.proc.send_signal(CTRL_BREAK_EVENT)
            self.proc.wait(timeout=5)
        except TimeoutExpired:
            self.proc.kill()
            self.log("STT forced kill", "warning")
        self.log("Server stop", "info")

# EXAMPLE OF USE
# from RealtimeSTT import AudioToTextRecorderClient
# from os import devnull
# from contextlib import redirect_stdout, redirect_stderr
# from time import sleep
# if __name__ == "__main__":
#     server = STT()
#     server.start()
#     try:
#         while True:
#             if not server.setup:
#                 sleep(1)
#                 continue
#             if server.recorder is None:
#                 # SILENCIAR EL MODULO
#                 with open(devnull, "w") as fnull:
#                     with redirect_stdout(fnull), redirect_stderr(fnull):
#                         server.recorder = AudioToTextRecorderClient(
#                             control_url="ws://127.0.0.1:8011",
#                             data_url="ws://127.0.0.1:8012",
#                             language="es",
#                         )
#             print("Recording ...")
#             text = server.play()
#             print(text)
#     except KeyboardInterrupt:
#         server.stop()