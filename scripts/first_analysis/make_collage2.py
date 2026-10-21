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

# map areas only: no FR24 info cards (third-party photos, ads), no browser chrome
panels = [
    ("67271932-image.png", (495, 140, 1420, 800), "A",
     "C-GWRS · King Air, Alberta Central Airways", "Edmonton Intl. to Wainwright · departed 10:44 p.m. MT"),
    ("f23fc43e-image.png", (485, 205, 1410, 865), "B",
     "SLG2 · Saskatchewan Air Ambulance (King Air)", "Departs Saskatoon heading west · 11:06 p.m. CST (= MT)"),
    ("aa307efe-image.png", (490, 250, 1320, 842), "C",
     "STAR03 · STARS air ambulance (EC145)", "Wainwright to Edmonton-area base · seen ~11:12 p.m. MT"),
]

W = 1600; gap = 20; pad = 40
cw = (W - 2 * pad - gap) // 2
header, lab, footer = 150, 86, 150
cells = []
for f, box, *_ in panels:
    im = Image.open(U + f).convert("RGB").crop(box)
    cells.append(im.resize((cw, int(im.height * cw / im.width)), Image.LANCZOS))
ch = max(c.height for c in cells)
H = header + 2 * (ch + lab) + gap + footer

img = Image.new("RGB", (W, H), BROWN_DK)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 10, H], fill=GOLD)
d.text((pad, 34), "FLIGHT TRACKING  ·  CFB WAINWRIGHT  ·  LATE EVENING, OCT. 17, 2026", font=font("Inter-Bold.otf", 24), fill=GOLD)
d.text((pad, 66), "Air ambulance flights continue hours into the response", font=font("InterDisplay-Black.otf", 50), fill=CREAM)

fl = font("Inter-Black.otf", 30); ft = font("InterDisplay-Bold.otf", 26); fd = font("Inter-Medium.otf", 22)
def slot(i):
    col, row = i % 2, i // 2
    return pad + col * (cw + gap), header + row * (ch + lab + gap)

for i, (c, (_, _, L, t, det)) in enumerate(zip(cells, panels)):
    x, y = slot(i)
    d.rounded_rectangle([x, y, x + 44, y + 44], radius=6, fill=GOLD)
    d.text((x + 22, y + 22), L, font=fl, fill=BROWN_DK, anchor="mm")
    d.text((x + 58, y + 2), t, font=ft, fill=CREAM)
    d.text((x + 58, y + 38), det, font=fd, fill=MUTED)
    iy = y + lab - 16
    d.rectangle([x - 2, iy - 2, x + cw + 1, iy + c.height + 1], fill=GOLD)
    img.paste(c, (x, iy))

# fourth slot: reading notes
x, y = slot(3)
iy = y + lab - 16
d.rounded_rectangle([x, iy, x + cw, iy + ch], radius=10, fill=(40, 30, 22), outline=GOLD, width=2)
tx = x + 34; ty = iy + 34
d.text((tx, ty), "How to read these maps", font=font("InterDisplay-Bold.otf", 30), fill=GOLD)
notes = [
    "• Captured about 11:10–11:15 p.m. MT, Oct. 17.",
    "• All times shown in Mountain Time. Saskatchewan",
    "  time matches Alberta in October.",
    "• A: fixed-wing aircraft still flying into Wainwright",
    "  nearly seven hours after the fire was reported.",
    "• B: Saskatchewan air ambulance heading west.",
    "  Its destination has not been confirmed.",
    "• C: STARS helicopter completing a run from",
    "  Wainwright to the Edmonton area.",
    "• Flight purposes and patient numbers",
    "  have not been confirmed.",
]
fn = font("Inter-Medium.otf", 22)
for k, line in enumerate(notes):
    d.text((tx, ty + 60 + k * 33), line, font=fn, fill=CREAM)

fy = H - footer + 10
d.rectangle([0, fy, W, H], fill=NAVY)
d.rectangle([0, fy, W, fy + 4], fill=GOLD)
fc = font("Inter-Medium.otf", 21)
d.text((pad, fy + 26), "Flight data: Flightradar24. Screenshots captured by Prime Rogue, Oct. 17–18, 2026. Times converted to Mountain Time.", font=fc, fill=CREAM)
d.text((pad, fy + 58), "The purpose of each flight and the number of people transported have not been confirmed.", font=fc, fill=CREAM)
d.text((pad, fy + 112), "PRIME ROGUE", font=font("Inter-Black.otf", 24), fill=GOLD, anchor="lm")
logo = Image.open(LOGO).convert("RGBA").resize((100, 100), Image.LANCZOS)
img = img.convert("RGBA"); img.alpha_composite(logo, (W - 100 - pad, fy + 20))
img.convert("RGB").save(sys.argv[1], quality=90, optimize=True)
print(img.size)
