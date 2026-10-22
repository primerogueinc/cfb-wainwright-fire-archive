"""Time-varying wind test of the "authentic-stoic alternative hypothesis".

Challenge (X, @AuthenticStoic, Oct. 22, 2026): CZWN peak gusts came from 269 deg at 3:16 p.m.
and 288 deg at 4:09 p.m., so the fire should have run east, not southeast, until after 4 p.m.,
and the burn should be stretched east. Our Oct. 21 analysis used a fixed 306 deg wind.

Method
  Grass-fire spread on a 40 m grid (NAD83 / Alberta 10-TM, EPSG:3400), solved as a
  time-dependent shortest-arrival problem (Dijkstra, 16-neighbour stencil). Spread in each
  direction follows an ellipse with the ignition point at its rear focus:
      R(phi) = R_head * (1 - e) / (1 - e cos phi),  e = sqrt(1 - 1/LB^2)
  with LB = 1.1 * U^0.464 (FBP grass, ST-X-3 eq. 80) at U = 48 km/h (CZWN 4 p.m. mean).
  Starting fire: outline of the Landsat 12:17 and VIIRS 14:49 detections, clipped to the scar
  (the same "pre-shift hull" as the Oct. 21 analysis). No spread before the front: the fire grew
  only about 1 km in 2.5 h before the shift (see fire_models.csv), so it is held fixed.
  Fuel: everything burnable except open water (Sentinel-2 Oct. 4 NDWI > 0.05). No roads, guards
  or suppression, so absolute extent is an upper bound; we compare shapes and timing.

Wind schedules (direction the wind comes FROM; linear between knots)
  S0_fixed306      306 from the front onward (Oct. 21 analysis)
  S1_stoic         269 at the front -> 288 at 4:09 -> 306 at 4:20 (the challenge's reading)
  S2_station_veer  269 at the front -> 305 at 3:50 -> 306 (4 p.m. 10-min mean 307, 10-min max gust from 305)
  S3_fast_veer     269 at the front -> 305 at 3:30 -> 306
  S4_fixed315      315 from the front onward (control: 5 p.m. 10-min max gust from 318)
Front arrival at the fire: 3:16 (station time) or 3:25 (front ~15 km east of CZWN at ~100 km/h).
Head spread: 4.4, 8 and 12 km/h (range of FBP O-1a/O-1b and CSIRO post-shift, fire_models.csv).

Tests
  T1 GOES-18: active burning (arrival in the preceding 10 min) inside each GOES pixel footprint
     at 3:30 and 3:40, against what GOES saw (3:30: W, E and S pixels hot; 3:40: S pixel only).
  T2 Shape: unconstrained run stopped when burned area equals the mapped scar; Jaccard overlap
     with the scar, and how far the burn reaches east vs south of the starting fire.
  T3 Timing: arrival at the candidate points (scar-limited and unconstrained runs), minutes after
     the front, and distance from the point to the starting fire at the front's arrival.
"""
import heapq, json, math, os, sys
import numpy as np, pandas as pd, geopandas as gpd
import rasterio
from rasterio import features
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = os.path.join(REPO, "data/authentic-stoic-alternative-hypothesis")
os.makedirs(OUT, exist_ok=True)
CRS = "EPSG:3400"
RES = 40.0

# ---------------- inputs
scar_all = gpd.read_file(os.path.join(REPO, "data/infrastructure/scar_patches_revised.geojson")).to_crs(CRS)
scar = max(scar_all.geometry, key=lambda g: g.area)
d = pd.read_csv(os.path.join(REPO, "data/firms/detections.csv"))
d = d[(d.latitude.between(52.7, 52.85)) & (d.longitude.between(-111.0, -110.82))]
pre = d[d.acq_datetime_mdt.isin(["2026-10-17 12:17 MDT", "2026-10-17 14:49 MDT"])]
pts = gpd.GeoSeries(gpd.points_from_xy(pre.longitude, pre.latitude), crs=4326).to_crs(CRS)
hull = pts.unary_union.convex_hull.intersection(scar)

minx, miny, maxx, maxy = scar.bounds
pad = 4000
minx, miny, maxx, maxy = minx - pad, miny - pad, maxx + pad, maxy + pad
W = int(math.ceil((maxx - minx) / RES)); H = int(math.ceil((maxy - miny) / RES))
T = from_origin(minx, maxy, RES, RES)

def rast(geom):
    return features.rasterize([(geom, 1)], out_shape=(H, W), transform=T, fill=0, dtype="uint8").astype(bool)

scar_m = rast(scar); hull_m = rast(hull)

# water from Sentinel-2 L2A Oct 4 (pre-fire)
S2 = os.path.join(REPO, "data/copernicus/manual_exports/2026-10-04/2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L2A_%s_(Raw).tiff")
def band(b):
    with rasterio.open(S2 % b) as r:
        dst = np.zeros((H, W), "float32")
        reproject(r.read(1).astype("float32"), dst, src_transform=r.transform, src_crs=r.crs,
                  dst_transform=T, dst_crs=CRS, resampling=Resampling.average)
    return dst
