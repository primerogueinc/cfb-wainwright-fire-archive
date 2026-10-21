import csv, math, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D
from PIL import Image

F = "/usr/share/fonts/opentype/inter/"
for n in ["Inter-Medium.otf", "Inter-SemiBold.otf", "Inter-Bold.otf", "Inter-Black.otf", "InterDisplay-Black.otf", "InterDisplay-Bold.otf"]:
    fm.fontManager.addfont(F + n)
plt.rcParams["font.family"] = "Inter"

BG = "#1C140F"; PANEL = "#271C15"; GOLD_UI = "#D4AF68"; CREAM = "#EEE6D6"
MUTED = "#B8AA92"; GRID = "#3A2C22"
LANDSAT = "#B98424"; VIIRS = "#4F8DD6"   # validated: dark mode, surface #1C140F

rows = list(csv.DictReader(open(sys.argv[1])))
ref = (52.778, -110.92)
def xy(lat, lon):
    return ((lon - ref[1]) * 111.32 * math.cos(math.radians(ref[0])), (lat - ref[0]) * 110.57)

fig = plt.figure(figsize=(16, 10.6), dpi=100, facecolor=BG)
fig.text(0.025, 0.955, "OSINT ANALYSIS  ·  NASA FIRMS SATELLITE DETECTIONS  ·  OCT. 17, 2026", color=GOLD_UI, fontsize=15, fontweight="bold")
fig.text(0.025, 0.905, "Satellites detected fire on the range before 4 p.m.", color=CREAM, fontsize=31, fontweight="black")

# ---------- left: where (map of detections, local km) ----------
axm = fig.add_axes([0.045, 0.26, 0.36, 0.57], facecolor=PANEL)
ls = [xy(float(r["latitude"]), float(r["longitude"])) for r in rows if r["sensor"].startswith("Landsat")]
vi = [xy(float(r["latitude"]), float(r["longitude"])) for r in rows if "VIIRS" in r["sensor"]]
for x, y in vi:  # VIIRS pixel footprint ~0.48 km
    axm.add_patch(plt.Rectangle((x - 0.24, y - 0.24), 0.48, 0.48, facecolor=VIIRS, alpha=0.16, edgecolor="none", zorder=1))
axm.scatter([p[0] for p in vi], [p[1] for p in vi], s=90, marker="o", color=VIIRS, edgecolor=PANEL, linewidth=2, zorder=3)
axm.scatter([p[0] for p in ls], [p[1] for p in ls], s=22, marker="s", color=LANDSAT, edgecolor=PANEL, linewidth=0.8, zorder=4)
axm.set_xlim(-2.4, 2.4); axm.set_ylim(-1.9, 2.3); axm.set_aspect("equal")
for s in axm.spines.values(): s.set_visible(False)
axm.tick_params(colors=MUTED, labelsize=11, length=0)
axm.set_xlabel("km east–west", color=MUTED, fontsize=12); axm.set_ylabel("km north–south", color=MUTED, fontsize=12)
axm.grid(color=GRID, linewidth=1); axm.set_axisbelow(True)
axm.set_title("Where: all 67 detections fall in one small area of the base", color=CREAM, fontsize=15, fontweight="bold", loc="left", pad=12)
axm.text(2.3, 2.18, "↗ Town of Wainwright\n≈ 8 km north-northeast", color=MUTED, fontsize=11, ha="right", va="top")
axm.text(-2.2, -1.75, "Landsat line ≈ 1.9 km, WSW–ENE", color=CREAM, fontsize=11.5)
leg = [Line2D([], [], marker="s", ls="", color=LANDSAT, ms=8, label="Landsat 8, 12:17 p.m. (59 pixels, low confidence)"),
       Line2D([], [], marker="o", ls="", color=VIIRS, ms=10, label="NOAA-20 VIIRS, 2:49 p.m. (8 pixels, nominal)")]
axm.legend(handles=leg, loc="upper left", frameon=False, fontsize=11, labelcolor=CREAM, bbox_to_anchor=(0, -0.11))

