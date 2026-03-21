# makeOutro.py
import os
import json
from PIL import Image
import numpy as np

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = r"E:\PomodojoFrames"
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(os.path.join(BASE_DIR, "config.json")) as f:
    config = json.load(f)

W, H = config["resolucao"]

focus_color = os.environ.get("FOCUS_COLOR", "#FFC2C2")
break_color = os.environ.get("BREAK_COLOR", "#FFE6E6")

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

COR_FUNDO = hex_to_rgb(focus_color)
COR_ELEM  = hex_to_rgb(break_color)

def branquear_e_recolorizar(img, cor):
    data  = np.array(img)
    alpha = data[:, :, 3]
    data[:, :, 0] = np.where(alpha > 30, 255, 0)
    data[:, :, 1] = np.where(alpha > 30, 255, 0)
    data[:, :, 2] = np.where(alpha > 30, 255, 0)
    data[:, :, 3] = np.where(alpha > 30, 255, 0)
    img_branca = Image.fromarray(data)
    r, g, b, a = img_branca.split()
    r = r.point(lambda p: int(p * cor[0] / 255))
    g = g.point(lambda p: int(p * cor[1] / 255))
    b = b.point(lambda p: int(p * cor[2] / 255))
    return Image.merge("RGBA", (r, g, b, a))

overlay_path = os.path.join(BASE_DIR, "assets", "pomodojo_outro_transparente.png")
overlay_raw  = Image.open(overlay_path).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
overlay      = branquear_e_recolorizar(overlay_raw, COR_ELEM)

def gerar_frame_outro():
    img = Image.new("RGB", (W, H), color=COR_FUNDO)
    img.paste(overlay, (0, 0), overlay)
    return img

print("Gerando frames do outro...")

DURACAO_SEGUNDOS = 20
FPS              = 30
TOTAL_FRAMES     = DURACAO_SEGUNDOS * FPS  # 600 frames = 20 segundos a 30fps

frame = gerar_frame_outro()  # gera uma vez e reutiliza
for i in range(TOTAL_FRAMES):
    frame.save(os.path.join(OUTPUT_DIR, f"outro_{str(i).zfill(4)}.png"))

print(f"✅ Outro gerado — {TOTAL_FRAMES} frames ({DURACAO_SEGUNDOS}s a {FPS}fps)")