def SystemPrompt():
    with open("prompts/hadaV4.txt", "r") as f:
        r = f.read()
        return r