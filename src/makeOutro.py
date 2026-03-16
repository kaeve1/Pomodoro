# makeOutro.py
import os
import json
from PIL import Image
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(os.path.join(BASE_DIR, "config.json")) as f:
    config = json.load(f)

W, H = config["resolucao"]

focus_color = os.environ.get("FOCUS_COLOR", "#FFC2C2")
break_color = os.environ.get("BREAK_COLOR", "#FFE6E6")

def hex_to_rgb(hex):
    hex = hex.lstrip("#")
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

COR_FUNDO = hex_to_rgb(focus_color)
COR_ELEM  = hex_to_rgb(break_color)

def branquear_e_recolorizar(img, cor):
    """Força todos os pixels visíveis pra branco puro, depois aplica a cor"""
    data = np.array(img)

    # pega o canal alpha
    alpha = data[:, :, 3]

    # força todos os pixels com alpha > 0 pra branco puro
    data[:, :, 0] = np.where(alpha > 30, 255, 0)  # R
    data[:, :, 1] = np.where(alpha > 30, 255, 0)  # G
    data[:, :, 2] = np.where(alpha > 30, 255, 0)  # B
    data[:, :, 3] = np.where(alpha > 30, 255, 0)  # A — binário, sem meios tons

    img_branca = Image.fromarray(data)

    # agora aplica a cor desejada
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

frame = gerar_frame_outro()
for i in range(20):
    frame.save(os.path.join(OUTPUT_DIR, f"outro_{str(i).zfill(3)}.png"))

print("✅ Outro gerado — 20 frames")