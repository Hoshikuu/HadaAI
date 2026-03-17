from openai import OpenAI

from reader import SystemPrompt

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="no-key"
)

stream = client.chat.completions.create(
    model="Hoshiku/HadaAI",
    messages=[
        {"role": "system", "content": SystemPrompt()},
        {"role": "user", "content": "patata?"}
    ],
    stream=True,
)

for chunk in stream:
    text = chunk.choices[0].delta.content or ""
    print(text, end="", flush=True)
