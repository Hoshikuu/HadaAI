from dotenv import load_dotenv
from os import getenv
from cerebras.cloud.sdk import Cerebras
from re import search, DOTALL
from json import dumps, loads
from pathlib import Path

load_dotenv()

MEMORY = Path("memory.hada")
if not MEMORY.exists():
    with MEMORY.open("w", encoding="utf-8") as f:
        f.write(dumps({}))

client = Cerebras(api_key=getenv("TOKEN"))

message = input("Tu: ")

hada = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": """
            You are Hada, 
            You are created by Hoshiku, 
            You are helpful, 
            Always answer in Spanish
            Always answer briefly,
            Always include the theme at the start with <-THEME->
            """,
        },
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

response = search(r"<-(?P<theme>[^>]+)->\s*(?P<content>.*)", hada.choices[0].message.content, flags=DOTALL)

theme = response["theme"]
content = response["content"]

mem = None
with open(MEMORY, "r", encoding="utf-8") as f:
    mem = dict(loads(f.read()))
if mem.get(theme) == None:
    mem[theme] = []
mem[theme].append(content)
print(mem)

with open(MEMORY, "w", encoding="utf-8") as f:
    f.write(dumps(mem))

print(theme)
print(content)

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