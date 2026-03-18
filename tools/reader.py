#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/reader.py - V0.2.1

def SystemPrompt():
    with open("prompts/hadaV4.txt", "r") as f:
        r = f.read()
        return r
    

def LlamaCommand():
    with open("commands/llama_server_command.txt", "r") as f:
        r = f.read()
        return r