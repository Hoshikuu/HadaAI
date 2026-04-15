from RealtimeTTS import TextToAudioStream
from RealtimeTTS.engines.faster_qwen_engine import FasterQwenEngine, FasterQwenVoice

sample_text = """
Son las seis de la mañana y me da igual
Voy a salir a la calle, voy a ponerme a gritar
Voy a gritar que te quiero, que te quiero de verdad
Con esa sonrisa puesta
De verdad que no me cuesta
Pensar en ti cuando me acuesto
Pero, Aitana, no imagines el resto
Que si no, no queda bonito esto
Voy a ir directa a ti
Voy a mirarte a los ojos, no te voy a mentir (no, no)
Y como dos niños chicos, te pediré salir
Esperando un sí, esperando un kiss
Y es que me encantas tanto
Si me miras mientras canto
Se me pone cara tonto (tonta)
Niña (niño), tú me tienes loco (loca)
Y es que me gustas no sé cuánto
"Gogoko zaitut", como dirían los vascos
Si quieres te lo digo en portugués
Eu gosto de você
"""

voice = FasterQwenVoice(
    name="HadaAI", 
    ref_audio="voices/HadaVoiceSample.wav", 
    ref_text=sample_text,
    language="Spanish",
    instruct="",
    speaker_pt="voices/speaker.pt"
)
engine = FasterQwenEngine(device="cuda", voice=voice)

stream = TextToAudioStream(engine)

stream.feed("Hola Como estas hoy? bien? me alegro, que tienes pensado hacer hoy?")

stream.play_async()