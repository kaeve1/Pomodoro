import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
import json
import io

#config
with open("config.json") as f:
    config = json.load(f)

duracao_focus = config["focus"]["duracao"]
duracao_break = config["break"]["duracao"]
ciclos = config["ciclos"]
transicao = config["audio"]["transicao"]

SAMPLE_RATE = 44100

# pinknoise
def gerar_pink_noise(duracao_segundos):
    print("Gerando pinknoise...")
    n = duracao_segundos * SAMPLE_RATE
    
    white = np.random.randn(n)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    
    from scipy.signal import lfilter
    pink = lfilter(b, a, white)
    
    pink = pink / np.max(np.abs(pink))
    
    pink_int16 = (pink * 32767 * 0.3).astype(np.int16)
    
    buffer = io.BytesIO()  
    wavfile.write(buffer, SAMPLE_RATE, pink_int16)
    buffer.seek(0)
    
    return AudioSegment.from_wav(buffer)

#tictack
def gerar_tick(duracao_ms=80, freq=1000):
    t = np.linspace(0, duracao_ms/1000, int(SAMPLE_RATE * duracao_ms/1000))
    tick = np.sin(2 * np.pi * freq * t)
    
    envelope = np.exp(-t * 30)
    tick = tick * envelope
    tick_int16 = (tick * 32767 * 0.4).astype(np.int16)
    
    buffer = io.BytesIO()
    wavfile.write(buffer, SAMPLE_RATE, tick_int16)
    buffer.seek(0)
    
    return AudioSegment.from_wav(buffer)

def montar_fase(duracao_segundos):
    audio = gerar_pink_noise(duracao_segundos)
    
    #fadein
    audio = audio.fade_in(3000)
    
    #tickdos10segundos
    tick = gerar_tick()
    tock = gerar_tick(freq=800)
    
    tick_tock = tick + AudioSegment.silent(duration=500) + tock + AudioSegment.silent(duration=500)
    inicio_tick = (duracao_segundos - 10) * 1000
    
    for i in range(10):
        pos = inicio_tick + (i * 1000)
        audio = audio.overlay(tick_tock, position=int(pos))
    
    return audio

#junta tudo
print("Montando áudio completo...")

transicao_audio = AudioSegment.from_file(transicao)
audio_final = AudioSegment.empty()

for ciclo in range(ciclos):
    print(f"Ciclo {ciclo + 1}/{ciclos} — Focus...")
    fase_focus = montar_fase(duracao_focus)
    audio_final += fase_focus + transicao_audio

    print(f"Ciclo {ciclo + 1}/{ciclos} — Break...")
    fase_break = montar_fase(duracao_break)
    audio_final += fase_break + transicao_audio

# exporta
audio_final.export("output/audio_pomodoro.mp3", format="mp3")
print(f"✅ Áudio completo gerado! Duração: {len(audio_final)/1000:.0f}s")

