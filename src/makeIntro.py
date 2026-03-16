# makeIntro.py
import os
import json
import math
import random
from PIL import Image, ImageDraw, ImageFont

mensagens = [
    "LET'S GO!", "FOCUS UP!", "DEEP WORK!", "LOCK IN!", "GRIND TIME!", "STAY SHARP!", "EYES ON IT!",
    "WORK MODE!", "BEAST MODE!",
]

mensagem_sorteada = random.choice(mensagens)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(BASE_DIR, "config.json")) as f:
    config = json.load(f)

W, H = config["resolucao"]

focus_color = os.environ.get("FOCUS_COLOR", "#FFC2C2")
break_color = os.environ.get("BREAK_COLOR", "#FFE6E6")

def hex_to_rgb(hex):
    hex = hex.lstrip("#")
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

COR_FUNDO      = hex_to_rgb(focus_color)   # fundo da intro = cor do Focus
COR_ELEM       = hex_to_rgb(break_color)   # elementos da intro = cor do Break
COR_INATIVO = tuple(min(255, c + 30) for c in COR_FUNDO)

FONT_BOLD = os.path.join(BASE_DIR, config["fontes"]["bold"])
font_titulo = ImageFont.truetype(FONT_BOLD, 80)
font_numero = ImageFont.truetype(FONT_BOLD, 380)

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FPS     = 30
DURACAO = 10
RAIO    = 300
CX      = W // 2
CY      = H // 2

def centralizar(draw, texto, font, y, cor):
    bbox = draw.textbbox((0, 0), texto, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) / 2
    draw.text((x, y), texto, font=font, fill=cor)

def desenhar_circulo_pontilhado(draw, cx, cy, raio, cor):
    for i in range(0, 360, 3):
        ang = math.radians(i)
        x1 = cx + (raio - 13) * math.cos(ang)
        y1 = cy + (raio - 13) * math.sin(ang)
        draw.ellipse([x1-3, y1-3, x1+3, y1+3], fill=cor)

def desenhar_arco(draw, cx, cy, raio, progresso, cor, largura=26):
    bbox = [cx - raio, cy - raio, cx + raio, cy + raio]
    angulo_fim = -90 + (360 * progresso)
    if angulo_fim > -90:
        draw.arc(bbox, start=-90, end=angulo_fim, fill=cor, width=largura)

def gerar_frame_intro(segundo, frame_no_segundo):
    img = Image.new("RGB", (W, H), color=COR_FUNDO)
    draw = ImageDraw.Draw(img)

    progresso = frame_no_segundo / FPS

    desenhar_circulo_pontilhado(draw, CX, CY, RAIO, COR_INATIVO)
    desenhar_arco(draw, CX, CY, RAIO, progresso, COR_ELEM)

    numero_str = str(segundo)
    bbox = draw.textbbox((0, 0), numero_str, font=font_numero)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (W - tw) / 2 - bbox[0]
    y = (H - th) / 2 - bbox[1]
    draw.text((x, y), numero_str, font=font_numero, fill=COR_ELEM)

    return img

def gerar_frame_mensagem():
    img = Image.new("RGB", (W, H), color=COR_FUNDO)
    draw = ImageDraw.Draw(img)

    desenhar_circulo_pontilhado(draw, CX, CY, RAIO, COR_INATIVO)
    desenhar_arco(draw, CX, CY, RAIO, 1.0, COR_ELEM)

    bbox = draw.textbbox((0, 0), mensagem_sorteada, font=font_titulo)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (W - tw) / 2 - bbox[0]
    y = (H - th) / 2 - bbox[1]
    draw.text((x, y), mensagem_sorteada, font=font_titulo, fill=COR_ELEM)

    return img

print("Gerando frames da intro (30fps)...")
print(f"  Mensagem sorteada: {mensagem_sorteada}")

contador = 0
for segundo in range(DURACAO, 0, -1):
    for frame in range(FPS):
        img = gerar_frame_intro(segundo, frame)
        img.save(os.path.join(OUTPUT_DIR, f"intro_{str(contador).zfill(4)}.png"))
        contador += 1
        if frame == 0:
            print(f"  Segundo {segundo}")

print("  Gerando frames de transição da intro...")
FRAMES_TRANSICAO = int(3 * FPS)
frame_msg = gerar_frame_mensagem()
for i in range(FRAMES_TRANSICAO):
    frame_msg.save(os.path.join(OUTPUT_DIR, f"intro_{str(contador).zfill(4)}.png"))
    contador += 1

print(f"✅ Intro gerada — {contador} frames")