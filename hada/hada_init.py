#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/hada_init.py - V0.2.1

from winpty import PtyProcess
from asyncio import sleep

class Hada():
    """Main class to execute Hada
    """
    def __init__(self, EXECUTE = True, model = "", host = "127.0.0.1", port = 8000):
        self.EXECUTE = EXECUTE
        self.model = model
        self.llama_command = ""

        self.host = host
        self.port = port

        # AI TWEAKING
        self.context = 16384
        self.predict = 1024
        self.threads = 8
        self.gpu = 16
        self.temp = 1.0
        self.top_p = 1.0
        self.top_k = 40
        self.min_p = 0.0
        self.presence = 2.0
        self.repeat = 1.0

    def __str__(self):
        pass

    async def StartHada(self):
        """Executes Hada
        llama.cpp command that execute in --> commands/llama.cpp-auto.txt --> contains a string that initializes the llama server
        EXECUTE var mantains this pty alive until StopHada is called
        time till start 8 seconds.
        """

        # Crea la subterminal que va a ejecutar a Hada con llama.cpp
        proc = PtyProcess.spawn(['cmd.exe'])

        # Espera 10 segundos iniciales para que la terminal se termine de cargar
        # Si no se espera el tiempo suficiente el siguiente comando no se ejecutara correctamente

        print(f"Hada will execute in 3 seconds...")
        await sleep(3)

        self.MakeLlamaString()
        # Ejecuta lo que viene siendo el comando para iniciar a Hada
        proc.write(self.llama_command + '\r\n')

        print("Hada is still loading...")
        await sleep(5)

        print("Hada is Online.")

        # Mantiene la subterminal viva hasta que EXECUTE este en False
        while self.EXECUTE and proc.isalive():
            await sleep(5) # Tiempo que se espera hasta el siguiente check, aumentar el numero para menor cantidad de checks

        # Cierra la conexion
        proc.close()

        print("Hada is Offline.")

    def StopHada(self):
        self.EXECUTE = False

    def MakeLlamaString(self):
        self.llama_command = ''
        self.llama_command += r'.\llama.cpp\build\bin\Release\llama-server.exe '
        self.llama_command += fr'--model "hada\models\HadaAI-{self.model}.gguf" '
        self.llama_command += '--alias "Hoshiku/HadaAI" '
        self.llama_command += f'--host {self.host} '
        self.llama_command += f'--port {self.port} '
        self.llama_command += f'--ctx-size {self.context} '
        self.llama_command += f'--predict {self.predict} '
        self.llama_command += f'--threads {self.threads} '
        self.llama_command += f'--gpu-layers {self.gpu} '
        self.llama_command += f'--temp {self.temp} '
        self.llama_command += f'--top-p {self.top_p} '
        self.llama_command += f'--top-k {self.top_k} '
        self.llama_command += f'--min-p {self.min_p} '
        self.llama_command += f'--presence-penalty {self.presence} '
        self.llama_command += f'--repeat-penalty {self.repeat} '
        self.llama_command += '--no-webui '