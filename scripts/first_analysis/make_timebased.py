from PIL import Image, ImageDraw, ImageFont
import sys

SRC = "/root/.claude/uploads/4df156cd-2792-5bb1-a5b6-4856cfddae18/62c3e90f-image.png"
LOGO = "/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png"
F = "/usr/share/fonts/opentype/inter/"
BROWN_DK, GOLD, CREAM, NAVY = (28, 20, 15), (212, 175, 104), (238, 230, 214), (30, 52, 82)
ORANGE, PALE = (255, 181, 0), (247, 231, 186)
def font(n, s): return ImageFont.truetype(F + n, s)

X0, Y0, X1, Y1 = 70, 150, 1395, 860      # map only: no FIRMS header, sidebar, toolbar, zoom buttons
W, pad = 1600, 40
iw = W - 2 * pad
k = iw / (X1 - X0)
src = Image.open(SRC).convert("RGB")
patch = src.crop((640, 305, 662, 340)); src.paste(patch, (668, 305))   # remove mouse cursor
m = src.crop((X0, Y0, X1, Y1))
ih = int(m.height * k)
m = m.resize((iw, ih), Image.LANCZOS).convert("RGBA")
def P(x, y): return ((x - X0) * k, (y - Y0) * k)

ov = Image.new("RGBA", m.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
def box_label(xy, lines, anchor_pt, swatch=None):
    fb, fr = font("Inter-Bold.otf", 22), font("Inter-Medium.otf", 19)
    x, y = xy
    off = 34 if swatch else 0
    bw = max([d.textlength(lines[0], font=fb) + off] + [d.textlength(l, font=fr) for l in lines[1:]]) + 28
    bh = 16 + 28 + 24 * (len(lines) - 1) + 8
    ax, ay = anchor_pt
    d.line([anchor_pt, (min(max(ax, x), x + bw), min(max(ay, y), y + bh))], fill=GOLD, width=3)
    d.ellipse([ax - 7, ay - 7, ax + 7, ay + 7], outline=GOLD, width=3)
    d.rounded_rectangle([x, y, x + bw, y + bh], radius=8, fill=(20, 14, 10, 230), outline=GOLD, width=2)
    if swatch:
        d.rectangle([x + 14, y + 15, x + 38, y + 37], fill=swatch, outline=(20, 14, 10), width=1)
    d.text((x + 14 + off, y + 12), lines[0], font=fb, fill=GOLD)
    for i, l in enumerate(lines[1:]):
        d.text((x + 14, y + 44 + 24 * i), l, font=fr, fill=CREAM)

box_label(P(130, 245), ["VIIRS, NOAA-20: 2:49 p.m.", "Orange = detected 6 to 12 hours", "before this capture"], P(775, 400), ORANGE)
box_label(P(110, 650), ["Landsat 8: 12:17 p.m.", "Pale yellow = detected 12 to 24 hours", "before this capture"], P(580, 578), PALE)
box_label(P(1010, 560), ["Earlier detections, same area", "Lower-confidence Landsat detections,", "about 2.5 hours before the VIIRS pass"], P(880, 447))
# own scale bar (source bar: 1000 m = 164 px), covering the clipped original
sb = 164 * k
d.rectangle([0, ih - 74, sb + 60, ih], fill=(20, 14, 10, 235))
d.rectangle([22, ih - 30, 22 + sb, ih - 22], fill=CREAM)
d.text((22, ih - 62), "1 km", font=font("Inter-Bold.otf", 20), fill=CREAM)

# capture stamp
fs = font("Inter-Bold.otf", 21)
st = "Captured 1:09 a.m. MDT, Oct. 18  ·  NASA FIRMS Time Based view"
tw = d.textlength(st, font=fs)
d.rounded_rectangle([iw - tw - 40, 14, iw - 12, 56], radius=8, fill=(20, 14, 10, 230))
d.text((iw - tw - 26, 24), st, font=fs, fill=CREAM)
m.alpha_composite(ov)

header, footer = 150, 180
H = header + ih + footer
img = Image.new("RGBA", (W, H), BROWN_DK + (255,)); dd = ImageDraw.Draw(img)
dd.rectangle([0, 0, 10, H], fill=GOLD)
dd.text((pad, 34), "OSINT ANALYSIS  ·  NASA FIRMS TIME-BASED VIEW  ·  CFB WAINWRIGHT", font=font("Inter-Bold.otf", 24), fill=GOLD)
dd.text((pad, 66), "NASA's own colour coding shows which fire came first", font=font("InterDisplay-Black.otf", 48), fill=CREAM)
dd.rectangle([pad - 2, header - 2, pad + iw + 1, header + ih + 1], fill=GOLD)
img.alpha_composite(m, (pad, header))
fy = H - footer + 14
dd.rectangle([0, fy, W, H], fill=NAVY); dd.rectangle([0, fy, W, fy + 4], fill=GOLD)
fc = font("Inter-Medium.otf", 21)
dd.text((pad, fy + 24), "FIRMS colours each detection by how long ago it was made. At 1:09 a.m. MDT, 2:49 p.m. is 10.3 hours earlier (orange)", font=fc, fill=CREAM)
dd.text((pad, fy + 54), "and 12:17 p.m. is 12.9 hours earlier (pale yellow), matching the acquisition times in NASA's data files.", font=fc, fill=CREAM)
dd.text((pad, fy + 92), "Imagery and data: NASA FIRMS. Annotations: Prime Rogue Inc. Detections show heat, not cause.", font=fc, fill=CREAM)
dd.text((pad, fy + 140), "PRIME ROGUE", font=font("Inter-Black.otf", 24), fill=GOLD, anchor="lm")
logo = Image.open(LOGO).convert("RGBA").resize((104, 104), Image.LANCZOS)
img.alpha_composite(logo, (W - 104 - pad, fy + 30))
img.convert("RGB").save(sys.argv[1], quality=90, optimize=True)
print(img.size)
