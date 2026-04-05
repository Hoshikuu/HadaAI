# ----------------------------------------------------
# Hoshikuu - https://github.com/Hoshikuu
# ----------------------------------------------------
# HadaAI/hada/tts_init.py - V0.2.1

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
    pitch_shift:  float = 0.2    # Semitonos   (-12.0 a +12.0)
    time_stretch: float = 1.15    # Velocidad   (  0.5 a  2.0)
    volume:       float = 0.5    # Volumen     (  0.1 a  3.0)
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
        def index(): 
            return Response(_PANEL_HTML, mimetype="text/html")

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

def _load_dev_panel():
    with open(Path(__file__).parent / "tts_dev_panel.html", "r", encoding="utf-8") as f:
        r = f.read()
        return r

_PANEL_HTML = _load_dev_panel()

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