from PIL import Image, ImageDraw, ImageFont
import math, sys

SRC = "/root/.claude/uploads/4df156cd-2792-5bb1-a5b6-4856cfddae18/801d1b83-image.png"
LOGO = "/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png"
F = "/usr/share/fonts/opentype/inter/"
BROWN_DK = (28, 20, 15)
GOLD = (212, 175, 104)
CREAM = (238, 230, 214)
NAVY = (30, 52, 82)
WHITE = (255, 255, 255)
LANDSAT = (170, 0, 0)
VIIRS = (255, 0, 0)

def font(n, s): return ImageFont.truetype(F + n, s)

# crop map area only (drop FIRMS UI: header, sidebar, toolbar, zoom controls)
X0, Y0, X1, Y1 = 60, 95, 1435, 800
W = 1600
pad = 40
iw = W - 2 * pad
k = iw / (X1 - X0)
src = Image.open(SRC).convert("RGB").crop((X0, Y0, X1, Y1))
ih = int(src.height * k)
m = src.resize((iw, ih), Image.LANCZOS).convert("RGBA")

def P(x, y):  # original screenshot coords -> annotated map coords
    return ((x - X0) * k, (y - Y0) * k)

ov = Image.new("RGBA", m.size, (0, 0, 0, 0))
d = ImageDraw.Draw(ov)

def dashed(p1, p2, fill, width, dash=14, gap=9):
    x1, y1 = p1; x2, y2 = p2
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L
    t = 0
    while t < L:
        e = min(t + dash, L)
        d.line([(x1 + ux * t, y1 + uy * t), (x1 + ux * e, y1 + uy * e)], fill=fill, width=width)
        t += dash + gap

def box_label(xy, lines, anchor_pt=None, w=None):
    fb = font("Inter-Bold.otf", 22); fr = font("Inter-Medium.otf", 19)
    x, y = xy
    widths = [d.textlength(lines[0], font=fb)] + [d.textlength(l, font=fr) for l in lines[1:]]
    bw = (w or max(widths)) + 28
    bh = 16 + 28 + 24 * (len(lines) - 1) + 8
    if anchor_pt:
        # leader from box edge to point
        cx = x + bw / 2; cy = y + bh / 2
        d.line([anchor_pt, (min(max(anchor_pt[0], x), x + bw), min(max(anchor_pt[1], y), y + bh))], fill=GOLD, width=3)
        r = 7
        d.ellipse([anchor_pt[0] - r, anchor_pt[1] - r, anchor_pt[0] + r, anchor_pt[1] + r], outline=GOLD, width=3)
    d.rounded_rectangle([x, y, x + bw, y + bh], radius=8, fill=(20, 14, 10, 225), outline=GOLD, width=2)
    d.text((x + 14, y + 12), lines[0], font=fb, fill=GOLD)
    for i, l in enumerate(lines[1:]):
        d.text((x + 14, y + 44 + 24 * i), l, font=fr, fill=CREAM)

# 1) built-up area: dashed rectangle
bx0, by0 = P(890, 220); bx1, by1 = P(1105, 335)
for a, b in [((bx0, by0), (bx1, by0)), ((bx1, by0), (bx1, by1)), ((bx1, by1), (bx0, by1)), ((bx0, by1), (bx0, by0))]:
    dashed(a, b, WHITE, 3)
box_label((P(1120, 200)[0], P(1120, 200)[1]), ["Built-up area on base", "Not identified by Prime Rogue"], anchor_pt=P(1105, 260))

# 2) measurement line offset below the band (SW-most -> NE-most detection centres)
sw, ne = P(668, 566), P(1064, 365)
dx, dy = ne[0] - sw[0], ne[1] - sw[1]
L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L  # perpendicular
if ny < 0: nx, ny = -nx, -ny  # push toward bottom-right
off = 150
a = (sw[0] + nx * off, sw[1] + ny * off); b = (ne[0] + nx * off, ne[1] + ny * off)
d.line([a, b], fill=WHITE, width=3)
for p in (a, b):
    d.line([(p[0] - nx * 14, p[1] - ny * 14), (p[0] + nx * 14, p[1] + ny * 14)], fill=WHITE, width=3)
