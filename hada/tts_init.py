# ----------------------------------------------------
# Hoshikuu - https://github.com/Hoshikuu
# ----------------------------------------------------
# HadaAI/hada/tts_init.py - V0.2.0

import subprocess
import threading
import types
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Generator, Optional

import numpy as np

if TYPE_CHECKING:
    from RealtimeTTS import TextToAudioStream

# Rutas fijas dentro del proyecto
_PIPER_EXE  = Path(__file__).parent / "piper" / "piper.exe"
_MODEL_FILE = Path(__file__).parent / "voices" / "es_ES-sharvard-medium.onnx"
_CONFIG_FILE = Path(__file__).parent / "voices" / "es_ES-sharvard-medium.onnx.json"

_SPEAKERS = {"M": 0, "F": 1}


# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
#  DEVELOPER — borrar esta sección cuando la voz
#  ya esté configurada a tu gusto
# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──

DEV_PANEL = True  # <- True para abrir el panel en http://localhost:5050


@dataclass
class VoiceParams:
    pitch_shift:  float = 0.0    # Semitonos   (-12.0 a +12.0)
    time_stretch: float = 1.0    # Velocidad   (  0.5 a  2.0)
    volume:       float = 1.0    # Volumen     (  0.1 a  3.0)
    trim_silence: bool  = False  # Eliminar silencios


def _process_audio(raw_bytes: bytes, params: VoiceParams, sample_rate: int = 22050) -> bytes:
    p = params
    if p.pitch_shift == 0.0 and p.time_stretch == 1.0 and p.volume == 1.0 and not p.trim_silence:
        return raw_bytes
    try:
        import librosa
        y = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        if p.pitch_shift  != 0.0: y = librosa.effects.pitch_shift(y, sr=sample_rate, n_steps=p.pitch_shift)
        if p.time_stretch != 1.0: y = librosa.effects.time_stretch(y, rate=max(0.1, p.time_stretch))
        if p.trim_silence:        y, _ = librosa.effects.trim(y, top_db=30)
        if p.volume       != 1.0: y = y * p.volume
        return (np.clip(y, -1.0, 1.0) * 32768.0).astype(np.int16).tobytes()
    except Exception as e:
        print(f"[Tts/Dev] Error procesando audio: {e}")
        return raw_bytes


def _start_dev_panel(params: VoiceParams, host: str = "127.0.0.1", port: int = 5050) -> None:
    def run():
        try:
            from flask import Flask, jsonify, request, Response
        except ImportError:
            print("[Tts/Dev] Flask no instalado: pip install flask")
            return
        import logging
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        app = Flask(__name__)

        @app.route("/")
        def index(): return Response(_PANEL_HTML, mimetype="text/html")

        @app.route("/api/params", methods=["GET"])
        def get_params():
            return jsonify({"pitch_shift": params.pitch_shift, "time_stretch": params.time_stretch,
                            "volume": params.volume, "trim_silence": params.trim_silence})

        @app.route("/api/params", methods=["POST"])
        def set_params():
            d = request.get_json(force=True)
            if "pitch_shift"  in d: params.pitch_shift  = float(d["pitch_shift"])
            if "time_stretch" in d: params.time_stretch = float(d["time_stretch"])
            if "volume"       in d: params.volume       = float(d["volume"])
            if "trim_silence" in d: params.trim_silence = bool(d["trim_silence"])
            return jsonify({"ok": True})

        @app.route("/api/reset", methods=["POST"])
        def reset():
            params.pitch_shift = 0.0; params.time_stretch = 1.0
            params.volume = 1.0;      params.trim_silence = False
            return jsonify({"ok": True})

        app.run(host=host, port=port, threaded=True, use_reloader=False)

    t = threading.Thread(target=run, daemon=True, name="TtsDevPanel")
    t.start()
    print(f"[Tts/Dev] Panel activo → http://{host}:{port}")


