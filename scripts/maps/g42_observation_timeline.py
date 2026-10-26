"""Table graphic: every direct observation of the Oct. 17 fire and the weather, by source and time (MDT). Prime Rogue style."""
import sys, os, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pr import *  # noqa
OUT = REPO + "data/graphics_published/oct26_range15/"; os.makedirs(OUT, exist_ok=True)
R = [("11:00 a.m. to 3:00 p.m.", "NOAA GOES-18 and GOES-19 (scan every 10 min)", "No fire detected. Cloud mask flags 96-100% cloud, so weak evidence of no fire.", False),
     ("12:17 p.m.", "Landsat 8 (NASA FIRMS)", "59 fire pixels in a line about 1.9 km long: first recorded position.", True),
     ("2:48 p.m.", "Environment Canada, CZWN (raw SWOB)", "Peak gust of the hour: 51 km/h from the south-west.", False),
     ("2:49 p.m.", "VIIRS, NOAA-20 (NASA FIRMS)", "8 fire pixels, 74.6 MW; fire north-east of the noon line.", True),
     ("3:00 p.m.", "Environment Canada, CZWN (hourly)", "Wind south-west (236°), 32 km/h; 23.3 °C; 17% humidity.", False),
     ("3:00 p.m.", "GOES-18", "No fire detected (98% cloud flagged).", False),
     ("3:10 p.m.", "GOES-18", "1 pixel, 76.5 MW.", True),
     ("3:16 p.m.", "Environment Canada, CZWN (raw SWOB)", "Peak gust 82 km/h from the west (269°): the front arrives.", True),
     ("3:20 p.m.", "GOES-18", "No fire detected; probably a missed detection.", False),
     ("3:30 p.m.", "GOES-18", "3 pixels, 1,215 MW: the run, about 16 times the 3:10 reading.", True),
     ("3:40 p.m.", "GOES-18", "1 pixel, 336 MW.", True),
     ("3:50 p.m. onward", "GOES-18", "No fire detected (smoke, or the run had passed).", False),
     ("4:00 p.m.", "Environment Canada, CZWN (hourly)", "Wind north-west (307°), 48 km/h; 12.9 °C; 43% humidity.", True),
     ("All afternoon", "GOES-19", "Nothing detected on any scan.", False),
     ("Oct. 18, 2:12 and 2:32 p.m.", "VIIRS, S-NPP and NOAA-20", "One small hotspot each (2.6 and 3.8 MW): smouldering.", False),
     ("Oct. 19 and Oct. 24", "Sentinel-2 (Copernicus); Landsat 8 (USGS)", "The final burn scar the model is fitted to; edge checks.", False)]
W = 1600; LH = 27; rowsH = []
for t, s, w, b in R:
    n = max(len(textwrap.wrap(s, 30)), len(textwrap.wrap(w, 58)), len(textwrap.wrap(t, 16)))
    rowsH.append(n * LH + 22)
TOP = 250; H = TOP + 60 + sum(rowsH) + 70 + 140
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · OCT. 17, 2026 · THE RECORD", "What the instruments saw, and when",
               "Every direct observation of the fire and the weather on Oct. 17, by source (times MDT). Everything between these points is the model.")
d = ImageDraw.Draw(im)
X = [60, 380, 830]; y = TOP
d.rectangle([50, y - 10, W - 50, y + 44], fill=NAVY)
for x, h in zip(X, ("Time (MDT)", "Source", "What it recorded")): d.text((x, y), h, font=B(23), fill=GOLD)
y += 60
for i, ((t, s, w, b), rh) in enumerate(zip(R, rowsH)):
    if i % 2 == 0: d.rectangle([50, y - 8, W - 50, y + rh - 12], fill=PANEL)
    for x, txt, wid, f in ((X[0], t, 16, B(21)), (X[1], s, 30, M(20)), (X[2], w, 58, (B(21) if b else M(21)))):
        yy = y
        for line in textwrap.wrap(txt, wid): d.text((x, yy), line, font=f, fill=(CREAM if (b or x != X[2]) else MUTED) if x == X[2] else CREAM); yy += LH
    y += rh
d.text((60, y + 10), "Bold: fire detected or key weather reading. The model is anchored on the 12:17 Landsat line and 2:49 VIIRS pixels, driven by the station weather,", font=M(18), fill=MUTED)
d.text((60, y + 36), "and fitted to the Oct. 19 burn scar; GOES is a timing check, not an input.", font=M(18), fill=MUTED)
footer(im, ["Sources: NOAA GOES-18/19 ABI fire detection (FDC) via NOAA open data on AWS; NASA FIRMS (Landsat 8, VIIRS); Environment and Climate Change Canada, CFB Wainwright (CZWN),",
            "raw SWOB records and hourly data; Copernicus Sentinel-2; USGS Landsat. Tables: data/goes/fire_timeline.csv, data/firms/detections.csv, data/weather_exports/.",
            "Graphic: Kevin Duska Jr. (Prime Rogue Inc.), CC BY-NC 4.0."], fh=130)
im.convert("RGB").save(OUT + "cfb-wainwright-observation-timeline.png", optimize=True); print(H)
