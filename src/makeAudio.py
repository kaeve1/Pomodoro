
import os
import json
from pydub import AudioSegment
import numpy as np

NOISE_TYPE = os.environ.get("NOISE_TYPE", "pink")

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

with open(os.path.join(BASE_DIR, "config.json")) as f:
    config = json.load(f)

INTRO_DURACAO            = 10
FPS                      = 30
FRAMES_TRANSICAO_DURACAO = 3

duracao_focus     = int(os.environ["FOCUS_DURATION"])
duracao_break     = int(os.environ["BREAK_DURATION"])
ciclos            = int(os.environ["CYCLES"])

TRANSICAO_PATH    = os.path.join(BASE_DIR, config["audio"]["transicao"])
transicao_audio   = AudioSegment.from_file(TRANSICAO_PATH) - 10
duracao_transicao = len(transicao_audio) / 1000

def gerar_noise(duracao, tipo="pink"):
    sr    = 44100
    n     = int(duracao * sr)
    white = np.random.normal(0, 1, n)
    from scipy.signal import butter, lfilter

    volumes = {
        "white":  -25, "pink":   -9, "brown":  10,
        "blue":   -25, "violet": -40, "grey":   -10, "green":  -28,
    }
    volume = volumes.get(tipo, -30)

    if tipo == "white":
        b, a  = butter(3, 0.08, btype='low')
        noise = lfilter(b, a, white)
    elif tipo == "pink":
        b = [0.049922, 0.095993, 0.050612, -0.004408]
        a = [1, -2.494956, 2.017265, -0.522189]
        noise = np.zeros(n)
        for i in range(4, n):
            noise[i] = (
                b[0]*white[i] + b[1]*white[i-1] +
                b[2]*white[i-2] + b[3]*white[i-3]
                - a[1]*noise[i-1] - a[2]*noise[i-2]
                - a[3]*noise[i-3]
            )
        b2, a2 = butter(3, 0.05, btype='low')
        noise  = lfilter(b2, a2, noise)
    elif tipo == "brown":
        noise = np.cumsum(white)
        noise = noise / np.max(np.abs(noise))
        b2, a2 = butter(2, 0.03, btype='low')
        noise  = lfilter(b2, a2, noise)
    elif tipo == "blue":
        b, a  = butter(2, 0.3, btype='high')
        noise = lfilter(b, a, white)
    elif tipo == "violet":
        noise = np.diff(white, prepend=white[0])
    elif tipo == "grey":
        b, a  = butter(3, 0.07, btype='low')
        noise = lfilter(b, a, white)
        noise = noise + white * 0.2
    elif tipo == "green":
        b, a  = butter(3, [0.03, 0.2], btype='band')
        noise = lfilter(b, a, white)
    else:
        noise = white

    noise = noise / (np.max(np.abs(noise)) + 1e-9)

    delay1 = int(sr * 0.3)
    eco1   = np.zeros(len(noise) + delay1)
    eco1[:len(noise)] += noise
    eco1[delay1:]     += noise * 0.4
    noise = eco1[:len(noise)]

    delay2 = int(sr * 0.6)
    eco2   = np.zeros(len(noise) + delay2)
    eco2[:len(noise)] += noise
    eco2[delay2:]     += noise * 0.2
    noise = eco2[:len(noise)]

    noise = noise / (np.max(np.abs(noise)) + 1e-9)

    audio = (noise * 32767).astype(np.int16).tobytes()
    seg   = AudioSegment(data=audio, sample_width=2, frame_rate=sr, channels=1)
    return seg.apply_gain(volume)

def gerar_tick_suave(freq=900, dur=80, volume=-18):
    sr   = 44100
    t    = np.linspace(0, dur/1000, int(sr * dur/1000))
    wave = 0.6 * np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(2 * np.pi * freq * 2 * t)
    wave = wave * np.exp(-t * 25)
    audio = (wave * 32767).astype(np.int16).tobytes()
    seg   = AudioSegment(data=audio, sample_width=2, frame_rate=sr, channels=1)
    return seg.apply_gain(volume)

