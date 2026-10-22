"""Authentic Stoic stress test, part 2: what does "about a kilometre" mean?

Part 1 held the band at 0.6-1.5 km downwind of the fire's pre-shift edge and varied the wind
(270-325 deg). Part 2 also varies:
  * the distance band: what range "about a kilometre" plausibly covers
  * the reference: what the kilometre was measured from
      edge_all      outline of Landsat 12:17 + VIIRS 2:49 detections (the part 1 baseline)
      edge_viirs    outline of the latest pass only (VIIRS 2:49, buffered 190 m = half a pixel)
      edge_landsat  outline of the 12:17 Landsat line only (buffered 15 m)
      main_body     the baseline outline shrunk 300 m (distance from the fire's body, not its fringe)
For each (reference, band) it computes, over all 12 winds, the ground that is in the band for every
wind (the "core"), its area, how much of it is the Range 2 zone (ACH zone H1), how far its centre
sits from the part 1 core, and whether Range 2 and the road's end are in it.
"""
import os, sys, json, itertools
import numpy as np, pandas as pd, geopandas as gpd, shapely
from shapely.geometry import Point

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = os.path.join(REPO, "data/authentic-stoic-stress-test/part2"); os.makedirs(OUT, exist_ok=True)
C = "EPSG:3400"
g = pd.read_csv(os.path.join(REPO, "data/location_analysis/scar_grid_upwind_distances.csv"))
P = gpd.GeoSeries(gpd.points_from_xy(g.x, g.y), crs=4326).to_crs(C); X, Y = P.x.values, P.y.values
CELL_KM2 = 50 * 50 / 1e6

scar = max(gpd.read_file(os.path.join(REPO, "data/infrastructure/scar_patches_revised.geojson")).to_crs(C).geometry, key=lambda q: q.area)
d = pd.read_csv(os.path.join(REPO, "data/firms/detections.csv"))
d = d[(d.latitude.between(52.7, 52.85)) & (d.longitude.between(-111.0, -110.82))]
def pts(times):
    s = d[d.acq_datetime_mdt.isin(times)]
    return gpd.GeoSeries(gpd.points_from_xy(s.longitude, s.latitude), crs=4326).to_crs(C)
L = pts(["2026-10-17 12:17 MDT"]); V = pts(["2026-10-17 14:49 MDT"])
base = shapely.unary_union(list(L) + list(V)).convex_hull.intersection(scar)
REFS = {
    "edge_all": base,
    "edge_viirs": shapely.unary_union([p.buffer(190) for p in V]).convex_hull.buffer(0).intersection(scar.buffer(200)),
    "edge_landsat": shapely.unary_union([p.buffer(15) for p in L]).convex_hull.intersection(scar),
    "main_body": base.buffer(-300),
}
BANDS = {"0.5-1.0": (500, 1000), "0.6-1.5 (part 1)": (600, 1500), "0.75-1.25": (750, 1250),
         "1.0-2.0": (1000, 2000), "0.4-2.0": (400, 2000)}
DIRS = list(range(270, 330, 5))

def downwind_dist(ref):
    """Distance (m) each scar cell lies downwind of `ref`, per wind direction; NaN if > 5 km."""
    shapely.prepare(ref)
    out = {}
    for w in DIRS:
        to = np.radians((w + 180) % 360); vx, vy = np.sin(to), np.cos(to)
        dist = np.full(len(X), np.nan)
        inside = shapely.contains_xy(ref, X, Y); dist[inside] = 0
        todo = ~inside
        for s in range(20, 5001, 20):
            hit = todo & shapely.contains_xy(ref, X - s * vx, Y - s * vy)
            dist[hit] = s; todo &= ~hit
            if not todo.any(): break
        out[w] = dist
    return out

cand = pd.read_csv(os.path.join(REPO, "data/location_analysis/candidate_points.csv")).set_index("point")
cp = gpd.GeoSeries(gpd.points_from_xy(cand.lon, cand.lat), crs=4326, index=cand.index).to_crs(C)
def nearest(name):
    p = cp[name]; j = int(np.argmin((X - p.x) ** 2 + (Y - p.y) ** 2))
    return j if np.hypot(X[j] - p.x, Y[j] - p.y) < 120 else None
iR2, iRD = nearest("Range2 centroid (OSM)"), nearest("Road dead end (CanVec)")

rows, cores = [], {}
for rn, ref in REFS.items():
    D = downwind_dist(ref)
    for bn, (lo, hi) in BANDS.items():
        B = np.array([(D[w] >= lo) & (D[w] <= hi) for w in DIRS])
        n = B.sum(0); core = n == 12; any_ = n >= 1
        cores[(rn, bn)] = core
        z = g.zone[core].value_counts(normalize=True)
        rows.append(dict(reference=rn, band_km=bn, ref_area_km2=round(ref.area / 1e6, 2),
                         core_km2=round(core.sum() * CELL_KM2, 2), any_wind_km2=round(any_.sum() * CELL_KM2, 2),
                         core_share_range2_zone=round(float(z.get("H1", 0)), 2),
                         core_share_other=", ".join(f"{k} {v:.2f}" for k, v in z.items() if k != "H1" and v >= 0.05),
                         range2_winds_in_band=int(n[iR2]) if iR2 is not None else None,
                         road_end_winds_in_band=int(n[iRD]) if iRD is not None else None,
                         core_centroid_x=float(X[core].mean()) if core.any() else None,
                         core_centroid_y=float(Y[core].mean()) if core.any() else None))
        print(rows[-1]["reference"], bn, rows[-1]["core_km2"], rows[-1]["core_share_range2_zone"], flush=True)

df = pd.DataFrame(rows)
b = df[(df.reference == "edge_all") & (df.band_km == "0.6-1.5 (part 1)")].iloc[0]
df["core_shift_m"] = np.hypot(df.core_centroid_x - b.core_centroid_x, df.core_centroid_y - b.core_centroid_y).round()
base_core = cores[("edge_all", "0.6-1.5 (part 1)")]
df["overlap_with_part1_core"] = [round((cores[(r, k)] & base_core).sum() / max(base_core.sum(), 1), 2) for r, k in zip(df.reference, df.band_km)]
df.drop(columns=["core_centroid_x", "core_centroid_y"]).to_csv(os.path.join(OUT, "part2_results.csv"), index=False)

# robustness map: in how many of the 20 (reference x band) cores is each cell?
freq = np.sum([c for c in cores.values()], axis=0)
out = g[["x", "y", "zone"]].copy(); out["n_scenarios_in_core"] = freq
out.to_csv(os.path.join(OUT, "part2_core_frequency.csv"), index=False)
json.dump({k: round(v.area / 1e6, 3) for k, v in REFS.items()}, open(os.path.join(OUT, "reference_areas_km2.json"), "w"), indent=1)
gpd.GeoDataFrame({"reference": list(REFS)}, geometry=list(REFS.values()), crs=C).to_crs(4326).to_file(os.path.join(OUT, "references.geojson"), driver="GeoJSON")
pd.set_option("display.width", 250)
print(df.drop(columns=["core_centroid_x", "core_centroid_y"]).to_string(index=False))
print("cells in >=15/20 cores:", int((freq >= 15).sum()), "zone mix:", g.zone[freq >= 15].value_counts(normalize=True).round(2).to_dict())
