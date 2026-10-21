from PIL import Image, ImageDraw, ImageFont
import csv, math, sys

LOGO = "/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png"
F = "/usr/share/fonts/opentype/inter/"
BROWN, BROWN_DK = (44, 32, 24), (28, 20, 15)
GOLD, CREAM, NAVY, MUTED = (212, 175, 104), (238, 230, 214), (30, 52, 82), (200, 188, 165)
LANDSAT, VIIRS = (185, 132, 36), (79, 141, 214)
def font(n, s): return ImageFont.truetype(F + n, int(s))
rows = list(csv.DictReader(open(sys.argv[1])))

def bg(W, H):
    img = Image.new("RGB", (W, H), BROWN_DK); d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(BROWN[i] * (1 - t) + BROWN_DK[i] * t) for i in range(3)))
    return img.convert("RGBA")

def motif(img, cx, cy, k):
    ref = (52.778, -110.92)
    def P(lat, lon):
        return cx + (lon - ref[1]) * 111.32 * math.cos(math.radians(ref[0])) * k, cy - (lat - ref[0]) * 110.57 * k
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for r in rows:
        if "VIIRS" in r["sensor"]:
            x, y = P(float(r["latitude"]), float(r["longitude"])); h = 0.24 * k
            od.rectangle([x - h, y - h, x + h, y + h], fill=VIIRS + (60,), outline=VIIRS + (180,), width=3)
    for r in rows:
        x, y = P(float(r["latitude"]), float(r["longitude"]))
        if "VIIRS" in r["sensor"]:
            rr = k * 0.05; od.ellipse([x - rr, y - rr, x + rr, y + rr], fill=VIIRS + (255,))
        else:
            h = k * 0.022; od.rectangle([x - h, y - h, x + h, y + h], fill=LANDSAT + (255,))
    img.alpha_composite(ov)

def pill(d, x, y, text, f, fill, tc, padx, h):
    w = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + w + 2 * padx, y + h], radius=h // 5, fill=fill)
    d.text((x + padx, y + h / 2), text, font=f, fill=tc, anchor="lm")
    return w + 2 * padx

# ---------- 16:9 thumbnail, 1280x720 ----------
W, H = 1280, 720
img = bg(W, H); motif(img, 1000, 275, 160); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 12, H], fill=GOLD)
pw = pill(d, 60, 48, "NASA DATA", font("Inter-Black.otf", 34), GOLD, BROWN_DK, 22, 60)
pill(d, 60 + pw + 14, 48, "CFB WAINWRIGHT", font("Inter-Black.otf", 34), NAVY, CREAM, 22, 60)
fh = font("InterDisplay-Black.otf", 150)
d.text((54, 128), "FIRE", font=fh, fill=CREAM)
d.text((54, 278), "BEFORE", font=fh, fill=CREAM)
d.text((54, 428), "4 P.M.", font=fh, fill=GOLD)
d.text((985, 592), "■ 12:17", font=font("Inter-Black.otf", 40), fill=LANDSAT, anchor="rm")
d.text((1005, 592), "● 2:49 P.M.", font=font("Inter-Black.otf", 40), fill=VIIRS, anchor="lm")
fy = H - 84
d.rectangle([0, fy, W, H], fill=NAVY); d.rectangle([0, fy, W, fy + 5], fill=GOLD)
d.text((60, fy + 44), "PRIME ROGUE ANALYSIS", font=font("Inter-Black.otf", 32), fill=GOLD, anchor="lm")
d.text((W - 150, fy + 44), "Satellites detect heat, not cause", font=font("Inter-Medium.otf", 24), fill=CREAM, anchor="rm")
logo = Image.open(LOGO).convert("RGBA").resize((70, 70), Image.LANCZOS)
img.alpha_composite(logo, (W - 70 - 40, fy + 9))
img.convert("RGB").save(sys.argv[2], quality=92, optimize=True)

# ---------- 9:16 Shorts cover, 1080x1920 ----------
W, H = 1080, 1920
img = bg(W, H); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 12, H], fill=GOLD)
x = 70
x += pill(d, x, 230, "NASA DATA", font("Inter-Black.otf", 40), GOLD, BROWN_DK, 26, 72) + 16
pill(d, x, 230, "CFB WAINWRIGHT", font("Inter-Black.otf", 40), NAVY, CREAM, 26, 72)
fh = font("InterDisplay-Black.otf", 152)
y = 350
for ln, c in [("SATELLITES", CREAM), ("SAW FIRE", CREAM), ("BEFORE", CREAM), ("4 P.M.", GOLD)]:
    d.text((62, y), ln, font=fh, fill=c); y += 158
motif(img, 600, 1190, 170)
d = ImageDraw.Draw(img)
# timeline chips
fy0 = 1460
items = [("12:17 P.M.", "Landsat 8: likely fire", LANDSAT), ("2:49 P.M.", "NOAA-20: fire detected", VIIRS), ("≈ 4 P.M.", "DND: fire “ignited”", CREAM)]
for i, (t, lab, c) in enumerate(items):
    yy = fy0 + i * 78
    d.ellipse([70, yy + 14, 100, yy + 44], fill=c)
    d.text((124, yy + 29), t, font=font("Inter-Black.otf", 46), fill=c, anchor="lm")
    d.text((440, yy + 29), lab, font=font("Inter-SemiBold.otf", 40), fill=CREAM, anchor="lm")
fy = H - 150
d.rectangle([0, fy, W, H], fill=NAVY); d.rectangle([0, fy, W, fy + 6], fill=GOLD)
d.text((70, fy + 58), "PRIME ROGUE ANALYSIS", font=font("Inter-Black.otf", 40), fill=GOLD, anchor="lm")
d.text((70, fy + 108), "Satellites detect heat, not cause", font=font("Inter-Medium.otf", 30), fill=CREAM, anchor="lm")
logo = Image.open(LOGO).convert("RGBA").resize((110, 110), Image.LANCZOS)
img.alpha_composite(logo, (W - 110 - 50, fy + 20))
img.convert("RGB").save(sys.argv[3], quality=92, optimize=True)
print("ok")
