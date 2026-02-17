# Hada Tu amiga IA de confianza

#TODO Optimizacion de tokens
# Cambiar la memoria para ahorrar en tokens
# uso promedio ahora 1000tokens por request
# si la memoria se amplia esto no va a aguantar
# con el millon de tokens diarios

#TODO Functions
# Lo mismo que en el otro script 
# wrapear todo en funciones para mantener el orden

#* Completado System prompt
# Separar el system prompt en un archivo diferente
# para mantener el orden dentro del codigo
# y tener una mejor manera de controlar el codigo

#TODO Tools
# Añadir herramientas de scripts separados
# para facilitar la lectura de archivos
# por ejemplo para leer la memoria
# o el system prompt
#* Completado leer System Prompt

#TODO Continued
# Continuar enviando el mensaje 
# y que no se pare al enviar un solo mensaje

#TODO STT & TTS
# BAJA PRIORIDAD

from dotenv import load_dotenv
from os import getenv
from cerebras.cloud.sdk import Cerebras
from re import search, DOTALL
from json import dumps, loads
from pathlib import Path

from tools import hada_system

# Load .env file into space
load_dotenv()

# AI Memory path
MEMORY = Path("mem/memory.hada")
if not MEMORY.exists(): # Creates the file if not exists
    with MEMORY.open("w", encoding="utf-8") as f:
        f.write(dumps({}))

# Reads the memory
mem = None
with open(MEMORY, "r", encoding="utf-8") as f:
    mem = dict(loads(f.read()))

# AI API Client
client = Cerebras(api_key=getenv("TOKEN"))

# User message
message = input("Tu: ")

# REQUEST
hada = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": hada_system(),
        },
        # {
        #     "role": "system",
        #     "content": "MEMORIA (SOLO LECTURA)" + dumps(mem),
        # },
        {
            "role": "user",
            "content": message,
        }
    ],
    model="gpt-oss-120b",
    max_completion_tokens=1000,
    temperature=1,
    top_p=1,
    reasoning_effort="low"
)

# Separates the AI response with theme and the content
print(hada.choices[0].message.content)
# response = search(r"<-(?P<theme>[^>]+)->\s*(?P<content>.*)", hada.choices[0].message.content, flags=DOTALL)
# theme = response["theme"]
# content = response["content"]

# # Saves the new content of the same theme together
# mem = None
# with open(MEMORY, "r", encoding="utf-8") as f:
#     mem = dict(loads(f.read()))
# if mem.get(theme) == None:
#     mem[theme] = []
# mem[theme].append(content)
# with open(MEMORY, "w", encoding="utf-8") as f:
#     f.write(dumps(mem, ensure_ascii=False, indent=2))

# # RESPONSE
# print(theme)
# print(content)

# EXAMPLE
# ChatCompletionResponse(
#     id='chatcmpl-99417c26-18a8-4100-ac72-ba7c1dc072b8', 
#     choices=[
#         ChatCompletionResponseChoice(
#             finish_reason='stop', 
#             index=0, 
#             message=ChatCompletionResponseChoiceMessage(
#                 role='assistant', 
#                 content='Hello! 👋 How can I assist you today?', 
#                 reasoning='We need to respond. The user just said "Hello". We should greet back. Possibly ask how can help. No specific instruction. Just friendly.', 
#                 tool_calls=None
#             ), 
#             logprobs=None, 
#             reasoning_logprobs=None
#         )
#     ], 
#     created=1771195917, 
#     model='gpt-oss-120b', 
#     object='chat.completion', 
#     system_fingerprint='fp_2d389d34367dd22b92f3', 
#     time_info=ChatCompletionResponseTimeInfo(
#         completion_time=0.025622551, 
#         prompt_time=0.001376392, 
#         queue_time=0.003943507, 
#         total_time=0.03223156929016113, 
#         created=1771195917.383853
#     ), 
#     usage=ChatCompletionResponseUsage(
#         completion_tokens=51, 
#         completion_tokens_details=ChatCompletionResponseUsageCompletionTokensDetails(
#             accepted_prediction_tokens=0, 
#             rejected_prediction_tokens=0, 
#             reasoning_tokens=0
#         ), 
#         prompt_tokens=68, 
#         prompt_tokens_details=ChatCompletionResponseUsagePromptTokensDetails(
#             cached_tokens=0
#         ), 
#         total_tokens=119), 
#     service_tier=None
# )