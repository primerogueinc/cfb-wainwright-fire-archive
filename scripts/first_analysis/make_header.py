from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random, sys

LOGO = "/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png"
F = "/usr/share/fonts/opentype/inter/"
BROWN = (44, 32, 24)
BROWN_DK = (28, 20, 15)
GOLD = (212, 175, 104)
CREAM = (238, 230, 214)
NAVY = (30, 52, 82)
RED = (196, 38, 38)

def font(name, size):
    return ImageFont.truetype(F + name, size)

def build(W, H, out):
    s = W / 1600.0
    img = Image.new("RGB", (W, H), BROWN_DK)
    d = ImageDraw.Draw(img)

    # vertical gradient brown
    for y in range(H):
        t = y / H
        c = tuple(int(BROWN[i] * (1 - t) + BROWN_DK[i] * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)

    # topographic contour texture (abstract, evokes terrain / range map)
    tex = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tex)
    random.seed(7)
    cx, cy = W * 0.70, H * 0.55
    for k in range(1, 26):
        r = k * 34 * s
        pts = []
        for a in range(0, 361, 3):
            rad = math.radians(a)
            wob = 1 + 0.10 * math.sin(3 * rad + k * 0.6) + 0.06 * math.sin(7 * rad - k)
            pts.append((cx + r * wob * math.cos(rad) * 1.35, cy + r * wob * math.sin(rad)))
        td.line(pts, fill=(GOLD[0], GOLD[1], GOLD[2], 22), width=max(1, int(2 * s)))
    img.paste(tex, (0, 0), tex)

    # navy band on left edge + gold rule
    d.rectangle([0, 0, int(14 * s), H], fill=GOLD)

    pad = int(90 * s)

    # LIVE badge
    fb = font("Inter-Black.otf", int(34 * s))
    label = "LIVE"
    bw = d.textlength(label, font=fb)
    bx, by = pad, int(92 * s)
    bh = int(58 * s)
    dot = int(14 * s)
    d.rounded_rectangle([bx, by, bx + bw + int(78 * s), by + bh], radius=int(8 * s), fill=RED)
    d.ellipse([bx + int(20 * s), by + bh // 2 - dot // 2, bx + int(20 * s) + dot, by + bh // 2 + dot // 2], fill=(255, 255, 255))
    d.text((bx + int(48 * s), by + bh // 2), label, font=fb, fill=(255, 255, 255), anchor="lm")

    # kicker
    fk = font("Inter-Bold.otf", int(30 * s))
    kx = bx + bw + int(110 * s)
    d.text((kx, by + bh // 2), "BREAKING  ·  ALBERTA  ·  CANADIAN ARMED FORCES", font=fk, fill=GOLD, anchor="lm")

    # headline
    maxw = W - int(430 * s) - int(80 * s) - pad - int(40 * s)
    size = int(124 * s)
    while True:
        fh = font("InterDisplay-Black.otf", size)
        if d.textlength("CFB WAINWRIGHT", font=fh) <= maxw: break
        size -= 2
    d.text((pad - int(4 * s), int(212 * s)), "CFB WAINWRIGHT", font=fh, fill=CREAM)

    # gold rule
    ry = int(352 * s)
    d.rectangle([pad, ry, pad + int(180 * s), ry + int(8 * s)], fill=GOLD)

    # subhead (wrapped)
    fs = font("InterDisplay-Bold.otf", int(52 * s))
    lines = ["Deaths and injuries confirmed", "after range fire spreads", "beyond the base"]
    y = int(392 * s)
    for ln in lines:
        d.text((pad, y), ln, font=fs, fill=CREAM)
        y += int(66 * s)

    # timestamp strip
    ft = font("Inter-SemiBold.otf", int(28 * s))
    d.text((pad, int(632 * s)), "Live updates  ·  Oct. 17, 2026  ·  What's confirmed, and what isn't", font=ft, fill=(200, 188, 165))

    # footer bar
    fy = H - int(110 * s)
    d.rectangle([0, fy, W, H], fill=NAVY)
    d.rectangle([0, fy, W, fy + int(5 * s)], fill=GOLD)
    ff = font("Inter-Black.otf", int(36 * s))
    d.text((pad, fy + int(55 * s)), "PRIME ROGUE", font=ff, fill=GOLD, anchor="lm")
    fw = d.textlength("PRIME ROGUE", font=ff)
    ff2 = font("Inter-Medium.otf", int(28 * s))
    d.text((pad + fw + int(24 * s), fy + int(57 * s)), "Independent reporting  ·  Strategic transparency", font=ff2, fill=CREAM, anchor="lm")

    # logo, right side, with soft shadow
    logo = Image.open(LOGO).convert("RGBA")
    ls = int(430 * s)
    logo = logo.resize((ls, ls), Image.LANCZOS)
    lx, ly = W - ls - int(80 * s), int(200 * s)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = logo.split()[3].point(lambda a: int(a * 0.55))
    blk = Image.new("RGBA", logo.size, (0, 0, 0, 255))
    blk.putalpha(sh)
    shadow.paste(blk, (lx + int(10 * s), ly + int(16 * s)), blk)
    shadow = shadow.filter(ImageFilter.GaussianBlur(int(18 * s)))
    img = img.convert("RGBA")
    img.alpha_composite(shadow)
    img.alpha_composite(logo, (lx, ly))
    img.convert("RGB").save(out, quality=90, optimize=True)

if __name__ == "__main__":
    build(1600, 900, sys.argv[1])
    build(1200, 675, sys.argv[2])
