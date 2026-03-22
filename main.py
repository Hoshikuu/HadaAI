#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/main.py - V0.1.1

from asyncio import run, sleep, create_task, get_event_loop, CancelledError
from openai import OpenAI
from hada import Hada, Stt, Mem

def HadaPrompt(version: int):
    """Reads the Hada System Prompt

    Args:
        version (int): The version of Hada System Prompt

    Returns:
        str: The content of that specific version
    """
    # Lee el archivo dependiendo de la version indicada
    with open(f"hada/prompts/hadaV{version}.txt", "r") as f:
        return f.read()

def QueryHada(prompt: str, mem: Mem):
    """Query to ask to Hada

    Args:
        prompt (str): The prompt string to pass it to Hada
        mem (Mem): The memory class initilized in main

    Returns:
        str: The response of Hada
    """

    # Url donde este hosteado Hada
    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="no-key"
    )

    # Lee la memorua de Hada
    memories = mem.ReadMem()
    # Añade el system prompt
    messages = [{"role": "system", "content": HadaPrompt(4)}]
    # Añade el historial de mensajes de la memoria a mensajes
    for memory in memories:
        messages.append(memory)
    # Añade el ultimo mensaje solicitado
    messages.append({"role": "user", "content": prompt})

    # Hace la solicitud a Hada
    stream = client.chat.completions.create(
        model="Hoshiku/HadaAI",
        messages=messages,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": False}, # Desactiva el Thinking de Hada
        }, 
        stream=True, # Devuelve el texto en trozos
    )

    # Procesamiento de la respuesta
    response = ""
    for chunk in stream:
        text = chunk.choices[0].delta.content or ""
        # Hace el efecto de generacion de texto poco a poco
        print(text, end="", flush=True)
        response += text # Guarda cada trozo en la variable de respuesta
    print()
    return response

async def main():
    """Async main function
    """
    # Inicializa los modulos
    hada = Hada()
    stt = Stt()
    mem = Mem()

    # No se que hace
    loop = get_event_loop()
    # Crea las tareas para ejecutar Hada y Stt
    task_hada = create_task(hada.StartHada())
    task_stt = create_task(stt.StartStt())

    await sleep(10)

    try:
        # Funcion principal para hacer preguntas a Hada
        while True:
            prompt = await loop.run_in_executor(None, stt.Play)
            await sleep(1)
            if prompt is None:
                break
            print(prompt)
            response = await loop.run_in_executor(None, QueryHada, prompt, mem)
            mem.Register(prompt, response)
    except (KeyboardInterrupt, CancelledError):
        pass
    finally:
        stt.StopStt()
        await task_stt
        hada.StopHada()
        await task_hada

if __name__ == "__main__":
    """Main function
    """
    try:
        run(main())
    except KeyboardInterrupt:
        pass