#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/hada/hada_init.py - V0.2.3

from winpty import PtyProcess
from asyncio import sleep

class Hada():
    """Main class to execute Hada

    Methods\n
    |    -> StartHada()\n
    |    -> StopHada()\n
    |    -> MakeLlamaString()\n
    """
    def __init__(self, EXECUTE = True, model = "", host = "127.0.0.1", port = 8000):
        """Initializes all the variables for Hada

        Args:
            EXECUTE (bool, optional): Keep it alive. Defaults to True.
            model (str, optional): Model version. Defaults to "".
            host (str, optional): host ip. Defaults to "127.0.0.1".
            port (int, optional): host port. Defaults to 8000.
        """

        self.EXECUTE = EXECUTE  # True = continuar - False = parar
        self.model = model      # "" = normal - "agg" = descensurado
        self.llama_command = "" # Comando para ejecutar llama.cpp

        self.host = host        # Host
        self.port = port        # Port

        #! AI PARAM TWEAKING
        self.context = 16384    # Maximo de tokens para usarlo de contexto del modelo
        self.predict = 1024     # Maximo de tokens para poder generar texto
        self.threads = 8        # Maximo de hilos de CPU para usar
        self.gpu = 16           # Maximo de capas para ejecutar en GPU
        self.temp = 1.0         # Controla la aleatoriedad, 0 = determinista - 1 = creativo
        self.top_p = 1.0        # Selecciona suma de grupo mas pequeño 0.9 palabras al 90% descartando opciones raras
        self.top_k = 40         # Maxima cantidad de palabras seleccionadas, 40 solo selecciona 40
        self.min_p = 0.0        # Considera tokens cuya probabilidad sea como minimo el porcentaje
        self.presence = 2.0     # Penaliza tokens que ya han aparecido en el texto generado sin importar cuantas veces
        self.repeat = 1.0       # Penaliza tokens basandose en aparicion para evitar bucles infinitos

    def __str__(self):
        pass

    async def StartHada(self):
        """Starts Hada
        Executes a llama.cpp command for starting Hada on a Server.
        self.EXECUTE = True, maintains the PTY alive.
        time to wait until start 8 (3 + 5) seconds.
        """

        # Crea la subterminal que va a ejecutar a Hada con llama.cpp
        proc = PtyProcess.spawn(['cmd.exe'])

        # Estos 3 segundos de espera son obligatorios para que el siguiente comando se ejecute correctamente
        #! TE LO ESTOY AISANDO EN SERIO, CMD TARDA MUCHO EN INICIAR
        #? no puedes enviar un comando a una terminal que no esta cargada
        print(f"Hada will execute in 3 seconds...")
        await sleep(3)

        # Genera el comando dinamicamente segun los parametros de la clase
        self.MakeLlamaString()

        # Ejecuta lo que viene siendo el comando para iniciar a Hada
        #! HADA ERES UNA CABRONA
        proc.write(self.llama_command + '\r\n')

        # Espera 5 segundos mas antes de seguir, para que se termine de cargar el modelo entero
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
        """Stops Hada
        """
        # Solo cambia la variable de EXECUTE, para que al siguiente check se salga del loop infinito
        self.EXECUTE = False

    def MakeLlamaString(self):
        """Makes the String to execute Hada with llama.cpp
        """
        self.llama_command = ''
        args = [
            r'.\llama.cpp\build\bin\Release\llama-server.exe ',
            fr'--model "hada\models\HadaAI-{self.model}.gguf" ',
            '--alias "Hoshiku/HadaAI" ',
            f'--host {self.host} ',
            f'--port {self.port} ',
            f'--ctx-size {self.context} ',
            f'--predict {self.predict} ',
            f'--threads {self.threads} ',
            f'--gpu-layers {self.gpu} ',
            f'--temp {self.temp} ',
            f'--top-p {self.top_p} ',
            f'--top-k {self.top_k} ',
            f'--min-p {self.min_p} ',
            f'--presence-penalty {self.presence} ',
            f'--repeat-penalty {self.repeat} ',
            '--no-webui '
        ]
        for arg in args:
            self.llama_command += arg