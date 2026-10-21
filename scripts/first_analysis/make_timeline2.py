import csv, math, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
from PIL import Image

F = "/usr/share/fonts/opentype/inter/"
for n in ["Inter-Medium.otf", "Inter-SemiBold.otf", "Inter-Bold.otf", "Inter-Black.otf", "InterDisplay-Black.otf", "InterDisplay-Bold.otf"]:
    fm.fontManager.addfont(F + n)
plt.rcParams["font.family"] = "Inter"

BG = "#1C140F"; PANEL = "#251A14"; GOLD_UI = "#D4AF68"; CREAM = "#EEE6D6"
MUTED = "#A99B84"; GRID = "#352820"; NAVY = "#1E3452"
LANDSAT = "#B98424"; VIIRS = "#4F8DD6"          # validated pair (dark, surface #1C140F)

rows = list(csv.DictReader(open(sys.argv[1])))
ref = (52.778, -110.92)
def xy(lat, lon):
    return ((lon - ref[1]) * 111.32 * math.cos(math.radians(ref[0])), (lat - ref[0]) * 110.57)
ls = [xy(float(r["latitude"]), float(r["longitude"])) for r in rows if r["sensor"].startswith("Landsat")]
vi = [xy(float(r["latitude"]), float(r["longitude"])) for r in rows if "VIIRS" in r["sensor"]]

W, H = 16, 11.6
fig = plt.figure(figsize=(W, H), dpi=100, facecolor=BG)
fig.patches.append(Rectangle((0, 0), 0.007, 1, transform=fig.transFigure, facecolor=GOLD_UI))
fig.text(0.03, 0.952, "OSINT ANALYSIS  ·  NASA FIRMS SATELLITE DATA  ·  CFB WAINWRIGHT  ·  OCT. 17, 2026", color=GOLD_UI, fontsize=14.5, fontweight="bold")
fig.text(0.03, 0.905, "Satellites detected fire on the range before 4 p.m.", color=CREAM, fontsize=32, fontweight="black")

# ---------- stat tiles ----------
tiles = [
    ("12:17 p.m.", "First detections", "Landsat 8 · 59 pixels · low confidence", LANDSAT),
    ("2:49 p.m.", "Fire detected", "NOAA-20 VIIRS · 8 pixels · nominal confidence", VIIRS),
    ("≈ 4 p.m.", "CAF: fire reported", "Canadian Armed Forces statement", CREAM),
]
tx0, tw, tg, ty, th = 0.03, 0.300, 0.017, 0.745, 0.115
for i, (big, head, sub, col) in enumerate(tiles):
    x = tx0 + i * (tw + tg)
    fig.patches.append(FancyBboxPatch((x, ty), tw, th, boxstyle="round,pad=0,rounding_size=0.008", transform=fig.transFigure, facecolor=PANEL, edgecolor="none"))
    fig.patches.append(Rectangle((x, ty), 0.0045, th, transform=fig.transFigure, facecolor=col))
    fig.text(x + 0.018, ty + th - 0.024, head.upper(), color=MUTED, fontsize=11.5, fontweight="bold", va="top")
    fig.text(x + 0.018, ty + 0.043, big, color=CREAM, fontsize=30, fontweight="black", va="baseline")
    fig.text(x + 0.018, ty + 0.017, sub, color=MUTED, fontsize=11, va="baseline")

# ---------- left: where ----------
fig.text(0.03, 0.695, "WHERE", color=GOLD_UI, fontsize=12, fontweight="bold")
fig.text(0.03, 0.668, "All 67 detections fall in one small area of the range", color=CREAM, fontsize=15, fontweight="bold")
axm = fig.add_axes([0.03, 0.175, 0.37, 0.475], facecolor=PANEL)
for x, y in vi:
    axm.add_patch(Rectangle((x - 0.24, y - 0.24), 0.48, 0.48, facecolor=(0.31,0.55,0.84,0.22), edgecolor=(0.31,0.55,0.84,0.7), linewidth=1, zorder=1))
