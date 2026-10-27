"""Part 7c: where did the fire burn outside Permanent Danger Area 2? If the section-attack range's
administrative area was outside PDA 2 (as admin areas normally are) and the fire overtook it, it must lie
on burned ground outside PDA 2."""
import os, sys, json, math
import pandas as pd, geopandas as gpd
from shapely.geometry import Point
REPO = sys.argv[1]; OUT = os.path.join(REPO, "data/authentic-stoic-stress-test/part7_briefing_check"); C = "EPSG:3400"
o = gpd.read_file(os.path.join(REPO, "data/infrastructure/osm_infrastructure_ODbL.geojson")).to_crs(C)
pda = o[o.name == "Permanent Danger Area 2"].geometry.iloc[0]
scar = max(gpd.read_file(os.path.join(REPO, "data/infrastructure/scar_patches_revised.geojson")).to_crs(C).geometry, key=lambda g: g.area)
d = pd.read_csv(os.path.join(REPO, "data/firms/detections.csv")); L = d[d.acq_datetime_mdt == "2026-10-17 12:17 MDT"]
Lp = gpd.GeoSeries(gpd.points_from_xy(L.longitude, L.latitude), crs=4326).to_crs(C); org = Point(Lp.x.mean(), Lp.y.mean())
B = gpd.GeoSeries([Point(-110.8996, 52.7705)], crs=4326).to_crs(C).iloc[0]
out = scar.difference(pda); parts = sorted(getattr(out, "geoms", [out]), key=lambda g: -g.area)
rows = []
for g in parts:
    c = g.centroid; ll = gpd.GeoSeries([c], crs=C).to_crs(4326).iloc[0]
    rows.append(dict(area_km2=round(g.area / 1e6, 4), lat=round(ll.y, 4), lon=round(ll.x, 4), dist_from_origin_m=round(org.distance(c)),
                     bearing_from_origin=round(math.degrees(math.atan2(c.x - org.x, c.y - org.y)) % 360), dist_to_road_head_m=round(B.distance(g))))
df = pd.DataFrame(rows); df.to_csv(os.path.join(OUT, "burn_outside_pda2.csv"), index=False)
res = dict(scar_km2=round(scar.area / 1e6, 2), outside_pda2_km2=round(out.area / 1e6, 3),
           outside_within_2km_of_origin_km2=round(sum(g.area for g in parts if org.distance(g.centroid) <= 2000) / 1e6, 4),
           largest_outside_patch=rows[0] if rows else None)
json.dump(res, open(os.path.join(OUT, "burn_outside_pda2.json"), "w"), indent=1); print(json.dumps(res, indent=1)); print(df.head(6).to_string())
