#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/hada/mem_init.py - V0.1.2

import datetime
from os.path import isfile

class Mem():
    """Memory Class, manage the memory of Hada, for now only DAILY memory

    Methods\n
    |    -> Register()\n
    |    -> ReadMem()\n
    |    -> ReadFile()\n
    |    -> CheckFile()\n
    """
    def __init__(self):
        """Defines the mem_file where is the memory file for today
        """
        # Guarda las conversaciones enteras por dia
        self.mem_file = f"hada/mem/{datetime.date.today()}.hada" # Fichero de memoria para cada dia
        self.content = ""   # Contenido del fichero

    def CheckFile(self):
        """Check if the memory file exists, if not creates it
        """
        #TODO Añadir para que cree la carpeta de mem
        if isfile(self.mem_file):
            return
        with open(self.mem_file, "w+", encoding="utf-8") as f:
            f.write("")

    def ReadFile(self):
        """Reads the mem file of today
        """
        self.CheckFile()
        with open(self.mem_file, "r", encoding="utf-8") as f:
            self.content = f.read()

    def Register(self, _in: str, _out: str):
        """Call this function for register a new conversation of Hada

        Args:
            _in (str): User phrase
            _out (str): Hada phrase
        """
        self.mem_file = f"hada/mem/{datetime.date.today()}.hada"
        self.ReadFile()

        # Escribe el contenido en el archivo
        with open(self.mem_file, "w+", encoding="utf-8") as f:
            self.content += f"_user_:{_in}\n"
            self.content += f"_hada_:{_out}\n"
            f.write(self.content)

    def ReadMem(self):
        """Reads the memory file

        Returns:
            list: Return a list of processed chunks of the memory ready to iterates
        """
        self.mem_file = f"hada/mem/{datetime.date.today()}.hada"
        self.ReadFile()

        mem = []    # La lista de memoria que se devuelve ya esta preparada para poder iterarse y ponerse dentro de Hada
        chunks = self.content.split("_user_:")

        for chunk in chunks:
            if chunk == "":
                continue
            chunk_split = chunk.split("_hada_:")
            mem.append({"role": "user", "content": chunk_split[0]})
            mem.append({"role": "assistant", "content": chunk_split[1]})

        return mem