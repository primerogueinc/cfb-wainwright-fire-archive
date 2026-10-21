import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle
from PIL import Image

F = "/usr/share/fonts/opentype/inter/"
for n in ["Inter-Medium.otf", "Inter-SemiBold.otf", "Inter-Bold.otf", "Inter-Black.otf", "InterDisplay-Black.otf", "InterDisplay-Bold.otf"]:
    fm.fontManager.addfont(F + n)
plt.rcParams["font.family"] = "Inter"

BG = "#1C140F"; PANEL = "#251A14"; GOLD_UI = "#D4AF68"; CREAM = "#EEE6D6"
MUTED = "#A99B84"; GRID = "#352820"; NAVY = "#1E3452"
HELI = "#4F8DD6"; FIXED = "#B98424"; RCAF = CREAM; SAT = "#A99B84"

def t(h, m): return h + m / 60.0
rows = [  # label, sublabel, colour, departure (x, text, pos, ha) or None, observations [(x, text, pos, ha)]
    ("Satellite fire detections", "NASA FIRMS", SAT, None, [(t(12, 17), "Landsat 8 · likely", "a", "center"), (t(14, 49), "NOAA-20 · detected", "a", "center")]),
    ("RCAF CC-130H Hercules", "from Winnipeg (17 Wing)", RCAF, (t(19, 48), "dep. Winnipeg", "a", "center"),
        [(t(21, 35), "inbound east of Edmonton", "b", "left"), (t(27, 30), "low near Wainwright–Lloydminster", "a", "right")]),
    ("STAR11 · STARS EC145", "helicopter air ambulance", HELI, None, [(t(21, 35), "Wainwright → Edmonton", "a", "left")]),
    ("STAR03 · STARS EC145", "helicopter air ambulance", HELI, None, [(t(21, 36), "→ Edmonton", "b", "left"), (t(23, 12), "Wainwright → Edmonton", "a", "left")]),
    ("CWA935 · King Air 350", "CanWest Air", FIXED, (t(21, 35), "dep. Edmonton → Wainwright area", "a", "left"), []),
    ("C-GWRS · King Air", "Alberta Central Airways", FIXED, (t(22, 44), "dep. Edmonton Intl. → Wainwright", "a", "left"), []),
    ("SLG2 · King Air", "Saskatchewan Air Ambulance", FIXED, (t(23, 6), "dep. Saskatoon, westbound", "a", "left"), []),
    ("SLG3 · King Air", "Saskatchewan Air Ambulance", FIXED, (t(26, 42), "dep. Saskatoon", "a", "right"), [(t(27, 28), "near Lloydminster", "b", "right")]),
]

fig = plt.figure(figsize=(16, 11.6), dpi=100, facecolor=BG)
fig.patches.append(Rectangle((0, 0), 0.007, 1, transform=fig.transFigure, facecolor=GOLD_UI))
fig.text(0.03, 0.952, "FLIGHT TRACKING  ·  CFB WAINWRIGHT  ·  OCT. 17–18, 2026", color=GOLD_UI, fontsize=14.5, fontweight="bold")
fig.text(0.03, 0.905, "Through the night: aircraft over Wainwright", color=CREAM, fontsize=32, fontweight="black")
fig.text(0.03, 0.872, "Aircraft Prime Rogue observed on public flight tracking, Mountain Time. Dots are moments we captured, not complete flight paths.",
         color=MUTED, fontsize=13.5)

ax = fig.add_axes([0.235, 0.17, 0.735, 0.665], facecolor=PANEL)
for s in ax.spines.values(): s.set_visible(False)
n = len(rows)
ax.set_ylim(n - 0.4, -0.75); ax.set_xlim(11.6, 28.4)
ax.set_yticks([])
xt = [12, 14, 16, 18, 20, 22, 24, 26, 28]
ax.set_xticks(xt); ax.set_xticklabels(["noon", "2 p.m.", "4 p.m.", "6 p.m.", "8 p.m.", "10 p.m.", "midnight", "2 a.m.", "4 a.m."], color=MUTED, fontsize=11.5)
ax.tick_params(length=0)
ax.grid(axis="x", color=GRID, lw=1); ax.set_axisbelow(True)
for i in range(n):
    ax.axhline(i, color=GRID, lw=1, zorder=0)

