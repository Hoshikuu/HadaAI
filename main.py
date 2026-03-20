#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/main.py - V0.0.3

from asyncio import run, sleep as asleep, create_task, get_event_loop
from openai import OpenAI
from hada import Hada

def HadaPrompt(version):
    with open(f"prompts/hadaV{version}.txt", "r") as f:
        return f.read()

def query_hada(prompt: str):
    """Bloqueante, corre en thread."""
    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="no-key"
    )
    stream = client.chat.completions.create(
        model="Hoshiku/HadaAI",
        messages=[
            {"role": "system", "content": HadaPrompt(4)},
            {"role": "user", "content": prompt}
        ],
        extra_body={
            "chat_template_kwargs": {"enable_thinking": False},
        }, 
        stream=True,
    )
    response = ""
    for chunk in stream:
        text = chunk.choices[0].delta.content or ""
        print(text, end="", flush=True)
        response += text
    print()  # salto de línea al terminar
    return response

async def main():
    hada = Hada()
    loop = get_event_loop()
    task = create_task(hada.StartHada())

    await asleep(10)  # espera a que llama-server arranque

    # Consulta en thread para no bloquear el event loop
    response = await loop.run_in_executor(None, query_hada, "Quien eres?")

    hada.StopHada()
    await task

if __name__ == "__main__":
    run(main())