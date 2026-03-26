
import os
import json
import subprocess
import glob

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
FRAMES_DIR = r"E:\PomodojoFrames"
TEMP_DIR   = os.path.join(OUTPUT_DIR, "temp")

os.makedirs(TEMP_DIR, exist_ok=True)

with open(os.path.join(BASE_DIR, "config.json")) as f:
    config = json.load(f)

# ─── VERIFICA FRAMES ──────────────────────────────────────
frames_intro = sorted(glob.glob(os.path.join(FRAMES_DIR, "intro_*.png")))
frames_video = sorted(glob.glob(os.path.join(FRAMES_DIR, "frame_*.jpg")))
frames_outro = sorted(glob.glob(os.path.join(FRAMES_DIR, "outro_*.png")))

if not frames_intro:
    raise Exception("❌ Nenhum frame de intro encontrado!")
if not frames_video:
    raise Exception("❌ Nenhum frame de vídeo encontrado!")
if not frames_outro:
    raise Exception("❌ Nenhum frame de outro encontrado!")

print(f"  Intro: {len(frames_intro)} frames")
print(f"  Vídeo: {len(frames_video)} frames")
print(f"  Outro: {len(frames_outro)} frames")

# ─── CAMINHOS ─────────────────────────────────────────────
intro_mp4  = os.path.join(TEMP_DIR, "intro.mp4")
video_mp4  = os.path.join(TEMP_DIR, "video.mp4")
outro_mp4  = os.path.join(TEMP_DIR, "outro.mp4")
concat_mp4 = os.path.join(TEMP_DIR, "concat.mp4")
final_mp4  = os.path.join(OUTPUT_DIR, "video_pomodoro.mp4")
lista_txt  = os.path.join(TEMP_DIR, "lista.txt")
audio_mp3  = os.path.join(OUTPUT_DIR, "audio_pomodoro.mp3")

temporarios = [intro_mp4, video_mp4, outro_mp4, concat_mp4, lista_txt]

def rodar_ffmpeg(args, descricao):
    print(f"\n{descricao}")
    resultado = subprocess.run(
        ["ffmpeg", "-y"] + args,
        capture_output=True,
        text=True
    )
    if resultado.returncode != 0:
        print(resultado.stderr)
        raise Exception(f"❌ FFmpeg falhou: {descricao}")
    print(f"✅ {descricao} concluído!")

def limpar_temporarios():
    print("\n🗑️ Limpando arquivos temporários...")
    for f in temporarios:
        if os.path.exists(f):
            os.remove(f)
    print("✅ Temporários removidos!")

# ─── EXECUÇÃO COM PROTEÇÃO ────────────────────────────────
try:

    # 1. INTRO
    print("\n🎬 Montando intro...")
    rodar_ffmpeg([
        "-framerate", "30",
        "-i", os.path.join(FRAMES_DIR, "intro_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        intro_mp4
    ], "Intro")

    # 2. VÍDEO PRINCIPAL
    print("\n🎬 Montando vídeo principal...")
    rodar_ffmpeg([
        "-framerate", "30",
        "-i", os.path.join(FRAMES_DIR, "frame_%06d.jpg"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        video_mp4
    ], "Vídeo principal")

    # 3. OUTRO
    print("\n🎬 Montando outro...")
    rodar_ffmpeg([
        "-framerate", "30",
        "-i", os.path.join(FRAMES_DIR, "outro_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        outro_mp4
    ], "Outro")

    # 4. CONCATENA
    print("\n🔗 Concatenando clipes...")
    with open(lista_txt, "w") as f:
        f.write(f"file '{intro_mp4}'\n")
        f.write(f"file '{video_mp4}'\n")
        f.write(f"file '{outro_mp4}'\n")

    rodar_ffmpeg([
        "-f", "concat",
        "-safe", "0",
        "-i", lista_txt,
        "-c", "copy",
        concat_mp4
    ], "Concatenação")

    # 5. ADICIONA ÁUDIO
    print("\n🎵 Adicionando áudio...")
    rodar_ffmpeg([
        "-i", concat_mp4,
        "-i", audio_mp3,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        final_mp4
    ], "Áudio")

    print(f"\n✅ Vídeo final gerado em: {final_mp4}")

except Exception as e:
    print(f"\n❌ Erro: {e}")
    raise

finally:
    # sempre limpa — mesmo se der erro
    limpar_temporarios()
