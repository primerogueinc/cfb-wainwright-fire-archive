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
        ("Four soldiers killed, serving", "with 3rd Battalion, PPCLI", "DND; Maj.-Gen. Rutland"),
        ("39 received hospital care:", "19 critical, 8 stable, 12 ambulatory", "Acute Care Alberta"),
        ("Range control knew of a fire for", "several hours; training continued", "Maj.-Gen. Rutland"),
        ("Wind shift drove fire 1 km onto", "troops in 30 to 60 seconds", "Maj.-Gen. Rutland"),
    ]),
    ("IN THE DATA", "NASA, Environment Canada", BLUE, [
        ("Fire detected on the range", "at 2:49 p.m. (8 detections)", "NOAA-20 VIIRS"),
        ("Likely fire at 12:17 p.m.", "59 detections, low confidence", "Landsat 8"),
        ("4 p.m.: wind swings NW,", "gusts 69 km/h, temp drops 10°C", "ECCC, CFB Wainwright"),
        ("No fire at the base on four", "overnight passes", "VIIRS, three satellites"),
    ]),
    ("DND IN WRITING", "official statements", AMBER, [
        ("Sat.: fire \u201creported\u201d ~1600;", "statement later removed", "CAF statement"),
        ("Early Sun.: fire \u201cignited\u201d", "at approx. 4:00 p.m.", "DND news release"),
        ("\u201cWhile conducting training", "a fire ignited\u201d", "DND release naming soldiers"),
        ("No mention of a fire known", "for hours; not corrected", "As of 9 p.m. MT"),
    ]),
    ("UNKNOWN", "questions put to DND", GREY, [
        ("Is the monitored fire the one", "that reached the soldiers?", ""),
        ("What started the fire,", "and when", ""),
        ("Who decided training would", "continue, and why", ""),
        ("Was the wind warning", "(gusts to 90 km/h) considered?", ""),
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
d.text((pad, 40), "CFB WAINWRIGHT  ·  WHAT WE KNOW NOW  ·  9 P.M. MT, OCT. 18, 2026", font=font("Inter-Bold.otf", 24), fill=GOLD)
d.text((pad, 74), "Known for hours. Written up as \u201cignited\u201d at 4 p.m.", font=font("InterDisplay-Black.otf", 46), fill=CREAM)
d.text((pad, 136), "The military's account fits the satellite and weather data. DND's written account never mentions the earlier fire.", font=font("Inter-Medium.otf", 23), fill=MUTED)

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
d.text((pad, fy + 26), "Times are Mountain Time. Satellite detections show heat, not cause. Status as of 9 p.m. MT, Oct. 18, 2026; a Board of Inquiry will report.", font=fc, fill=CREAM)
d.text((pad, fy + 58), "Sources: military briefing (CPAC), DND and CAF statements, Acute Care Alberta, NASA FIRMS, ECCC. Graphic: Prime Rogue Inc.", font=fc, fill=CREAM)
d.text((pad, fy + 108), "PRIME ROGUE", font=font("Inter-Black.otf", 24), fill=GOLD, anchor="lm")
logo = Image.open(LOGO).convert("RGBA").resize((96, 96), Image.LANCZOS)
img.alpha_composite(logo, (W - 96 - pad, fy + 24))
img.convert("RGB").save(sys.argv[1], quality=90, optimize=True)
print(img.size)
