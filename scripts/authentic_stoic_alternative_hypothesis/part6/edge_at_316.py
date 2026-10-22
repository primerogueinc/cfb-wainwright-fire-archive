"""Authentic Stoic stress test, part 6: where was the fire's edge when the wind turned?

Parts 1-5 measured from the "pre-shift hull" (Landsat 12:17 + VIIRS 14:49 detections) and assumed
no growth between the last satellite pass (14:49) and the front (3:16 or 3:25 p.m.). This tests that.
  1. Empirical pre-front spread: advance of the fire's head between Landsat 12:17 and VIIRS 14:49.
  2. Fire power check: VIIRS 14:49 FRP vs GOES-18 FDC FRP at 15:10 (pre-front) and 15:30 (post-front).
  3. Growth model: Huygens expansion of the hull with an elliptical template (ignition at rear focus),
     pre-front wind from CZWN (236-256 deg, 30-33 km/h, RH 16-22%), clipped to the mapped scar + 150 m.
  4. Effect: distance from scenarios A-E to the 3:16 edge, and the part 1/2 downwind band
     (0.6-1.5 km, winds 270-325 deg) recomputed from the grown edge.
"""
import os, sys, json
import numpy as np, pandas as pd, geopandas as gpd, shapely
from shapely.geometry import Point, Polygon
from shapely import affinity

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = os.path.join(REPO, "data/authentic-stoic-stress-test/part6_edge"); os.makedirs(OUT, exist_ok=True)
C = "EPSG:3400"
scar = max(gpd.read_file(os.path.join(REPO, "data/infrastructure/scar_patches_revised.geojson")).to_crs(C).geometry, key=lambda q: q.area)
d = pd.read_csv(os.path.join(REPO, "data/firms/detections.csv"))
d = d[(d.latitude.between(52.7, 52.85)) & (d.longitude.between(-111.0, -110.82))]
def pts(t):
    s = d[d.acq_datetime_mdt == t]
    return s, gpd.GeoSeries(gpd.points_from_xy(s.longitude, s.latitude), crs=4326).to_crs(C)
Ls, L = pts("2026-10-17 12:17 MDT"); Vs, V = pts("2026-10-17 14:49 MDT")
hull = shapely.unary_union(list(L) + list(V)).convex_hull.intersection(scar)

# 1. empirical head advance along the pre-front spread direction (wind 225-251 -> heading 45-71)
emp = []
for head in (45, 55, 65, 71):
    u = np.array([np.sin(np.radians(head)), np.cos(np.radians(head))])
    pl = max(p.x * u[0] + p.y * u[1] for p in L); pv = max(p.x * u[0] + p.y * u[1] for p in V)
    adv = pv - pl
    emp.append(dict(heading_deg=head, advance_m=round(adv), advance_lo_m=round(adv - 190), advance_hi_m=round(adv + 190),
                    rate_kmh=round(adv / 152 * 60 / 1000, 2), rate_lo_kmh=round((adv - 190) / 152 * 60 / 1000, 2),
                    rate_hi_kmh=round((adv + 190) / 152 * 60 / 1000, 2)))
emp = pd.DataFrame(emp); emp.to_csv(os.path.join(OUT, "empirical_head_advance.csv"), index=False); print(emp.to_string())

# 2. fire power
tl = pd.read_csv(os.path.join(REPO, "data/goes/fire_timeline.csv"))
g18 = tl[(tl.satellite == "GOES-18") & tl.scan_start_mdt.between("14:30 MDT", "16:00 MDT")][["scan_start_mdt", "cloud_pct", "c07_max_c", "fdc_fire_pixels", "fdc_power_mw"]]
frp = dict(viirs_1449_sum_mw=round(float(Vs.frp.sum()), 1), viirs_1449_pixels=len(Vs), goes18=g18.to_dict("records"))
json.dump(frp, open(os.path.join(OUT, "fire_power.json"), "w"), indent=1); print(frp["viirs_1449_sum_mw"]); print(g18.to_string())
# Byram intensity -> expected FRP for a given head rate (grass, 0.3 kg/m2 consumed, 18 MJ/kg, radiative fraction 0.15, 1.0-1.3 km front)
def frp_expected(ros_kmh, front_m):
    I = 18000 * 0.3 * ros_kmh / 3.6  # kW/m
    return I * front_m * 0.15 / 1000  # MW
frp_tab = pd.DataFrame([dict(ros_kmh=r, frp_mw_1km_front=round(frp_expected(r, 1000)), frp_mw_1p3km_front=round(frp_expected(r, 1300))) for r in (0.45, 1.5, 4.0, 8.0)])
frp_tab.to_csv(os.path.join(OUT, "frp_expected.csv"), index=False); print(frp_tab.to_string())

# 3. growth model
def template(head_m, LB):
    e = np.sqrt(1 - 1 / LB ** 2); a = head_m * (1 + e) / 2 / 1  # semi-major so that rear-focus to head = head_m
    a = head_m / (1 + e); b = a / LB; c = a * e
    t = np.linspace(0, 2 * np.pi, 72)
    # ellipse along +y with rear focus at origin: centre at (0, c)
    return Polygon(np.c_[b * np.sin(t), c + a * np.cos(t)])
