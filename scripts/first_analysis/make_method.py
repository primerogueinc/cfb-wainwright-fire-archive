from PIL import Image, ImageDraw, ImageFont
import sys

LOGO = "/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png"
F = "/usr/share/fonts/opentype/inter/"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
BROWN_DK, PANEL = (28, 20, 15), (40, 29, 22)
GOLD, CREAM, NAVY, MUTED = (212, 175, 104), (238, 230, 214), (30, 52, 82), (176, 162, 138)
LANDSAT, VIIRS = (185, 132, 36), (79, 141, 214)
def font(n, s): return ImageFont.truetype(F + n, s)
def mono(s): return ImageFont.truetype(MONO, s)

W, pad = 1600, 60
header, rowh, footer = 230, 168, 250
steps = [
  ("DOWNLOAD", "NASA FIRMS active-fire files for Alberta,", "24-hour window, every sensor.",
   [("t", "10 files: Landsat 8/9 · VIIRS (NOAA-20, NOAA-21,"), ("t", "Suomi-NPP) · MODIS (Aqua, Terra)"),
    ("m", "Pulled 11:50 p.m. and 1:10 a.m. MT: identical")]),
  ("FILTER", "Keep only detections inside the", "CFB Wainwright training area.",
   [("b", "67 detections"), ("c", [("59 Landsat 8", LANDSAT), ("  ·  ", MUTED), ("8 NOAA-20 VIIRS", VIIRS)]),
    ("m", "Cluster centre 8.2 km SSW of the town")]),
  ("READ THE CLOCK", "Every detection carries the satellite's", "acquisition time, recorded in UTC.",
   [("mono", "18:17 UTC  →  12:17 p.m. MDT", LANDSAT), ("mono", "20:49 UTC  →   2:49 p.m. MDT", VIIRS),
    ("m", "MDT = UTC − 6 hours")]),
  ("CHECK CONFIDENCE", "NASA grades each detection. We", "report the grade, not just the dot.",
   [("c", [("Landsat: all 59 Low", LANDSAT), ("  →  \"likely\"", CREAM)]),
    ("c", [("VIIRS: all 8 Nominal", VIIRS), ("  →  \"detected\"", CREAM)]),
    ("m", "VIIRS fire power 5.8 to 11.5 MW per pixel")]),
  ("CROSS-CHECK", "NASA's own map colours detections by", "age. It must agree with the files.",
   [("t", "Captured 1:09 a.m. MDT:"), ("c", [("orange (6–12 h old)", (255, 181, 0)), ("  =  2:49 p.m.  ✓", CREAM)]),
    ("c", [("pale yellow (12–24 h old)", (247, 231, 186)), ("  =  12:17 p.m.  ✓", CREAM)])]),
  ("COMPARE", "Line the detection times up against", "the official record.",
   [("c", [("CAF: fire “reported” ≈ 4 p.m.", CREAM)]), ("c", [("DND: fire “ignited” ≈ 4 p.m.", CREAM)]),
    ("b", "2:49 p.m. is ≈ 70 min earlier")]),
]
H = header + rowh * len(steps) + footer
img = Image.new("RGBA", (W, H), BROWN_DK + (255,)); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 10, H], fill=GOLD)
d.text((pad, 44), "METHODOLOGY  ·  NASA FIRMS SATELLITE DATA  ·  CFB WAINWRIGHT", font=font("Inter-Bold.otf", 24), fill=GOLD)
d.text((pad, 80), "How we built the timeline, step by step", font=font("InterDisplay-Black.otf", 54), fill=CREAM)
d.text((pad, 152), "Every number below comes from NASA's public files. Anyone can repeat this.", font=font("Inter-Medium.otf", 26), fill=MUTED)

cx = pad + 34
top = header + 20
d.line([(cx, top + 34), (cx, top + rowh * (len(steps) - 1) + 34)], fill=GOLD, width=4)
ex0, ex1 = 780, W - pad
for i, (title, l1, l2, ev) in enumerate(steps):
    y = top + i * rowh
    d.ellipse([cx - 34, y, cx + 34, y + 68], fill=GOLD)
    d.text((cx, y + 34), str(i + 1), font=font("Inter-Black.otf", 34), fill=BROWN_DK, anchor="mm")
    d.text((cx + 62, y + 4), title, font=font("Inter-Black.otf", 32), fill=GOLD)
    d.text((cx + 62, y + 50), l1, font=font("Inter-Medium.otf", 25), fill=CREAM)
    d.text((cx + 62, y + 82), l2, font=font("Inter-Medium.otf", 25), fill=CREAM)
    d.rounded_rectangle([ex0, y - 6, ex1, y + rowh - 26], radius=10, fill=PANEL)
    ly = y + 10
    for item in ev:
        kind = item[0]
        if kind == "t":
            d.text((ex0 + 24, ly), item[1], font=font("Inter-SemiBold.otf", 24), fill=CREAM)
        elif kind == "m":
            d.text((ex0 + 24, ly), item[1], font=font("Inter-Medium.otf", 22), fill=MUTED)
        elif kind == "b":
            d.text((ex0 + 24, ly - 2), item[1], font=font("Inter-Black.otf", 28), fill=GOLD)
        elif kind == "mono":
            d.text((ex0 + 24, ly), item[1], font=mono(25), fill=item[2])
        elif kind == "c":
            x = ex0 + 24
            for txt, col in item[1]:
                f = font("Inter-Bold.otf", 24)
                d.text((x, ly), txt, font=f, fill=col); x += d.textlength(txt, font=f)
        ly += 40

fy = H - footer + 10
d.rectangle([0, fy, W, H], fill=NAVY); d.rectangle([0, fy, W, fy + 5], fill=GOLD)
fc = font("Inter-Medium.otf", 23)
d.text((pad, fy + 30), "WHAT THIS CANNOT SHOW", font=font("Inter-Black.otf", 24), fill=GOLD)
d.text((pad, fy + 66), "Satellites detect heat, not cause. No high-resolution satellite passed over the base from about", font=fc, fill=CREAM)
d.text((pad, fy + 98), "3:30 p.m. until dark, so this data says nothing about what happened at or after 4 p.m., including the explosion.", font=fc, fill=CREAM)
d.text((pad, fy + 142), "Check it yourself: firms.modaps.eosdis.nasa.gov  ·  Our raw detection file is published with the analysis.", font=fc, fill=CREAM)
d.text((pad, fy + 200), "PRIME ROGUE", font=font("Inter-Black.otf", 26), fill=GOLD, anchor="lm")
d.text((pad + 190, fy + 201), "Data: NASA FIRMS. Analysis and graphic: Prime Rogue Inc.", font=font("Inter-Medium.otf", 21), fill=MUTED, anchor="lm")
logo = Image.open(LOGO).convert("RGBA").resize((110, 110), Image.LANCZOS)
img.alpha_composite(logo, (W - 110 - pad, fy + 120))
img.convert("RGB").save(sys.argv[1], quality=90, optimize=True)
print(img.size)
