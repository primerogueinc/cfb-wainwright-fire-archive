"""Graphic: September vs October fire days and fire danger at CFB Wainwright, 2012-2026. Usage: python3 scripts/maps/g37_yoy.py"""
import sys, json; sys.path.insert(0, "scripts/maps")
from v4fig import *
import pandas as pd, numpy as np
D = pd.read_csv(REPO + "data/fire_compare/yoy/yoy_by_year_month.csv"); S = json.load(open(REPO + "data/fire_compare/yoy/summary.json"))
yrs = list(range(2012, 2027)); x = np.arange(len(yrs)); SEP, OCT = (214, 140, 60), (79, 141, 214)
def get(m, c): return D[D.month == m].set_index("year").reindex(yrs)[c].values
f, ax = fig(1480, 430)
ax.bar(x - 0.2, get("Sep", "snpp_fire_days"), 0.38, color=hx(SEP), label="September"); ax.bar(x + 0.2, get("Oct", "snpp_fire_days"), 0.38, color=hx(OCT), label="October")
ax.bar(x - 0.2, get("Sep", "snpp_fire_days_pda2"), 0.38, color="none", edgecolor=hx(CREAM), hatch="///", lw=0); ax.bar(x + 0.2, get("Oct", "snpp_fire_days_pda2"), 0.38, color="none", edgecolor=hx(CREAM), hatch="///", lw=0)
ax.set_xticks(x); ax.set_xticklabels(yrs, color=hx(CREAM), fontsize=13); ax.set_ylabel("Days with satellite fire detections", color=hx(CREAM), fontsize=13)
ax.grid(axis="y", color=hx(GRIDC)); ax.set_axisbelow(True); ax.set_xlim(-0.6, len(yrs) - 0.4)
ax.legend(frameon=False, labelcolor=hx(CREAM), fontsize=13, loc="upper left"); f.subplots_adjust(0.05, 0.1, 0.995, 0.97); top = to_img(f)
f, ax = fig(1480, 330)
ax.plot(x, get("Sep", "fwi_mean"), "o-", color=hx(SEP), lw=2.5, ms=7); ax.plot(x, get("Oct", "fwi_mean"), "o-", color=hx(OCT), lw=2.5, ms=7)
ax.axhline(18.5, color=hx(MUTED), ls="--", lw=1); ax.text(0.2, 19.3, "Very High", color=hx(MUTED), fontsize=12, ha="left")
ax.axhline(29.5, color=hx(RED), ls="--", lw=1); ax.text(0.2, 30.5, "Extreme", color=hx(RED), fontsize=12, ha="left")
ax.plot(len(yrs) - 1, 30.8, "*", ms=20, color=hx(YEL)); ax.annotate("Oct. 17, 2026: 30.8", (len(yrs) - 1, 30.8), (-170, 6), textcoords="offset points", color=hx(YEL), fontsize=13, weight="bold")
ax.set_xticks(x); ax.set_xticklabels(yrs, color=hx(CREAM), fontsize=13); ax.set_ylabel("Mean daily FWI", color=hx(CREAM), fontsize=13); ax.set_ylim(0, 42)
ax.grid(axis="y", color=hx(GRIDC)); ax.set_xlim(-0.6, len(yrs) - 0.4); f.subplots_adjust(0.05, 0.12, 0.995, 0.97); bot = to_img(f)
W, H = 1600, 1275
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · SEPTEMBER VS OCTOBER, 2012-2026",
               "Fire on the range is routine in September and October",
               f"Days with a NASA VIIRS (S-NPP) fire detection in the central training area, 2012-2025: September {S['snpp_fire_days']['Sep']}, October {S['snpp_fire_days']['Oct']}. "
               f"Inside Permanent Danger Area 2: {S['snpp_fire_days_pda2']['Sep']} and {S['snpp_fire_days_pda2']['Oct']}.\n"
               f"Fire danger at the base station: September averaged FWI {S['fwi_mean']['Sep']}, October {S['fwi_mean']['Oct']}. Oct. 17's 30.8 was matched or beaten on {S['oct17_2026_fwi_rank']['share_of_october_days_2012_2025_at_or_above']*100:.0f}% of October days since 2012.")
d.text((54, 205), "Days with fire detected (hatched: inside Permanent Danger Area 2)", font=B(20), fill=GOLD); im.paste(top, (54, 238))
d.text((54, 690), "Fire danger: mean daily Fire Weather Index, CFB Wainwright station", font=B(20), fill=GOLD); im.paste(bot, (54, 722))
y = 1062
for l in ("One satellite (S-NPP) for every year so years compare fairly; it passes about twice a day and misses small or brief fires. 2026 (all satellites): Sept. 16, 18, 20, 21; Oct. 14, 17, 18. Oct. 2026 FWI to Oct. 24.",
          "Detections show heat, not cause. FWI months with gaps: Oct. 2013 (2 days), Oct. 2016 (6), Oct. 2017 (17). NBAC: 1,500-10,400 ha a year burned on DND land here (2021: none)."):
    d.text((54, y), l, font=M(15), fill=MUTED); y += 26
footer(im, ["Data: NASA FIRMS (VIIRS S-NPP standard and near-real-time); NRCan CWFIS station FWI (301S001); NRCan National Burned Area Composite 2012-2025.", "PDA 2 outline: OpenStreetMap contributors (ODbL), not official.", SRC], fh=135)
im.convert("RGB").save(REPO + "data/graphics_published/oct25_oct14_fire/cfb-wainwright-sept-vs-oct-yoy.jpg", quality=92); print("ok")
