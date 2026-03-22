#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/hada/mem_init.py - V0.1.0

import datetime
from os.path import isfile

class Mem():
    def __init__(self):
        self.mem_file = f"hada/mem/{datetime.date.today()}.hada"
        self.content = ""

    def CheckFile(self):
        if isfile(self.mem_file):
            return
        with open(self.mem_file, "w+", encoding="utf-8") as f:
            f.write("")

    def ReadFile(self):
        self.CheckFile()
        with open(self.mem_file, "r", encoding="utf-8") as f:
            self.content = f.read()

    def Register(self, _in, _out):
        self.mem_file = f"hada/mem/{datetime.date.today()}.hada"
        self.ReadFile()

        with open(self.mem_file, "w+", encoding="utf-8") as f:
            content += f"_user_:{_in}\n"
            content += f"_hada_:{_out}\n"
            f.write(content)

    def ReadMem(self):
        self.mem_file = f"hada/mem/{datetime.date.today()}.hada"
        self.ReadFile()

        mem = []
        chunks = self.content.split("_user_:")

        for chunk in chunks:
            if chunk == "":
                continue
            chunk_split = chunk.split("_hada_:")
            mem.append({"role": "user", "content": chunk_split[0]})
            mem.append({"role": "assistant", "content": chunk_split[1]})

        return mem