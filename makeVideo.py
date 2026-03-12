# makeVideo.py
import glob
from moviepy import ImageSequenceClip, AudioFileClip
import json

with open("config.json") as f:
    config = json.load(f)
    
print("📽️ Carregando frames...")
frames_intro = sorted(glob.glob("output/intro_*.png"))
frames_video = sorted(glob.glob("output/frame_*.png"))
frames = frames_intro + frames_video
print(f"{len(frames)} frames encontrados!")

print("📽️ Carregando frames...")

print(f"{len(frames)} frames encontrados!")

print("🎬 Montando vídeo...")
clipe_video = ImageSequenceClip(frames, fps=1)

print("🎵 Carregando áudio...")
clipe_audio = AudioFileClip("output/audio_pomodoro.mp3")

print("🔗 Conectando áudio ao vídeo...")
clipe_final = clipe_video.with_audio(clipe_audio)

clipe_final.write_videofile("output/video_pomodoro.mp4", fps=1)
print("✅ Vídeo final gerado!")