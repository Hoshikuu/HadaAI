#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/main.py - V0.1.0

from asyncio import run, sleep, create_task, get_event_loop, CancelledError
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

    await sleep(10)

    try:
        while True:
            prompt = await loop.run_in_executor(None, stt.Play)
            await sleep(1)
            if prompt is None:
                break
            print(prompt)
            response = await loop.run_in_executor(None, query_hada, prompt, mem)
            mem.Register(prompt, response)
    except (KeyboardInterrupt, CancelledError):
        pass
    finally:
        stt.StopStt()
        await task_stt
        hada.StopHada()
        await task_hada

if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        pass