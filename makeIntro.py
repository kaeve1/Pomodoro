# makeIntro.py
from PIL import Image, ImageDraw, ImageFont
import json

with open("config.json") as f:
    config = json.load(f)

W, H = config["resolucao"]
FONT_BOLD = config["fontes"]["bold"]

def hex_to_rgb(hex):
    hex = hex.lstrip("#")
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

COR_FOCUS = hex_to_rgb(config["focus"]["cor_fundo"])
COR_BREAK = hex_to_rgb(config["break"]["cor_fundo"])

font_titulo = ImageFont.truetype(FONT_BOLD, size=80)
font_numero = ImageFont.truetype(FONT_BOLD, size=400)

def centralizar_texto(draw, texto, font, y, cor):
    bbox = draw.textbbox((0, 0), texto, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) / 2
    draw.text((x, y), texto, font=font, fill=cor)

print("Gerando frames da intro...")

for segundo in range(10, 0, -1):
    img = Image.new("RGB", (W, H), color=COR_FOCUS)
    draw = ImageDraw.Draw(img)

    # texto "FOCUS STARTS IN"
    centralizar_texto(draw, "FOCUS STARTS IN", font_titulo, 180, COR_BREAK)

    # número grande
    centralizar_texto(draw, str(segundo), font_numero, H//2 - 220, COR_BREAK)

    img.save(f"output/intro_{str(segundo).zfill(2)}.png")
    print(f"Intro {segundo}")

print("✅ Frames da intro gerados!")