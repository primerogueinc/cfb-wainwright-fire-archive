"""Working model v3, step 3: after the 3:16 p.m. wind shift. Usage: python3 post_front.py REPO PREFRONT_TIF CASE

Runs the part 1 post-front model (spread.py: 5 wind schedules x head spread 4.4/8/12 km/h x steady/gusty shape = 30 fires,
40 m grid) from a new starting fire: the area the v3 pre-front model has burned by 3:16 p.m. (PREFRONT_TIF, hours since
midnight Oct. 17). The starting fire is that area joined with the outline of the 12:17 and 2:49 p.m. detections used in parts 1-8
(the fire cannot have been smaller than what the satellites saw). Then the part 4 escape analysis (perm.py, clock.py) on the 30 fires. Outputs go to data/.../model_v3/<CASE>/."""
import sys, os, math, subprocess, shutil
import numpy as np, rasterio
from rasterio.warp import reproject, Resampling
REPO, PRE, CASE = sys.argv[1], sys.argv[2], sys.argv[3]
SP = "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/"
WORK = os.path.join(SP, f"p4_v3_{CASE}"); os.makedirs(WORK, exist_ok=True)
OUTD = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v3", CASE); os.makedirs(OUTD, exist_ok=True)
src = open(os.path.join(REPO, "scripts/authentic_stoic_alternative_hypothesis/spread.py")).read().split("# ---------------- runs")[0]
src = src.replace('OUT = os.path.join(REPO, "data/authentic-stoic-alternative-hypothesis")', f'OUT = "{WORK}"')
src = src.replace("r = R * (1 - E) / (1 - E * math.cos(phi))", "r = R * (1 - EE) / (1 - EE * math.cos(phi))")
src = src.replace('def run(sched, tf, ros_kmh, fuel, t_end=mdt("18:00")):', 'def run(sched, tf, ros_kmh, fuel, t_end=mdt("18:00"), EE=None):\n    EE = E if EE is None else EE')
sys.argv = ["x", REPO]; exec(src)
# ---- new starting fire: v3 pre-front burned area at 3:16 p.m.
with rasterio.open(PRE) as r:
    a = np.full((H, W), np.nan, "float32")
    reproject(r.read(1), a, src_transform=r.transform, src_crs=r.crs, src_nodata=np.nan, dst_transform=T, dst_crs=CRS, dst_nodata=np.nan, resampling=Resampling.nearest)
v3_m = np.isfinite(a) & (a <= 15 + 16 / 60)
# Keep ground the satellites saw burning before the front (outline of the 12:17 Landsat and 2:49 p.m. VIIRS detections, as in
# parts 1-8): the narrower v3 fire does not always reach the 2:49 detections on its southeast side, and the fire cannot have
# been smaller than what was observed.
hull_m = v3_m | hull_m
fuel_scar = (rast(scar.buffer(150)) | hull_m) & ~water
np.save(os.path.join(WORK, "meta.npy"), np.array([minx, maxy, RES, H, W])); np.save(os.path.join(WORK, "start316.npy"), hull_m)
# distance from the 3:16 edge to the scenario points
from scipy import ndimage
D = ndimage.distance_transform_edt(~hull_m) * RES
import pandas as pd, geopandas as gpd
from shapely.geometry import Point
PTS = {"A_range2": (52.7728, -110.9063), "B_road_head": (52.7705, -110.8996), "C": (52.7640, -110.9160), "D": (52.7628, -110.8995), "E": (52.7530, -110.8990),
       "well_1-11_registered": (52.773642, -110.898943), "line_58333-78_west_end": (52.77186, -110.90429)}
P = gpd.GeoSeries([Point(lo, la) for la, lo in PTS.values()], crs=4326, index=list(PTS)).to_crs(CRS)
edge = {k: int(round(D[int((maxy - p.y) // RES), int((p.x - minx) // RES)])) for k, p in P.items()}
pd.Series(edge, name="edge_to_point_m_at_316").to_csv(os.path.join(OUTD, "edge_distance_316.csv"))
print("start fire km2", round(hull_m.sum() * RES * RES / 1e6, 3), "added by v3", round((v3_m & ~rast(hull)).sum() * RES * RES / 1e6, 3), edge, flush=True)
for lbname, lb in (("steady", LB), ("gusty", 3.0)):
    EE = math.sqrt(1 - 1 / lb ** 2)
    for s in ["S0_fixed306", "S1_stoic", "S2_station_veer", "S3_fast_veer", "S4_fixed315"]:
        for ros in (4.4, 8.0, 12.0):
            A = run(schedule(s, mdt("15:16")), mdt("15:16"), ros, fuel_scar, t_end=mdt("18:30"), EE=EE)
            np.save(os.path.join(WORK, f"arr_{s}_{ros}_{lbname}.npy"), A.astype("float32"))
    print("grids", lbname, flush=True)
P4 = os.path.join(REPO, "scripts/authentic_stoic_alternative_hypothesis/part4")
for scr in ("perm.py", "clock.py"):
    shutil.copy(os.path.join(P4, scr), WORK)
subprocess.run([sys.executable, "perm.py"], cwd=WORK, check=True, stdout=open(os.path.join(OUTD, "perm_log.txt"), "w"))
subprocess.run([sys.executable, "clock.py"], cwd=WORK, check=True)
shutil.copy(os.path.join(WORK, "clock.csv"), os.path.join(OUTD, "escape_clock.csv"))
shutil.copy(os.path.join(WORK, "perm.csv.gz"), os.path.join(OUTD, "escape_perm.csv.gz"))
d = pd.read_csv(os.path.join(OUTD, "escape_clock.csv")); d["ros"] = d.grid.str.extract(r"', ([\d.]+),").astype(float)
pm = pd.read_csv(os.path.join(OUTD, "escape_perm.csv.gz")); pm = pm[pm.cue != "FAN"]
rows = []
for k in "AB":
    x = d[(d.point == k) & (d.speed == "jog in kit (8 km/h)")]
    arr = pm[pm.point == k].drop_duplicates(["schedule", "ros", "gust"]).arrival - 16
    rows.append(dict(point=k, arrival_min_after_front_median=round(arr.median(), 1), arrival_min_after_front_min=round(arr.min(), 1), arrival_min_after_front_max=round(arr.max(), 1),
                     escape_jog_at_gust=round(x[x.t0 == 16].optimal.mean() * 100), escape_jog_plus3=round(x[x.t0 == 19].optimal.mean() * 100), escape_jog_plus7=round(x[x.t0 == 23].optimal.mean() * 100),
                     fast_at_gust=round(x[(x.t0 == 16) & (x.ros >= 8)].optimal.mean() * 100), fast_plus3=round(x[(x.t0 == 19) & (x.ros >= 8)].optimal.mean() * 100), fast_plus7=round(x[(x.t0 == 23) & (x.ros >= 8)].optimal.mean() * 100)))
pd.DataFrame(rows).to_csv(os.path.join(OUTD, "summary.csv"), index=False); print(pd.DataFrame(rows).to_string())
