"""Graphic: every satellite-detected fire day in CFB Wainwright's central training area, April-October 2025 and 2026, with the base
station's daily fire danger and DND's announced spring fuel-reduction burn window. Usage: python3 scripts/maps/g39_2025_2026.py"""
import sys; sys.path.insert(0, "scripts/maps")
from v4fig import *
import pandas as pd, numpy as np, geopandas as gpd
F = pd.read_csv(REPO + "data/firms/history_2012-2026/all_detections_merged.csv"); F = F[F.source != "GOES_NRT"]
F["t"] = pd.to_datetime(F.acq_date + " " + F.acq_time.astype(str).str.zfill(4), format="%Y-%m-%d %H%M") - pd.Timedelta(hours=6)
F = F[F.t >= "2025-01-01"]; F["d"] = F.t.dt.normalize()
o = gpd.read_file(REPO + "data/infrastructure/osm_infrastructure_ODbL.geojson"); da = o[o.military == "danger_area"]
G = gpd.GeoSeries(gpd.points_from_xy(F.longitude, F.latitude), crs=4326)
F["area"] = [next((n for n, g in zip(da.name, da.geometry) if g.contains(p)), "outside") for p in G]
F["cls"] = np.where(F.area == "Permanent Danger Area 2", "PDA 2", np.where(F.area.str.startswith("Permanent"), "Other danger area", "Outside danger areas"))
F["night"] = (F.t.dt.hour < 6) | (F.t.dt.hour >= 21)
C = []
for f in ("cwfis_fwi2020s_301S001.csv",):
    c = pd.read_csv(REPO + "data/nrcan_cwfis/history/" + f, skipinitialspace=True); c["d"] = pd.to_datetime(c.rep_date.str[:10]); C.append(c[["d", "fwi"]])
c26 = pd.read_csv(REPO + "data/nrcan_cwfis/history/cwfis_fwi_2026_wainwright.csv", skipinitialspace=True).drop_duplicates(); c26.columns = [x.strip().lower() for x in c26.columns]
c26["d"] = pd.to_datetime(c26.repdate.astype(str).str.strip(), format="%Y%m%d"); C.append(c26[["d", "fwi"]]); C = pd.concat(C).drop_duplicates("d", keep="last").sort_values("d"); C["fwi"] = pd.to_numeric(C.fwi, errors="coerce"); C = C[C.fwi.notna()]
COL = {"PDA 2": RED, "Other danger area": (190, 120, 255), "Outside danger areas": MUTED}
rows = []
for yr in (2025, 2026):
    f, ax = fig(1480, 330); s, e = pd.Timestamp(f"{yr}-04-01"), pd.Timestamp(f"{yr}-10-31")
    c = C[(C.d >= s) & (C.d <= e)]; ax.fill_between(c.d, 0, c.fwi, color=hx((90, 70, 55)), step="mid", lw=0)
    ax.axhline(29.5, color=hx(RED), ls="--", lw=1); ax.text(s + pd.Timedelta(days=1), 30.5, "Extreme", color=hx(RED), fontsize=11)
    ax.axhline(18.5, color=hx(MUTED), ls="--", lw=0.8); ax.text(s + pd.Timedelta(days=1), 19.5, "Very High", color=hx(MUTED), fontsize=11)
    if yr == 2026: ax.axvspan(pd.Timestamp("2026-04-10"), pd.Timestamp("2026-05-05"), color=hx(TEAL), alpha=0.18, lw=0); ax.text(pd.Timestamp("2026-04-11"), 52, "Announced fuel-reduction\nburns, Apr. 10-May 5", color=hx(TEAL), fontsize=11, va="top")
    x = F[(F.d >= s) & (F.d <= e)]
    for (d, cls), g in x.groupby(["d", "cls"]):
        yv = {"PDA 2": 45, "Other danger area": 40, "Outside danger areas": 35}[cls]
        ax.plot(d, yv, "s", ms=9, color=hx(COL[cls]), mec=hx(INK)); 
        if g.night.any(): ax.plot(d, yv + 4, "*", ms=9, color=hx(YEL))
        rows.append(dict(year=yr, date=d.date(), cls=cls, detections=len(g), night=bool(g.night.any()), sensors=",".join(sorted(set(g.source)))))
    if yr == 2026:
        ax.annotate("Oct. 17", (pd.Timestamp("2026-10-17"), 45), (-10, 14), textcoords="offset points", color=hx(CREAM), fontsize=12, weight="bold", ha="right")
    ax.set_xlim(s, e); ax.set_ylim(0, 55); ax.set_ylabel("Daily FWI", color=hx(CREAM), fontsize=12)
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator()); ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b"))
    ax.tick_params(axis="x", labelsize=13); ax.grid(axis="x", color=hx(GRIDC)); f.subplots_adjust(0.05, 0.12, 0.995, 0.97); rows.append(None); globals()[f"P{yr}"] = to_img(f)
pd.DataFrame([r for r in rows if r]).to_csv(REPO + "data/fire_compare/fire_days_2025_2026.csv", index=False)
W, H = 1600, 1150
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · 2025 AND 2026, APRIL TO OCTOBER",
               "Spring burns are announced. We found no notice of the fall fires",
               "Each square is a day with a NASA satellite fire detection in the central training area, coloured by where it fell; a star means at least one detection at night (9 p.m.-6 a.m.).\n"
               "Shading: the base station's daily Fire Weather Index. DND announced spring fuel-reduction burns for Apr. 10-May 5, 2026; we found no public notice of fall burns.")
d.text((54, 205), "2025", font=B(22), fill=GOLD); im.paste(P2025, (54, 236))
d.text((54, 590), "2026", font=B(22), fill=GOLD); im.paste(P2026, (54, 621))
lx, ly = 54, 965
for txt, col in (("Permanent Danger Area 2", RED), ("Other permanent danger areas", (190, 120, 255)), ("Outside the danger areas", MUTED)):
    d.rectangle([lx, ly + 4, lx + 18, ly + 22], fill=col); d.text((lx + 26, ly), txt, font=M(16), fill=CREAM); lx += d.textlength(txt, font=M(16)) + 60
d.text((lx, ly), "★ detection at night", font=M(16), fill=YEL)
d.text((54, ly + 34), "2025 uses one satellite (S-NPP) plus Landsat; 2026 adds NOAA-20 and NOAA-21, so 2026 catches more small fires. Danger areas: OpenStreetMap, not official.", font=M(15), fill=MUTED)
footer(im, ["Data: NASA FIRMS (VIIRS, Landsat); NRCan CWFIS station FWI (301S001). Burn window: Lakeland Connect / Border Pulse, Apr. 9, 2026.", SRC], fh=110)
im.convert("RGB").save(REPO + "data/graphics_published/oct25_oct14_fire/cfb-wainwright-fires-2025-2026.jpg", quality=92); print("ok")
