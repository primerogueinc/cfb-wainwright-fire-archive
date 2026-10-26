"""Graphic: long-term fire record on CFB Wainwright's central training area, 2012-2026: satellite fire days by month and year
(VIIRS S-NPP, the one sensor covering every year), and burned area on DND land per year (NRCan NBAC). Usage: python3 scripts/maps/g38_long_term.py"""
import sys; sys.path.insert(0, "scripts/maps")
from v4fig import *
import pandas as pd, numpy as np, geopandas as gpd
F = pd.read_csv(REPO + "data/firms/history_2012-2026/all_detections_merged.csv"); F = F[F.source.str.startswith("VIIRS_SNPP")]
F["t"] = pd.to_datetime(F.acq_date + " " + F.acq_time.astype(str).str.zfill(4), format="%Y-%m-%d %H%M") - pd.Timedelta(hours=6)
F["d"] = F.t.dt.date; F["y"] = F.t.dt.year; F["m"] = F.t.dt.month
o = gpd.read_file(REPO + "data/infrastructure/osm_infrastructure_ODbL.geojson"); pda2 = o[o.name == "Permanent Danger Area 2"].geometry.iloc[0]
F["pda2"] = gpd.GeoSeries(gpd.points_from_xy(F.longitude, F.latitude), crs=4326).within(pda2).values
yrs = list(range(2012, 2027)); MD = np.zeros((len(yrs), 12), int)
for (y, m), g in F.groupby(["y", "m"]): MD[yrs.index(y), m - 1] = g.d.nunique()
nb = gpd.read_file(REPO + "data/nbac/nbac_wainwright_2012-2025.geojson"); nb = nb[nb.ADMIN_NAME == "DND"].groupby("YEAR").POLY_HA.sum()
pd.DataFrame(MD, index=yrs, columns=range(1, 13)).to_csv(REPO + "data/fire_compare/yoy/snpp_fire_days_by_year_month.csv")
# heatmap
f, ax = fig(1100, 620); cm = matplotlib.colors.LinearSegmentedColormap.from_list("f", [hx(BG), hx((120, 60, 30)), hx((214, 140, 60)), hx(YEL)])
ax.imshow(MD, cmap=cm, vmin=0, vmax=max(10, MD.max()), aspect="auto")
for i in range(len(yrs)):
    for j in range(12):
        if MD[i, j]: ax.text(j, i, MD[i, j], ha="center", va="center", color=hx(INK) if MD[i, j] >= 5 else hx(CREAM), fontsize=12, weight="bold")
ax.set_xticks(range(12)); ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], color=hx(CREAM), fontsize=13)
ax.set_yticks(range(len(yrs))); ax.set_yticklabels(yrs, color=hx(CREAM), fontsize=12)
for j in (8, 9): ax.add_patch(matplotlib.patches.Rectangle((j - 0.5, -0.5), 1, len(yrs), fill=False, ec=hx(GOLD), lw=2))
ax.add_patch(matplotlib.patches.Rectangle((9 - 0.5, len(yrs) - 1.5), 1, 1, fill=False, ec=hx(RED), lw=3))
f.subplots_adjust(0.07, 0.06, 0.99, 0.99); HM = to_img(f)
# NBAC bars
f, ax = fig(420, 620); ys = list(range(2012, 2026)); v = [nb.get(float(y), 0) for y in ys]
ax.barh(range(len(ys)), v, color=hx((214, 140, 60))); ax.set_yticks(range(len(ys))); ax.set_yticklabels(ys, color=hx(CREAM), fontsize=12); ax.invert_yaxis()
for i, x in enumerate(v): ax.text(x + 150, i, f"{x:,.0f}" if x else "none mapped", va="center", color=hx(CREAM), fontsize=11)
ax.set_xlabel("Hectares burned on DND land", color=hx(CREAM), fontsize=12); ax.set_xlim(0, 13500); ax.grid(axis="x", color=hx(GRIDC)); ax.set_axisbelow(True)
f.subplots_adjust(0.17, 0.1, 0.97, 0.99); NB = to_img(f)
tot = int(MD[:-1].sum()); share = {mn: int(MD[:-1, k].sum()) for k, mn in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
top = sorted(share.items(), key=lambda kv: -kv[1])[:3]
W, H = 1600, 1080
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · THE LONG-TERM RECORD, 2012-2026",
               "Fire on the training area every year; spring and fall are the peaks",
               f"Days with a NASA VIIRS (S-NPP) fire detection in the central training area, by month, 2012-2025: {tot} fire days; busiest months "
               + ", ".join(f"{m} ({n})" for m, n in top) + ".\nGold boxes: September and October. Red box: October 2026 (Oct. 18 only; S-NPP did not detect the Oct. 14 or Oct. 17 fires). Right: NRCan's yearly burned-area maps.")
d.text((54, 205), "Fire days by month (VIIRS S-NPP)", font=B(20), fill=GOLD); im.paste(HM, (54, 236))
d.text((54 + 1100 + 30, 205), "Area burned on DND land (NBAC)", font=B(20), fill=GOLD); im.paste(NB, (54 + 1100 + 20, 236))
y = 236 + 620 + 16
for l in ("One satellite, S-NPP, passes about twice a day; small or short fires are missed (it saw neither the Oct. 14 nor the Oct. 17 fire). Detections show heat, not cause; many are",
          "likely training-related or prescribed burns. NBAC maps a year's burns as one composite (no month); 2021 has no DND polygon. 2026 NBAC not yet published."):
    d.text((54, y), l, font=M(15), fill=MUTED); y += 25
footer(im, ["Data: NASA FIRMS, VIIRS S-NPP (standard processing to June 2026, near-real-time after), box 52.67-52.88 N, 110.75-111.10 W;",
            "NRCan National Burned Area Composite 2012-2025 (polygons administered by DND in -111.4 to -110.5 E, 52.55-53.0 N).", SRC], fh=135)
im.convert("RGB").save(REPO + "data/graphics_published/oct25_oct14_fire/cfb-wainwright-fire-record-2012-2026.jpg", quality=92); print("ok", top)