_PANEL_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hada · Voice Panel</title>
<style>
  :root {
    --bg:#111110; --surface:#1a1a18; --surface-2:#222220; --border:#2e2e2c;
    --text:#e8e6e3; --muted:#7a7875; --faint:#454441;
    --accent:#4f98a3; --accent-glow:rgba(79,152,163,.18); --accent-dim:rgba(79,152,163,.08);
    --warn:#bb653b; --r:10px; --r-sm:6px;
    --font:'JetBrains Mono','Fira Code',monospace;
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  body{font-family:var(--font);background:var(--bg);color:var(--text);min-height:100vh;
       display:flex;flex-direction:column;align-items:center;padding:2rem 1rem 4rem;
       font-size:13px;line-height:1.6;-webkit-font-smoothing:antialiased}
  header{width:100%;max-width:520px;margin-bottom:1.75rem;display:flex;align-items:center;gap:.75rem}
  .logo{width:36px;height:36px;background:var(--accent-dim);border:1px solid var(--accent);
        border-radius:50%;display:grid;place-items:center;font-size:16px}
  .ht h1{font-size:14px;font-weight:700;letter-spacing:.04em}
  .ht p{font-size:11px;color:var(--muted)}
  .badge{margin-left:auto;background:var(--accent-dim);border:1px solid var(--accent);
         color:var(--accent);border-radius:99px;padding:2px 10px;font-size:10px;
         letter-spacing:.08em;text-transform:uppercase}
  .card{width:100%;max-width:520px;background:var(--surface);border:1px solid var(--border);
        border-radius:var(--r);padding:1.25rem 1.5rem;margin-bottom:.75rem}
  .card-title{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);
              margin-bottom:1.1rem;display:flex;align-items:center;gap:.5rem}
  .card-title::after{content:"";flex:1;height:1px;background:var(--border)}
  .row{display:grid;grid-template-columns:110px 1fr 56px;align-items:center;gap:.75rem;
       padding:.55rem 0;border-bottom:1px solid var(--border)}
  .row:last-child{border-bottom:none}
  .lbl{font-size:12px;color:var(--muted)}
  .lbl small{display:block;font-size:10px;color:var(--faint);margin-top:1px}
  .val{text-align:right;font-size:13px;font-weight:700;color:var(--accent)}
  input[type=range]{-webkit-appearance:none;width:100%;height:4px;background:var(--surface-2);
                    border-radius:99px;outline:none;cursor:pointer;accent-color:var(--accent)}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;
    border-radius:50%;background:var(--accent);border:2px solid var(--bg);
    box-shadow:0 0 0 2px var(--accent-glow);transition:box-shadow .15s}
  input[type=range]:hover::-webkit-slider-thumb{box-shadow:0 0 0 5px var(--accent-glow)}
  .tog{position:relative;width:40px;height:22px;flex-shrink:0}
  .tog input{opacity:0;width:0;height:0}
  .ts{position:absolute;inset:0;background:var(--surface-2);border:1px solid var(--border);
      border-radius:99px;cursor:pointer;transition:background .2s}
  .ts::before{content:"";position:absolute;width:14px;height:14px;left:3px;top:3px;
              background:var(--muted);border-radius:50%;transition:transform .2s,background .2s}
  .tog input:checked+.ts{background:var(--accent-dim);border-color:var(--accent)}
  .tog input:checked+.ts::before{transform:translateX(18px);background:var(--accent)}
  .status{width:100%;max-width:520px;background:var(--surface);border:1px solid var(--border);
          border-radius:var(--r);padding:.65rem 1.25rem;display:flex;flex-wrap:wrap;gap:.4rem 1.25rem;
          font-size:11px;color:var(--muted);margin-bottom:.75rem}
  .status span{color:var(--text);font-weight:600}
  .btns{width:100%;max-width:520px;display:flex;gap:.65rem}
  button{flex:1;padding:.6rem 1rem;border-radius:var(--r-sm);border:1px solid var(--border);
         background:var(--surface-2);color:var(--text);font-family:var(--font);font-size:12px;
         font-weight:600;cursor:pointer;letter-spacing:.04em;transition:background .15s,border-color .15s}
  button:hover{background:var(--surface);border-color:var(--faint)}
  .btn-p{background:var(--accent-dim);border-color:var(--accent);color:var(--accent)}
  .btn-p:hover{background:rgba(79,152,163,.22)}
  .btn-d{background:rgba(187,101,59,.08);border-color:var(--warn);color:var(--warn)}
  .btn-d:hover{background:rgba(187,101,59,.18)}
  #toast{position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%) translateY(20px);
         background:var(--surface);border:1px solid var(--accent);color:var(--accent);
         padding:.45rem 1.2rem;border-radius:99px;font-size:11px;opacity:0;
         transition:opacity .2s,transform .2s;pointer-events:none;white-space:nowrap}
  #toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
