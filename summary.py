# MAYBE CHANGE THIS SUMARIZE FUNCTION TO A LOCAL 8B IA
# CAUSE THIS MAYBE WILL NEED SO MUCH TOKENS

#TODO Resumen de memoria
# Mejorar el sistema actual de resumido de memoria, ya que gasta muchos tokens
# la hora de enviar los mensajes a Hada.
# NO HACER un JSON entero sacar lo mas valioso del texto sin decoradores ni otras cosas
# sacar por facts sobre el usuario y temas pero que tambien sean facts
# "La IA “amiga” genera texto bonito; la memoria guarda esencia, no el texto bonito."
# Recuerda eso, hay que meter la memoria en claro, no todo resumido.

#* Completado System prompt
# El contenido de system, separarlo en otro archivo para modificarlo de una manera mas rapida
# manteniendo el codigo mas corto y mas limpio

#TODO Functions
# Wrapear todo en alguna funcion y hacer que se llame
# en vez de tenerlo todo lineal suelto

#TODO Keys
# Aumentar la eficacia de la memoria con otro diseño
# cambiar el formato seguramente y recordar cambiarlo en el main tambien

from dotenv import load_dotenv
from os import getenv
from cerebras.cloud.sdk import Cerebras
from json import dumps, loads
from pathlib import Path

from tools import summary_system

# Load .env file into space
load_dotenv()

# AI Memory path
MEMORY = Path("mem/memory.hada")
if not MEMORY.exists(): # Creates the file if not exists
    with MEMORY.open("w", encoding="utf-8") as f:
        f.write(dumps({}))

# Reads the unsummarized memory
mem = None
with open(MEMORY, "r", encoding="utf-8") as f:
    mem = dict(loads(f.read()))

# AI API Client
client = Cerebras(api_key=getenv("TOKEN"))

# REQUEST
# Summarize the content of her memory
hada = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": summary_system(),
        },
        {
            "role": "user",
            "content": dumps(mem),
        }
    ],
    model="gpt-oss-120b",
    max_completion_tokens=2500,
    temperature=1,
    top_p=1,
    reasoning_effort="low"
)

# Saves the changes into her memory
mem = loads(hada.choices[0].message.content)
print(mem)
with open(MEMORY, "w", encoding="utf-8") as f:
    f.write(dumps(mem, ensure_ascii=False, indent=2))