g, n = band("B03"), band("B08")
ndwi = (g - n) / np.maximum(g + n, 1e-6)
water = (ndwi > 0.05) & ~scar_m & ~hull_m
fuel_free = ~water            # unconstrained fuel
fuel_scar = (rast(scar.buffer(150)) | hull_m) & ~water   # mapped scar + 150 m (points on its edge, mapping error)

# GOES-18 pixel footprints
gp = pd.read_csv(os.path.join(REPO, "data/location_analysis/goes_fire_pixels.csv"))
foot = {}
for _, r in gp.drop_duplicates(["lat", "lon"]).iterrows():
    xy = [tuple(map(float, c.split(","))) for c in r.corners.split(";")]
    poly = gpd.GeoSeries([Polygon(xy)], crs=4326).to_crs(CRS).iloc[0]
    name = {(-110.9056): "W (start)", (-110.8668): "E", (-110.8962): "S"}[round(r.lon, 4)]
    foot[name] = rast(poly)
GOES_OBS = {"15:30": {"W (start)": 278, "E": 517, "S": 420}, "15:40": {"W (start)": 0, "E": 0, "S": 336}}

cand = pd.read_csv(os.path.join(REPO, "data/location_analysis/candidate_points.csv"))
cxy = gpd.GeoSeries(gpd.points_from_xy(cand.lon, cand.lat), crs=4326).to_crs(CRS)
cidx = [(int((maxy - p.y) // RES), int((p.x - minx) // RES)) for p in cxy]
dist_hull = [round(hull.distance(p)) for p in cxy]

# ---------------- model
def mdt(hhmm):  # minutes after 15:00 MDT
    h, m = map(int, hhmm.split(":")); return (h - 15) * 60 + m

def schedule(name, tf):
    k = {"S0_fixed306": [(tf, 306), (999, 306)],
         "S1_stoic": [(tf, 269), (mdt("16:09"), 288), (mdt("16:20"), 306), (999, 306)],
         "S2_station_veer": [(tf, 269), (mdt("15:50"), 305), (mdt("16:00"), 306), (999, 306)],
         "S3_fast_veer": [(tf, 269), (mdt("15:30"), 305), (mdt("15:40"), 306), (999, 306)],
         "S4_fixed315": [(tf, 315), (999, 315)]}[name]
    ts, ds = zip(*k)
    return lambda t: float(np.interp(t, ts, ds))

U = 48.0
LB = 1.1 * U ** 0.464
E = math.sqrt(1 - 1 / LB ** 2)
OFF = [(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3)
       if (dy, dx) != (0, 0) and math.gcd(abs(dy), abs(dx)) == 1]

def run(sched, tf, ros_kmh, fuel, t_end=mdt("18:00")):
    R = ros_kmh * 1000 / 60  # m/min
    arr = np.full((H, W), np.inf)
    pq = []
    for y, x in zip(*np.nonzero(hull_m)):
        arr[y, x] = tf; pq.append((tf, y, x))
    heapq.heapify(pq)
    # precompute geometry of offsets (x east, y north)
    geo = [(dy, dx, math.hypot(dx, dy) * RES, math.atan2(dx, -dy)) for dy, dx in OFF]  # bearing of step (rad, from north)
    while pq:
        t, y, x = heapq.heappop(pq)
        if t > arr[y, x] or t > t_end:
            continue
        head = math.radians((sched(t) + 180) % 360)  # direction the fire is pushed
        for dy, dx, dist, brg in geo:
            yy, xx = y + dy, x + dx
            if not (0 <= yy < H and 0 <= xx < W) or not fuel[yy, xx]:
                continue
            phi = brg - head
            r = R * (1 - E) / (1 - E * math.cos(phi))
            nt = t + dist / r
            if nt < arr[yy, xx]:
                arr[yy, xx] = nt; heapq.heappush(pq, (nt, yy, xx))
    return arr

def hm(t):
    if not np.isfinite(t): return "not reached"
    t = 15 * 60 + t; return f"{int(t // 60)}:{int(round(t % 60)):02d}"

# ---------------- runs
SCHED = ["S0_fixed306", "S1_stoic", "S2_station_veer", "S3_fast_veer", "S4_fixed315"]
FRONT = {"3:16": mdt("15:16"), "3:25": mdt("15:25")}
ROS = [4.4, 8.0, 12.0]
scar_area = scar_m.sum()
yy, xx = np.mgrid[0:H, 0:W]
X = minx + (xx + 0.5) * RES; Y = maxy - (yy + 0.5) * RES
hc = hull.centroid
rows, goes_rows, pt_rows = [], [], []
keep = {}
for s in SCHED:
    for fl, tf in FRONT.items():
        for ros in ROS:
            sched = schedule(s, tf)
            A = run(sched, tf, ros, fuel_free, t_end=mdt("21:00"))
            # T2 shape: stop when burned area == scar area
            fin = np.sort(A[np.isfinite(A)])
            tstop = fin[min(scar_area, len(fin)) - 1]
            burn = A <= tstop
            inter = (burn & scar_m).sum(); uni = (burn | scar_m).sum()
            new = burn & ~hull_m
            east = float(np.percentile(X[new] - hc.x, 95)) if new.any() else 0
            south = float(np.percentile(hc.y - Y[new], 95)) if new.any() else 0
            # T1 GOES and T3 timing on the scar-limited run
            As = run(sched, tf, ros, fuel_scar)
            for runlab, AA in (("scar_limited", As), ("unconstrained", A)):
                for lab in ("15:30", "15:40"):
                    t = mdt(lab)
                    for k, m in foot.items():
                        act = ((AA > t - 10) & (AA <= t) & m).sum() * RES * RES / 1e6
                        goes_rows.append(dict(run=runlab, schedule=s, front=fl, ros_kmh=ros, time=lab, pixel=k,
                                              active_km2=round(act, 3), goes_mw=GOES_OBS[lab][k]))
                for (name, (cy, cx)), dh in zip(zip(cand.point, cidx), dist_hull):
                    a = AA[cy, cx]
                    pt_rows.append(dict(run=runlab, schedule=s, front=fl, ros_kmh=ros, point=name, arrival=hm(a),
                                        min_after_front=round(a - tf, 1) if np.isfinite(a) else None,
                                        dist_to_starting_fire_m=dh))
            rows.append(dict(schedule=s, front=fl, ros_kmh=ros, stop_time=hm(tstop),
                             jaccard_vs_scar=round(inter / uni, 3), share_of_scar_reached=round(inter / scar_area, 3),
                             reach_east_m=round(east), reach_south_m=round(south),
                             east_to_south_ratio=round(east / max(south, 1), 2)))
            if ros == 8.0 and fl == "3:16":
                keep[s] = (A, As, burn)
            print(s, fl, ros, rows[-1]["jaccard_vs_scar"], rows[-1]["east_to_south_ratio"], flush=True)

shape = pd.DataFrame(rows); goes = pd.DataFrame(goes_rows); pts_df = pd.DataFrame(pt_rows)
shape.to_csv(os.path.join(OUT, "shape_test.csv"), index=False)
goes.to_csv(os.path.join(OUT, "goes_test.csv"), index=False)
pts_df.to_csv(os.path.join(OUT, "arrival_times.csv"), index=False)

# observed scar shape for reference
sc = scar_m & ~hull_m
obs = dict(reach_east_m=round(float(np.percentile(X[sc] - hc.x, 95))),
           reach_south_m=round(float(np.percentile(hc.y - Y[sc], 95))))
obs["east_to_south_ratio"] = round(obs["reach_east_m"] / obs["reach_south_m"], 2)

# GOES pattern score: 3:30 all three active, 3:40 S active and E quiet
def gscore(df):
    p = df.pivot_table(index="time", columns="pixel", values="active_km2")
    s = 0
    s += sum(p.loc["15:30", k] > 0.05 for k in ("W (start)", "E", "S"))
    s += p.loc["15:40", "S"] > 0.05
    s += p.loc["15:40", "S"] > p.loc["15:40", "E"]
    return int(s)
gs = goes[goes.run == "unconstrained"].groupby(["schedule", "front", "ros_kmh"]).apply(gscore).rename("goes_pattern_score_of_5").reset_index()
summary = shape.merge(gs, on=["schedule", "front", "ros_kmh"])
summary.to_csv(os.path.join(OUT, "summary.csv"), index=False)
fp = {k: dict(scar_km2=round((m & scar_m).sum() * RES * RES / 1e6, 2), start_fire_km2=round((m & hull_m).sum() * RES * RES / 1e6, 2)) for k, m in foot.items()}
json.dump(dict(observed_scar=obs, goes_footprints=fp, LB=round(LB, 2), grid_m=RES, scar_cells=int(scar_area)),
          open(os.path.join(OUT, "observed_reference.json"), "w"), indent=1)

# save arrival grids for the mid case (8 km/h, front 3:25) as GeoTIFF (minutes after 15:00 MDT)
for s, (A, As, burn) in keep.items():
    for tag, arr in (("unconstrained", A), ("scar_limited", As)):
        with rasterio.open(os.path.join(OUT, f"arrival_{s}_{tag}_8kmh_front316.tif"), "w", driver="GTiff",
                           height=H, width=W, count=1, dtype="float32", crs=CRS, transform=T,
                           nodata=-9999, compress="deflate") as dst:
            dst.write(np.where(np.isfinite(arr), arr, -9999).astype("float32"), 1)
print(json.dumps(obs))
print(summary.to_string(index=False))
