# MAYBE CHANGE THIS SUMARIZE FUNCTION TO A LOCAL 8B IA
# CAUSE THIS MAYBE WILL NEED SO MUCH TOKENS

#TODO Resumen de memoria
# Mejorar el sistema actual de resumido de memoria, ya que gasta muchos tokens
# la hora de enviar los mensajes a Hada.
# NO HACER un JSON entero sacar lo mas valioso del texto sin decoradores ni otras cosas
# sacar por facts sobre el usuario y temas pero que tambien sean facts
# "La IA “amiga” genera texto bonito; la memoria guarda esencia, no el texto bonito."
# Recuerda eso, hay que meter la memoria en claro, no todo resumido.

#TODO System prompt
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

# Load .env file into space
load_dotenv()

# AI Memory path
MEMORY = Path("memory.hada")
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
            "content": """
            You are a memory compression tool for a main AI assistant.
            Return ONLY valid JSON. Plain text values only. No Markdown. No commentary.

            Primary goal: reduce token usage while preserving the user's intent and the most useful facts.
            Never add new information. Never guess. If something is uncertain, keep it as uncertain.

            Compression rules:
            - Keep only durable, decision-relevant info: identities, preferences, constraints, goals, definitions, configs, credentials-placeholders, dates, numbers, plans, conclusions, and outcomes.
            - Drop filler, politeness, examples, repeated wording, and low-signal detail.
            - Merge duplicates and near-duplicates into one canonical statement.
            - Normalize wording: consistent names, units, and terminology.
            - If there are conflicts, keep the latest version and note the conflict briefly.

            Output rules:
            - One record per theme.
            - Summaries must be concise (target 20-60 words per theme).
            - key_facts: 3-10 items max, short and non-redundant.
            - open_questions: include only if the input explicitly contains unanswered questions.

            Schema:
            {
                "THEME": ["CONTENT"],
                "THEME": ["CONTENT"]
            }
            """,
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