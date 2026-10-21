from PIL import Image, ImageDraw, ImageFont
import sys

LOGO = "/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png"
F = "/usr/share/fonts/opentype/inter/"
BROWN_DK, PANEL = (28, 20, 15), (40, 29, 22)
GOLD, CREAM, NAVY, MUTED = (212, 175, 104), (238, 230, 214), (30, 52, 82), (176, 162, 138)
GREEN, BLUE, AMBER = (120, 170, 110), (79, 141, 214), (214, 150, 60)
def font(n, s): return ImageFont.truetype(F + n, s)

# (time, text, source, kind)  kind: O official, D data, R reported, P Prime Rogue
ev = [
    ("12:17 p.m.", "Likely fire on the range: 59 low-confidence detections", "Landsat 8 (NASA FIRMS)", "D"),
    ("2:49 p.m.", "Fire detected on the range: 8 detections", "NOAA-20 VIIRS (NASA FIRMS)", "D"),
    ("≈ 4 p.m.", "Fire “reported” on the range (CAF); “ignited” (later DND release)", "CAF statement; DND release", "O"),
    ("≈ 4 p.m.", "RCMP respond to a request for assistance", "RCMP Alberta", "O"),
    ("≈ 4 p.m.", "Exercise hit gas line or well, explosion (unconfirmed)", "Global News, CAF sources", "R"),
    ("Evening", "Fire crosses the base fence, spreads south of Wainwright", "MD of Wainwright", "O"),
    ("≈ 7:30–8 p.m.", "McGuinty confirms “both fatalities and injuries”", "Defence Minister, Ottawa", "O"),
    ("10:47 p.m.", "Fire “being held”; fire watch in place", "MD of Wainwright", "O"),
    ("≈ midnight", "Code Orange at several acute care facilities", "Acute Care Alberta", "O"),
    ("≈ midnight", "Seven CAF members parachute in with medical gear", "The Globe and Mail", "R"),
    ("Overnight", "DND release: fire “ignited” at approx. 4 p.m.; no cause given", "DND news release, dated Oct. 18", "O"),
    ("2:00 a.m.", "Satellite timeline analysis published", "Prime Rogue", "P"),
    ("2:40–4:25 a.m.", "Four satellite passes: no fire at the base", "VIIRS (NASA FIRMS)", "D"),
    ("Early Sunday", "Exercise fire may have set off a gas well (“possible”)", "CBC's Murray Brewster", "R"),
    ("6 p.m. Sun.", "Deadline for DND response to Prime Rogue's questions", "Prime Rogue", "P"),
]
COL = {"O": GREEN, "D": BLUE, "R": AMBER, "P": CREAM}
NAME = {"O": "OFFICIAL", "D": "SATELLITE DATA", "R": "REPORTED, UNCONFIRMED", "P": "PRIME ROGUE"}

W, pad = 1600, 60
header, rowh, footer = 230, 78, 150
H = header + len(ev) * rowh + 40 + footer
img = Image.new("RGBA", (W, H), BROWN_DK + (255,)); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 10, H], fill=GOLD)
d.text((pad, 40), "CFB WAINWRIGHT  ·  TIMELINE  ·  OCT. 17–18, 2026, MOUNTAIN TIME", font=font("Inter-Bold.otf", 24), fill=GOLD)
d.text((pad, 74), "How the night unfolded", font=font("InterDisplay-Black.otf", 52), fill=CREAM)
x = pad
for k in ["O", "D", "R", "P"]:
    d.ellipse([x, 160, x + 20, 180], fill=COL[k])
    d.text((x + 30, 170), NAME[k], font=font("Inter-Bold.otf", 19), fill=COL[k], anchor="lm")
    x += 44 + d.textlength(NAME[k], font=font("Inter-Bold.otf", 19)) + 26

tx, lx, cx = pad, pad + 250, pad + 290
top = header + 10
d.line([(lx, top + 20), (lx, top + (len(ev) - 1) * rowh + 20)], fill=(70, 55, 44), width=4)
# 4 p.m. divider
for i, (t, txt, src, k) in enumerate(ev):
    y = top + i * rowh
    if i % 2 == 0:
        d.rounded_rectangle([pad - 16, y - 8, W - pad + 16, y + rowh - 14], radius=8, fill=(34, 25, 19))
    d.text((lx - 28, y + 20), t, font=font("Inter-Bold.otf", 22), fill=CREAM, anchor="rm")
    d.ellipse([lx - 11, y + 9, lx + 11, y + 31], fill=COL[k], outline=BROWN_DK, width=3)
    d.text((cx, y + 4), txt, font=font("Inter-SemiBold.otf", 23), fill=CREAM)
    d.text((cx, y + 36), src, font=font("Inter-Medium.otf", 18), fill=COL[k])

fy = H - footer + 10
d.rectangle([0, fy, W, H], fill=NAVY); d.rectangle([0, fy, W, fy + 5], fill=GOLD)
fc = font("Inter-Medium.otf", 21)
d.text((pad, fy + 26), "Times approximate where marked (≈). Satellite detections show heat, not cause. Cause and casualty count not confirmed by officials.", font=fc, fill=CREAM)
d.text((pad, fy + 58), "Status as of 7 a.m. MT, Oct. 18. Sources as listed. Graphic: Prime Rogue Inc.", font=fc, fill=CREAM)
d.text((pad, fy + 108), "PRIME ROGUE", font=font("Inter-Black.otf", 24), fill=GOLD, anchor="lm")
logo = Image.open(LOGO).convert("RGBA").resize((96, 96), Image.LANCZOS)
img.alpha_composite(logo, (W - 96 - pad, fy + 24))
img.convert("RGB").save(sys.argv[1], quality=90, optimize=True)
print(img.size)
