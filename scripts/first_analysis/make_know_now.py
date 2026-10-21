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
        ("Four soldiers killed, all", "3rd Battalion, PPCLI", "Military; PM Carney"),
        ("39 hospitalized: 19 critical,", "8 stable, 12 ambulatory", "Acute Care Alberta"),
        ("Wind shift drove fire 1 km onto", "troops in 30 to 60 seconds", "Maj.-Gen. Rutland"),
        ("Gas infrastructure not believed", "involved; no terrorism", "CAF; DND"),
    ]),
    ("IN THE DATA", "NASA, Environment Canada", BLUE, [
        ("Fire detected on the range", "at 2:49 p.m. (8 detections)", "NOAA-20 VIIRS"),
        ("Likely fire at 12:17 p.m.", "59 detections, low confidence", "Landsat 8"),
        ("4 p.m.: wind swings NW,", "gusts 69 km/h, temp drops 10°C", "ECCC, CFB Wainwright"),
        ("No fire at the base on four", "overnight passes", "VIIRS, three satellites"),
    ]),
    ("REPORTED", "from briefing accounts", AMBER, [
        ("Range Control knew of fire for", "several hours, monitored it", "Edmonton Journal; CTV"),
        ("Officials decided to", "continue training", "CTV News"),
        ("C Company on grenade range,", "section attack; ~84 soldiers", "Rutland, per CTV"),
        ("Training for Latvia and the", "Global Response Task Force", "Edmonton Journal"),
    ]),
    ("UNKNOWN", "questions put to DND", GREY, [
        ("What started the grass fire,", "and when", ""),
        ("Who decided training would", "continue, and why", ""),
        ("Whether the forecast wind", "shift was considered", ""),
        ("What \"ignited\" at 4 p.m.;", "whether deaths preventable", ""),
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
d.text((pad, 40), "CFB WAINWRIGHT  ·  WHAT WE KNOW NOW  ·  7 P.M. MT, OCT. 18, 2026", font=font("Inter-Bold.otf", 24), fill=GOLD)
d.text((pad, 74), "A fire known for hours, then a deadly wind shift", font=font("InterDisplay-Black.otf", 46), fill=CREAM)
d.text((pad, 136), "The military's account is consistent with the satellite and weather data. The key question: why training continued.", font=font("Inter-Medium.otf", 23), fill=MUTED)

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
d.text((pad, fy + 26), "Times are Mountain Time. Satellite detections show heat, not cause. Status as of 7 p.m. MT, Oct. 18, 2026; a Board of Inquiry will report.", font=fc, fill=CREAM)
d.text((pad, fy + 58), "Sources: CAF briefing, DND, Acute Care Alberta, NASA FIRMS, ECCC, Edmonton Journal, CTV News. Graphic: Prime Rogue Inc.", font=fc, fill=CREAM)
d.text((pad, fy + 108), "PRIME ROGUE", font=font("Inter-Black.otf", 24), fill=GOLD, anchor="lm")
logo = Image.open(LOGO).convert("RGBA").resize((96, 96), Image.LANCZOS)
img.alpha_composite(logo, (W - 96 - pad, fy + 24))
img.convert("RGB").save(sys.argv[1], quality=90, optimize=True)
print(img.size)
