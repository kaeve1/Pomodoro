# run.py
import subprocess
import sys
import os
os.makedirs("output", exist_ok=True)

print("🚀 Iniciando geração do vídeo pomodoro...\n")

print("🎬 Passo 1/4 — Gerando intro...")
resultado = subprocess.run([sys.executable, "makeIntro.py"])
if resultado.returncode != 0:
    print("❌ Erro ao gerar intro. Abortando.")
    sys.exit(1)

print("\n📸 Passo 2/4 — Gerando frames...")
resultado = subprocess.run([sys.executable, "makeFrames.py"])
if resultado.returncode != 0:
    print("❌ Erro ao gerar frames. Abortando.")
    sys.exit(1)

print("\n🎵 Passo 3/4 — Gerando áudio...")
resultado = subprocess.run([sys.executable, "makeAudio.py"])
if resultado.returncode != 0:
    print("❌ Erro ao gerar áudio. Abortando.")
    sys.exit(1)

print("\n🎬 Passo 4/4 — Montando vídeo...")
resultado = subprocess.run([sys.executable, "makeVideo.py"])
if resultado.returncode != 0:
    print("❌ Erro ao montar vídeo. Abortando.")
    sys.exit(1)

print("\n✅ Tudo pronto! Vídeo salvo em output/video_pomodoro.mp4")