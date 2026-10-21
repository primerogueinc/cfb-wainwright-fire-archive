"""Stress test of the C Company location estimate against all held layers."""
import sys, json, math
sys.path.insert(0, "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/vis")
from pr import *
import shapely
from shapely.geometry import LineString, Point, box
OUT = "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/stress/"
import os; os.makedirs(OUT, exist_ok=True)
P = "EPSG:3400"
to = lambda g: gpd.GeoSeries([g], crs=4326).to_crs(P).iloc[0]

scar = scar_main(); scarP = to(scar); hull = preshift_hull(); hullP = to(hull)
o = osm(); r2 = o[o["name"] == "Range 2 (Grenade)"].geometry.iloc[0]; r3 = o[o["name"] == "Range 3"].geometry.iloc[0]
Z = {
    "H1 Range 2 / N-S road": box(-110.912, 52.760, -110.895, 52.778).intersection(scar),
    "H4b strip north of Jamieson Lake": box(-110.930, 52.755, -110.912, 52.768).intersection(scar),
    "H6 south-central run": box(-110.912, 52.735, -110.880, 52.760).intersection(scar),
    "H2 Range 3 / north end": box(-110.915, 52.778, -110.895, 52.795).intersection(scar).union(r3),
    "H3 east lobe past road": box(-110.880, 52.735, -110.850, 52.770).intersection(scar),
    "H4a west interior": scar.intersection(box(-110.96, 52.768, -110.912, 52.80)),
}
ZP = {k: to(v) for k, v in Z.items()}
res = {"zones": {}}

# ---------------- layers
wells = pd.read_csv(REPO + "data/infrastructure/wells_within_5km_of_scar.csv")
wells = gpd.GeoDataFrame(wells, geometry=gpd.points_from_xy(wells.lon, wells.lat), crs=4326).to_crs(P)
pipes = gpd.read_file(REPO + "data/reference/aer_pipelines_near_site.geojson").to_crs(P)
tr = gpd.read_file(REPO + "data/reference/canvec50k_transport_near_site.geojson").to_crs(P)
rm = gpd.read_file(REPO + "data/reference/canvec50k_res_mgt_near_site.geojson").to_crs(P)
mm = gpd.read_file(REPO + "data/reference/canvec50k_manmade_near_site.geojson").to_crs(P)
roads = tr[tr.layer.isin(["road_segment_1_2", "track_segment_1", "trail_1"])]
osm_lines = o[o.geom_type == "LineString"].to_crs(P)
bld = mm[mm.layer.str.startswith("building")]; tanks = mm[mm.layer.isin(["tank_0", "liquid_storage_facility_0"])]
cvwells = rm[rm.layer == "petroleum_well_0"]; cvpipe = rm[rm.layer == "pipeline_1"]; pwr = rm[rm.layer == "power_line_1"]; agg = rm[rm.layer == "aggregate_2"]

# dead ends: road/track endpoints not touching another segment (CanVec + OSM tracks)
allr = pd.concat([roads.geometry, osm_lines.geometry], ignore_index=True)
ends = []
for g in allr:
    for ln in getattr(g, "geoms", [g]):
        if ln.geom_type != "LineString": continue
        ends += [Point(ln.coords[0]), Point(ln.coords[-1])]
ends_g = gpd.GeoSeries(ends, crs=P)
sidx = allr.sindex
dead = []
for p_ in ends_g:
    hits = sidx.query(p_.buffer(8))
    if sum(1 for h in hits if allr.iloc[h].distance(p_) < 8) <= 1:
        dead.append(p_)
dead = gpd.GeoSeries(dead, crs=P)
dead = dead[dead.distance(scarP) < 3000]

for k, z in ZP.items():
    zb = z.buffer(150)  # include the immediate edge
    r = {
        "area_km2": round(z.area / 1e6, 2),
        "AER wells (any status)": int(wells.within(zb).sum()),
        "AER wells by status": wells[wells.within(zb)].Lic_Status.value_counts().to_dict(),
        "AER pipeline km": round(pipes.intersection(zb).length.sum() / 1000, 2),
        "AER pipeline km operating": round(pipes[pipes.SEG_STATUS == "Operating"].intersection(zb).length.sum() / 1000, 2),
        "CanVec petroleum wells": int(cvwells.within(zb).sum()),
        "CanVec pipeline km": round(cvpipe.intersection(zb).length.sum() / 1000, 2),
        "power line km": round(pwr.intersection(zb).length.sum() / 1000, 2),
        "buildings": int(bld.intersects(zb).sum()),
        "tanks / storage": int(tanks.intersects(zb).sum()),
        "gravel pits": int(agg.intersects(zb).sum()),
        "road + track km (CanVec)": round(roads.intersection(zb).length.sum() / 1000, 2),
        "OSM track km": round(osm_lines.intersection(zb).length.sum() / 1000, 2),
        "road/track dead ends": int(dead.within(zb).sum()),
    }
    res["zones"][k] = r

