"""September vs October, year over year (2012-2026), CFB Wainwright central training area.
Usage: python3 yoy.py REPO
- Fire days: days with at least one NASA FIRMS detection in the archive box (52.67-52.88 N, 110.75-111.10 W) and in Permanent Danger Area 2
  (OpenStreetMap outline, not official). Main series uses VIIRS S-NPP only (standard processing to June 2026, near-real-time after), the one
  sensor covering every year, so years are comparable. All-sensor fire days are given too (Landsat from mid-2022; NOAA-20/21 only in 2026).
- Fire danger: CWFIS daily FWI at Wainwright CFB Airfield 21 (301S001): mean FWI, and days at Alberta's Very High (>= 18.5) or Extreme (>= 29.5).
- Burned area: NRCan NBAC polygons administered by DND inside the NBAC box (-111.4 to -110.5 E, 52.55-53.0 N), hectares per year (no month: NBAC
  polygons are annual composites).
Writes data/fire_compare/yoy/{yoy_by_year_month.csv, summary.json}."""
import sys, os, json, numpy as np, pandas as pd, geopandas as gpd
REPO = sys.argv[1]; OUT = os.path.join(REPO, "data/fire_compare/yoy"); os.makedirs(OUT, exist_ok=True)
F = pd.read_csv(os.path.join(REPO, "data/firms/history_2012-2026/all_detections_merged.csv"))
F["t"] = pd.to_datetime(F.acq_date + " " + F.acq_time.astype(str).str.zfill(4), format="%Y-%m-%d %H%M") - pd.Timedelta(hours=6)  # MDT
F["date_mdt"] = F.t.dt.date.astype(str); F["year"] = F.t.dt.year; F["month"] = F.t.dt.month
o = gpd.read_file(os.path.join(REPO, "data/infrastructure/osm_infrastructure_ODbL.geojson")); pda2 = o[o.name == "Permanent Danger Area 2"].geometry.iloc[0]
G = gpd.GeoDataFrame(F, geometry=gpd.points_from_xy(F.longitude, F.latitude), crs=4326); F["in_pda2"] = G.within(pda2).values
F = F[F.source != "GOES_NRT"]
snpp = F[F.source.str.startswith("VIIRS_SNPP")]
rows = []
for y in range(2012, 2027):
    for m, mn in ((9, "Sep"), (10, "Oct")):
        a = snpp[(snpp.year == y) & (snpp.month == m)]; b = F[(F.year == y) & (F.month == m)]
        rows.append(dict(year=y, month=mn, snpp_fire_days=a.date_mdt.nunique(), snpp_fire_days_pda2=a[a.in_pda2].date_mdt.nunique(), snpp_detections=len(a),
                         all_sensor_fire_days=b.date_mdt.nunique(), all_sensor_fire_days_pda2=b[b.in_pda2].date_mdt.nunique(),
                         dates=";".join(sorted(b.date_mdt.unique()))))
D = pd.DataFrame(rows)
# fire danger
C = []
for f in ("cwfis_fwi2010s_301S001.csv", "cwfis_fwi2020s_301S001.csv"):
    c = pd.read_csv(os.path.join(REPO, "data/nrcan_cwfis/history", f), skipinitialspace=True); c["d"] = pd.to_datetime(c.rep_date.str[:10]); C.append(c[["d", "fwi", "isi", "ffmc"]])
c26 = pd.read_csv(os.path.join(REPO, "data/nrcan_cwfis/history/cwfis_fwi_2026_wainwright.csv"), skipinitialspace=True).drop_duplicates()
c26.columns = [x.strip().lower() for x in c26.columns]; c26["d"] = pd.to_datetime(c26.repdate.astype(str).str.strip(), format="%Y%m%d")
C.append(c26[["d", "fwi", "isi", "ffmc"]]); C = pd.concat(C); C = C[C.d.dt.year >= 2012].drop_duplicates("d", keep="last")
for k in ("fwi", "isi", "ffmc"): C[k] = pd.to_numeric(C[k], errors="coerce")
C = C[C.fwi.notna()]
fw = C.groupby([C.d.dt.year, C.d.dt.month]).agg(fwi_mean=("fwi", "mean"), days_with_fwi=("fwi", "size"), days_very_high_plus=("fwi", lambda s: int((s >= 18.5).sum())), days_extreme=("fwi", lambda s: int((s >= 29.5).sum())))
fw.index.names = ["year", "m"]; fw = fw.reset_index(); fw["month"] = fw.m.map({9: "Sep", 10: "Oct"}); fw = fw[fw.month.notna()].drop(columns="m")
D = D.merge(fw, on=["year", "month"], how="left")
n = gpd.read_file(os.path.join(REPO, "data/nbac/nbac_wainwright_2012-2025.geojson")); nb = n[n.ADMIN_NAME == "DND"].groupby("YEAR").POLY_HA.sum().round(0)
D["nbac_dnd_ha_year"] = D.year.map(lambda y: nb.get(float(y), np.nan) if y <= 2025 else np.nan)
D.round(2).to_csv(os.path.join(OUT, "yoy_by_year_month.csv"), index=False)
def tot(m, col, yrs=range(2012, 2026)): return int(D[(D.month == m) & D.year.isin(yrs)][col].sum())
S = dict(years="2012-2025 (2026 separate)",
         snpp_fire_days=dict(Sep=tot("Sep", "snpp_fire_days"), Oct=tot("Oct", "snpp_fire_days")),
         snpp_fire_days_pda2=dict(Sep=tot("Sep", "snpp_fire_days_pda2"), Oct=tot("Oct", "snpp_fire_days_pda2")),
         years_with_fire=dict(Sep=int((D[(D.month == "Sep") & (D.year < 2026)].snpp_fire_days > 0).sum()), Oct=int((D[(D.month == "Oct") & (D.year < 2026)].snpp_fire_days > 0).sum())),
         years_with_fire_pda2=dict(Sep=int((D[(D.month == "Sep") & (D.year < 2026)].snpp_fire_days_pda2 > 0).sum()), Oct=int((D[(D.month == "Oct") & (D.year < 2026)].snpp_fire_days_pda2 > 0).sum())),
         fwi_mean=dict(Sep=round(float(C[(C.d.dt.month == 9) & (C.d.dt.year < 2026)].fwi.mean()), 1), Oct=round(float(C[(C.d.dt.month == 10) & (C.d.dt.year < 2026)].fwi.mean()), 1)),
         y2026=D[D.year == 2026].drop(columns=["nbac_dnd_ha_year"]).to_dict("records"),
         oct17_2026_fwi_rank=dict(fwi=float(C[C.d == "2026-10-17"].fwi.iloc[0]), share_of_october_days_2012_2025_at_or_above=round(float((C[(C.d.dt.month == 10) & (C.d.dt.year < 2026)].fwi >= float(C[C.d == "2026-10-17"].fwi.iloc[0])).mean()), 4),
                                  october_days_2012_2025=int(((C.d.dt.month == 10) & (C.d.dt.year < 2026)).sum())),
         nbac_dnd_ha_by_year={int(k): float(v) for k, v in nb.items()})
json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=str); print(json.dumps(S, indent=1, default=str)); print(D.drop(columns="dates").to_string())