def grow(ref, wind_from, ros_kmh, minutes, LB):
    if ros_kmh * minutes == 0: return ref
    T = template(ros_kmh * 1000 / 60 * minutes, LB)
    T = affinity.rotate(T, -((wind_from + 180) % 360), origin=(0, 0))  # rotate +y to heading (clockwise)
    bd = ref.exterior; S = [bd.interpolate(s) for s in np.arange(0, bd.length, 20)]
    parts = [affinity.translate(T, p.x, p.y) for p in S]
    return shapely.unary_union(parts + [ref]).intersection(scar.buffer(150).union(ref))

cand = {"A Range 2": (52.7728, -110.9063), "B Road's end": (52.7705, -110.8996), "C Strip N of Jamieson Lake": (52.7640, -110.9160),
        "D Range road south": (52.7628, -110.8995), "E South-central run": (52.7530, -110.8990)}
cp = gpd.GeoSeries([Point(lo, la) for la, lo in cand.values()], crs=4326, index=list(cand)).to_crs(C)

g = pd.read_csv(os.path.join(REPO, "data/location_analysis/scar_grid_upwind_distances.csv"))
P = gpd.GeoSeries(gpd.points_from_xy(g.x, g.y), crs=4326).to_crs(C); X, Y = P.x.values, P.y.values
DIRS = list(range(270, 330, 5))
def core(ref, lo=600, hi=1500):
    shapely.prepare(ref); n = np.zeros(len(X), int)
    inside = shapely.contains_xy(ref, X, Y)
    for w in DIRS:
        to = np.radians((w + 180) % 360); vx, vy = np.sin(to), np.cos(to)
        dist = np.full(len(X), np.nan); todo = ~inside.copy()
        for s in range(20, 1501, 20):
            hit = todo & shapely.contains_xy(ref, X - s * vx, Y - s * vy); dist[hit] = s; todo &= ~hit
        n += ((dist >= lo) & (dist <= hi))
    return (n == 12), inside
core0, _ = core(hull)
c0 = np.array([X[core0].mean(), Y[core0].mean()])

rows, edges = [], {}
for minutes, flab in ((27, "front 3:16"), (36, "front 3:25")):
    for ros in (0.45, 1.5, 4.0, 8.0):
        for LB in (3.0, 5.4):
            for wf in (236, 246, 256):
                E = grow(hull, wf, ros, minutes, LB)
                cr, inside = core(E)
                c1 = np.array([X[cr].mean(), Y[cr].mean()]) if cr.any() else np.array([np.nan, np.nan])
                r = dict(front=flab, minutes=minutes, head_ros_kmh=ros, LB=LB, wind_from=wf,
                         area_km2=round(E.area / 1e6, 2), growth_km2=round((E.area - hull.area) / 1e6, 2),
                         part1_core_already_burned_pct=round(100 * (core0 & inside).sum() / core0.sum()),
                         part1_core_still_core_pct=round(100 * (core0 & cr).sum() / core0.sum()),
                         core_centre_shift_m=round(float(np.hypot(*(c1 - c0)))) if cr.any() else None,
                         core_centre_shift_bearing=round(float(np.degrees(np.arctan2(*(c1 - c0))) % 360)) if cr.any() else None,
                         range2_zone_share=round(float(g.zone[cr].eq("H1").mean()), 2) if cr.any() else None)
                for k, p in cp.items():
                    r[f"dist_{k.split()[0]}_m"] = round(E.distance(p)) if not E.contains(p) else 0
                rows.append(r)
                if LB == 5.4 and wf == 246: edges[(minutes, ros)] = E
df = pd.DataFrame(rows); df.to_csv(os.path.join(OUT, "edge_growth_scenarios.csv"), index=False)
base = {f"dist_{k.split()[0]}_m": round(hull.distance(p)) for k, p in cp.items()}
print("hull distances:", base)
pd.set_option("display.width", 250)
print(df.groupby(["front", "head_ros_kmh"])[["growth_km2", "part1_core_already_burned_pct", "part1_core_still_core_pct", "core_centre_shift_m",
       "core_centre_shift_bearing", "range2_zone_share"] + [c for c in df if c.startswith("dist_")]].agg(["min", "max"]).to_string())
gpd.GeoDataFrame([dict(minutes=m, head_ros_kmh=r) for (m, r) in edges], geometry=list(edges.values()), crs=C).to_crs(4326).to_file(
    os.path.join(OUT, "edge_at_front.geojson"), driver="GeoJSON")
gpd.GeoDataFrame([dict(name="preshift_hull")], geometry=[hull], crs=C).to_crs(4326).to_file(os.path.join(OUT, "preshift_hull.geojson"), driver="GeoJSON")
json.dump(dict(hull_dist=base, part1_core_cells=int(core0.sum())), open(os.path.join(OUT, "baseline.json"), "w"), indent=1)
