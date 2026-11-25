#!/usr/bin/env python3
"""Draw the 25 November 2026 world-news front page (1024x1024 PNG).

Build-time only. Uses Pillow if available; the shipped entry.png is drawn
by this script and copied verbatim by main.py at run time.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (160, 30, 30)
DARKRED = (120, 20, 20)
GREY = (90, 84, 72)
RULE = (26, 26, 26)
SKY_TOP = (38, 48, 84)
SKY_MID = (214, 110, 52)
SKY_LOW = (242, 178, 96)
SEA = (16, 42, 66)
SEA2 = (24, 62, 92)
FLAME = (255, 150, 40)
FLAME2 = (255, 210, 90)
SMOKE = (70, 66, 60)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill, spacing=4):
    lines = wrap(draw, text, fnt, max_w)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def hero(img, x0, y0, x1, y1):
    """Dawn over the Strait of Hormuz: burning tanker, mines, warships.

    Drawn on a separate layer so flames and smoke can never spill
    outside the hero box.
    """
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGB", (w, h), SEA)
    ld = ImageDraw.Draw(layer)
    # sky gradient (top ~52% of the box)
    sky_h = int(h * 0.52)
    for i in range(sky_h):
        t = i / max(1, sky_h - 1)
        if t < 0.5:
            c = tuple(int(SKY_TOP[k] + (SKY_MID[k] - SKY_TOP[k]) * t * 2) for k in range(3))
        else:
            c = tuple(int(SKY_MID[k] + (SKY_LOW[k] - SKY_MID[k]) * (t - 0.5) * 2) for k in range(3))
        ld.line([(0, i), (w, i)], fill=c)
    # low sun
    sx, sy = int(w * 0.72), int(h * 0.30)
    for r, col in ((34, (255, 190, 110)), (25, (255, 214, 140)), (17, (255, 236, 180))):
        ld.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col)
    # distant headlands
    ld.polygon([(0, sky_h), (150, int(h * 0.36)), (270, sky_h)], fill=(52, 44, 66))
    ld.polygon([(w, sky_h), (w - 120, int(h * 0.40)), (w - 230, sky_h)], fill=(52, 44, 66))
    # sea
    ld.rectangle([0, sky_h, w, h], fill=SEA)
    for j in range(5):
        yy = sky_h + 8 + j * 12
        ld.line([(16, yy), (w - 16, yy)], fill=SEA2, width=2)
    # sun reflection
    for j in range(4):
        yy = sky_h + 10 + j * 13
        rw = 70 - j * 12
        ld.line([(sx - rw, yy), (sx + rw, yy)], fill=(255, 190, 110), width=3)
    # tanker hull (left-centre)
    hx0, hy = 70, sky_h + 14
    ld.polygon([(hx0, hy), (hx0 + 350, hy), (hx0 + 325, hy + 38),
                (hx0 + 25, hy + 38)], fill=(18, 18, 20))
    ld.rectangle([hx0 + 50, hy - 32, hx0 + 270, hy], fill=(30, 30, 34))
    ld.rectangle([hx0 + 50, hy - 32, hx0 + 270, hy - 24], fill=(140, 30, 30))
    # funnel with flames, sitting on the deck (deck spans hx0+50..hx0+270)
    ld.rectangle([hx0 + 230, hy - 52, hx0 + 262, hy - 28], fill=(200, 40, 30))
    for fx, fw, fh in ((232, 10, 22), (241, 12, 30), (252, 9, 18)):
        ld.polygon([(hx0 + fx, hy - 52), (hx0 + fx + fw // 2, hy - 52 - fh),
                    (hx0 + fx + fw, hy - 52)], fill=FLAME)
        ld.polygon([(hx0 + fx + 3, hy - 52), (hx0 + fx + fw // 2, hy - 52 - fh + 11),
                    (hx0 + fx + fw - 3, hy - 52)], fill=FLAME2)
    # smoke plume rising from the funnel, light grey, inside the box
    for i, (cx, cy, r) in enumerate(((hx0 + 240, 34, 9), (hx0 + 232, 22, 11),
                                     (hx0 + 222, 12, 13))):
        ld.ellipse([cx - r, cy - r, cx + r, cy + r],
                   fill=(150, 145, 138) if i % 2 == 0 else (122, 117, 110))
    # naval mines in the water, right of the tanker (above the caption strip)
    for mx, my in ((540, 118), (610, 126), (480, 122)):
        ld.ellipse([mx - 10, my - 10, mx + 10, my + 10], fill=(12, 12, 12))
        for dx, dy in ((-10, 0), (10, 0), (0, -10), (-7, -7), (7, -7)):
            ld.line([(mx, my), (mx + dx, my + dy)], fill=(12, 12, 12), width=3)
        ld.arc([mx - 16, my - 3, mx + 16, my + 11], 0, 180,
               fill=(120, 180, 210), width=2)
    # small warship silhouette, far right
    wx0, wy = 760, sky_h + 22
    ld.polygon([(wx0, wy), (wx0 + 150, wy), (wx0 + 132, wy + 22),
                (wx0 + 16, wy + 22)], fill=(10, 10, 12))
    ld.rectangle([wx0 + 52, wy - 20, wx0 + 96, wy], fill=(10, 10, 12))
    ld.line([(wx0 + 73, wy - 34), (wx0 + 73, wy - 20)], fill=(10, 10, 12), width=4)
    # caption strip
    ld.rectangle([0, h - 24, w, h], fill=(0, 0, 0))
    ld.text((12, h - 21),
            "A tanker burns in the Strait of Hormuz at dawn, 25 November 2026.",
            font=font(SANS, 14), fill=(240, 240, 240))
    # paste the layer (clips flames/smoke to the hero box)
    img.paste(layer, (x0, y0))


def card(draw, x, y, w, h, kicker, headline, body):
    draw.rectangle([x, y, x + w, y + h], outline=(180, 172, 156), width=1)
    draw.line([(x + 12, y + 26), (x + w - 12, y + 26)], fill=(200, 192, 176), width=1)
    draw.text((x + 12, y + 6), kicker, font=font(SANS_B, 13), fill=RED)
    yy = y + 32
    yy = draw_wrapped(draw, x + 12, yy, headline, font(SERIF_B, 19), w - 24, INK, spacing=1)
    draw_wrapped(draw, x + 12, yy + 3, body, font(SANS, 13), w - 24, (60, 56, 48), spacing=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # thin outer frame
    d.rectangle([10, 10, W - 11, H - 11], outline=INK, width=2)

    # top bar
    f_top = font(SANS_B, 15)
    d.text((28, 22), "WEDNESDAY, 25 NOVEMBER 2026", font=f_top, fill=INK)
    d.text((W - 28 - d.textlength("WORLD NEWS  •  ONE DAY, ONE PAGE", font=f_top),
            22), "WORLD NEWS  •  ONE DAY, ONE PAGE", font=f_top, fill=INK)
    d.line([(28, 46), (W - 28, 46)], fill=RULE, width=2)

    # masthead (largest size that fits the page width)
    title = "THE WORLD TODAY"
    mast_size = 88
    while mast_size > 40:
        f_mast = font(SERIF_B, mast_size)
        if d.textlength(title, font=f_mast) <= W - 56:
            break
        mast_size -= 2
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 52), title, font=f_mast, fill=INK)
    d.line([(28, 148), (W - 28, 148)], fill=RULE, width=3)
    d.line([(28, 154), (W - 28, 154)], fill=RULE, width=1)

    # headline
    f_head = font(SERIF_B, 74)
    hl = "STRAIT OF FIRE"
    d.text(((W - d.textlength(hl, font=f_head)) / 2, 162), hl,
           font=f_head, fill=DARKRED)
    sub = ("Mines hit more tankers in Hormuz as the Gulf war widens — "
           "Riyadh tower struck, Hodeidah hit back")
    draw_wrapped(d, 60, 246, sub, font(SERIF, 24), W - 120, INK, spacing=2)

    # hero illustration
    hero(img, 28, 306, W - 28, 470)

    # lead paragraph
    lead = ("Iran's Revolutionary Guards say two more oil tankers struck naval mines "
            "in the Strait of Hormuz at dawn — a day after claiming three. A Houthi "
            "projectile hit Riyadh's PIF Tower, wounding 11. The Saudi-led coalition "
            "ordered civilians out of Hodeidah port, then struck Hodeidah, Saada and "
            "Amran. Strait transits are down over 40% and Brent crude is near $89.")
    draw_wrapped(d, 28, 478, lead, font(SERIF, 18), W - 56, INK, spacing=3)

    # story cards: 2 columns x 3 rows
    cards = [
        ("UKRAINE  •  RUSSIA",
         "Putin vows \"inevitable\" retaliation",
         "Speaking to oil executives at the Kremlin, Putin promises payback for "
         "Ukraine's refinery strikes."),
        ("UKRAINE  •  NORWAY",
         "Sparta II hit; Norway pledges $7bn to Kyiv",
         "Zelensky confirms the strike in the Gulf of Finland; Norway pledges "
         "at least $7bn for 2027, air defence first."),
        ("BALTICS",
         "Latvia weighs closing its border with Russia",
         "Riga considers sealing the frontier; Moscow summons Latvia's "
         "diplomat in protest."),
        ("HUNGARY  •  UKRAINE",
         "Magyar meets Zelensky in Uzhhorod",
         "Hungary's PM holds his first formal meeting with President Zelensky "
         "in western Ukraine."),
        ("FRANCE",
         "Sarkozy and Bruni ordered to stand trial",
         "The ex-president and Carla Bruni face trial in the Libya case; "
         "hearing 1 April 2027."),
        ("MIDDLE EAST  •  SPACE",
         "Gaza strikes kill seven; Shenzhou-24 launches",
         "Israeli strikes kill seven in Gaza, including a senior Hamas official; "
         "Shenzhou-24 launches from Jiuquan."),
    ]
    cw, ch, gap = 472, 112, 8
    x0, y0 = 28, 570
    for i, (kick, head, body) in enumerate(cards):
        cx = x0 + (i % 2) * (cw + gap)
        cy = y0 + (i // 2) * (ch + gap)
        card(d, cx, cy, cw, ch, kick, head, body)

    # footer ticker
    fy = 570 + 3 * ch + 2 * gap + 8
    d.rectangle([28, fy, W - 28, H - 28], fill=(26, 26, 26))
    f_tick = font(SANS_B, 14)
    d.text((44, fy + 7), "ALSO TODAY", font=f_tick, fill=(255, 190, 110))
    briefs = ("South Korea: Russian jets in its air-defence zone  •  Iraq to seize "
              "Kurdish oilfields  •  DR Congo rebels pull back  •  Indonesia VP "
              "resigns  •  Shein $100m settlement  •  FBI database breach  •  "
              "Giuliani Medal of Freedom; turkeys Freedom and Feathers pardoned")
    draw_wrapped(d, 44, fy + 27, briefs, font(SANS, 13), W - 88,
                 (235, 235, 235), spacing=2)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
