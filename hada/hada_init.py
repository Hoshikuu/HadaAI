#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/hada_init.py - V0.1.1

from winpty import PtyProcess
from asyncio import sleep
from tools.reader import LlamaCommand

EXECUTE = True

async def StartHada():
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

    # Ejecuta lo que viene siendo el comando para iniciar a Hada
    proc.write(LlamaCommand() + '\r\n')

    print("Hada is still loading...")
    await sleep(5)

    print("Hada is Online.")

    # Mantiene la subterminal viva hasta que EXECUTE este en False
    while EXECUTE and proc.isalive():
        await sleep(5) # Tiempo que se espera hasta el siguiente check, aumentar el numero para menor cantidad de checks

    # Cierra la conexion
    proc.close()

    print("Hada is Offline.")

def StopHada():
    global EXECUTE
    EXECUTE = False