# ---------- right: when (pass timeline) ----------
axt = fig.add_axes([0.53, 0.26, 0.445, 0.57], facecolor=PANEL)
sats = ["Landsat 8", "NOAA-21 VIIRS", "Suomi-NPP VIIRS", "NOAA-20 VIIRS", "Aqua MODIS", "Terra MODIS"]
Y = {s: len(sats) - 1 - i for i, s in enumerate(sats)}
def h(hh, mm): return hh + mm / 60
det = [("Landsat 8", h(12, 17), LANDSAT, "s", "59 detections"),
       ("NOAA-20 VIIRS", h(14, 49), VIIRS, "o", "8 detections")]
nodet = [("NOAA-21 VIIRS", h(13, 52)), ("Suomi-NPP VIIRS", h(14, 29)), ("Aqua MODIS", h(16, 55)), ("Terra MODIS", h(21, 29))]
axt.axvspan(h(15, 35), h(21, 20), color="#ffffff", alpha=0.035, zorder=0)
axt.text(h(18, 50), 5.62, "after ~3:30 p.m.: only coarse MODIS passes", color=MUTED, fontsize=10.5, ha="center")
axt.axvline(16, color=CREAM, lw=2, zorder=2)
axt.text(16.08, -0.78, "CAF: fire reported\n≈ 4 p.m.", color=CREAM, fontsize=11.5, fontweight="bold", va="bottom")
for s, t, c, m, lab in det:
    axt.scatter([t], [Y[s]], s=260, marker=m, color=c, edgecolor=PANEL, linewidth=2, zorder=4)
    right = s == "Landsat 8"
    axt.text(t + (0.25 if right else -0.25), Y[s], lab, color=CREAM, fontsize=11.5, va="center", ha="left" if right else "right", fontweight="semibold")
for s, t in nodet:
    axt.scatter([t], [Y[s]], s=170, marker="o", facecolor="none", edgecolor=MUTED, linewidth=1.8, zorder=4)
    right = s == "Aqua MODIS"
    axt.text(t + (0.25 if right else -0.25), Y[s], "no detection*", color=MUTED, fontsize=10.5, va="center", ha="left" if right else "right")
axt.set_yticks(list(Y.values())); axt.set_yticklabels(list(Y.keys()), color=CREAM, fontsize=12)
ticks = list(range(11, 23, 2))
axt.set_xticks(ticks); axt.set_xticklabels([f"{t-12 if t>12 else t} {'p.m.' if t>=12 else 'a.m.'}" for t in ticks], color=MUTED, fontsize=11)
axt.set_xlim(10.4, 22.4); axt.set_ylim(-0.9, 5.9)
for s in axt.spines.values(): s.set_visible(False)
axt.tick_params(length=0)
axt.grid(axis="x", color=GRID, linewidth=1); axt.set_axisbelow(True)
axt.set_title("When: satellite passes, Mountain Time", color=CREAM, fontsize=15, fontweight="bold", loc="left", pad=12)
fig.text(0.53, 0.195, "* Pass coverage inferred from where each pass detected fires elsewhere.\n  Not detecting a fire does not prove there was none.", color=MUTED, fontsize=10.5, va="top")

# ---------- footer ----------
fig.patches.append(plt.Rectangle((0, 0), 1, 0.115, transform=fig.transFigure, facecolor="#1E3452", zorder=0))
fig.patches.append(plt.Rectangle((0, 0.115), 1, 0.004, transform=fig.transFigure, facecolor=GOLD_UI, zorder=0))
fig.text(0.025, 0.075, "Data: NASA FIRMS near-real-time files (Landsat, VIIRS, MODIS), current to 11:50 p.m. MT Oct. 17. Analysis: Prime Rogue Inc.", color=CREAM, fontsize=12.5)
fig.text(0.025, 0.045, "Detections show heat, not cause. The data does not show whether this is the fire involved in the incident that caused casualties.", color=CREAM, fontsize=12.5)
fig.text(0.025, 0.012, "PRIME ROGUE", color=GOLD_UI, fontsize=14, fontweight="black")
fig.patches.append(plt.Rectangle((0, 0), 0.007, 1, transform=fig.transFigure, facecolor=GOLD_UI, zorder=0))
fig.savefig(sys.argv[2], facecolor=BG, dpi=100)

im = Image.open(sys.argv[2]).convert("RGBA")
logo = Image.open("/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png").convert("RGBA").resize((104, 104), Image.LANCZOS)
im.alpha_composite(logo, (im.width - 104 - 40, im.height - 104 - 10))
im.convert("RGB").save(sys.argv[2].replace(".png", ".jpg"), quality=90, optimize=True)
print(im.size)