</style>
</head>
<body>
<header>
  <div class="logo">🎙</div>
  <div class="ht"><h1>HADA · VOICE PANEL</h1><p>es_ES-sharvard-medium — speaker F</p></div>
  <div class="badge">DEV</div>
</header>

<div class="status" id="st">Cargando...</div>

<div class="card">
  <div class="card-title">🎵 pitch &amp; velocidad</div>
  <div class="row">
    <div class="lbl">Pitch<small>-12 a +12 st</small></div>
    <input type="range" id="pitch_shift" min="-12" max="12" step="0.5" value="0">
    <div class="val" id="v_pitch">0.0</div>
  </div>
  <div class="row">
    <div class="lbl">Velocidad<small>0.5 a 2.0×</small></div>
    <input type="range" id="time_stretch" min="0.5" max="2.0" step="0.05" value="1">
    <div class="val" id="v_stretch">1.00</div>
  </div>
</div>

<div class="card">
  <div class="card-title">🔊 volumen</div>
  <div class="row">
    <div class="lbl">Volumen<small>0.1 a 3.0</small></div>
    <input type="range" id="volume" min="0.1" max="3.0" step="0.05" value="1">
    <div class="val" id="v_vol">1.00</div>
  </div>
</div>

<div class="card">
  <div class="card-title">⚙ opciones</div>
  <div class="row">
    <div class="lbl">Trim silencio<small>Elimina silencios</small></div>
    <label class="tog"><input type="checkbox" id="trim_silence"><span class="ts"></span></label>
    <div class="val" id="v_trim" style="font-size:11px;color:var(--muted)">OFF</div>
  </div>
</div>

<div class="btns">
  <button class="btn-p" onclick="apply()">✓ Aplicar</button>
  <button class="btn-d" onclick="reset()">↺ Reset</button>
</div>
<div id="toast"></div>

<script>
const API="/api/params";
const f1=v=>parseFloat(v).toFixed(1), f2=v=>parseFloat(v).toFixed(2);

document.getElementById("pitch_shift").oninput=function(){document.getElementById("v_pitch").textContent=f1(this.value);debounce()};
document.getElementById("time_stretch").oninput=function(){document.getElementById("v_stretch").textContent=f2(this.value);debounce()};
document.getElementById("volume").oninput=function(){document.getElementById("v_vol").textContent=f2(this.value);debounce()};
document.getElementById("trim_silence").onchange=function(){
  const v=document.getElementById("v_trim");
  v.textContent=this.checked?"ON":"OFF";
  v.style.color=this.checked?"var(--accent)":"var(--muted)";
  apply();
};

function updateStatus(d){
  document.getElementById("st").innerHTML=
    `pitch <span>${f1(d.pitch_shift)} st</span> &nbsp;·&nbsp; `+
    `velocidad <span>${f2(d.time_stretch)}×</span> &nbsp;·&nbsp; `+
    `volumen <span>${f2(d.volume)}</span> &nbsp;·&nbsp; `+
    `trim <span>${d.trim_silence?"on":"off"}</span>`;
}

async function load(){
  const r=await fetch(API); const d=await r.json();
  document.getElementById("pitch_shift").value=d.pitch_shift; document.getElementById("v_pitch").textContent=f1(d.pitch_shift);
  document.getElementById("time_stretch").value=d.time_stretch; document.getElementById("v_stretch").textContent=f2(d.time_stretch);
  document.getElementById("volume").value=d.volume; document.getElementById("v_vol").textContent=f2(d.volume);
  document.getElementById("trim_silence").checked=d.trim_silence;
  const vt=document.getElementById("v_trim"); vt.textContent=d.trim_silence?"ON":"OFF"; vt.style.color=d.trim_silence?"var(--accent)":"var(--muted)";
  updateStatus(d);
}

