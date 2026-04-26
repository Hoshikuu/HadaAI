# import json
import torch

# version_config_list = [
#     "hada/utils/configs/v1/32k.json",
#     "hada/utils/configs/v1/40k.json",
#     "hada/utils/configs/v1/48k.json",
#     "hada/utils/configs/v2/48k.json",
#     "hada/utils/configs/v2/32k.json",
# ]

class Config:
    def __init__(self):
        self.device = "cuda:0"
        self.is_half = True
        # self.use_jit = False
        # self.n_cpu = 0
        self.gpu_name = None
        # self.json_config = self.load_config_json()
        self.gpu_mem = None
        # self.instead = ""
        self.x_pad, self.x_query, self.x_center, self.x_max = self.device_config()

    # @staticmethod
    # def load_config_json() -> dict:
    #     d = {}
    #     for config_file in version_config_list:
    #         with open(config_file, "r") as f:
    #             d[config_file] = json.load(f)
    #     return d

    def device_config(self) -> tuple:
        i_device = int(self.device.split(":")[-1])
        self.gpu_name = torch.cuda.get_device_name(i_device)
        self.gpu_mem = int(
            torch.cuda.get_device_properties(i_device).total_memory
            / 1024
            / 1024
            / 1024
            + 0.4
        )

        if self.is_half:
            x_pad = 3
            x_query = 10
            x_center = 60
            x_max = 65
        else:
            x_pad = 1
            x_query = 6
            x_center = 38
            x_max = 41

        if self.gpu_mem is not None and self.gpu_mem <= 4:
            x_pad = 1
            x_query = 5
            x_center = 30
            x_max = 32
        return x_pad, x_query, x_center, x_max