def gerar_tick_eco(freq=900, dur=80, volume=-14):
    sr   = 44100
    t    = np.linspace(0, dur/1000, int(sr * dur/1000))
    wave = 0.6 * np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(2 * np.pi * freq * 2 * t)
    wave = wave * np.exp(-t * 25)
    ds   = int(sr * 0.08)
    eco  = np.zeros(len(wave) + ds)
    eco[:len(wave)] += wave
    eco[ds:]        += wave * 0.3
    wave  = eco[:len(wave)]
    audio = (wave * 32767).astype(np.int16).tobytes()
    seg   = AudioSegment(data=audio, sample_width=2, frame_rate=sr, channels=1)
    return seg.apply_gain(volume)

tick_normal = gerar_tick_suave(freq=950, dur=80,  volume=-18)
tock_normal = gerar_tick_suave(freq=700, dur=100, volume=-20)
tick_enfase = gerar_tick_eco(freq=950,  dur=80,  volume=-14)
tock_enfase = gerar_tick_eco(freq=700,  dur=100, volume=-14)

def adicionar_tick_tock(timeline, cursor, duracao_fase):
    inicio_tick = cursor + duracao_fase - 10
    for i in range(10):
        pos = int((inicio_tick + i) * 1000)
        som = (tick_enfase if i % 2 == 0 else tock_enfase) if (10 - i) <= 3 else (tick_normal if i % 2 == 0 else tock_normal)
        timeline = timeline.overlay(som, position=pos)
    return timeline

def adicionar_tick_intro(timeline):
    for i in range(INTRO_DURACAO):
        pos = i * 1000
        som = (tick_enfase if i % 2 == 0 else tock_enfase) if (INTRO_DURACAO - i) <= 3 else (tick_normal if i % 2 == 0 else tock_normal)
        timeline = timeline.overlay(som, position=pos)
    return timeline

# ─── DURAÇÃO TOTAL ────────────────────────────────────────
total = INTRO_DURACAO + FRAMES_TRANSICAO_DURACAO  # intro + transição visual da mensagem
for c in range(ciclos):
    total += duracao_focus
    if duracao_break > 0 and c < ciclos - 1:
        total += FRAMES_TRANSICAO_DURACAO   # transição visual focus→break
        total += duracao_break
        total += FRAMES_TRANSICAO_DURACAO   # transição visual break→focus
total += duracao_transicao  # toqueSuave do último focus
total += 20                 # outro

total_ms = int(total * 1000) + 5000
timeline  = AudioSegment.silent(duration=total_ms)

# ─── INTRO ────────────────────────────────────────────────
# tick durante o countdown
timeline = adicionar_tick_intro(timeline)
cursor   = INTRO_DURACAO

# toqueSuave toca DURANTE a transição visual da mensagem
timeline = timeline.overlay(transicao_audio, position=int(cursor * 1000))
cursor  += FRAMES_TRANSICAO_DURACAO  # avança 3s da transição visual

# ─── CICLOS ───────────────────────────────────────────────
for c in range(ciclos):

    print(f"Ciclo {c+1}/{ciclos} — focus")
    noise    = gerar_noise(duracao_focus, NOISE_TYPE)
    noise    = noise.fade_in(8000)
    timeline = timeline.overlay(noise, position=int(cursor * 1000))
    timeline = adicionar_tick_tock(timeline, cursor, duracao_focus)
    cursor  += duracao_focus

    if duracao_break > 0 and c < ciclos - 1:
        # toqueSuave toca NO INÍCIO da transição visual focus→break
        timeline = timeline.overlay(transicao_audio, position=int(cursor * 1000))
        cursor  += FRAMES_TRANSICAO_DURACAO  # avança 3s da transição visual

        print(f"Ciclo {c+1}/{ciclos} — break")
        noise    = gerar_noise(duracao_break, NOISE_TYPE)
        noise    = noise.fade_in(8000)
        timeline = timeline.overlay(noise, position=int(cursor * 1000))
        timeline = adicionar_tick_tock(timeline, cursor, duracao_break)
        cursor  += duracao_break

        # toqueSuave toca NO INÍCIO da transição visual break→focus
        timeline = timeline.overlay(transicao_audio, position=int(cursor * 1000))
        cursor  += FRAMES_TRANSICAO_DURACAO  # avança 3s da transição visual

# toqueSuave do último focus — toca após o focus terminar
timeline = timeline.overlay(transicao_audio, position=int(cursor * 1000))
cursor  += duracao_transicao

# ─── EXPORT ───────────────────────────────────────────────
saida = os.path.join(OUTPUT_DIR, "audio_pomodoro.mp3")
timeline.export(saida, format="mp3", bitrate="192k")
print("✅ Áudio gerado:", saida)
