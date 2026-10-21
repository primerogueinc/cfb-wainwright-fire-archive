from PIL import Image, ImageDraw, ImageFont
import sys

LOGO = "/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png"
F = "/usr/share/fonts/opentype/inter/"
BROWN_DK, PANEL = (28, 20, 15), (40, 29, 22)
GOLD, CREAM, NAVY, MUTED = (212, 175, 104), (238, 230, 214), (30, 52, 82), (176, 162, 138)
GREEN, BLUE, AMBER, GREY = (120, 170, 110), (79, 141, 214), (214, 150, 60), (150, 140, 125)
def font(n, s): return ImageFont.truetype(F + n, s)

cols = [
    ("CONFIRMED", "by officials", GREEN, [
        ("A fire ignited in the training", "area at approx. 4 p.m.", "DND news release"),
        ("Both fatalities and injuries", "", "Defence Minister McGuinty"),
        ("RCMP responded to a request for", "assistance at approx. 4 p.m.", "RCMP Alberta"),
        ("Fire crossed the base fence;", "\"being held\" at 10:47 p.m.", "MD of Wainwright"),
    ]),
    ("IN THE DATA", "NASA FIRMS, analyzed by Prime Rogue", BLUE, [
        ("Fire detected at 2:49 p.m.", "8 detections, nominal confidence", "NOAA-20 VIIRS"),
        ("Likely fire at 12:17 p.m.", "59 detections, low confidence", "Landsat 8"),
        ("No fire at the base on four", "overnight passes, 2:40–4:25", "VIIRS, three satellites"),
        ("No VIIRS/Landsat coverage", "from ~3:30 p.m. to night", "Orbital analysis"),
    ]),
    ("REPORTED", "not confirmed by officials", AMBER, [
        ("Live-fire exercise hit a gas line", "or gas well, explosion ~4 p.m.", "Global News, CAF sources"),
        ("An exercise fire may have set", "off a gas well (\"possible\")", "CBC's Murray Brewster"),
        ("At least seven killed,", "dozens injured", "Global News, military sources"),
        ("Seven CAF members parachuted", "in with medical gear, ~midnight", "The Globe and Mail"),
    ]),
    ("UNKNOWN", "questions put to DND", GREY, [
        ("What \"ignited\" at 4 p.m.,", "and how the time was set", ""),
        ("Whether the earlier fire was", "exercise-caused or planned", ""),
        ("Whether Range Control knew of", "fire at 12:17 or 2:49 p.m.", ""),
        ("Cause, and the number", "killed and injured", ""),
    ]),
]

W, pad = 1600, 50
header, footer = 190, 150
colw = (W - 2 * pad - 3 * 20) // 4
cardh, gap = 168, 14
top = header + 96
H = top + 4 * (cardh + gap) + 20 + footer
img = Image.new("RGBA", (W, H), BROWN_DK + (255,)); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 10, H], fill=GOLD)
d.text((pad, 40), "CFB WAINWRIGHT  ·  WHERE THE STORY STANDS  ·  7 A.M. MT, OCT. 18, 2026", font=font("Inter-Bold.otf", 24), fill=GOLD)
d.text((pad, 74), "What's confirmed, what the data shows, what's only reported", font=font("InterDisplay-Black.otf", 46), fill=CREAM)
d.text((pad, 136), "The gas-well scenario is reported but unconfirmed. The satellite record is consistent with it; it does not prove it.", font=font("Inter-Medium.otf", 23), fill=MUTED)

for i, (title, sub, col, cards) in enumerate(cols):
    x = pad + i * (colw + 20)
    d.rectangle([x, header + 10, x + colw, header + 18], fill=col)
    d.text((x, header + 28), title, font=font("Inter-Black.otf", 28), fill=col)
    d.text((x, header + 64), sub, font=font("Inter-Medium.otf", 18), fill=MUTED)
    for j, (l1, l2, src) in enumerate(cards):
        y = top + j * (cardh + gap)
        d.rounded_rectangle([x, y, x + colw, y + cardh], radius=10, fill=PANEL)
        d.rectangle([x, y + 10, x + 5, y + cardh - 10], fill=col)
        d.text((x + 22, y + 20), l1, font=font("Inter-SemiBold.otf", 20), fill=CREAM)
        if l2: d.text((x + 22, y + 50), l2, font=font("Inter-SemiBold.otf", 20), fill=CREAM)
        if src: d.text((x + 22, y + cardh - 38), src, font=font("Inter-Medium.otf", 17), fill=col)

fy = H - footer + 10
d.rectangle([0, fy, W, H], fill=NAVY); d.rectangle([0, fy, W, fy + 5], fill=GOLD)
fc = font("Inter-Medium.otf", 21)
d.text((pad, fy + 26), "Times are Mountain Time. Satellite detections show heat, not cause. Status as of 7 a.m. MT, Oct. 18, 2026; officials may update.", font=fc, fill=CREAM)
d.text((pad, fy + 58), "Sources: DND, RCMP, MD of Wainwright, NASA FIRMS, Global News, CBC News, The Globe and Mail. Graphic: Prime Rogue Inc.", font=fc, fill=CREAM)
d.text((pad, fy + 108), "PRIME ROGUE", font=font("Inter-Black.otf", 24), fill=GOLD, anchor="lm")
logo = Image.open(LOGO).convert("RGBA").resize((96, 96), Image.LANCZOS)
img.alpha_composite(logo, (W - 96 - pad, fy + 24))
img.convert("RGB").save(sys.argv[1], quality=90, optimize=True)
print(img.size)
