#!/usr/bin/env python3
"""
GALLUS GALLUS DOMESTICUS — Laminar Field Study  (refined pass)
Museum-quality anatomical plate in the Laminar Field aesthetic.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

W, H   = 2400, 3000
OUTPUT = "/Users/itayzit/projects/cross-the-road/chicken.png"
FONTS  = "/Users/itayzit/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/082504a1-6a32-4ade-abce-ba4c352a055c/06023871-884f-4144-b321-32a7f8da2191/skills/canvas-design/canvas-fonts"

# ── Palette ──────────────────────────────────────────────────────────────────
BG         = ( 11,   9,   5)
F_LIGHT    = (220, 196, 148)
F_MID      = (186, 157, 104)
F_DARK     = (142, 110,  60)
F_SHADOW   = ( 90,  62,  22)
COMB_COL   = (186,  32,  22)
COMB_DK    = (135,  16,  10)
WATTLE_COL = (196,  42,  26)
BEAK_COL   = (190, 152,  28)
LEG_COL    = (184, 145,  33)
EYE_RING   = ( 44,  28,   8)
EYE_IRIS   = (105,  70,  16)
ANNOT      = ( 82,  64,  32)
T_BRIGHT   = (222, 196, 146)
T_DIM      = (110,  86,  44)
T_GHOST    = ( 60,  48,  24)
GRID_COL   = ( 18,  15,   8)

def font(name, size):
    try:
        return ImageFont.truetype(f"{FONTS}/{name}", size)
    except:
        return ImageFont.load_default()

f_hero  = font("IBMPlexSerif-Regular.ttf",   86)
f_sub   = font("IBMPlexSerif-Regular.ttf",   40)
f_mono  = font("GeistMono-Regular.ttf",      25)
f_label = font("DMMono-Regular.ttf",         22)
f_tiny  = font("GeistMono-Regular.ttf",      18)

# ── Canvas & vignette ────────────────────────────────────────────────────────
canvas = Image.new("RGB", (W, H), BG)
draw   = ImageDraw.Draw(canvas)

# Subtle background vignette — paint dark ellipse at edges
vignette = Image.new("RGB", (W, H), (0, 0, 0))
vd = ImageDraw.Draw(vignette)
for i in range(80):
    t = i / 79
    alpha_like = int(38 * (1 - t)**1.8)
    r = (alpha_like, alpha_like//2, 0)
    m = i * 10
    vd.ellipse([m, m, W-m, H-m], fill=None, outline=r, width=12)
# Blend: darken edges
vblur = vignette.filter(ImageFilter.GaussianBlur(radius=60))
canvas = Image.blend(canvas, vblur, alpha=0.0)   # keep bg pure, just use for reference
draw = ImageDraw.Draw(canvas)

# Grid
for x in range(0, W+1, 120):
    draw.line([(x, 0), (x, H)], fill=GRID_COL, width=1)
for y in range(0, H+1, 120):
    draw.line([(0, y), (W, y)], fill=GRID_COL, width=1)

# ── Helpers ──────────────────────────────────────────────────────────────────
def lerp_col(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def bezier2(p0, p1, p2, n=70):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t**2*p2[0]
        y = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t**2*p2[1]
        pts.append((int(x), int(y)))
    return pts

def bezier3(p0, p1, p2, p3, n=70):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
        y = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
        pts.append((int(x), int(y)))
    return pts

def crosshair(x, y, r=10):
    draw.line([(x-r, y), (x+r, y)], fill=ANNOT, width=1)
    draw.line([(x, y-r), (x, y+r)], fill=ANNOT, width=1)
    draw.ellipse([x-3, y-3, x+3, y+3], fill=ANNOT)

# ── Chicken anchor points ─────────────────────────────────────────────────────
CX, CY  = 1190, 1680        # body centre
BRX, BRY = 468, 284         # body radii
HX, HY  = 615,  1370        # head centre
HR      = 157
TAIL    = (CX + BRX - 55, CY - 125)   # tail attachment

# ── 1. Tail feathers ─────────────────────────────────────────────────────────
tail_data = [
    (36,  18, 400, 12, F_LIGHT),
    (48,  20, 448, 14, F_MID),
    (59,  18, 478, 16, F_DARK),
    (70,  15, 465, 15, F_MID),
    (81,  12, 430, 13, F_DARK),
    (92,   9, 385, 11, F_SHADOW),
    (102,  7, 330,  9, F_SHADOW),
]
for base, sw, length, lw, col in tail_data:
    rad  = math.radians(base)
    crad = math.radians(base + sw)
    ex = TAIL[0] + int(math.cos(rad)  * length)
    ey = TAIL[1] - int(math.sin(rad)  * length)
    cx_= TAIL[0] + int(math.cos(crad) * length * 0.52)
    cy_= TAIL[1] - int(math.sin(crad) * length * 0.52)
    pts = bezier2(TAIL, (cx_, cy_), (ex, ey))
    draw.line(pts, fill=col, width=lw)
    # Barb lines
    for i in range(6, len(pts)-6, 6):
        px, py = pts[i]
        dx = pts[i+1][0] - pts[i-1][0]
        dy = pts[i+1][1] - pts[i-1][1]
        norm = math.hypot(dx, dy) or 1
        px2, py2 = -dy/norm, dx/norm
        barb = max(5, 24 - i * 0.19)
        draw.line([
            (int(px + px2*barb), int(py + py2*barb)),
            (int(px - px2*barb), int(py - py2*barb)),
        ], fill=lerp_col(col, BG, 0.38), width=1)

# ── 2. Legs (before body so body covers tops) ─────────────────────────────────
def draw_leg(ox, oy, dx, dy, s=1.0):
    ax, ay = ox + dx, oy + dy
    draw.line([(ox, oy), (ax, ay)], fill=LEG_COL, width=int(10*s))
    tx, ty = ax + int(20*s), ay + int(92*s)
    draw.line([(ax, ay), (tx, ty)], fill=LEG_COL, width=int(8*s))
    for ang in [62, 87, 113]:
        r = math.radians(ang)
        draw.line([(tx, ty), (tx+int(math.cos(r)*115*s), ty+int(math.sin(r)*115*s))],
                  fill=LEG_COL, width=int(5*s))
    draw.line([(tx, ty), (tx - int(65*s), ty + int(48*s))], fill=LEG_COL, width=int(5*s))

draw_leg(CX - 88, CY + 238, -16, 118, s=1.0)
draw_leg(CX + 58, CY + 258,  12, 108, s=0.87)

# ── 3. Body (base) ───────────────────────────────────────────────────────────
body_box = [CX - BRX, CY - BRY, CX + BRX, CY + BRY]
draw.ellipse(body_box, fill=F_LIGHT)

# Subtle body shading — darker lower half & edges
for i in range(18):
    t = i / 17
    shrink = i * 12
    shade_t = (t ** 1.5) * 0.55
    sc = lerp_col(F_LIGHT, F_SHADOW, shade_t)
    # Only draw lower half arc for bottom shading
    box = [CX - BRX + shrink//2, CY - BRY + shrink//3,
           CX + BRX - shrink//2, CY + BRY - shrink//3 + shrink//4]
    if box[2] > box[0] and box[3] > box[1]:
        draw.arc(box, start=10, end=170, fill=sc, width=1)

# ── 4. Feather scales (bottom → top so each row peeks out) ───────────────────
SCALE_W, SCALE_H = 64, 48
ROWS_, COLS_ = 18, 22

for row_inv in range(ROWS_ + 3):
    row = ROWS_ + 2 - row_inv          # draw bottom rows first
    fy = CY - BRY * 0.90 + (row / ROWS_) * BRY * 1.80
    stagger = (row % 2) * (SCALE_W // 2)
    for col in range(COLS_ + 3):
        fx = CX - BRX * 1.05 + stagger + (col / COLS_) * BRX * 2.15
        rel_x = (fx - CX) / BRX
        rel_y = (fy - CY) / BRY
        d2 = rel_x**2 + rel_y**2
        if d2 > 0.96:
            continue
        dist = math.sqrt(d2)
        edge_t = dist ** 1.35
        vert_t = max(0.0, rel_y * 0.42)
        t = min(1.0, edge_t * 0.72 + vert_t)
        sc = lerp_col(F_MID, F_SHADOW, t)
        ax, ay = int(fx - SCALE_W//2), int(fy - SCALE_H//2)
        draw.arc([ax, ay, ax+SCALE_W, ay+SCALE_H], start=198, end=342, fill=sc, width=2)

# ── 5. Neck ──────────────────────────────────────────────────────────────────
# Smooth neck using cubic bezier outline
n_top_l = (CX - BRX + 128, CY - int(BRY * 0.52))
n_bot_l = (CX - BRX + 45,  CY + 45)
n_bot_r = (HX + HR - 18,   HY + int(HR * 0.62))
n_top_r = (HX + 28,        HY - int(HR * 0.40))

# Draw filled neck polygon
neck_poly = [n_top_l, n_bot_l, n_bot_r, n_top_r]
draw.polygon(neck_poly, fill=F_LIGHT)

# Neck feather scales
for i in range(11):
    t = i / 10
    nx = int(n_top_l[0] * (1-t) + n_top_r[0] * t)
    ny = int(n_top_l[1] * (1-t) + n_top_r[1] * t)
    sc = lerp_col(F_MID, F_DARK, t * 0.35)
    draw.arc([nx-26, ny-18, nx+26, ny+18], 200, 340, fill=sc, width=2)

# ── 6. Head ──────────────────────────────────────────────────────────────────
draw.ellipse([HX-HR, HY-HR, HX+HR, HY+HR], fill=F_LIGHT)
# Head scales
for r in range(7):
    fy2 = HY - HR*0.82 + r*(HR*1.64/6)
    stag = (r%2)*18
    for c in range(7):
        fx2 = HX - HR*0.82 + stag + c*(HR*1.64/6)
        if ((fx2-HX)/HR)**2 + ((fy2-HY)/HR)**2 > 0.82:
            continue
        draw.arc([int(fx2-22), int(fy2-16), int(fx2+22), int(fy2+16)],
                 200, 340, fill=F_MID, width=1)

# ── 7. Comb ──────────────────────────────────────────────────────────────────
comb_bumps = [(HX-6, HY-HR, 43, 56), (HX+31, HY-HR+7, 36, 46), (HX-45, HY-HR+14, 32, 41)]
for bx, by, brx, bry in comb_bumps:
    draw.ellipse([bx-brx, by-bry, bx+brx, by+bry], fill=COMB_COL, outline=COMB_DK, width=2)

# ── 8. Wattle ────────────────────────────────────────────────────────────────
draw.ellipse([HX-HR-6, HY+38, HX-HR+60, HY+126], fill=WATTLE_COL, outline=(148,22,14), width=2)

# ── 9. Beak ──────────────────────────────────────────────────────────────────
beak = [(HX-HR+14, HY-24), (HX-HR-96, HY+11), (HX-HR+6, HY+44)]
draw.polygon(beak, fill=BEAK_COL)
draw.polygon(beak, outline=(162, 120, 14), width=2)
draw.line([beak[0], beak[1]], fill=(150, 112, 10), width=3)

# ── 10. Eye ──────────────────────────────────────────────────────────────────
ex, ey = HX-10, HY-40
draw.ellipse([ex-33, ey-33, ex+33, ey+33], fill=EYE_RING)
draw.ellipse([ex-23, ey-23, ex+23, ey+23], fill=EYE_IRIS)
draw.ellipse([ex-13, ey-13, ex+13, ey+13], fill=(5, 3, 1))
draw.ellipse([ex+4,  ey-12, ex+10, ey-6], fill=(244, 230, 198))

# ── 11. Wing detail ──────────────────────────────────────────────────────────
draw.arc([CX-BRX+50, CY-BRY+18, CX+BRX-18, CY+BRY+8], 205, 332, fill=F_DARK, width=3)
for i in range(9):
    ang = math.radians(212 + i*8)
    fx_ = CX + int(math.cos(ang)*(BRX-20))
    fy_ = CY + int(math.sin(ang)*(BRY-12))
    tx_ = fx_ + int(math.cos(ang)*52)
    ty_ = fy_ + int(math.sin(ang)*52)
    draw.line([(fx_, fy_), (tx_, ty_)], fill=lerp_col(F_MID, F_SHADOW, i/8), width=max(2, 5-i//3))

# ── 12. Final outlines ────────────────────────────────────────────────────────
draw.ellipse(body_box, fill=None, outline=F_MID, width=3)
draw.ellipse([HX-HR, HY-HR, HX+HR, HY+HR], fill=None, outline=F_MID, width=3)
draw.polygon(neck_poly, fill=None, outline=F_MID)

# ── 13. Annotations ───────────────────────────────────────────────────────────
# Carefully arranged so left labels go to left margin, right labels to right margin
#   source: (sx, sy)  label_anchor: (lx, ly)
annotations = [
    # right-side labels
    (TAIL[0]+155, TAIL[1]-240, 2000,  820,  "RECTRICES",         "V"),
    (CX+BRX-8,   CY-55,       2000, 1280,  "CORPUS",            "VI"),
    (CX+BRX-28,  CY+175,      2000, 1620,  "ALA  /  REMIGES",   "VIII"),
    (CX+18,      CY+348,      1900, 2100,  "TARSUS  PEDIS",     "VII"),
    # left-side labels
    (HX-HR-85,   HY+14,        390, 1280,  "ROSTRUM",           "III"),
    (HX-HR-4,    HY+80,        390, 1020,  "PALEAR",            "II"),
    (ex,         ey,           420,  820,  "OCULUS",            "IV"),
    (HX-4,       HY-HR-46,     500,  560,  "CRISTA  CAPITIS",   "I"),
]

for sx, sy, lx, ly, name, idx in annotations:
    crosshair(int(sx), int(sy))
    draw.line([(int(sx), int(sy)), (lx, ly)], fill=ANNOT, width=1)
    tick = 46
    right_side = lx >= W // 2
    if right_side:
        draw.line([(lx, ly), (lx+tick, ly)], fill=ANNOT, width=1)
        draw.text((lx+tick+10, ly-12), f"[{idx}]",  fill=T_DIM, font=f_label, anchor="ls")
        draw.text((lx+tick+10, ly+4),  name,         fill=T_DIM, font=f_label, anchor="ls")
    else:
        draw.line([(lx-tick, ly), (lx, ly)], fill=ANNOT, width=1)
        draw.text((lx-tick-10, ly-12), f"[{idx}]",  fill=T_DIM, font=f_label, anchor="rs")
        draw.text((lx-tick-10, ly+4),  name,         fill=T_DIM, font=f_label, anchor="rs")

# ── 14. Measurement bars ──────────────────────────────────────────────────────
def mbar_h(x1, x2, y, label):
    draw.line([(x1, y), (x2, y)], fill=ANNOT, width=1)
    draw.line([(x1, y-10), (x1, y+10)], fill=ANNOT, width=1)
    draw.line([(x2, y-10), (x2, y+10)], fill=ANNOT, width=1)
    draw.text(((x1+x2)//2, y+16), label, fill=T_DIM, font=f_tiny, anchor="mt")

def mbar_v(x, y1, y2, label):
    draw.line([(x, y1), (x, y2)], fill=ANNOT, width=1)
    draw.line([(x-10, y1), (x+10, y1)], fill=ANNOT, width=1)
    draw.line([(x-10, y2), (x+10, y2)], fill=ANNOT, width=1)
    draw.text((x+16, (y1+y2)//2), label, fill=T_DIM, font=f_tiny, anchor="lm")

mbar_h(HX-HR, CX+BRX+195, CY+BRY+80, "LONGITUDO  ·  1840 mm")
mbar_v(CX+BRX+52, CY-BRY, CY+BRY, "570 mm")

# ── 15. Border ────────────────────────────────────────────────────────────────
M = 76
draw.rectangle([M, M, W-M, H-M], fill=None, outline=ANNOT, width=1)
draw.rectangle([M+7, M+7, W-M-7, H-M-7], fill=None, outline=(28, 21, 10), width=1)

# ── 16. Map reference grid ────────────────────────────────────────────────────
for i, y in enumerate(range(215, H-215, 248)):
    lbl = f"{i+1:02d}"
    draw.text((60, y),    lbl, fill=T_GHOST, font=f_tiny, anchor="rm")
    draw.text((W-60, y),  lbl, fill=T_GHOST, font=f_tiny, anchor="lm")
for i, x in enumerate(range(235, W-200, 200)):
    ch = chr(65 + i % 26)
    draw.text((x, 58),   ch, fill=T_GHOST, font=f_tiny, anchor="mm")
    draw.text((x, H-58), ch, fill=T_GHOST, font=f_tiny, anchor="mm")

# ── 17. Title ────────────────────────────────────────────────────────────────
draw.text((W//2, 148), "GALLUS  GALLUS  DOMESTICUS",
          fill=T_BRIGHT, font=f_hero, anchor="mm")

rule_y = 206
draw.line([(M+55, rule_y), (W-M-55, rule_y)], fill=ANNOT, width=1)
draw.text((W//2, 236),
          "PLUMAGE  ·  ANATOMICAL  FIELD  STUDY  ·  SPECIMEN  VII",
          fill=T_DIM, font=f_mono, anchor="mm")

# ── 18. Footer ────────────────────────────────────────────────────────────────
fr_y = H - 185
draw.line([(M+55, fr_y), (W-M-55, fr_y)], fill=ANNOT, width=1)
draw.text((W//2, H-150), "LAMINAR  FIELD",
          fill=T_DIM, font=f_sub, anchor="mm")
draw.text((W//2, H-105),
          "PLATE  XII  ·  MMXXV  ·  AVIAN  MORPHOLOGICAL  ATLAS",
          fill=T_GHOST, font=f_tiny, anchor="mm")

# ── Post-processing: paint edges darker (vignette) ───────────────────────────
vig = Image.new("L", (W, H), 0)
vd2 = ImageDraw.Draw(vig)
for i in range(55):
    t = 1 - (i / 54)
    alpha = int(105 * t**2.2)
    m2 = i * 16
    vd2.rectangle([m2, m2, W-m2, H-m2], fill=None, outline=alpha, width=18)
vig = vig.filter(ImageFilter.GaussianBlur(radius=80))
from PIL import ImageChops
vig_rgb = Image.new("RGB", (W, H), (0, 0, 0))
mask = ImageChops.invert(vig)
canvas = Image.composite(canvas, vig_rgb, mask)

# ── Save ─────────────────────────────────────────────────────────────────────
canvas.save(OUTPUT, "PNG")
print(f"Rendered → {OUTPUT}")