km = (math.hypot(668 - 1064, 566 - 365)) / 125.0  # 125 px = 1,000 m on FIRMS scale bar
mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
fl = font("Inter-Black.otf", 26)
lbl = "≈ 3 km of detections  ·  SW → NE"
tw = d.textlength(lbl, font=fl)
lx, ly = mid[0] + 10, mid[1] + 24
d.rounded_rectangle([lx - 12, ly - 8, lx + tw + 12, ly + 36], radius=8, fill=(20, 14, 10, 225))
d.text((lx, ly), lbl, font=fl, fill=WHITE)

# 3) Landsat fire-front callout
box_label(P(110, 590), ["Landsat detections (30 m)", "Thin lines consistent with active fire", "fronts at the moment of the pass"], anchor_pt=P(690, 562))

# 4) VIIRS callout
box_label(P(330, 250), ["VIIRS detections (375 m)", "Each square is a heat-detection pixel,", "not the size of the burned area"], anchor_pt=P(828, 430))

# north arrow (FIRMS map is north-up)
na_x, na_y = iw - 70, 60
d.polygon([(na_x, na_y - 34), (na_x - 16, na_y + 12), (na_x, na_y + 2), (na_x + 16, na_y + 12)], fill=WHITE)
d.text((na_x, na_y + 32), "N", font=font("Inter-Black.otf", 26), fill=WHITE, anchor="mm")

# scale bar 1 km
sb = 144 * k  # calibrated from detection coordinates (3.08 km between farthest detections = 444 px)
sx, sy = 30, ih - 50
d.rectangle([sx - 10, sy - 34, sx + sb + 60, sy + 22], fill=(20, 14, 10, 200))
d.rectangle([sx, sy, sx + sb, sy + 8], fill=WHITE)
d.text((sx, sy - 30), "1 km", font=font("Inter-Bold.otf", 20), fill=WHITE)

# legend
lgx, lgy = iw - 330, ih - 110
d.rounded_rectangle([lgx, lgy, lgx + 310, lgy + 92], radius=8, fill=(20, 14, 10, 225), outline=GOLD, width=2)
fr = font("Inter-Medium.otf", 19)
d.rectangle([lgx + 16, lgy + 18, lgx + 40, lgy + 34], fill=LANDSAT); d.text((lgx + 52, lgy + 15), "Landsat, 30 m", font=fr, fill=CREAM)
d.rectangle([lgx + 16, lgy + 54, lgx + 40, lgy + 70], fill=VIIRS); d.text((lgx + 52, lgy + 51), "VIIRS, 375 m", font=fr, fill=CREAM)

m.alpha_composite(ov)

header, footer = 150, 180
H = header + ih + footer
img = Image.new("RGBA", (W, H), BROWN_DK + (255,))
dd = ImageDraw.Draw(img)
dd.rectangle([0, 0, 10, H], fill=GOLD)
dd.text((pad, 34), "OSINT ANALYSIS  ·  NASA FIRMS SATELLITE DATA  ·  CFB WAINWRIGHT", font=font("Inter-Bold.otf", 24), fill=GOLD)
dd.text((pad, 66), "Satellite heat detections trace the fire across the base", font=font("InterDisplay-Black.otf", 50), fill=CREAM)
dd.rectangle([pad - 2, header - 2, pad + iw + 1, header + ih + 1], fill=GOLD)
img.alpha_composite(m, (pad, header))

fy = H - footer + 14
dd.rectangle([0, fy, W, H], fill=NAVY)
dd.rectangle([0, fy, W, fy + 4], fill=GOLD)
fc = font("Inter-Medium.otf", 21)
dd.text((pad, fy + 24), "Data and imagery: NASA FIRMS, 24-hour window to Oct. 18, 2026 (UTC). Annotations: Prime Rogue Inc.", font=fc, fill=CREAM)
dd.text((pad, fy + 56), "Distances approximate, calibrated from NASA detection coordinates. Times verified from FIRMS data.", font=fc, fill=CREAM)
dd.text((pad, fy + 88), "Satellite detections show heat, not cause.", font=fc, fill=CREAM)
dd.text((pad, fy + 140), "PRIME ROGUE", font=font("Inter-Black.otf", 24), fill=GOLD, anchor="lm")
logo = Image.open(LOGO).convert("RGBA").resize((104, 104), Image.LANCZOS)
img.alpha_composite(logo, (W - 104 - pad, fy + 22))
img.convert("RGB").save(sys.argv[1], quality=90, optimize=True)
print(img.size, round(km, 2))
