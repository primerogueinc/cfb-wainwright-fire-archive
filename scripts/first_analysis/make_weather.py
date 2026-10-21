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
SUST = "#4F8DD6"; GUST = "#B98424"   # validated pair (dark, surface #1C140F)

# ECCC, CFB Wainwright station, MDT. x = hours after midnight Oct 17
x = list(range(10, 26))
dirn = ["SSW","SSW","SSW","SW","SW","SW","NW","NW","NW","NW","W","W","WSW","W","W","WNW"]
spd  = [12,21,12,14,31,32,51,35,29,28,22,18,17,22,24,32]
gst  = [None,None,None,None,46,45,69,61,47,41,31,None,None,35,34,44]
temp = [9.7,13.9,15.2,20.2,22.8,23.3,12.9,12.0,11.1,10.3,8.5,7.8,6.6,7.1,6.9,7.6]
rh   = [44,33,32,23,16,17,43,42,44,44,53,58,59,55,54,55]

fig = plt.figure(figsize=(16, 12.2), dpi=100, facecolor=BG)
fig.patches.append(Rectangle((0, 0), 0.007, 1, transform=fig.transFigure, facecolor=GOLD_UI))
fig.text(0.03, 0.955, "WEATHER  ·  ENVIRONMENT CANADA STATION, CFB WAINWRIGHT  ·  OCT. 17–18, 2026", color=GOLD_UI, fontsize=14.5, fontweight="bold")
fig.text(0.03, 0.91, "Hot, dry and windy, then a sudden wind shift at 4 p.m.", color=CREAM, fontsize=32, fontweight="black")
fig.text(0.03, 0.878, "Hourly observations, Mountain Time. The wind swung from southwest to northwest and the temperature fell 10°C in an hour, consistent with a cold front.", color=MUTED, fontsize=13.5)

L, Wd = 0.085, 0.885
axw = fig.add_axes([L, 0.53, Wd, 0.29], facecolor=PANEL)
axt = fig.add_axes([L, 0.335, Wd, 0.16], facecolor=PANEL, sharex=axw)
axh = fig.add_axes([L, 0.14, Wd, 0.16], facecolor=PANEL, sharex=axw)

events = [(12 + 17/60, "Landsat\n12:17 p.m."), (14 + 49/60, "NOAA-20\n2:49 p.m."), (16, "DND: fire ignited ≈ 4 p.m.")]
for ax in (axw, axt, axh):
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0, colors=MUTED, labelsize=11)
    ax.grid(axis="y", color=GRID, lw=1); ax.set_axisbelow(True)
    ax.axvspan(10, 16, color="#E0A93B", alpha=0.045, zorder=0)
    for ex, _ in events:
        ax.axvline(ex, color=CREAM if ex == 16 else MUTED, lw=2 if ex == 16 else 1.2, ls="-" if ex == 16 else (0, (4, 3)), zorder=1)

# wind panel
gx = [a for a, g in zip(x, gst) if g is not None]; gy = [g for g in gst if g is not None]
axw.plot(x, spd, color=SUST, lw=2.4, marker="o", ms=7, mec=PANEL, mew=2, zorder=3)
axw.plot(gx, gy, color=GUST, lw=0, marker="D", ms=8, mec=PANEL, mew=2, zorder=4)
for a, g, sv in zip(x, gst, spd):
    if g is not None: axw.plot([a, a], [sv, g], color=GUST, lw=1.4, alpha=0.6, zorder=2)
for a, d, sv, g in zip(x, dirn, spd, gst):
    top = (g if g is not None else sv)
    if a == 16:
        axw.text(a - 0.12, top + 1, d, color=CREAM, fontsize=10.5, fontweight="bold", ha="right", va="center")
    else:
        axw.text(a, top + 4.5, d, color=CREAM, fontsize=10.5, fontweight="bold", ha="center")
