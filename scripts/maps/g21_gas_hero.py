import sys; sys.path.insert(0, "vis")
from pr import *
ROWS = [
 ("Where it started", "Range 11's impact area. No gas line or well in its firing sector within 2.5 km.", "POINTS AWAY", TEAL),
 ("How far from gas", "Start ~1.4 km and the 12:17 p.m. fire ~0.9 km from the nearest gas line.\nThe fire reached the lines about 3:25 p.m., hours after it started.", "POINTS AWAY", TEAL),
 ("Fire heat (GOES-18)", "Heat rose with the wind shift and spread along the front; none after 3:40 p.m.\nClear skies from ~7:30 p.m.: no hot spot all night.", "POINTS AWAY", TEAL),
 ("Burn scars (Sentinel-2)", "No scorch circle on the lines; the burn was lighter there. The well's site did not burn.", "POINTS AWAY", TEAL),
 ("The air, Oct. 17 (Sentinel-5P)", "Passed at 2:34 p.m., before the fire reached the lines; cloud over the base.", "CAN'T TELL", MUTED),
 ("The air, Oct. 18 (Sentinel-5P)", "No methane leak at or downwind of the base the next day.", "POINTS AWAY", TEAL),
 ("The paperwork", "Regulator (Oct. 18): no incident reports. But the wells were under a suspension order\nand, per the operator, had not been shut in. Lines were probably live.", "OPEN", GOLD),
]
W, H = 1700, 1185
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · GAS INFRASTRUCTURE TEST · WORKING MODEL V2.1",
               "Another sign pointing away from gas",
               "We tested the claim that a live-fire round struck a gas line or well against every source we have. Gas is not ruled out.\nBut each test that can see it points away from gas starting the fire or feeding it.")
y = 220
for k, (h, t, chip, c) in enumerate(ROWS):
    lines = t.split("\n"); rh = 40 + 28 * len(lines)
    d.rounded_rectangle([54, y, W - 54, y + rh], radius=10, fill=PANEL)
    d.text((80, y + 18), h, font=B(22), fill=CREAM)
    for i, l in enumerate(lines): d.text((480, y + 20 + i * 28), l, font=M(19), fill=CREAM)
    cw = d.textlength(chip, font=B(17)) + 34
    d.rounded_rectangle([W - 80 - cw, y + rh / 2 - 19, W - 80, y + rh / 2 + 19], radius=19, fill=c)
    d.text((W - 80 - cw / 2, y + rh / 2), chip, font=B(17), fill=INK, anchor="mm")
    y += rh + 14
d.rounded_rectangle([54, y + 10, W - 54, y + 130], radius=10, outline=GOLD, width=3)
d.text((80, y + 30), "NOT RULED OUT", font=B(19), fill=GOLD)
d.text((80, y + 62), "A brief release, seconds to minutes, as the fire crossed the lines around 3:25 p.m. No satellite we have", font=M(20), fill=CREAM)
d.text((80, y + 92), "could see it. Open records (operator, Orphan Well Association, DND's infrastructure check) could.", font=M(20), fill=CREAM)
footer(im, ["Sources: Alberta Energy Regulator licence data and suspension order (Oct. 5, amended Oct. 9); NOAA GOES-18; Copernicus Sentinel-2 and Sentinel-5P; NASA FIRMS;",
            "Sumerian Oil & Gas statement (Oct. 19); Prime Rogue working model v2.1 (fire start and spread from Range 11). Contains modified Copernicus Sentinel data [2026].",
            "Graphic: Kevin Duska Jr. (Prime Rogue Inc.), CC BY-NC 4.0. Data and method: github.com/primerogueinc/cfb-wainwright-fire-archive (part 9)"], fh=140)
im = im.crop((0, 0, W, H)); im.convert("RGB").save("vis/cfb-wainwright-gas-hero.jpg", quality=92); print(y + 130 + 30 + 140, H)
