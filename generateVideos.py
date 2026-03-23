
import subprocess
import sys
import os
import json
import shutil

BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
SRC_DIR            = os.path.join(BASE_DIR, "src")
OUTPUT_DIR         = os.path.join(BASE_DIR, "output")
VIDEOS_DIR         = os.path.join(OUTPUT_DIR, "videos")
FRAMES_DIR         = r"E:\PomodojoFrames"
VIDEOS_CONFIG_PATH = os.path.join(BASE_DIR, "videos.json")

def preparar_pastas():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(FRAMES_DIR, exist_ok=True)

def limpar_frames_temporarios():
    for file in os.listdir(FRAMES_DIR):
        path = os.path.join(FRAMES_DIR, file)
        if os.path.isfile(path):
            os.remove(path)
    print("🗑️ Frames temporários removidos!")

def limpar_output_temporario():
    for file in os.listdir(OUTPUT_DIR):
        path = os.path.join(OUTPUT_DIR, file)
        if os.path.isfile(path):
            if file.endswith(".png") or file.endswith(".mp3") or file.endswith(".jpg"):
                os.remove(path)

def run_step(nome, script, env):
    print(f"\n{nome}")
    script_path = os.path.join(SRC_DIR, script)
    subprocess.run(
        [sys.executable, script_path],
        check=True,
        cwd=BASE_DIR,
        env=env
    )

def gerar_video(video):
    nome = video["nome"]

    print("\n=================================")
    print(f"🎬 Gerando vídeo: {nome}")
    print("=================================")

    limpar_output_temporario()
    limpar_frames_temporarios()

    env = os.environ.copy()
    env["BREAK_COLOR"]    = str(video["break_color"])
    env["FOCUS_COLOR"]    = str(video["focus_color"])
    env["FOCUS_DURATION"] = str(video["focus"])
    env["BREAK_DURATION"] = str(video["break"])
    env["CYCLES"]         = str(video.get("ciclos", 1))
    env["NOISE_TYPE"]     = video.get("noise", "pink")

    passos = [
        ("🎬 Gerando intro...",   "makeIntro.py"),
        ("📸 Gerando frames...",  "makeFrames.py"),
        ("🎵 Gerando áudio...",   "makeAudio.py"),
        ("🎬 Gerando outro...",   "makeOutro.py"),
        ("🎞️ Montando vídeo...", "makeVideo.py"),
    ]

    for nome_passo, script in passos:
        run_step(nome_passo, script, env)

    video_final = os.path.join(OUTPUT_DIR, "video_pomodoro.mp4")
    destino     = os.path.join(VIDEOS_DIR, f"{nome}.mp4")

    if os.path.exists(video_final):
        shutil.move(video_final, destino)
        print(f"\n✅ Vídeo salvo em: {destino}")
    else:
        print("❌ Vídeo final não encontrado")

    limpar_frames_temporarios()

def main():
    preparar_pastas()
    with open(VIDEOS_CONFIG_PATH) as f:
        videos = json.load(f)["videos"]
    print("🚀 Iniciando geração automática de vídeos...\n")
    for video in videos:
        gerar_video(video)
    print("\n🏁 Todos os vídeos foram gerados!")

if __name__ == "__main__":
    main()