"""v4 graphic: DND's stated time against two government instruments (ECCC CZWN, NOAA GOES-18) and the model.
Usage (repo root): python3 scripts/maps/g34_dnd_clock.py"""
import sys; sys.path.insert(0, "scripts/maps")
from v4fig import *
W, H = 1600, 1250
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · WORKING MODEL V4 · DND'S CLOCK",
               "DND said \"just before 4:00\". The instruments say 3:16-3:30",
               "DND, Oct. 22: \"Just before 4:00 local time, uncommonly high winds took a pre-existing range fire towards the pairs range and it overtook their position.\"\n"
               "Environment Canada's weather station and NOAA's GOES-18 satellite put the wind, and the fire's run, about half an hour earlier.")
X0, X1, T0, T1 = 330, W - 70, 14 * 60 + 45, 16 * 60 + 15
tx = lambda h, m: X0 + (h * 60 + m - T0) / (T1 - T0) * (X1 - X0)
top, bot = 230, 900
for m in range(T0, T1 + 1, 15):
    x = tx(0, m); d.line([(x, top), (x, bot)], fill=GRIDC, width=1)
    d.text((x, bot + 10), f"{m // 60 - 12}:{m % 60:02d}", font=M(16), fill=MUTED, anchor="ma")
d.text((X1, bot + 36), "p.m., Oct. 17", font=M(15), fill=MUTED, anchor="ra")
# DND band
xa, xb = tx(15, 50), tx(16, 0)
d.rectangle([xa, top, xb, bot], fill=(70, 30, 22)); d.line([(tx(16, 0), top), (tx(16, 0), bot)], fill=RED, width=4)
rows = [("Weather station\nECCC CZWN\n(about 15 km west)", 285), ("Fire power\nNOAA GOES-18\n(whole fire)", 445),
        ("When the fire reached\nthe range\n(model v4, 240 fires)", 615), ("What DND said", 790)]
for t, y in rows:
    for k, l in enumerate(t.split("\n")): d.text((54, y - 30 + k * 22), l, font=B(17) if k == 0 else M(15), fill=CREAM if k == 0 else MUTED)
# station
x = tx(15, 16); d.line([(x, 250), (x, 330)], fill=TEAL, width=5)
label(d, (x + 12, 250), "3:16 p.m.: peak gust 82 km/h", col=TEAL, size=18)
label(d, (x + 12, 290), "3 p.m. -> 4 p.m.: wind SW -> NW, 32 -> 48 km/h; 23.3 -> 12.9 °C; humidity 17 -> 43%", col=CREAM, size=15)
# GOES bars
base = 500; sc = 0.075
for hh, mm, p in ((15, 0, 0), (15, 10, 76.5), (15, 20, 0), (15, 30, 1215.4), (15, 40, 336.3), (15, 50, 0), (16, 0, 0)):
    xa_ = tx(hh, mm); xb_ = tx(hh, mm + 10) - 4
    d.rectangle([xa_, base - max(2, p * sc), xb_, base], fill=GOLD if p else GRIDC)
    if p: d.text(((xa_ + xb_) / 2, base - p * sc - 6), f"{p:,.0f} MW", font=B(15), fill=GOLD, anchor="mb")
label(d, (tx(16, 0) + 10, 440), "from 3:50: no detection\n(smoke, or run over)", col=MUTED, size=14)
# model windows
for nm, a, b, y in (("Range 2", (15, 21), (15, 30), 585), ("Road head", (15, 26), (15, 34), 640)):
    xa_, xb_ = tx(*a), tx(*b); d.rounded_rectangle([xa_, y, xb_, y + 34], radius=6, fill=RED)
    d.text((xb_ + 10, y + 17), f"{nm}: median {a[0]-12}:{a[1]:02d}-{b[0]-12}:{b[1]:02d}", font=B(16), fill=CREAM, anchor="lm")
# DND statements
label(d, (tx(15, 16) + 4, 742), "Oct. 18: fire \"about a kilometre\" away\nwhen the wind shifted", col=CREAM, size=15)
label(d, (tx(15, 50) - 300, 830), "Oct. 22: \"just before 4:00\"\nOct. 17 release: \"approximately 4:00 p.m.\"", col=RED, size=17)
d.text(((tx(15, 30) + tx(15, 50)) / 2, 700), "about 25-35 min", font=B(18), fill=YEL, anchor="mm")
d.line([(tx(15, 30), 718), (tx(15, 50), 718)], fill=YEL, width=3)
# bottom text
y = 970
for l, f, c in (("The arithmetic: a fire 1 km away at 3:16-3:25 that arrives just before 4:00 averaged 1.4-2.4 km/h.", B(20), CREAM),
                ("After the wind shift this fire ran at 4.4-12 km/h in every version we modelled, and GOES saw its power jump 16 times by the 3:30 scan.", M(18), CREAM),
                ("Both statements cannot be literally true at once, except on a thin strip of the fire's flank (0-3% of the likely ground).", M(18), CREAM)):
    d.text((54, y), l, font=f, fill=c); y += 34
footer(im, ["Sources: ECCC CZWN hourly SWOB (Oct. 17); NOAA GOES-18 ABI fire product (10-minute full-disk scans, start times shown); DND briefings Oct. 18 and 22 and Oct. 17 release.",
            "Model: working model v4 (Prime Rogue), medians weighted by fit to the final Sentinel-2 scar; first time front at the fire 3:16, second 3:25. No ground observations.",
            SRC], fh=150)
im.convert("RGB").save(OUTD + "cfb-wainwright-dnd-clock.jpg", quality=92); print("ok")
