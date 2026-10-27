"""Table graphic: distances around Range 15 / the road head and travel times on foot (v4 escape-model speeds). Prime Rogue style."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pr import *  # noqa
OUT = REPO + "data/graphics_published/oct26_range15/"; os.makedirs(OUT, exist_ok=True)
rows = [("Range 15 to the road head", "20 m", "9 s", "14 s", "24 s", "36 s"),
        ("Range 2 to Range 15", "188 m", "1 min 25 s", "2 min 15 s", "3 min 45 s", "5 min 40 s"),
        ("Range 15 to the fire's edge at 3:16 p.m.", "1.13 km", "8 min 30 s", "13 min 30 s", "22 min 35 s", "33 min 50 s")]
head = ("Distance", "", "Jog in kit\n8 km/h", "Walk\n5 km/h", "In smoke\n3 km/h", "Helping injured\n2 km/h")
W, H = 1600, 960
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · WORKING MODEL V4 · RANGE STANDING ORDERS", "Seconds on foot, minutes for the fire",
               "Range 15, the field firing range in the 2024 Range Standing Orders, sits 20 m from the road head. On Oct. 17 the fire\ncovered the 1.13 km from its 3:16 p.m. edge to Range 15 in about 10 minutes, roughly the speed of a soldier jogging in kit.")
d = ImageDraw.Draw(im)
X = [60, 560, 760, 960, 1160, 1360]; y0 = 250
d.rectangle([50, y0 - 10, W - 50, y0 + 70], fill=NAVY)
for x, h in zip(X, head):
    d.multiline_text((x, y0), h, font=B(22), fill=GOLD, spacing=4)
y = y0 + 95
for i, r in enumerate(rows):
    if i % 2 == 0: d.rectangle([50, y - 14, W - 50, y + 58], fill=PANEL)
    for j, (x, v) in enumerate(zip(X, r)):
        d.text((x, y), v, font=(B(24) if j < 2 else M(24)), fill=CREAM if j else CREAM)
    y += 80
y += 20
for t in ["The fire (v4, front at the fire 3:16 p.m., 240 runs weighted by fit to the scar): reaches Range 15 at a median 3:26 p.m. (3:22-3:35)",
          "and Range 2 at 3:25 p.m. (3:21-3:32); at 3:16 they were 1.13 km and 0.97 km from the fire's edge. The mapped burn stopped 18 m short",
          "of Range 15's grid reference, at the track junction; a 33-35 ha pocket to the north-east never burned.",
          "Where C Company was is not confirmed by DND. A range's grid reference is one point (likely its entrance or firing point), not the whole range."]:
    d.text((60, y), t, font=M(20), fill=MUTED); y += 32
footer(im, ["Grid references: 3 CDSB Edmonton Det Wainwright Range and Training Area Standing Orders, 2024 edition (ch. 1 para 51; Annex H).",
            "Speeds: Prime Rogue escape model (part 4). Fire timing: working model v4. Data and code: github.com/primerogueinc/cfb-wainwright-fire-archive.",
            "Graphic: Kevin Duska Jr. (Prime Rogue Inc.), CC BY-NC 4.0."], fh=130)
im.convert("RGB").save(OUT + "cfb-wainwright-range15-run-times.png", optimize=True); print("ok")
