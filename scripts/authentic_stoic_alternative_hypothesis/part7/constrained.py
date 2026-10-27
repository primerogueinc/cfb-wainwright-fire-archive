"""Part 7b: split the likely ground (part 2) by Permanent Danger Area 2 and recompute visibility (part 5),
escape odds (part 4 surface) and fire arrival (part 1 S2 8 km/h scar-limited) for each side.
Rationale: officials said the fire overtook a section-attack range's administrative area; admin areas
normally sit outside danger areas, while an attack lane can run into one."""
import os, sys, json
import numpy as np, pandas as pd, geopandas as gpd, rasterio, shapely
REPO = sys.argv[1]; SP = sys.argv[2]
OUT = os.path.join(REPO, "data/authentic-stoic-stress-test/part7_briefing_check")
C = "EPSG:3400"
o = gpd.read_file(os.path.join(REPO, "data/infrastructure/osm_infrastructure_ODbL.geojson")).to_crs(C)
pda = o[o.name == "Permanent Danger Area 2"].geometry.iloc[0]
z = pd.read_csv(os.path.join(SP, "p5/zone_visibility_vegetation.csv"))
P = gpd.GeoSeries(gpd.points_from_xy(z.x, z.y), crs=4326).to_crs(C)
z["X"], z["Y"] = P.x.values, P.y.values
z["in_pda2"] = shapely.contains_xy(pda, z.X.values, z.Y.values)
z["dist_boundary_m"] = [pda.exterior.distance(p) for p in P]
s = pd.read_csv(os.path.join(SP, "p4/surface.csv"))
# nearest surface point (70 m grid) for each zone cell
from scipy.spatial import cKDTree
tr = cKDTree(s[["x", "y"]].values); d, i = tr.query(z[["X", "Y"]].values)
for c in ["gust_jog", "gust_smoke", "within500_jog", "within500_smoke", "within200_jog", "within200_smoke"]:
    z[c] = np.where(d < 80, s[c].values[i], np.nan)
ar = rasterio.open(os.path.join(REPO, "data/authentic-stoic-alternative-hypothesis/arrival_S2_station_veer_scar_limited_8kmh_front316.tif"))
A = ar.read(1).astype(float); A[A < -9000] = np.nan
cc, rr = (~ar.transform) * (z.X.values, z.Y.values)
z["arrival_min_after_3pm"] = A[np.clip(rr.astype(int), 0, A.shape[0]-1), np.clip(cc.astype(int), 0, A.shape[1]-1)]
w = z.n_scenarios_in_core.astype(float)
def summ(m):
    ww = w[m]
    def wa(col): v = z.loc[m, col]; k = v.notna(); return round(float(np.average(v[k], weights=ww[k])), 3) if k.any() else None
    return {"cells": int(m.sum()), "weight_share": round(float(ww.sum() / w.sum()), 3),
            "sees_edge_standing": wa("sees_standing"), "sees_edge_prone": wa("sees_prone"),
            "escape_gust_jog": wa("gust_jog"), "escape_gust_smoke": wa("gust_smoke"),
            "escape_fire500_jog": wa("within500_jog"), "escape_fire200_jog": wa("within200_jog"),
            "median_arrival_min_after_3pm": round(float(np.nanmedian(z.loc[m, "arrival_min_after_3pm"])), 1)}
res = {"all_likely_ground": summ(np.ones(len(z), bool)), "inside_PDA2": summ(z.in_pda2.values),
       "outside_PDA2": summ(~z.in_pda2.values), "outside_PDA2_within_300m_of_boundary": summ((~z.in_pda2.values) & (z.dist_boundary_m.values <= 300))}
z.drop(columns=["X", "Y"]).to_csv(os.path.join(OUT, "likely_ground_by_pda2.csv"), index=False)
json.dump(res, open(os.path.join(OUT, "constrained_summary.json"), "w"), indent=1); print(json.dumps(res, indent=1))
