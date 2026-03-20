#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/stt.py - V0.0.1

from RealtimeSTT import AudioToTextRecorder

def on_realtime_update(text: str):
    print(f"\r[rt] {text}", end="")

def on_realtime_stable(text: str):
    print(f"\r[stable] {text}", end="")

def on_final(text: str):
    print(f"\n[final] {text}")

if __name__ == '__main__':
    recorder = AudioToTextRecorder(
        #TODO Añadir wakeword de hada o cualquier otra cosa que incluya hada para esto
        # wake_words="jarvis",
        # wakeword_backend="pvporcupine",
        # wake_words_sensitivity=0.45,
        # wake_word_timeout=5,
        # wake_word_buffer_duration=0.4,
        device="cpu",
        language="es",

        model="small",
        compute_type="int8",
        beam_size=5,

        enable_realtime_transcription=True,
        use_main_model_for_realtime=False,
        realtime_model_type="tiny",
        realtime_processing_pause=0.5,
        realtime_batch_size=8,
        beam_size_realtime=2,

        on_realtime_transcription_update=on_realtime_update,
        on_realtime_transcription_stabilized=on_realtime_stable,

        silero_use_onnx=True,
        post_speech_silence_duration=0.65,
        min_length_of_recording=0.8,
        pre_recording_buffer_duration=0.3,

        spinner=False,
        print_transcription_time=True,
        no_log_file=True
    )

    while True:
        recorder.text(on_final)
