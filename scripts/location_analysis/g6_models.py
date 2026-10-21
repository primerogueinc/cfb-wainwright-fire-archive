import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/vis")
from pr import *
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for n in ["Inter-Medium.otf", "Inter-Bold.otf", "Inter-Black.otf"]: fm.fontManager.addfont(F + n)
plt.rcParams["font.family"] = "Inter"
hx = lambda c: "#%02x%02x%02x" % c
OUT = "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/vis/"
import numpy as np
x = np.linspace(0, 5, 200)
lo, hi = 4.4, 12.0   # post-shift model head spread, km/h
fig = plt.figure(figsize=(16.92, 8.9), dpi=100, facecolor=hx(BG))
ax = fig.add_axes([0.08, 0.1, 0.62, 0.84], facecolor=hx(BG))
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(colors=hx(MUTED), labelsize=13, length=0); ax.grid(color=hx(GRIDC), lw=1)
ax.axvspan(0.6, 1.5, color=hx(TEAL), alpha=0.13, lw=0)
ax.text(1.05, 61, "Range 2 area\n(0.6 to 1.5 km)", ha="center", va="top", color=hx(TEAL), fontsize=14, fontweight="bold")
ax.fill_between(x, x / hi * 60, x / lo * 60, color=hx(RED), alpha=0.35, lw=0)
ax.plot(x, x / hi * 60, color=hx(RED), lw=2.5); ax.plot(x, x / lo * 60, color=hx(RED), lw=2.5)
ax.plot(x, x / 16.4 * 60, color=hx(GOLD), lw=2, ls=(0, (5, 3)))
ax.plot(x, x * 0.5, color=hx(CREAM), lw=3); ax.plot(x, x * 1.0, color=hx(CREAM), lw=3)
ax.fill_between(x, x * 0.5, x * 1.0, color=hx(CREAM), alpha=0.25, lw=0)
ax.text(4.95, 6.3, "Rutland's \"a kilometre in 30 to 60 seconds\"", ha="right", va="bottom", color=hx(CREAM), fontsize=14, fontweight="bold")
ax.text(3.15, 3.15 / lo * 60 + 1, "slowest model\n4.4 km/h", color=hx(RED), fontsize=13, fontweight="bold", ha="right")
ax.text(2.9, 2.9 / hi * 60 + 1.2, "fastest model, 12 km/h", color=hx(RED), fontsize=13, fontweight="bold", ha="right", va="bottom")
ax.text(4.95, 4.95 / 16.4 * 60 - 3.6, "20% rule at the 82 km/h gust", color=hx(GOLD), fontsize=12.5, ha="right", va="top")
ax.set_xlim(0, 5); ax.set_ylim(0, 62)
ax.set_xlabel("Distance downwind of the fire's side when the wind turned (km)", color=hx(MUTED), fontsize=13)
ax.set_ylabel("Minutes for the fire front to arrive", color=hx(MUTED), fontsize=13)
fig.savefig(OUT + "_models.png", facecolor=hx(BG), dpi=100)

im, d = canvas(1800, 1240, "FIRE BEHAVIOUR MODELS  ·  CFB WAINWRIGHT  ·  OCT. 17, 2026",
               "Models: 5 to 14 minutes to cover 1 km, not 30 seconds",
               "Grass fire spread after the 3:16 p.m. wind shift, from three standard models fed with the base's own weather readings.")
ch = Image.open(OUT + "_models.png").convert("RGBA"); im.alpha_composite(ch, (30, 180)); d = ImageDraw.Draw(im)
X, y = 1250, 214
d.text((X, y), "What the models say", font=K(24), fill=GOLD); y += 44
items = [("5 to 14 minutes", ["for the front to cover 1 km after the", "shift: 4.4 to 12 km/h. Rutland's figure", "needs 60 to 120 km/h."]),
         ("Seconds of warning, not of spread", ["A 2 km side turning into the front,", "with smoke and dust ahead of it, can", "hide a fire 1 km away until it is close."]),
         ("Before the shift, the fire was held", ["Free-burning, it could have run 5 to", "8 km/h. It grew about 1 km in 2.5 hours.", "Its side crept 200 to 320 m at most."]),
         ("6,500 to 21,000 kW/m", ["Fireline intensity after the shift.", "Ground crews can't attack a fire", "above about 4,000 kW/m."])]
for h, ls in items:
    d.text((X, y), h, font=B(20), fill=CREAM); y += 30
    for l in ls: d.text((X, y), l, font=M(17), fill=MUTED); y += 25
    y += 16
footer(im, ["Models: Canadian FBP System, grass fuel types O-1a and O-1b (Forestry Canada 1992); CSIRO grassland model, natural and grazed (Cheney et al. 1998); Cruz et al. (2022) 20% rule.",
            "Inputs: ECCC CZWN, Oct. 17 (wind 48 km/h, gust 82; 13-18 C; RH 25-43%); FFMC 92.3-92.9; grass 90-100% cured. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"])
im.convert("RGB").save(OUT + "cfb-wainwright-fire-models.jpg", quality=91, optimize=True)
print(im.size)
