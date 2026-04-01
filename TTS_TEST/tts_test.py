import warnings
warnings.filterwarnings("ignore")

import numpy as np
import sounddevice as sd
import soundfile as sf
import librosa
import tempfile, os
from scipy.signal import butter, sosfilt
from RealtimeTTS import TextToAudioStream, KokoroEngine

# ── pip install chatterbox-voice-conversion ──────────────────
from chatterbox.tts import ChatterboxTTS


# ============================================================
# CONFIG
# ============================================================

VOICE        = "ef_dora"
SPEED        = 1.05

# --- Chatterbox Voice Conversion ---
VC_ENABLED        = True
VC_REFERENCE_WAV  = "neuro_reference.wav"  # <-- clip de 5-30s de la voz objetivo
VC_DEVICE         = "cpu"   # o "cpu"

# --- Pitch ---
PITCH_ENABLED   = True
PITCH_SEMITONES = 1
PITCH_QUALITY   = "kaiser_fast"

# --- Time stretch ---
STRETCH_ENABLED = False
STRETCH_RATE    = 1.0

# --- Volumen ---
VOLUME = 1.2

# --- Filtro paso alto ---
HIGHPASS_ENABLED = True
HIGHPASS_CUTOFF  = 200

# --- Eco ---
ECHO_ENABLED  = False
ECHO_DELAY_MS = 20
ECHO_DECAY    = 0.15

# --- Tremolo ---
TREMOLO_ENABLED = False
TREMOLO_RATE    = 12
TREMOLO_DEPTH   = 0.4

# --- Padding anti-corte ---
PADDING_SECONDS = 0.3

# --- RealtimeTTS ---
FRAMES_PER_BUFFER       = 128
PLAYOUT_CHUNK_SIZE      = 256
BUFFER_THRESHOLD        = 0.0
MIN_SENTENCE_LENGTH     = 3
MIN_FIRST_FRAGMENT      = 3
FORCE_FIRST_AFTER_WORDS = 8

# ============================================================


# ── Kokoro ───────────────────────────────────────────────────
engine = KokoroEngine()
engine.set_voice(VOICE)
engine.set_speed(SPEED)
_, _, SAMPLE_RATE = engine.get_stream_info()


# ── Chatterbox VC ────────────────────────────────────────────
vc_model = None
if VC_ENABLED:
    try:
        vc_model = ChatterboxTTS.from_pretrained(device=VC_DEVICE)
        print(f"[VC] Chatterbox cargado. Referencia: {VC_REFERENCE_WAV}")
    except Exception as e:
        print(f"[VC] Error al cargar Chatterbox: {e}  →  VC desactivado")


audio_buffer = []


# ── Filtros ──────────────────────────────────────────────────
def _highpass(audio, cutoff):
    sos = butter(4, cutoff / (SAMPLE_RATE / 2), btype="high", output="sos")
    return sosfilt(sos, audio).astype(np.float32)


# ── Chatterbox inference ─────────────────────────────────────
def _apply_vc(audio: np.ndarray) -> np.ndarray:
    if vc_model is None or not os.path.exists(VC_REFERENCE_WAV):
        return audio
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            in_path = f.name
        sf.write(in_path, audio, SAMPLE_RATE)

        wav_tensor = vc_model.generate(
            audio=in_path,
            target_voice_path=VC_REFERENCE_WAV,
        )
        result = wav_tensor.squeeze().cpu().numpy()

        # re-muestrear si es necesario (Chatterbox suele devolver 24kHz)
        cb_sr = 24000
        if cb_sr != SAMPLE_RATE:
            result = librosa.resample(result, orig_sr=cb_sr, target_sr=SAMPLE_RATE)
        return result.astype(np.float32)
    except Exception as e:
        print(f"[VC] Error en inferencia: {e}")
        return audio
    finally:
        if os.path.exists(in_path):
            os.remove(in_path)


# ── Pipeline de efectos ──────────────────────────────────────
def process_audio(audio: np.ndarray) -> np.ndarray:
    audio = audio.astype(np.float32)

    if PITCH_ENABLED and PITCH_SEMITONES != 0:
        audio = librosa.effects.pitch_shift(
            audio, sr=SAMPLE_RATE, n_steps=PITCH_SEMITONES, res_type=PITCH_QUALITY
        )

    if STRETCH_ENABLED and STRETCH_RATE != 1.0:
        audio = librosa.effects.time_stretch(audio, rate=STRETCH_RATE)

    # ── Voice conversion ─────────────────────────────────────
    audio = _apply_vc(audio)

    if HIGHPASS_ENABLED:
        audio = _highpass(audio, HIGHPASS_CUTOFF)

    if ECHO_ENABLED:
        delay_samples = int(SAMPLE_RATE * ECHO_DELAY_MS / 1000)
        echo = np.zeros_like(audio)
        echo[delay_samples:] = audio[:-delay_samples] * ECHO_DECAY
        audio = (audio + echo).astype(np.float32)

    if TREMOLO_ENABLED:
        t = np.linspace(0, len(audio) / SAMPLE_RATE, len(audio))
        mod = 1.0 - TREMOLO_DEPTH * (0.5 + 0.5 * np.sin(2 * np.pi * TREMOLO_RATE * t))
        audio = (audio * mod).astype(np.float32)

    audio = np.clip(audio * VOLUME, -1.0, 1.0)
    padding = np.zeros(int(SAMPLE_RATE * PADDING_SECONDS), dtype=np.float32)
    return np.concatenate([audio, padding])


# ── Callbacks ────────────────────────────────────────────────
def on_audio_chunk(chunk):
    audio = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
    audio_buffer.append(audio)

def on_audio_stream_stop():
    if not audio_buffer:
        return
    full_audio = np.concatenate(audio_buffer)
    full_audio = process_audio(full_audio)
    sd.play(full_audio, samplerate=SAMPLE_RATE)
    sd.wait()
    audio_buffer.clear()


# ── Stream ───────────────────────────────────────────────────
stream = TextToAudioStream(
    engine,
    on_audio_stream_stop=on_audio_stream_stop,
    frames_per_buffer=FRAMES_PER_BUFFER,
    playout_chunk_size=PLAYOUT_CHUNK_SIZE,
    muted=True,
    language="es",
)

def speak(text: str):
    stream.feed(text)
    stream.play(
        on_audio_chunk=on_audio_chunk,
        muted=True,
        language="es",
        fast_sentence_fragment=True,
        fast_sentence_fragment_allsentences=True,
        fast_sentence_fragment_allsentences_multiple=True,
        minimum_sentence_length=MIN_SENTENCE_LENGTH,
        minimum_first_fragment_length=MIN_FIRST_FRAGMENT,
        force_first_fragment_after_words=FORCE_FIRST_AFTER_WORDS,
        buffer_threshold_seconds=BUFFER_THRESHOLD,
        tokenizer="nltk",
    )


if __name__ == "__main__":
    speak("Hola. Soy Hada, ¿qué quieres hacer hoy?")
    speak("¿Necesitas que te diga algo?")