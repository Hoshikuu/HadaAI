#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/main.py - V0.0.6

from asyncio import run, sleep, create_task, get_event_loop
from openai import OpenAI
from hada import Hada, Stt, Mem

def HadaPrompt(version):
    with open(f"hada/prompts/hadaV{version}.txt", "r") as f:
        return f.read()

def query_hada(prompt: str, mem: Mem):
    """Bloqueante, corre en thread."""
    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="no-key"
    )
    memories = mem.ReadMem()
    messages = [{"role": "system", "content": HadaPrompt(4)}]
    for memory in memories:
        messages.append(memory)
    messages.append({"role": "user", "content": prompt})
    stream = client.chat.completions.create(
        model="Hoshiku/HadaAI",
        messages=messages,
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
    mem = Mem()
    loop = get_event_loop()
    task_hada = create_task(hada.StartHada())
    task_stt = create_task(stt.StartStt())

    await sleep(10)  # espera a que llama-server arranque

    # Consulta en thread para no bloquear el event loop
    prompt = await loop.run_in_executor(None, stt.Play)
    print(prompt)
    await loop.run_in_executor(None, stt.Pause)
    # prompt = "hada porque eres tan fria conmigo?"

    response = await loop.run_in_executor(None, query_hada, prompt, mem)

    mem.Register(prompt, response)

    stt.StopStt()
    await task_stt
    hada.StopHada()
    await task_hada

if __name__ == "__main__":
    run(main())