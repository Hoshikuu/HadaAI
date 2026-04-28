import numpy as np
import torch

from fairseq import checkpoint_utils

from hada.utils.infer.pipeline import Pipeline
from hada.utils.inferpack.models import (
    SynthesizerTrnMs256NSFsid,
    SynthesizerTrnMs256NSFsid_nono,
    SynthesizerTrnMs768NSFsid,
    SynthesizerTrnMs768NSFsid_nono,
)

class VC:
    def __init__(self, config):
        self.net_g = None
        self.pipeline = None
        
        self.cpt = None
        self.tgt_sr = None
        self.if_f0 = None
        self.version = None
        self.config = config

        self.person = None
        self.hubert_model = None
        self.person_index = None

    def load_hubert(self, hubert_path):
        models, _, _ = checkpoint_utils.load_model_ensemble_and_task(
            [hubert_path],
            suffix="",
        )
        hubert_model = models[0]
        hubert_model = hubert_model.to(self.config.device)
        if self.config.is_half:
            hubert_model = hubert_model.half()
        else:
            hubert_model = hubert_model.float()
        return hubert_model.eval()

    def get_vc(self, voice_path, hubert_path, index_path):
        self.person = voice_path
        self.hubert_model = self.load_hubert(hubert_path)
        self.person_index = index_path

        self.cpt = torch.load(self.person, map_location="cpu")
        self.tgt_sr = self.cpt["config"][-1]
        self.cpt["config"][-3] = self.cpt["weight"]["emb_g.weight"].shape[0]  # n_spk
        self.if_f0 = self.cpt.get("f0", 1)
        self.version = self.cpt.get("version", "v1")

        synthesizer_class = {
            ("v1", 1): SynthesizerTrnMs256NSFsid,
            ("v1", 0): SynthesizerTrnMs256NSFsid_nono,
            ("v2", 1): SynthesizerTrnMs768NSFsid,
            ("v2", 0): SynthesizerTrnMs768NSFsid_nono,
        }

        self.net_g = synthesizer_class.get(
            (self.version, self.if_f0), SynthesizerTrnMs256NSFsid
        )(*self.cpt["config"], is_half=self.config.is_half)

        del self.net_g.enc_q

        self.net_g.load_state_dict(self.cpt["weight"], strict=False)
        self.net_g.eval().to(self.config.device)

        if self.config.is_half:
            self.net_g = self.net_g.half()
        else:
            self.net_g = self.net_g.float()

        self.pipeline = Pipeline(self.tgt_sr, self.config)
        n_spk = self.cpt["config"][-3]

        return {"visible": True, "maximum": n_spk, "__type__": "update"}

    def vc_single(self, audio):
        if audio is None:
            print("NO AUDIO")
            return None, None

        audio_max = np.abs(audio).max() / 0.95
        if audio_max > 1:
            audio /= audio_max

        times = [0, 0, 0]

        audio_opt = self.pipeline.pipeline(self.hubert_model, self.net_g, 0, audio, audio, times, 2, "rmvpe", self.person_index, 0.75, self.if_f0, 3, self.tgt_sr, 0, 0.25, self.version, 0.33, None)

        if self.tgt_sr != 0 >= 16000:
            tgt_sr = 0
        else:
            tgt_sr = self.tgt_sr

        return tgt_sr, audio_opt