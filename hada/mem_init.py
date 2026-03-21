#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/hada/mem_init.py - V0.0.1

import datetime
from os.path import isfile

def Register(_in, _out):
    date = datetime.date.today()
    content = ""
    if not isfile(f"hada/mem/{date}.txt"):
        with open(f"hada/mem/{date}.txt", "w+", encoding="utf-8") as f:
            pass
    with open(f"hada/mem/{date}.txt", "r", encoding="utf-8") as f:
        content = f.read()
    with open(f"hada/mem/{date}.txt", "w+", encoding="utf-8") as f:
        content += f"_user_:{_in}\n"
        content += f"_hada_:{_out}\n"
        f.write(content)

def Load():
    date = datetime.date.today()
    content = ""
    if not isfile(f"hada/mem/{date}.txt"):
        with open(f"hada/mem/{date}.txt", "w+", encoding="utf-8") as f:
            pass
    with open(f"hada/mem/{date}.txt", "r", encoding="utf-8") as f:
        content = f.read()
    print("content")
    print(content)
    user_split = content.split("_user_:")
    print("user_split")
    print(user_split)
    mem = []

    for chunk in user_split:
        print("chunk")
        print(chunk)
        if chunk == "":
            continue
        chunk_split = chunk.split("_hada_:")
        print("chunk split")
        print(chunk_split)
        mem.append({"role": "user", "content": chunk_split[0]})
        mem.append({"role": "assistant", "content": chunk_split[1]})

    return mem