# ---------------- infrastructure near the pre-shift fire (12:17 line + 2:49 pixels)
L, V, _ = detections()
lp = gpd.GeoSeries(gpd.points_from_xy(L.longitude, L.latitude), crs=4326).to_crs(P)
fire_line = lp.unary_union.convex_hull
near = {}
for name, lay in (("AER wells", wells), ("AER pipelines", pipes), ("CanVec petroleum wells", cvwells), ("CanVec pipelines", cvpipe), ("power lines", pwr), ("buildings", bld), ("tanks", tanks)):
    dd = lay.distance(fire_line)
    near[name] = {"within_250m": int((dd < 250).sum()), "within_500m": int((dd < 500).sum()), "nearest_m": round(float(dd.min()), 0) if len(dd) else None}
nw = wells.assign(d=wells.distance(fire_line)).sort_values("d").head(5)
near["nearest AER wells"] = nw[["Licensee", "Lic_Status", "Status_Dat", "category", "d"]].round(0).to_dict("records")
npipe = pipes.assign(d=pipes.distance(fire_line)).sort_values("d").head(5)
near["nearest AER pipelines"] = npipe[["COMP_NAME", "SEG_STATUS", "SUBSTANCE1", "OUT_DIAMET", "d"]].round(0).to_dict("records")
res["near_12_17_fire_line"] = near

# ---------------- firebreak test: share of scar perimeter within 40 m of a road/track or pipeline
per = scarP.exterior
def share(lines, buf=40):
    u = lines.buffer(buf).unary_union
    return round(per.intersection(u).length / per.length * 100, 1)
res["scar_edge_on_roads_tracks_pct"] = share(pd.concat([roads.geometry, osm_lines.geometry]).pipe(lambda s: gpd.GeoSeries(s, crs=P)).loc[lambda s: s.distance(scarP) < 100])
res["scar_edge_on_pipelines_pct"] = share(pipes.geometry[pipes.distance(scarP) < 100])
res["scar_edge_on_lakes_note"] = "lakes not in vector layers; see map"

# ---------------- sensitivity sweep
g = pd.read_csv(ACH + "scar_grid_upwind_distances.csv")
pts = gpd.GeoSeries(gpd.points_from_xy(g.x, g.y), crs=4326).to_crs(P)
zone_of = np.array(["other"] * len(pts), dtype=object)
for k, z in ZP.items():
    zone_of[pts.within(z).values & (zone_of == "other")] = k.split()[0]
xs, ys = pts.x.values, pts.y.values
sweep = []
for grow in (0, 400, 800):
    hg = hullP.buffer(grow).intersection(scarP.buffer(50)) if grow else hullP
    for wd in (270, 285, 295, 306, 315, 325):
        a = math.radians(wd)  # direction wind comes FROM: upwind vector
        ux, uy = math.sin(a), math.cos(a)
        segs = shapely.linestrings(np.stack([np.stack([xs, ys], 1), np.stack([xs + ux * 7000, ys + uy * 7000], 1)], 1))
        inter = shapely.intersection(segs, hg)
        dist = np.where(shapely.is_empty(inter), np.nan, shapely.distance(shapely.points(xs, ys), inter))
        inside = shapely.contains_xy(hg, xs, ys)
        dist[inside] = 0
        for lo, hi, lab in ((200, 600, "0.2-0.6 km"), (600, 1500, "0.6-1.5 km"), (1500, 2500, "1.5-2.5 km"), (2500, 4500, "2.5-4.5 km")):
            sel = (dist >= lo) & (dist < hi)
            n = int(sel.sum())
            row = {"growth_m": grow, "wind_from": wd, "band": lab, "cells": n}
            for zk in ("H1", "H4b", "H6", "H2", "H3", "H4a", "other"):
                row[zk] = round(100 * float((zone_of[sel] == zk).sum()) / n, 0) if n else None
            sweep.append(row)
sw = pd.DataFrame(sweep); sw.to_csv(OUT + "sensitivity.csv", index=False)
k1 = sw[sw.band == "0.6-1.5 km"]
res["sweep_1km_band_H1_plus_H4b_pct"] = {"min": float((k1.H1 + k1.H4b).min()), "max": float((k1.H1 + k1.H4b).max()), "median": float((k1.H1 + k1.H4b).median())}
res["sweep_1km_band_H2_max_pct"] = float(k1.H2.max()); res["sweep_1km_band_H3_max_pct"] = float(k1.H3.max()); res["sweep_1km_band_H4a_max_pct"] = float(k1.H4a.max())

json.dump(res, open(OUT + "stress_results.json", "w"), indent=1, default=str)
gpd.GeoSeries(list(dead), crs=P).to_crs(4326).to_file(OUT + "dead_ends.geojson")
print(json.dumps(res, indent=1, default=str)[:6000])
print(k1.to_string())