axw.set_ylim(0, 84); axw.set_yticks([0, 20, 40, 60, 80])
axw.text(-0.065, 1.0, "Wind (km/h)", transform=axw.transAxes, color=CREAM, fontsize=13, fontweight="bold", va="bottom")
axw.text(16.15, 74.5, "Peak gust 69 km/h", color=GOLD_UI, fontsize=11.5, fontweight="bold")
axw.text(10.15, 76, "Midday: southwest winds", color=MUTED, fontsize=11)
for ex, lab in events:
    axw.text(ex + 0.08, 84, lab, color=CREAM if ex == 16 else MUTED, fontsize=10.5, fontweight="bold" if ex == 16 else "medium", va="top")
# legend
axw.plot([], [], color=SUST, marker="o", lw=2.4, label="Sustained wind")
axw.plot([], [], color=GUST, marker="D", lw=0, label="Gust")
leg = axw.legend(loc="upper right", frameon=False, fontsize=11.5, labelcolor=CREAM, ncol=2, bbox_to_anchor=(1.0, 1.13))

# temperature
axt.plot(x, temp, color=CREAM, lw=2.4, marker="o", ms=6.5, mec=PANEL, mew=2, zorder=3)
axt.set_ylim(0, 28); axt.set_yticks([0, 10, 20])
axt.text(-0.065, 1.0, "Temperature (°C)", transform=axt.transAxes, color=CREAM, fontsize=13, fontweight="bold", va="bottom")
axt.annotate("23.3°C at 3 p.m.", xy=(15, 23.3), xytext=(12.6, 25.3), color=CREAM, fontsize=11, fontweight="bold",
             arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
axt.annotate("12.9°C at 4 p.m.", xy=(16, 12.9), xytext=(16.4, 20.5), color=CREAM, fontsize=11, fontweight="bold",
             arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))

# humidity
axh.plot(x, rh, color=CREAM, lw=2.4, marker="o", ms=6.5, mec=PANEL, mew=2, zorder=3)
axh.set_ylim(0, 70); axh.set_yticks([0, 30, 60])
axh.text(-0.065, 1.0, "Relative humidity (%)", transform=axh.transAxes, color=CREAM, fontsize=13, fontweight="bold", va="bottom")
axh.annotate("16% at 2 p.m.", xy=(14, 16), xytext=(11.0, 6), color=CREAM, fontsize=11, fontweight="bold",
             arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))

labels = ["10 a.m.", "", "noon", "", "2 p.m.", "", "4 p.m.", "", "6 p.m.", "", "8 p.m.", "", "10 p.m.", "", "midnight", ""]
axh.set_xticks(x); axh.set_xticklabels(labels, color=MUTED, fontsize=11)
plt.setp(axw.get_xticklabels(), visible=False); plt.setp(axt.get_xticklabels(), visible=False)
axw.set_xlim(9.6, 25.4)
fig.text(L, 0.105, "Shaded: before the reported 4 p.m. ignition. Dashed lines: satellite fire detections. Gusts are reported only when they exceed thresholds.", color=MUTED, fontsize=11)

fig.patches.append(Rectangle((0, 0), 1, 0.085, transform=fig.transFigure, facecolor=NAVY))
fig.patches.append(Rectangle((0, 0.085), 1, 0.004, transform=fig.transFigure, facecolor=GOLD_UI))
fig.text(0.03, 0.054, "Data: Environment and Climate Change Canada, CFB Wainwright station, hourly observations (MDT). Graphic: Prime Rogue Inc.", color=CREAM, fontsize=12.5)
fig.text(0.03, 0.026, "Weather data provides context for fire behaviour. It does not show what caused the fire.", color=CREAM, fontsize=12.5)
fig.text(0.03, 0.007, "PRIME ROGUE", color=GOLD_UI, fontsize=12.5, fontweight="black")
fig.savefig(sys.argv[1], facecolor=BG, dpi=100)
im = Image.open(sys.argv[1]).convert("RGBA")
logo = Image.open("/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png").convert("RGBA").resize((88, 88), Image.LANCZOS)
im.alpha_composite(logo, (im.width - 88 - 40, im.height - 88 - 8))
im.convert("RGB").save(sys.argv[2], quality=90, optimize=True)
print(im.size)
