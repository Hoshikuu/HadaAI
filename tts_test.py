import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch")

import numpy as np
import sounddevice as sd
import librosa
from scipy.signal import butter, sosfilt
from RealtimeTTS import TextToAudioStream, KokoroEngine

# ============================================================
# CONFIG — toquetea aquí
# ============================================================

# --- Voz base ---
VOICE = "ef_dora"
SPEED = 1.05

# --- Pitch (tono) ---
PITCH_ENABLED   = True
PITCH_SEMITONES = 4
PITCH_QUALITY   = "kaiser_fast"  # más rápido que soxr_hq

# --- Time stretch (velocidad sin cambiar tono) ---
STRETCH_ENABLED = False
STRETCH_RATE    = 1.2

# --- Volumen ---
VOLUME = 1.2

# --- Distorsión ---
DISTORTION_ENABLED = True
DISTORTION_AMOUNT  = 1.5

# --- Filtro paso alto ---
HIGHPASS_ENABLED = True
HIGHPASS_CUTOFF  = 200

# --- Filtro paso bajo ---
LOWPASS_ENABLED = False
LOWPASS_CUTOFF  = 8000

# --- Eco ---
ECHO_ENABLED  = False
ECHO_DELAY_MS = 80
ECHO_DECAY    = 0.3

# --- Tremolo ---
TREMOLO_ENABLED = False
TREMOLO_RATE    = 6.0
TREMOLO_DEPTH   = 0.4

# --- Bitcrusher ---
BITCRUSH_ENABLED = False
BITCRUSH_BITS    = 8

# --- Anti-corte al final ---
PADDING_SECONDS = 0.3  # sube a 0.5 si sigue cortando

# --- RealtimeTTS ---
FRAMES_PER_BUFFER       = 128
PLAYOUT_CHUNK_SIZE      = 256
BUFFER_THRESHOLD        = 0.0
MIN_SENTENCE_LENGTH     = 3
MIN_FIRST_FRAGMENT      = 3
FORCE_FIRST_AFTER_WORDS = 8

# ============================================================

engine = KokoroEngine()
engine.set_voice(VOICE)
engine.set_speed(SPEED)

_, _, SAMPLE_RATE = engine.get_stream_info()

audio_buffer = []


def _highpass(audio, cutoff):
    sos = butter(4, cutoff / (SAMPLE_RATE / 2), btype="high", output="sos")
    return sosfilt(sos, audio)

def _lowpass(audio, cutoff):
    sos = butter(4, cutoff / (SAMPLE_RATE / 2), btype="low", output="sos")
    return sosfilt(sos, audio)


def process_audio(audio: np.ndarray) -> np.ndarray:
    audio = audio.astype(np.float16)

    # Pitch shift
    if PITCH_ENABLED and PITCH_SEMITONES != 0:
        audio32 = audio.astype(np.float32)
        audio32 = librosa.effects.pitch_shift(
            audio32, sr=SAMPLE_RATE,
            n_steps=PITCH_SEMITONES,
            res_type=PITCH_QUALITY,
        )
        audio = audio32.astype(np.float16)

    # Time stretch
    if STRETCH_ENABLED and STRETCH_RATE != 1.0:
        audio32 = audio.astype(np.float32)
        audio32 = librosa.effects.time_stretch(audio32, rate=STRETCH_RATE)
        audio = audio32.astype(np.float16)

    # Filtro paso alto
    if HIGHPASS_ENABLED:
        audio = _highpass(audio.astype(np.float32), HIGHPASS_CUTOFF).astype(np.float16)

    # Filtro paso bajo
    if LOWPASS_ENABLED:
        audio = _lowpass(audio.astype(np.float32), LOWPASS_CUTOFF).astype(np.float16)

    # Distorsión
    if DISTORTION_ENABLED and DISTORTION_AMOUNT > 1.0:
        audio = (np.tanh(audio * DISTORTION_AMOUNT) / np.tanh(DISTORTION_AMOUNT)).astype(np.float16)

    # Eco
    if ECHO_ENABLED:
        delay_samples = int(SAMPLE_RATE * ECHO_DELAY_MS / 1000)
        echo = np.zeros_like(audio)
        echo[delay_samples:] = audio[:-delay_samples] * ECHO_DECAY
        audio = (audio + echo).astype(np.float16)

    # Tremolo
    if TREMOLO_ENABLED:
        t = np.linspace(0, len(audio) / SAMPLE_RATE, len(audio))
        tremolo = 1.0 - TREMOLO_DEPTH * (0.5 + 0.5 * np.sin(2 * np.pi * TREMOLO_RATE * t))
        audio = (audio * tremolo).astype(np.float16)

    # Bitcrusher
    if BITCRUSH_ENABLED:
        max_val = 2 ** (BITCRUSH_BITS - 1)
        audio = (np.round(audio * max_val) / max_val).astype(np.float16)

    # Volumen + clipping
    audio = np.clip(audio * VOLUME, -1.0, 1.0)

    # Padding anti-corte
    padding = np.zeros(int(SAMPLE_RATE * PADDING_SECONDS), dtype=np.float16)
    audio = np.concatenate([audio, padding])

    return audio.astype(np.float32)


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
    speak("Hola. Soy una inteligencia artificial con voz sintética femenina.")
    speak("¿En qué puedo ayudarte hoy?")