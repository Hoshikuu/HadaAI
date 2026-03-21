#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/main.py - V0.0.5

from asyncio import run, sleep, create_task, get_event_loop
from openai import OpenAI
from hada import Hada, Stt, Register, Load

def HadaPrompt(version):
    with open(f"hada/prompts/hadaV{version}.txt", "r") as f:
        return f.read()

def query_hada(prompt: str):
    """Bloqueante, corre en thread."""
    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="no-key"
    )
    mem = Load()
    mess = [{"role": "system", "content": HadaPrompt(4)}]
    for m in mem:
        mess.append(m)
    mess.append({"role": "user", "content": prompt})
    stream = client.chat.completions.create(
        model="Hoshiku/HadaAI",
        messages=mess,
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
    stt = Stt()
    loop = get_event_loop()
    task = create_task(hada.StartHada())

    await sleep(10)  # espera a que llama-server arranque

    # Consulta en thread para no bloquear el event loop
    # prompt = stt.Start()
    prompt = "hada porque eres tan fria conmigo?"
    response = await loop.run_in_executor(None, query_hada, prompt)

    Register(prompt, response)

    hada.StopHada()
    await task
    stt.Stop()

if __name__ == "__main__":
    run(main())