# reference lines
ax.axvline(16, color=CREAM, lw=2.2, zorder=1)
ax.text(16.08, -0.62, "DND: fire “ignited” ≈ 4 p.m.", color=CREAM, fontsize=11, fontweight="bold", va="center")
ax.axvline(t(21, 20), color=MUTED, lw=1.3, ls=(0, (4, 3)), zorder=1)
ax.text(t(21, 20) + 0.1, -0.62, "CTV reports parachutes (by 9:20 p.m.)", color=MUTED, fontsize=10.5, ha="left", va="center")

def put(x, i, text, pos, ha, col):
    dx = {"left": 0.12, "right": -0.12, "center": 0}[ha]
    ax.text(x + dx, i + (-0.32 if pos == "a" else 0.32), text, color=col, fontsize=10.5, ha=ha, va="center")

for i, (lab, sub, col, dep, obs) in enumerate(rows):
    ax.text(11.45, i - 0.1, lab, color=CREAM, fontsize=12.5, fontweight="bold", ha="right", va="center", clip_on=False)
    ax.text(11.45, i + 0.22, sub, color=MUTED, fontsize=10.5, ha="right", va="center", clip_on=False)
    pts = ([dep[0]] if dep else []) + [o[0] for o in obs]
    if len(pts) > 1 and col != SAT:
        ax.plot([min(pts), max(pts)], [i, i], color=col, lw=2, ls=(0, (2, 3)), alpha=0.7, zorder=2)
    if dep:
        ax.plot(dep[0], i, marker="o", ms=11, mfc=PANEL, mec=col, mew=2.5, zorder=3)
        put(dep[0], i, dep[1], dep[2], dep[3], col)
    for x, l, pos, ha in obs:
        ax.plot(x, i, marker="s" if col == SAT else "o", ms=11, mfc=col, mec=PANEL, mew=2, zorder=4)
        put(x, i, l, pos, ha, MUTED if col == SAT else CREAM)

# legend
lx, ly = 0.235, 0.115
items = [("Satellite pass", SAT, "s", True), ("RCAF", RCAF, "o", True), ("Helicopter air ambulance", HELI, "o", True),
         ("Fixed-wing air ambulance / charter", FIXED, "o", True), ("Departure", MUTED, "o", False)]
x = lx
for name, col, mk, filled in items:
    fig.lines.append(plt.Line2D([x], [ly], marker=mk, ms=10, mfc=col if filled else BG, mec=col, mew=2.2, transform=fig.transFigure, ls=""))
    fig.text(x + 0.012, ly, name, color=CREAM, fontsize=11.5, va="center")
    x += 0.025 + len(name) * 0.0068

fig.patches.append(Rectangle((0, 0), 1, 0.085, transform=fig.transFigure, facecolor=NAVY))
fig.patches.append(Rectangle((0, 0.085), 1, 0.004, transform=fig.transFigure, facecolor=GOLD_UI))
fig.text(0.03, 0.054, "Flight data: Flightradar24 screenshots captured by Prime Rogue; times converted to MT. Military helicopters such as the CH-146 Griffon", color=CREAM, fontsize=12)
fig.text(0.03, 0.03, "may not appear on public trackers. Flight purposes, destinations and patients carried have not been confirmed.", color=CREAM, fontsize=12)
fig.text(0.03, 0.008, "PRIME ROGUE", color=GOLD_UI, fontsize=12.5, fontweight="black")
fig.savefig(sys.argv[1], facecolor=BG, dpi=100)
im = Image.open(sys.argv[1]).convert("RGBA")
logo = Image.open("/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png").convert("RGBA").resize((84, 84), Image.LANCZOS)
im.alpha_composite(logo, (im.width - 84 - 40, im.height - 84 - 6))
im.convert("RGB").save(sys.argv[2], quality=90, optimize=True)
print(im.size)
