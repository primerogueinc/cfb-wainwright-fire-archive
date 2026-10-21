from PIL import Image, ImageDraw, ImageFont, ImageFilter
import csv, math, sys

LOGO = "/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png"
F = "/usr/share/fonts/opentype/inter/"
BROWN, BROWN_DK = (44, 32, 24), (28, 20, 15)
GOLD, CREAM, NAVY, MUTED = (212, 175, 104), (238, 230, 214), (30, 52, 82), (200, 188, 165)
LANDSAT, VIIRS = (185, 132, 36), (79, 141, 214)
def font(n, s): return ImageFont.truetype(F + n, s)

def build(W, H, out, csvpath):
    s = W / 1600.0
    img = Image.new("RGB", (W, H), BROWN_DK)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(BROWN[i] * (1 - t) + BROWN_DK[i] * t) for i in range(3)))

    # right side: actual detection pattern as a motif (real data, not decoration)
    rows = list(csv.DictReader(open(csvpath)))
    ref = (52.778, -110.92)
    cx, cy, k = W * 0.78, H * 0.47, 150 * s   # px per km
    def P(lat, lon):
        x = (lon - ref[1]) * 111.32 * math.cos(math.radians(ref[0]))
        y = (lat - ref[0]) * 110.57
        return cx + x * k, cy - y * k
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for r in rows:
        if "VIIRS" in r["sensor"]:
            x, y = P(float(r["latitude"]), float(r["longitude"])); h = 0.24 * k
            od.rectangle([x - h, y - h, x + h, y + h], fill=VIIRS + (55,), outline=VIIRS + (170,), width=max(1, int(2 * s)))
    for r in rows:
        if "VIIRS" in r["sensor"]:
            x, y = P(float(r["latitude"]), float(r["longitude"])); rr = 7 * s
            od.ellipse([x - rr, y - rr, x + rr, y + rr], fill=VIIRS + (255,))
        else:
            x, y = P(float(r["latitude"]), float(r["longitude"])); h = 3.2 * s
            od.rectangle([x - h, y - h, x + h, y + h], fill=LANDSAT + (255,))
    img = img.convert("RGBA"); img.alpha_composite(ov); d = ImageDraw.Draw(img)
    d.text((cx, H * 0.86), "NASA FIRMS detections, CFB Wainwright, Oct. 17", font=font("Inter-Medium.otf", int(20 * s)), fill=MUTED, anchor="mm")
    d.text((cx - 150 * s, H * 0.86 - 34 * s), "■ 12:17 p.m.", font=font("Inter-Bold.otf", int(20 * s)), fill=LANDSAT, anchor="mm")
    d.text((cx + 120 * s, H * 0.86 - 34 * s), "● 2:49 p.m.", font=font("Inter-Bold.otf", int(20 * s)), fill=VIIRS, anchor="mm")

    d.rectangle([0, 0, int(14 * s), H], fill=GOLD)
    pad = int(90 * s)
    fb = font("Inter-Black.otf", int(30 * s)); lab = "PRIME ROGUE ANALYSIS · FOLLOW-UP"
    bw = d.textlength(lab, font=fb); bx, by, bh = pad, int(88 * s), int(56 * s)
    d.rounded_rectangle([bx, by, bx + bw + int(40 * s), by + bh], radius=int(8 * s), fill=GOLD)
    d.text((bx + int(20 * s), by + bh // 2), lab, font=fb, fill=BROWN_DK, anchor="lm")
    d.text((bx + bw + int(66 * s), by + bh // 2), "CFB WAINWRIGHT", font=font("Inter-Bold.otf", int(28 * s)), fill=GOLD, anchor="lm")

    fh = font("InterDisplay-Black.otf", int(92 * s))
    y = int(196 * s)
    for ln in ["FIRE ON THE", "RANGE BEFORE", "4 P.M."]:
        d.text((pad - int(4 * s), y), ln, font=fh, fill=CREAM); y += int(98 * s)
    d.rectangle([pad, y + int(14 * s), pad + int(180 * s), y + int(22 * s)], fill=GOLD)
    fs = font("InterDisplay-Bold.otf", int(36 * s))
    yy = y + int(48 * s)
    for ln in ["Overnight passes see no fire. Every NASA detection", "at the base came before DND's ignition time"]:
        d.text((pad, yy), ln, font=fs, fill=CREAM); yy += int(46 * s)

    fy = H - int(100 * s)
    d.rectangle([0, fy, W, H], fill=NAVY); d.rectangle([0, fy, W, fy + int(5 * s)], fill=GOLD)
    ff = font("Inter-Black.otf", int(34 * s))
    d.text((pad, fy + int(50 * s)), "PRIME ROGUE", font=ff, fill=GOLD, anchor="lm")
    fw = d.textlength("PRIME ROGUE", font=ff)
    d.text((pad + fw + int(24 * s), fy + int(52 * s)), "Independent reporting  ·  Strategic transparency", font=font("Inter-Medium.otf", int(26 * s)), fill=CREAM, anchor="lm")
    logo = Image.open(LOGO).convert("RGBA").resize((int(84 * s), int(84 * s)), Image.LANCZOS)
    img.alpha_composite(logo, (W - int(84 * s) - int(40 * s), fy + int(8 * s)))
    img.convert("RGB").save(out, quality=90, optimize=True)

build(1600, 900, sys.argv[2], sys.argv[1])
build(1200, 675, sys.argv[3], sys.argv[1])
