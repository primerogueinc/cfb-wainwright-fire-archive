"""Part 7: test the model against what DND/CAF officials said at the Oct. 22 briefing.
Statements tested: fire reported on the automatic grenade launcher range; it initially stayed inside
Permanent Danger Area 2 (no direct suppression); range control monitored it all day; the AGL range and the
section-attack range are separate; the sudden wind change increased its speed; no gas infrastructure involved."""
import os, sys, json, math
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import Point
REPO = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = os.path.join(REPO, "data/authentic-stoic-stress-test/part7_briefing_check"); os.makedirs(OUT, exist_ok=True)
C = "EPSG:3400"
o = gpd.read_file(os.path.join(REPO, "data/infrastructure/osm_infrastructure_ODbL.geojson")).to_crs(C)
pda = o[o.name == "Permanent Danger Area 2"].geometry.iloc[0]
scar = max(gpd.read_file(os.path.join(REPO, "data/infrastructure/scar_patches_revised.geojson")).to_crs(C).geometry, key=lambda g: g.area)
d = pd.read_csv(os.path.join(REPO, "data/firms/detections.csv"))
def pts(t):
    s = d[d.acq_datetime_mdt == t]; return gpd.GeoSeries(gpd.points_from_xy(s.longitude, s.latitude), crs=4326).to_crs(C)
L = pts("2026-10-17 12:17 MDT"); V = pts("2026-10-17 14:49 MDT")
hull = L.union_all().union(V.union_all()).convex_hull.intersection(scar)
origin = Point(L.x.mean(), L.y.mean())
P = gpd.GeoSeries([Point(-110.9063, 52.7728), Point(-110.8996, 52.7705)], crs=4326, index=["A_range2", "B_road_head"]).to_crs(C)
res = {
  "landsat_1217_in_PDA2": f"{int(L.within(pda).sum())}/{len(L)}",
  "viirs_1449_in_PDA2": f"{int(V.within(pda).sum())}/{len(V)}",
  "preshift_fire_outline_share_in_PDA2": round(hull.intersection(pda).area / hull.area, 3),
  "final_scar_share_in_PDA2": round(scar.intersection(pda).area / scar.area, 3),
  "origin_centroid_lonlat": [round(v, 4) for v in gpd.GeoSeries([origin], crs=C).to_crs(4326).iloc[0].coords[0]],
  "points": {k: {"inside_PDA2": bool(pda.contains(p)), "dist_to_PDA2_boundary_m": round(pda.exterior.distance(p)),
                 "dist_from_origin_m": round(origin.distance(p)), "dist_to_scar_edge_m": round(scar.exterior.distance(p))} for k, p in P.items()},
}
json.dump(res, open(os.path.join(OUT, "briefing_check.json"), "w"), indent=1); print(json.dumps(res, indent=1))