axm.scatter([p[0] for p in vi], [p[1] for p in vi], s=95, marker="o", color=VIIRS, edgecolor=PANEL, linewidth=2, zorder=3)
axm.scatter([p[0] for p in ls], [p[1] for p in ls], s=20, marker="s", color=LANDSAT, edgecolor=PANEL, linewidth=0.6, zorder=4)
axm.set_xlim(-2.2, 2.2); axm.set_ylim(-1.75, 1.95); axm.set_aspect("equal", adjustable="box")
axm.set_xticks([]); axm.set_yticks([])
for s in axm.spines.values(): s.set_visible(False)
# direction arrow along fire-front lines
axm.add_patch(FancyArrowPatch((-1.35, -1.15), (0.85, 0.05), arrowstyle="-|>", mutation_scale=18, color=CREAM, lw=1.4, alpha=0.6, linestyle=(0, (4, 3)), zorder=2))
axm.text(-1.55, -1.42, "Landsat fire-front lines\n≈ 1.9 km, SW to NE", color=CREAM, fontsize=11, va="top")
axm.text(1.0, 1.42, "VIIRS pixel footprint\n(≈ 480 m)", color=MUTED, fontsize=10.5, ha="center", va="bottom")
axm.text(2.1, 1.85, "↗ Wainwright townsite ≈ 8 km", color=MUTED, fontsize=10.5, ha="right", va="top")
# scale bar + north arrow
axm.plot([-2.05, -1.05], [1.62, 1.62], color=CREAM, lw=3, solid_capstyle="butt")
axm.text(-1.55, 1.68, "1 km", color=CREAM, fontsize=10.5, ha="center", va="bottom")
axm.annotate("N", xy=(-1.95, 1.48), xytext=(-1.95, 1.12), color=CREAM, fontsize=11, fontweight="bold", ha="center", va="top",
             arrowprops=dict(arrowstyle="-|>", color=CREAM, lw=1.4))
# legend
ly = 0.135
fig.patches.append(Rectangle((0.03, ly + 0.004), 0.009, 0.013, transform=fig.transFigure, facecolor=LANDSAT))
fig.text(0.045, ly + 0.0105, "Landsat 8, 12:17 p.m.", color=CREAM, fontsize=11.5, va="center")
fig.lines.append(plt.Line2D([0.2185], [ly + 0.0105], transform=fig.transFigure, marker="o", color=VIIRS, ms=10, ls=""))
fig.text(0.227, ly + 0.0105, "NOAA-20 VIIRS, 2:49 p.m.", color=CREAM, fontsize=11.5, va="center")

# ---------- right: when ----------
fig.text(0.445, 0.695, "WHEN", color=GOLD_UI, fontsize=12, fontweight="bold")
fig.text(0.445, 0.668, "Every satellite pass over the base, Mountain Time", color=CREAM, fontsize=15, fontweight="bold")
axt = fig.add_axes([0.555, 0.175, 0.42, 0.475], facecolor=PANEL)
sats = [("Landsat 8", "30 m"), ("NOAA-21 VIIRS", "375 m"), ("Suomi-NPP VIIRS", "375 m"), ("NOAA-20 VIIRS", "375 m"), ("Aqua MODIS", "1 km"), ("Terra MODIS", "1 km")]
Y = {s: len(sats) - 1 - i for i, (s, _) in enumerate(sats)}
def h(hh, mm): return hh + mm / 60
for s, res in sats:
    axt.axhline(Y[s], color=GRID, lw=1, zorder=0)
axt.axvspan(h(15, 35), 22.6, color="#ffffff", alpha=0.03, zorder=0)
axt.text(h(19, 10), 5.55, "after ~3:30 p.m. only coarse 1 km MODIS passes", color=MUTED, fontsize=10, ha="center")
axt.axvline(16, color=CREAM, lw=2.2, zorder=2)
axt.text(16.1, -0.62, "CAF: fire reported ≈ 4 p.m.", color=CREAM, fontsize=11, fontweight="bold", va="center")
# gap brackets
def bracket(x0, x1, y, label, right_align=False):
    axt.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops=dict(arrowstyle="<->", color=GOLD_UI, lw=1.6, shrinkA=8, shrinkB=2))
    axt.text(x1 - 0.12 if right_align else (x0 + x1) / 2, y - 0.12, label, color=GOLD_UI, fontsize=11, fontweight="bold", ha="right" if right_align else "center", va="top")
