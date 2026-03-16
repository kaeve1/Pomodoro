# makeVideo.py
import glob
import os
import json
from moviepy import ImageSequenceClip, AudioFileClip, concatenate_videoclips

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

with open(os.path.join(BASE_DIR, "config.json")) as f:
    config = json.load(f)

print("📽️ Carregando frames...")
frames_intro = sorted(glob.glob(os.path.join(OUTPUT_DIR, "intro_*.png")))
frames_video = sorted(glob.glob(os.path.join(OUTPUT_DIR, "frame_*.png")))
frames_outro = sorted(glob.glob(os.path.join(OUTPUT_DIR, "outro_*.png")))  

print(f"  Intro: {len(frames_intro)} frames (30fps)")
print(f"  Vídeo: {len(frames_video)} frames (1fps)")
print(f"  Outro: {len(frames_outro)} frames (1fps)")  

print("🎬 Montando clipes...")
clipe_intro = ImageSequenceClip(frames_intro, fps=30)
clipe_video = ImageSequenceClip(frames_video, fps=1)
clipe_outro = ImageSequenceClip(frames_outro, fps=1)

print("🔗 Concatenando intro + vídeo + outro...")
clipe_final = concatenate_videoclips([clipe_intro, clipe_video, clipe_outro])

print("🎵 Carregando áudio...")
clipe_audio = AudioFileClip(os.path.join(OUTPUT_DIR, "audio_pomodoro.mp3"))
print(f"  Duração do áudio: {clipe_audio.duration:.1f}s")
print(f"  Duração do vídeo: {clipe_final.duration:.1f}s")

print("🔗 Conectando áudio...")
clipe_final = clipe_final.with_audio(clipe_audio)

clipe_final.write_videofile(
    os.path.join(OUTPUT_DIR, "video_pomodoro.mp4"),
    fps=30,
    codec="libx264",
    audio_codec="aac",
    audio=True
)
print("✅ Vídeo final gerado!")