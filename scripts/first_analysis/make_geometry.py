import csv, math, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch
from PIL import Image

F = "/usr/share/fonts/opentype/inter/"
for n in ["Inter-Medium.otf", "Inter-SemiBold.otf", "Inter-Bold.otf", "Inter-Black.otf", "InterDisplay-Black.otf", "InterDisplay-Bold.otf"]:
    fm.fontManager.addfont(F + n)
plt.rcParams["font.family"] = "Inter"
BG = "#1C140F"; PANEL = "#251A14"; GOLD = "#D4AF68"; CREAM = "#EEE6D6"; MUTED = "#A99B84"
GRID = "#352820"; NAVY = "#1E3452"; LANDSAT = "#B98424"; VIIRS = "#4F8DD6"; RED = "#C85C46"; GREEN = "#78AA6E"

rows = list(csv.DictReader(open(sys.argv[1])))
ref = (52.778, -110.919)
def xy(la, lo): return ((lo - ref[1]) * 111.32 * math.cos(math.radians(ref[0])), (la - ref[0]) * 110.57)
L = np.array([xy(float(r["latitude"]), float(r["longitude"])) for r in rows if "Landsat" in r["sensor"]])
V = np.array([xy(float(r["latitude"]), float(r["longitude"])) for r in rows if "VIIRS" in r["sensor"]])

fig = plt.figure(figsize=(16, 13), dpi=100, facecolor=BG)
fig.patches.append(Rectangle((0, 0), 0.007, 1, transform=fig.transFigure, facecolor=GOLD))
fig.text(0.04, 0.955, "STRUCTURED ANALYSIS  ·  CFB WAINWRIGHT  ·  OCT. 17, 2026  ·  MOUNTAIN TIME", color=GOLD, fontsize=15, fontweight="bold")
fig.text(0.04, 0.912, "A fire burning toward the northeast, until the wind turned", color=CREAM, fontsize=31, fontweight="black")
fig.text(0.04, 0.882, "NASA detections show a long, narrow fire aligned with the southwest wind. A northwest wind turns its long southeast side into the front.", color=MUTED, fontsize=13.5)

ax = fig.add_axes([0.06, 0.17, 0.60, 0.68], facecolor=PANEL)
ax.set_xlim(-3.2, 3.6); ax.set_ylim(-3.6, 3.0); ax.set_aspect("equal")
for s in ax.spines.values(): s.set_color(GRID)
ax.tick_params(colors=MUTED, labelsize=11)
ax.set_xticks(range(-3, 4)); ax.set_yticks(range(-3, 3))
ax.grid(color=GRID, lw=1)
ax.set_xlabel("km east of reference point (52.778° N, 110.919° W)", color=MUTED, fontsize=12)
ax.set_ylabel("km north", color=MUTED, fontsize=12)

# SE flank line: offset of fire envelope along perpendicular
allp = np.vstack([L, V]); c = allp.mean(0)
u, s, vt = np.linalg.svd(allp - c); axv = vt[0]; perp = vt[1]
if perp[1] > 0: perp = -perp  # point south-east-ish
if axv[1] < 0: axv = -axv
proj = (allp - c) @ axv; pp = (allp - c) @ perp
a0, a1 = proj.min() - 0.19, proj.max() + 0.19
edge = pp.max() + 0.45
p0 = c + axv * a0 + perp * edge; p1 = c + axv * a1 + perp * edge
# downwind 1 km band from SE flank toward SE (NW wind blows toward 135 deg)
d = np.array([math.sin(math.radians(135)), math.cos(math.radians(135))])
band = Polygon([p0, p1, p1 + d * 1.0, p0 + d * 1.0], closed=True, facecolor=RED, alpha=0.18, edgecolor=RED, lw=1.5, ls="--")
ax.add_patch(band)
ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=RED, lw=4, solid_capstyle="round")

for (x, y) in V:
    ax.add_patch(Rectangle((x - 0.1875, y - 0.1875), 0.375, 0.375, facecolor=VIIRS, alpha=0.35, edgecolor=VIIRS, lw=1.5))