bracket(h(12, 17), 16, 5.0 - 0.3, "≈ 3 h 43 min before")
bracket(h(14, 49), 16, 2.0 - 0.3, "≈ 70 min before", right_align=True)
axt.scatter([h(12, 17)], [Y["Landsat 8"]], s=300, marker="s", color=LANDSAT, edgecolor=PANEL, linewidth=2, zorder=4)
axt.text(h(12, 17) + 0.28, Y["Landsat 8"], "59 detections", color=CREAM, fontsize=11.5, fontweight="semibold", ha="left", va="center")
axt.scatter([h(14, 49)], [Y["NOAA-20 VIIRS"]], s=300, marker="o", color=VIIRS, edgecolor=PANEL, linewidth=2, zorder=4)
axt.text(h(14, 49) - 0.28, Y["NOAA-20 VIIRS"], "8 detections", color=CREAM, fontsize=11.5, fontweight="semibold", ha="right", va="center")
for s, t, side in [("NOAA-21 VIIRS", h(13, 52), "L"), ("Suomi-NPP VIIRS", h(14, 29), "L"), ("Aqua MODIS", h(16, 55), "R"), ("Terra MODIS", h(21, 29), "L")]:
    axt.scatter([t], [Y[s]], s=170, marker="o", facecolor=PANEL, edgecolor=MUTED, linewidth=1.8, zorder=4)
    axt.text(t + (0.28 if side == "R" else -0.28), Y[s], "none detected*", color=MUTED, fontsize=10.5, ha="left" if side == "R" else "right", va="center")
axt.set_yticks(list(Y.values()))
axt.set_yticklabels([f"{s}" for s, _ in sats], color=CREAM, fontsize=12)
for (s, res) in sats:
    axt.text(10.12, Y[s] - 0.27, res, color=MUTED, fontsize=9.5, ha="right", va="center", transform=axt.transData)
ticks = list(range(11, 23))
axt.set_xticks(ticks)
axt.set_xticklabels([("noon" if t == 12 else f"{t-12 if t>12 else t} {'p.m.' if t>12 else 'a.m.'}") if t % 2 == 0 else "" for t in ticks], color=MUTED, fontsize=11)
axt.grid(axis="x", color=GRID, lw=1); axt.set_axisbelow(True)
axt.set_xlim(10.3, 22.6); axt.set_ylim(-1.0, 5.9)
for s in axt.spines.values(): s.set_visible(False)
axt.tick_params(length=0)
fig.text(0.555, 0.14, "* Which passes covered the base is inferred from where each pass detected fires elsewhere.\n   A missed detection does not prove there was no fire.", color=MUTED, fontsize=10.5, va="top")

# ---------- footer ----------
fig.patches.append(Rectangle((0, 0), 1, 0.095, transform=fig.transFigure, facecolor=NAVY))
fig.patches.append(Rectangle((0, 0.095), 1, 0.004, transform=fig.transFigure, facecolor=GOLD_UI))
fig.text(0.03, 0.064, "Data: NASA FIRMS near-real-time files (Landsat, VIIRS, MODIS), current to 11:50 p.m. MT Oct. 17. Analysis: Prime Rogue Inc.", color=CREAM, fontsize=12.5)
fig.text(0.03, 0.037, "Detections show heat, not cause. They do not show whether this is the fire involved in the incident that caused casualties.", color=CREAM, fontsize=12.5)
fig.text(0.03, 0.01, "PRIME ROGUE", color=GOLD_UI, fontsize=13.5, fontweight="black")
fig.savefig(sys.argv[2], facecolor=BG, dpi=100)

im = Image.open(sys.argv[2]).convert("RGBA")
logo = Image.open("/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png").convert("RGBA").resize((96, 96), Image.LANCZOS)
im.alpha_composite(logo, (im.width - 96 - 40, im.height - 96 - 8))
im.convert("RGB").save(sys.argv[3], quality=90, optimize=True)
print(im.size)
