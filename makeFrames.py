from PIL import Image, ImageDraw, ImageFont
import json
import math

# ─── CONFIG ───────────────────────────────────────────────
with open("config.json") as f:
    config = json.load(f)

W, H = config["resolucao"]
FONT_BOLD = config["fontes"]["bold"]
FONT_REGULAR = config["fontes"]["regular"]

# ─── CORES ────────────────────────────────────────────────
def hex_to_rgb(hex):
    hex = hex.lstrip("#")
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

COR_FOCUS   = hex_to_rgb(config["focus"]["cor_fundo"])
COR_BREAK   = hex_to_rgb(config["break"]["cor_fundo"])
COR_INATIVO = (240, 210, 210)

# ─── FONTES ───────────────────────────────────────────────
font_titulo = ImageFont.truetype(FONT_BOLD, size=80)
font_timer  = ImageFont.truetype(FONT_BOLD, size=200)

# ─── ÍCONES ───────────────────────────────────────────────
icone_focus = Image.open(config["focus"]["icone"]).convert("RGBA").resize((220, 220), Image.Resampling.LANCZOS)
icone_break = Image.open(config["break"]["icone"]).convert("RGBA").resize((220, 220), Image.Resampling.LANCZOS)

# ─── FUNÇÕES ──────────────────────────────────────────────
def formatar_tempo(segundos):
    m = segundos // 60
    s = segundos % 60
    return f"{m:02d}:{s:02d}"

def centralizar_texto(draw, texto, font, area_x, area_largura, y, cor=(255, 255, 255)):
    bbox = draw.textbbox((0, 0), texto, font=font)
    tw = bbox[2] - bbox[0]
    x = area_x + (area_largura - tw) / 2
    draw.text((x, y), texto, font=font, fill=cor)

def desenhar_circulo_progresso(draw, cx, cy, raio, progresso, cor_ativo, cor_inativo):
    bbox = [cx - raio, cy - raio, cx + raio, cy + raio]

    for i in range(0, 360, 8):
        ang = math.radians(i)
        x1 = cx + (raio - 3) * math.cos(ang)
        y1 = cy + (raio - 3) * math.sin(ang)
        draw.ellipse([x1-3, y1-3, x1+3, y1+3], fill=cor_inativo)

    angulo_inicio = -90
    angulo_fim = -90 + (360 * progresso)
    if angulo_fim > angulo_inicio:
        draw.arc(bbox, start=angulo_inicio, end=angulo_fim, fill=cor_ativo, width=4)

def desenhar_icone(img, icone, cx, cy, ativo=True, offset_x=0, offset_y=0):
    iw, ih = icone.size
    x = cx - iw // 2 + offset_x
    y = cy - ih // 2 + offset_y

    if not ativo:
        icone_copia = icone.copy()
        r, g, b, a = icone_copia.split()
        a = a.point(lambda p: p * 0.4)
        icone_copia = Image.merge("RGBA", (r, g, b, a))
        img.paste(icone_copia, (x, y), icone_copia)
    else:
        img.paste(icone, (x, y), icone)

def gerar_frame(frame_focus, frame_break, fase, duracao_focus, duracao_break):
    img = Image.new("RGB", (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    cor_fundo_focus  = COR_FOCUS
    cor_fundo_break  = COR_BREAK
    cor_elem_ativo   = COR_BREAK if fase == "focus" else COR_FOCUS
    cor_elem_inativo = COR_INATIVO

    draw.rectangle([0,    0, W//2, H], fill=cor_fundo_focus)
    draw.rectangle([W//2, 0, W,   H], fill=cor_fundo_break)

    # ── LADO FOCUS ──
    cx_focus = W // 4
    cy_focus = H // 2
    raio = 250

    cor_arco_focus = cor_elem_ativo   if fase == "focus" else cor_elem_inativo
    cor_txt_focus  = COR_BREAK

    prog_focus = max(frame_focus / duracao_focus, 0.01)

    centralizar_texto(draw, "FOCUS", font_titulo, 0, W//2, 60, cor=cor_txt_focus)
    desenhar_circulo_progresso(draw, cx_focus, cy_focus, raio, prog_focus, cor_arco_focus, cor_elem_inativo)
    desenhar_icone(img, icone_focus, cx_focus, cy_focus, ativo=(fase == "focus"))
    centralizar_texto(draw, formatar_tempo(frame_focus), font_timer, 0, W//2, H - 280, cor=cor_txt_focus)

    # ── LADO BREAK ──
    cx_break = W - W // 4
    cy_break = H // 2

    cor_arco_break = cor_elem_ativo   if fase == "break" else cor_elem_inativo
    cor_txt_break  = COR_FOCUS

    prog_break = max(frame_break / duracao_break, 0.01)

    centralizar_texto(draw, "BREAK", font_titulo, W//2, W//2, 60, cor=cor_txt_break)
    desenhar_circulo_progresso(draw, cx_break, cy_break, raio, prog_break, cor_arco_break, cor_elem_inativo)
    desenhar_icone(img, icone_break, cx_break, cy_break, ativo=(fase == "break"), offset_x=18, offset_y=-18)
    centralizar_texto(draw, formatar_tempo(frame_break), font_timer, W//2, W//2, H - 280, cor=cor_txt_break)

    return img

# ─── GERAÇÃO ──────────────────────────────────────────────
duracao_focus = config["focus"]["duracao"]
duracao_break = config["break"]["duracao"]
ciclos        = config["ciclos"]
contador      = 0

for ciclo in range(ciclos):
    print(f"\n🔴 Ciclo {ciclo + 1}/{ciclos} — FOCUS")
    for frame in range(duracao_focus, 0, -1):
        img = gerar_frame(frame, duracao_break, "focus", duracao_focus, duracao_break)
        img.save(f"output/frame_{str(contador).zfill(5)}.png")
        contador += 1
        if frame % 100 == 0:
            print(f"  Focus {formatar_tempo(frame)}")

    print(f"🟢 Ciclo {ciclo + 1}/{ciclos} — BREAK")
    for frame in range(duracao_break, 0, -1):
        img = gerar_frame(duracao_focus, frame, "break", duracao_focus, duracao_break)
        img.save(f"output/frame_{str(contador).zfill(5)}.png")
        contador += 1
        if frame % 100 == 0:
            print(f"  Break {formatar_tempo(frame)}")

print(f"\n✅ {contador} frames gerados!")