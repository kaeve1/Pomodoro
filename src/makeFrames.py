# makeFrames.py
from PIL import Image, ImageDraw, ImageFont
import json
import math
import os
from multiprocessing import Pool, Value
import ctypes

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = r"E:\PomodojoFrames"

FPS            = 30
THREADS        = 13
QUALIDADE_JPEG = 95

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

# contador compartilhado entre workers
contador_global = None

def init_counter(c):
    global contador_global
    contador_global = c

def gerar_e_salvar(args):
    """Worker — tudo passado por argumento, sem depender de globais"""
    (contador, prog_focus, prog_break, fase, timer_focus, timer_break,
     base_dir, cor_focus, cor_break, cor_focus_elem, cor_break_elem,
     cor_inativo, duracao_break_val, output_dir) = args

    from PIL import Image, ImageDraw, ImageFont
    import math, os, json

    with open(os.path.join(base_dir, "config.json")) as f:
        config = json.load(f)

    W2, H2    = config["resolucao"]
    FONT_BOLD = os.path.join(base_dir, config["fontes"]["bold"])

    font_titulo = ImageFont.truetype(FONT_BOLD, size=80)
    font_timer  = ImageFont.truetype(FONT_BOLD, size=200)

    def recolorizar(icone, cor):
        r, g, b, a = icone.split()
        r = r.point(lambda p: int(p * cor[0] / 255))
        g = g.point(lambda p: int(p * cor[1] / 255))
        b = b.point(lambda p: int(p * cor[2] / 255))
        return Image.merge("RGBA", (r, g, b, a))

    _if = Image.open(os.path.join(base_dir, config["focus"]["icone"])).convert("RGBA").resize((220, 220), Image.Resampling.LANCZOS)
    _ib = Image.open(os.path.join(base_dir, config["break"]["icone"])).convert("RGBA").resize((220, 220), Image.Resampling.LANCZOS)
    icone_focus_w = recolorizar(_if, cor_focus_elem)
    icone_break_w = recolorizar(_ib, cor_break_elem)

    img  = Image.new("RGB", (W2, H2), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    cor_elem_ativo   = cor_focus_elem if fase == "focus" else cor_break_elem
    cor_elem_inativo = cor_inativo

    draw.rectangle([0,      0, W2//2, H2], fill=cor_focus)
    draw.rectangle([W2//2,  0, W2,   H2], fill=cor_break)

    def centralizar(texto, font, area_x, area_w, y, cor):
        bbox = draw.textbbox((0, 0), texto, font=font)
        x = area_x + (area_w - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), texto, font=font, fill=cor)

    def circulo(cx, cy, raio, prog, cor_a, cor_i):
        bbox = [cx-raio, cy-raio, cx+raio, cy+raio]
        for i in range(0, 360, 3):
            ang = math.radians(i)
            x1  = cx + (raio-13) * math.cos(ang)
            y1  = cy + (raio-13) * math.sin(ang)
            draw.ellipse([x1-3, y1-3, x1+3, y1+3], fill=cor_i)
        af = -90 + (360 * prog)
        if af > -90:
            draw.arc(bbox, start=-90, end=af, fill=cor_a, width=26)

    def desenhar_icone(ic, cx, cy, ativo, ox=0, oy=0):
        iw, ih = ic.size
        x, y = cx - iw//2 + ox, cy - ih//2 + oy
        if not ativo:
            ic2 = ic.copy()
            r, g, b, a = ic2.split()
            a = a.point(lambda p: int(p * 0.4))
            ic2 = Image.merge("RGBA", (r, g, b, a))
            img.paste(ic2, (x, y), ic2)
        else:
            img.paste(ic, (x, y), ic)

    def fmt(s):
        return f"{s//60:02d}:{s%60:02d}"

    raio     = 250
    cx_focus = W2 // 4
    cy_focus = H2 // 2
    cx_break = W2 - W2 // 4
    cy_break = H2 // 2

    cor_arco_f = cor_elem_ativo   if fase == "focus" else cor_elem_inativo
    cor_txt_f  = cor_focus_elem   if fase == "focus" else cor_inativo
    cor_arco_b = cor_elem_ativo   if fase == "break" else cor_elem_inativo
    cor_txt_b  = cor_break_elem   if fase == "break" else cor_inativo

    centralizar("FOCUS", font_titulo, 0,      W2//2, 60,       cor_txt_f)
    circulo(cx_focus, cy_focus, raio, max(prog_focus, 0.01), cor_arco_f, cor_elem_inativo)
    desenhar_icone(icone_focus_w, cx_focus, cy_focus, fase=="focus")
    centralizar(fmt(timer_focus), font_timer, 0, W2//2, H2-280, cor_txt_f)

    prog_b = max(prog_break, 0.01) if duracao_break_val > 0 else 0
    centralizar("BREAK", font_titulo, W2//2, W2//2, 60,       cor_txt_b)
    circulo(cx_break, cy_break, raio, prog_b, cor_arco_b, cor_elem_inativo)
    desenhar_icone(icone_break_w, cx_break, cy_break, fase=="break", ox=18, oy=-18)
    centralizar(fmt(timer_break), font_timer, W2//2, W2//2, H2-280, cor_txt_b)

    caminho = os.path.join(output_dir, f"frame_{str(contador).zfill(6)}.jpg")
    img.save(caminho, "JPEG", quality=95)

    # progresso a cada 1000 frames
    with contador_global.get_lock():
        contador_global.value += 1
        if contador_global.value % 1000 == 0:
            print(f"  ⚡ {contador_global.value} frames gerados...")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # lê config
    with open(os.path.join(BASE_DIR, "config.json")) as f:
        config = json.load(f)

    # lê variáveis de ambiente
    duracao_focus = int(os.environ["FOCUS_DURATION"])
    duracao_break = int(os.environ["BREAK_DURATION"])
    ciclos        = int(os.environ["CYCLES"])

    # calcula cores
    cor_focus      = hex_to_rgb(os.environ["FOCUS_COLOR"])
    cor_break      = hex_to_rgb(os.environ["BREAK_COLOR"])
    cor_focus_elem = cor_break
    cor_break_elem = cor_focus
    cor_inativo    = tuple((a + b) // 2 for a, b in zip(cor_focus, cor_break))

    # argumentos fixos passados pra cada worker
    args_fixos = (
        BASE_DIR, cor_focus, cor_break,
        cor_focus_elem, cor_break_elem,
        cor_inativo, duracao_break, OUTPUT_DIR
    )

    # ─── MONTA TAREFAS ────────────────────────────────────
    tarefas  = []
    contador = 0

    for ciclo in range(ciclos):

        # focus
        for segundo in range(duracao_focus, 0, -1):
            for sf in range(FPS):
                prog = (segundo - sf / FPS) / duracao_focus
                tarefas.append((contador, prog, 1.0, "focus", segundo, duracao_break) + args_fixos)
                contador += 1

        if duracao_break > 0 and ciclo < ciclos - 1:

            # transição focus→break
            for i in range(3 * FPS):
                p  = (i + 1) / (3 * FPS)
                tf = int(duracao_focus * p)
                tarefas.append((contador, p, 1.0, "focus", tf, duracao_break) + args_fixos)
                contador += 1

            # break
            for segundo in range(duracao_break, 0, -1):
                for sf in range(FPS):
                    prog = (segundo - sf / FPS) / duracao_break
                    tarefas.append((contador, 1.0, prog, "break", duracao_focus, segundo) + args_fixos)
                    contador += 1

            # transição break→focus
            for i in range(3 * FPS):
                p  = (i + 1) / (3 * FPS)
                tb = int(duracao_break * p)
                tarefas.append((contador, 1.0, p, "break", duracao_focus, tb) + args_fixos)
                contador += 1

    print(f"📋 Total de frames: {len(tarefas)}")
    print(f"⚡ Usando {THREADS} threads...")

    c = Value(ctypes.c_int, 0)
    with Pool(THREADS, initializer=init_counter, initargs=(c,)) as pool:
        pool.map(gerar_e_salvar, tarefas)

    print(f"\n✅ {contador} frames gerados em {OUTPUT_DIR}")