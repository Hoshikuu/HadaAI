def hada_system():
    with open("prompts/hada.txt", "r", encoding="utf-8") as f:
        return f.read()
    
def summary_system():
    with open("prompts/summary.txt", "r", encoding="utf-8") as f:
        return f.read()