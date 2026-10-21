from PIL import Image, ImageDraw, ImageFont
import sys

U = "/root/.claude/uploads/4df156cd-2792-5bb1-a5b6-4856cfddae18/"
LOGO = "/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png"
F = "/usr/share/fonts/opentype/inter/"
BROWN_DK = (28, 20, 15)
GOLD = (212, 175, 104)
CREAM = (238, 230, 214)
NAVY = (30, 52, 82)
MUTED = (200, 188, 165)

def font(n, s): return ImageFont.truetype(F + n, s)

# (file, crop box (map area only, no ads/photos/bookmarks), letter, title, detail)
panels = [
    ("08116c24-image.png", (495, 185, 1425, 830), "A",
     "STAR11 · STARS air ambulance (EC145)", "Leaves Wainwright area toward Edmonton · ~9:35 p.m. MT"),
    ("ab2c91a9-image.png", (492, 145, 1420, 790), "B",
     "STAR03 · STARS air ambulance (EC145)", "Northwest of Wainwright toward Edmonton · ~9:36 p.m. MT"),
    ("a79e583b-image.png", (490, 150, 1420, 795), "C",
     "CWA935 · King Air 350, CanWest Air", "Edmonton to Wainwright area · departed 9:35 p.m. MT"),
    ("81398058-image.png", (490, 145, 1420, 790), "D",
     "RCAF CC-130H Hercules", "Inbound to Edmonton from the east · departed ~7:48 p.m. MT"),
]

W = 1600
gap = 20
pad = 40
cw = (W - 2 * pad - gap) // 2
header = 150
footer = 150
cells = []
for f, box, *_ in panels:
    im = Image.open(U + f).convert("RGB").crop(box)
    ch = int(im.height * cw / im.width)
    cells.append(im.resize((cw, ch), Image.LANCZOS))
ch = max(c.height for c in cells)
lab = 86
H = header + 2 * (ch + lab) + gap + footer

img = Image.new("RGB", (W, H), BROWN_DK)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 10, H], fill=GOLD)

d.text((pad, 34), "FLIGHT TRACKING  ·  CFB WAINWRIGHT  ·  OCT. 17, 2026", font=font("Inter-Bold.otf", 24), fill=GOLD)
d.text((pad, 66), "Air ambulance and RCAF movements during the response", font=font("InterDisplay-Black.otf", 50), fill=CREAM)

fl = font("Inter-Black.otf", 30)
ft = font("InterDisplay-Bold.otf", 26)
fd = font("Inter-Medium.otf", 22)
for i, (c, (_, _, L, t, det)) in enumerate(zip(cells, panels)):
    col, row = i % 2, i // 2
    x = pad + col * (cw + gap)
    y = header + row * (ch + lab + gap)
    # letter badge + text label above image
    d.rounded_rectangle([x, y, x + 44, y + 44], radius=6, fill=GOLD)
    d.text((x + 22, y + 22), L, font=fl, fill=BROWN_DK, anchor="mm")
    d.text((x + 58, y + 2), t, font=ft, fill=CREAM)
    d.text((x + 58, y + 38), det, font=fd, fill=MUTED)
    iy = y + lab - 16
    d.rectangle([x - 2, iy - 2, x + cw + 1, iy + c.height + 1], fill=GOLD)
    img.paste(c, (x, iy))

fy = H - footer + 10
d.rectangle([0, fy, W, H], fill=NAVY)
d.rectangle([0, fy, W, fy + 4], fill=GOLD)
fc = font("Inter-Medium.otf", 21)
d.text((pad, fy + 26), "Flight data: Flightradar24. Screenshots captured by Prime Rogue, Oct. 17–18, 2026. Times converted to Mountain Time.", font=fc, fill=CREAM)
d.text((pad, fy + 58), "The purpose of each flight and the number of people transported have not been confirmed.", font=fc, fill=CREAM)
d.text((pad, fy + 112), "PRIME ROGUE", font=font("Inter-Black.otf", 24), fill=GOLD, anchor="lm")

logo = Image.open(LOGO).convert("RGBA").resize((100, 100), Image.LANCZOS)
img = img.convert("RGBA")
img.alpha_composite(logo, (W - 100 - pad, fy + 20))
img.convert("RGB").save(sys.argv[1], quality=90, optimize=True)
print(img.size)
