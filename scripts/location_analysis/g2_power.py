import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/vis")
from pr import *
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for n in ["Inter-Medium.otf", "Inter-Bold.otf", "Inter-Black.otf"]:
    fm.fontManager.addfont(F + n)
plt.rcParams["font.family"] = "Inter"
hx = lambda c: "#%02x%02x%02x" % c
OUT = "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/vis/"

t = pd.read_csv(REPO + "data/goes/fire_timeline.csv")
t = t[t.satellite == "GOES-18"].copy()
t["hm"] = t.scan_start_mdt.str[:5]
t = t[(t.scan_start_utc >= "2026-10-17T18:00") & (t.scan_start_utc <= "2026-10-17T23:00")]
t["x"] = t.hm.map(lambda s: int(s[:2]) + int(s[3:]) / 60)

w = pd.read_csv(REPO + "data/eccc/swob_observations.csv")
w = w[(w.tc_id == "CZWN") & (w.time_mdt.between("2026-10-17 13:00", "2026-10-17 17:00"))].copy()
w["x"] = w.time_mdt.str[11:13].astype(int)

fig = plt.figure(figsize=(16.92, 8.6), dpi=100, facecolor=hx(BG))
ax = fig.add_axes([0.075, 0.42, 0.9, 0.53], facecolor=hx(BG))
ax2 = fig.add_axes([0.075, 0.07, 0.9, 0.26], facecolor=hx(BG), sharex=ax)
for a in (ax, ax2):
    for s in a.spines.values(): s.set_visible(False)
    a.tick_params(colors=hx(MUTED), labelsize=13, length=0)
    a.grid(axis="y", color=hx(GRIDC), lw=1)
    a.axvspan(15 + 20 / 60, 15 + 35 / 60, color=hx(RED), alpha=0.16, lw=0)
    a.axvline(15 + 16 / 60, color=hx(CREAM), lw=1.5, ls=(0, (4, 3)))

# fire power bars
fp = t[t.fdc_power_mw > 0]
ax.bar(fp.x, fp.fdc_power_mw, width=0.1, color=hx(RED), zorder=3)
for _, r in fp.iterrows():
    off = {"15:10": (-0.06, "center"), "15:30": (0, "center"), "15:40": (-0.045, "left")}[r.hm]
    ax.text(r.x + off[0], r.fdc_power_mw + 30, f"{r.fdc_power_mw:,.0f} MW", ha=off[1], va="bottom", color=hx(CREAM), fontsize=16, fontweight="bold")
    ax.text(r.x, -95, r.hm.replace("15:", "3:"), ha="center", va="top", color=hx(CREAM), fontsize=12.5, fontweight="bold")
ax.set_ylim(0, 1600); ax.set_ylabel("NOAA fire power over the base (MW)", color=hx(MUTED), fontsize=13)
ax.text(15 + 16 / 60 - 0.03, 1560, "3:16 p.m.  82 km/h gust,\nwind swings northwest", ha="right", va="top", color=hx(CREAM), fontsize=14, fontweight="bold")
ax.text(15 + 36 / 60 + 0.03, 1560, "Likely overrun window,\nabout 3:20 to 3:35 p.m.", ha="left", va="top", color=hx(RED), fontsize=14, fontweight="bold")
ax.text(12.8, 1560, "GOES flagged no fire before 3:10 p.m.: its cloud mask\nshows the base covered all afternoon (cloud, smoke or dust).\nLandsat and NOAA-20 saw the fire burning at 12:17 and 2:49.", va="top", color=hx(MUTED), fontsize=13)
ax.text(15 + 30 / 60 + 0.1, 1215 * 0.55, "16 times the\npower of 20\nminutes earlier", va="center", color=hx(CREAM), fontsize=14)
# x ticks
ticks = [13, 14, 15, 16, 17]
ax2.set_xticks(ticks); ax2.set_xticklabels(["1 p.m.", "2 p.m.", "3 p.m.", "4 p.m.", "5 p.m."])
plt.setp(ax.get_xticklabels(), visible=False)
ax.set_xlim(12.75, 17.45)

# wind panel: direction arrows sized by speed, temp text
ax2.set_ylim(0, 100); ax2.set_yticks([0, 50, 100]); ax2.set_ylabel("Wind (km/h)", color=hx(MUTED), fontsize=13)
ax2.plot(w.x, w.avg_wnd_spd_10m_pst10mts, color=hx(BLUE), lw=3, marker="o", ms=7, zorder=3)
ax2.plot(w.x, w.max_wnd_spd_10m_pst1hr, color=hx(GOLD), lw=0, marker="^", ms=9, zorder=3)
import math as _m
for _, r in w.iterrows():
    dg = r.avg_wnd_dir_10m_pst10mts; to = _m.radians((dg + 180) % 360)
    dx, dy = 0.1 * _m.sin(to), 14 * _m.cos(to)
    ax2.annotate("", xy=(r.x + dx, 78 + dy), xytext=(r.x - dx, 78 - dy), arrowprops=dict(arrowstyle="-|>", color=hx(CREAM), lw=2.4, mutation_scale=20))
    ax2.text(r.x - 0.14, 78, f"{int(dg)}°\n{r.air_temp:.0f} °C", ha="right", va="center", color=hx(CREAM), fontsize=11.5)
ax2.text(15 + 16 / 60 + 0.04, 57, "gust 82 km/h, 3:16", color=hx(GOLD), fontsize=12, fontweight="bold")
ax2.plot([15 + 16 / 60], [82], marker="^", color=hx(GOLD), ms=11)
ax2.text(12.8, 8, "line: 10-minute average   ▲ peak gust in the hour", color=hx(MUTED), fontsize=11.5)
fig.savefig(OUT + "_chart.png", facecolor=hx(BG), dpi=100)

im, d = canvas(1800, 1220, "NOAA GOES-18  ·  ENVIRONMENT CANADA  ·  OCT. 17, 2026",
               "The fire surged minutes after the wind turned",
               "Fire power measured from orbit every 10 minutes, against the wind at CFB Wainwright's weather station.")
ch = Image.open(OUT + "_chart.png").convert("RGBA")
im.alpha_composite(ch, (40, 190))
d = ImageDraw.Draw(im)
d.text((1690, 1048), "Arrows: wind direction at the station", font=M(14), fill=MUTED, anchor="ra")
footer(im, ["Fire power: NOAA GOES-18 Fire Detection and Characterization (full disk, every 10 min), pixels over the base. Wind: ECCC CZWN hourly observations; gust time from the station record.",
            "The station is 14.7 km west-northwest of the fire, so the front likely reached the fire a few minutes after 3:16. Times MDT. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"])
im.convert("RGB").save(OUT + "cfb-wainwright-fire-power-wind.jpg", quality=91, optimize=True)
print(im.size)