async function apply(){
  const body={pitch_shift:parseFloat(document.getElementById("pitch_shift").value),
              time_stretch:parseFloat(document.getElementById("time_stretch").value),
              volume:parseFloat(document.getElementById("volume").value),
              trim_silence:document.getElementById("trim_silence").checked};
  await fetch(API,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  updateStatus(body); toast("✓ Aplicado");
}

async function reset(){
  await fetch("/api/reset",{method:"POST"}); await load(); toast("↺ Reset");
}

function toast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),2000)}

let dt; function debounce(){clearTimeout(dt);dt=setTimeout(apply,400)}

load();
setInterval(async()=>{try{const r=await fetch(API);updateStatus(await r.json())}catch{}},3000);
</script>
</body>
</html>"""

# ── FIN DEVELOPER ── ── ── ── ── ── ── ── ── ── ──


class Tts:
    """Text-to-Speech para Hada.

    Usa RealtimeTTS + PiperEngine con la voz es_ES-sharvard-medium.

    Methods
    | -> Speak(text)
    | -> SpeakGenerator(generator, asincrono)
    | -> StopTts()
    """

    def __init__(self, speaker: str = "F", dev_panel: bool = DEV_PANEL):
        """
        Args:
            speaker:   "F" (Femenino, default) | "M" (Masculino)
            dev_panel: True para activar el panel en http://localhost:5050
        """
        self.speaker = speaker
        self.params  = VoiceParams()

        if dev_panel:
            _start_dev_panel(self.params)

    def _build_stream(self) -> "TextToAudioStream":
        import json
        from RealtimeTTS import TextToAudioStream, PiperEngine, PiperVoice

        speaker_id = _SPEAKERS.get(self.speaker, 1)
        voz        = PiperVoice(model_file=str(_MODEL_FILE), config_file=str(_CONFIG_FILE))
        motor      = PiperEngine(piper_path=str(_PIPER_EXE), voice=voz)
        _tts_ref   = self

        # Fix: piper_engine.py abre el JSON sin encoding en Windows → UnicodeDecodeError
        # Parcheamos el método para forzar utf-8
        def _sample_rate_utf8(self_engine) -> int:
            if not self_engine.voice or not self_engine.voice.config_file:
                return 16000
            try:
                with open(self_engine.voice.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("audio", {}).get("sample_rate", 16000)
            except Exception:
                return 16000

        motor._get_sample_rate_from_config = types.MethodType(_sample_rate_utf8, motor)

        def _synthesize(self_engine, text: str) -> bool:
            cmd = [self_engine.piper_path, "-m", self_engine.voice.model_file,
                   "-c", self_engine.voice.config_file,
                   "--speaker", str(speaker_id), "--output-raw"]
            try:
                result = subprocess.run(cmd, input=text.encode("utf-8"),
                                        capture_output=True, check=True, shell=False)
                self_engine.queue.put(_process_audio(result.stdout, _tts_ref.params))
                return True
            except Exception as e:
                print(f"[Tts] Error: {e}")
                return False

        motor.synthesize = types.MethodType(_synthesize, motor)
        return TextToAudioStream(motor)

    def Speak(self, text: str) -> None:
        """Reproduce un texto (bloqueante)."""
        if not text or not text.strip():
            return
        stream = self._build_stream()
        stream.feed(text)
        stream.play()

    def SpeakGenerator(
        self,
        generador: Generator[str, None, None],
        asincrono: bool = False,
    ) -> Optional["TextToAudioStream"]:
        """Reproduce voz en tiempo real desde un generator Python.

        Úsalo con el stream de QueryHada para que Hada empiece a hablar
        antes de terminar de generar la respuesta.
        """
        stream = self._build_stream()
        stream.feed(generador)
        if asincrono:
            stream.play_async()
            return stream
        stream.play()
        return None

    def StopTts(self) -> None:
        pass