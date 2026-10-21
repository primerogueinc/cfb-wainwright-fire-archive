import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle
from PIL import Image

F = "/usr/share/fonts/opentype/inter/"
for n in ["Inter-Medium.otf", "Inter-SemiBold.otf", "Inter-Bold.otf", "Inter-Black.otf", "InterDisplay-Black.otf"]:
    fm.fontManager.addfont(F + n)
plt.rcParams["font.family"] = "Inter"
BG = "#1C140F"; PANEL = "#251A14"; GOLD_UI = "#D4AF68"; CREAM = "#EEE6D6"
MUTED = "#A99B84"; GRID = "#352820"; NAVY = "#1E3452"
LANDSAT = "#B98424"; VIIRS = "#4F8DD6"

def t(h, m): return h + m / 60.0
# (time, label, detections, kind)  kind: hit / clear (covered, no fire) / uncertain (cloud or coverage unconfirmed)
passes = [
    (t(12, 17), "Landsat 8", 59, "hit_l"),
    (t(13, 52), "NOAA-21", 0, "uncertain"),
    (t(14, 29), "Suomi-NPP", 0, "uncertain"),
    (t(14, 49), "NOAA-20", 8, "hit_v"),
    (t(16, 55), "Aqua MODIS", 0, "uncertain"),
    (t(21, 30), "Terra MODIS", 0, "uncertain"),
    (t(26, 42), "Suomi-NPP", 0, "clear"),
    (t(27, 2), "NOAA-20", 0, "clear"),
    (t(27, 46), "NOAA-21", 0, "clear"),
    (t(28, 22), "Suomi-NPP", 0, "clear"),
]

fig = plt.figure(figsize=(16, 10.4), dpi=100, facecolor=BG)
fig.patches.append(Rectangle((0, 0), 0.007, 1, transform=fig.transFigure, facecolor=GOLD_UI))
fig.text(0.03, 0.948, "NASA FIRMS  ·  EVERY SATELLITE PASS  ·  CFB WAINWRIGHT  ·  OCT. 17–18, 2026", color=GOLD_UI, fontsize=14.5, fontweight="bold")
fig.text(0.03, 0.895, "16 hours of satellite passes. Every detection came before 4 p.m.", color=CREAM, fontsize=31, fontweight="black")
fig.text(0.03, 0.858, "Fire detections at the base per satellite pass, Mountain Time. Bars show detections; markers at zero show passes that recorded none.",
         color=MUTED, fontsize=13.5)

ax = fig.add_axes([0.06, 0.25, 0.91, 0.55], facecolor=PANEL)
for s in ax.spines.values(): s.set_visible(False)
ax.set_xlim(11.4, 29.4); ax.set_ylim(-9, 78)
ax.tick_params(length=0, colors=MUTED, labelsize=11.5)
ax.set_xticks([12, 14, 16, 18, 20, 22, 24, 26, 28])
ax.set_xticklabels(["noon", "2 p.m.", "4 p.m.", "6 p.m.", "8 p.m.", "10 p.m.", "midnight", "2 a.m.", "4 a.m."], color=MUTED)
ax.set_yticks([0, 20, 40, 60]); ax.grid(axis="y", color=GRID, lw=1); ax.set_axisbelow(True)
ax.text(-0.045, 1.0, "Detections", transform=ax.transAxes, color=CREAM, fontsize=12.5, fontweight="bold", va="bottom")

# gap: no VIIRS/Landsat coverage ~3:30 p.m. to night
ax.axvspan(t(15, 40), 25.9, color="#000000", alpha=0.22, zorder=0)
ax.text(20.7, 66, "No VIIRS or Landsat coverage\n(explosion, spread and response not captured)", color=MUTED, fontsize=11, ha="center", va="center")
# reference lines
ax.axvline(16, color=CREAM, lw=2.3, zorder=1)
ax.text(16.1, 75, "≈ 4 p.m.  DND: fire “ignited”", color=CREAM, fontsize=11.5, fontweight="bold", va="top")
ax.axvline(t(22, 47), color=MUTED, lw=1.3, ls=(0, (4, 3)), zorder=1)
ax.text(t(22, 47) + 0.1, 56, "10:47 p.m.\nMD: fire\n“being held”", color=MUTED, fontsize=10.5, va="top")