ax.scatter(L[:, 0], L[:, 1], s=14, marker="s", color=LANDSAT, zorder=5)

def arrow(x, y, deg_to, col, lab, lx, ly, ha="left"):
    dx, dy = math.sin(math.radians(deg_to)) * 0.9, math.cos(math.radians(deg_to)) * 0.9
    ax.add_patch(FancyArrowPatch((x, y), (x + dx, y + dy), arrowstyle="-|>", mutation_scale=28, color=col, lw=3))
    ax.text(lx, ly, lab, color=col, fontsize=13, fontweight="bold", ha=ha, va="center")
arrow(-2.9, -2.6, 35, GREEN, "Before 4 p.m.: wind from SSW–SW\npushes the fire northeast", -2.9, -3.15)
arrow(-2.5, 2.6, 135, RED, "≈4 p.m.: wind swings to the NW,\ngusts 69 km/h", -1.4, 2.65)

mid = (p0 + p1) / 2
ax.annotate("Long southeast side becomes\nthe front after the shift", xy=(mid[0], mid[1]), xytext=(1.25, -1.15),
            color=RED, fontsize=13, fontweight="bold", arrowprops=dict(arrowstyle="-", color=RED, lw=1.5))
bc = mid + d * 0.75
ax.text(bc[0] + 0.15, bc[1] - 0.55, "Zone within 1 km downwind\n(where troops 1 km away would be,\nIF this was the fire that reached them)", color=CREAM, fontsize=11.5, ha="left")
ax.plot([0, 1], [-3.35, -3.35], color=CREAM, lw=3); ax.text(0.5, -3.25, "1 km", color=CREAM, fontsize=12, ha="center", fontweight="bold")

# right column
def block(y, head, col, body):
    fig.text(0.70, y, head, color=col, fontsize=15, fontweight="black")
    fig.text(0.70, y - 0.012, body, color=CREAM, fontsize=12.5, va="top", linespacing=1.45)
block(0.84, "■  12:17 p.m.  Landsat 8", LANDSAT, "59 low-confidence detections in a narrow\nband about 1.9 km long, aligned\nsouthwest–northeast (bearing ~55°).")
block(0.71, "■  2:49 p.m.  NOAA-20 VIIRS", VIIRS, "8 detections, 375 m pixels, over an area\nabout 2.8 x 1 km, centred ~0.3 km\nnortheast of the earlier band. Low\nintensity: 6–12 MW per pixel.")
block(0.565, "What it suggests", GOLD, "A fire burning with the wind, toward\nthe northeast, for at least 2.5 hours.\nIts long sides faced northwest and\nsoutheast. A northwest wind turns the\nentire southeast side, about 3 km\nlong, into the front.")
block(0.36, "What it can't show", MUTED, "Where C Company was. Whether this\nis the fire that reached them. Flame\nposition at 4 p.m. Cause.")

fy = 0.0; fh = 0.115
fig.patches.append(Rectangle((0, fy), 1, fh, transform=fig.transFigure, facecolor=NAVY))
fig.patches.append(Rectangle((0, fh), 1, 0.004, transform=fig.transFigure, facecolor=GOLD))
fig.text(0.04, 0.083, "Prime Rogue assessment, not confirmed by DND. Positions from NASA FIRMS (VIIRS pixels drawn at nominal 375 m; Landsat 30 m). Wind: Environment Canada, CFB Wainwright", color=CREAM, fontsize=12)
fig.text(0.04, 0.060, "station. The shaded zone is illustrative geometry from Maj.-Gen. Rutland's account (fire ~1 km away when the wind shifted), not a known troop location.", color=CREAM, fontsize=12)
fig.text(0.04, 0.025, "PRIME ROGUE", color=GOLD, fontsize=16, fontweight="black")
out = sys.argv[2]
fig.savefig(out + ".png", facecolor=BG)
im = Image.open(out + ".png").convert("RGBA")
logo = Image.open("/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png").convert("RGBA").resize((96, 96), Image.LANCZOS)
im.alpha_composite(logo, (im.width - 96 - 50, im.height - 96 - 9))
im.convert("RGB").save(out, quality=90, optimize=True)
print(im.size)