for x, lab, n, k in passes:
    if k.startswith("hit"):
        col = LANDSAT if k == "hit_l" else VIIRS
        ax.bar(x, n, width=0.42, color=col, zorder=3)
        ax.text(x, n + 2, f"{n}", color=CREAM, fontsize=15, fontweight="black", ha="center")
        ax.text(x, -4.2, lab, color=col, fontsize=10.5, fontweight="bold", ha="center", va="center")
    elif k == "clear":
        ax.plot(x, 0, marker="o", ms=12, mfc=VIIRS, mec=PANEL, mew=2, zorder=4)
        ax.text(x, -4.2 if x in (t(26, 42), t(27, 46)) else -7.4, lab, color=CREAM, fontsize=10, ha="center", va="center")
    else:
        ax.plot(x, 0, marker="o", ms=12, mfc=PANEL, mec=MUTED, mew=2, zorder=4)
        ax.text(x, -4.2 if lab not in ("Suomi-NPP",) else -7.2, lab, color=MUTED, fontsize=10, ha="center", va="center")
for xx, lb, yy in [(t(15, 15), "Aqua", -7.4), (t(15, 33), "NOAA-21", 3.6)]:
    ax.plot(xx, 0, marker="o", ms=12, mfc=PANEL, mec=MUTED, mew=2, zorder=4)
    ax.text(xx, yy, lb, color=MUTED, fontsize=10, ha="center", va="center")
ax.text(t(12, 17) + 0.32, 50, "12:17 p.m.\nlow confidence", color=LANDSAT, fontsize=10.5, ha="left", va="center")
ax.text(t(14, 49) + 0.28, 14, "2:49 p.m.\nnominal", color=VIIRS, fontsize=10.5, ha="left", va="center")
ax.text(t(27, 30), 12, "4 overnight passes,\nbase covered, clear skies:\nno fire detected", color=CREAM, fontsize=11, ha="center", va="center", fontweight="semibold")

# legend
ly = 0.165; x = 0.06
items = [("Landsat 8 detections (30 m)", LANDSAT, "s", True), ("VIIRS detections (375 m)", VIIRS, "s", True),
         ("Pass covered base, no fire", VIIRS, "o", True), ("No fire; cloud or coverage unconfirmed", MUTED, "o", False)]
for name, col, mk, filled in items:
    fig.lines.append(plt.Line2D([x], [ly], marker=mk, ms=11, mfc=col if filled else BG, mec=col, mew=2.2, transform=fig.transFigure, ls=""))
    fig.text(x + 0.012, ly, name, color=CREAM, fontsize=11.5, va="center")
    x += 0.03 + len(name) * 0.0067

fig.patches.append(Rectangle((0, 0), 1, 0.11, transform=fig.transFigure, facecolor=NAVY))
fig.patches.append(Rectangle((0, 0.11), 1, 0.004, transform=fig.transFigure, facecolor=GOLD_UI))
fig.text(0.03, 0.077, "Data: NASA FIRMS, downloads 11:50 p.m.–4:27 a.m. MT. Revised Oct. 19: passes at 3:15 and 3:33 p.m. added. Times approximate.", color=CREAM, fontsize=12)
fig.text(0.03, 0.05, "Detections show heat, not cause. MODIS passes are 1 km resolution. NOAA GOES geostationary data not included. Graphic: Prime Rogue Inc.", color=CREAM, fontsize=12)
fig.text(0.03, 0.018, "PRIME ROGUE", color=GOLD_UI, fontsize=13, fontweight="black")
fig.savefig(sys.argv[1], facecolor=BG, dpi=100)
im = Image.open(sys.argv[1]).convert("RGBA")
logo = Image.open("/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png").convert("RGBA").resize((88, 88), Image.LANCZOS)
im.alpha_composite(logo, (im.width - 88 - 40, im.height - 88 - 12))
im.convert("RGB").save(sys.argv[2], quality=90, optimize=True)
print(im.size)
