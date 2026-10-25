"""Working model v4, step 1: score the 30 post-front fires of each v3 case against the final burn scar.
Usage: python3 fit_post.py REPO P4_DIR_PREFIX EDGE_DIR OUT_DIR
In v3 the post-front fires could only burn inside the mapped scar (+150 m), so they could not be wrong about where the fire
stopped. Here each fire starts from the same 3:16 p.m. fire (start316.npy) but may burn anything except open water, and is
stopped when its burned area equals the mapped scar's. Scores, at that moment:
  jaccard        overlap with the mapped scar (intersection / union)
  edge_agree     share of 40 m cells within 600 m of the Range 2 point and road head classed the same (burned/unburned)
                 as the Oct. 24 Sentinel-2 dNBR map (edge_check.py)
  pocket_burned  share of the unburned pocket northeast of the road head (Oct. 24 dNBR, >= 0.27 = burned) that the fire burned
  stop_time      clock time at which it reached the scar's area
plus arrival at the Range 2 point and road head (minutes after 3 p.m.)."""
import sys, os, math
import numpy as np, pandas as pd
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from scipy import ndimage
REPO, P4, EDGE, OUTD = sys.argv[1:5]; os.makedirs(OUTD, exist_ok=True)
src = open(os.path.join(REPO, "scripts/authentic_stoic_alternative_hypothesis/spread.py")).read().split("# ---------------- runs")[0]
src = src.replace('OUT = os.path.join(REPO, "data/authentic-stoic-alternative-hypothesis")', f'OUT = "{OUTD}"')
src = src.replace("r = R * (1 - E) / (1 - E * math.cos(phi))", "r = R * (1 - EE) / (1 - EE * math.cos(phi))")
src = src.replace('def run(sched, tf, ros_kmh, fuel, t_end=mdt("18:00")):', 'def run(sched, tf, ros_kmh, fuel, t_end=mdt("18:00"), EE=None):\n    EE = E if EE is None else EE')
sys.argv = ["x", REPO]; exec(src)
from pyproj import Transformer
tf_ = Transformer.from_crs(4326, CRS, always_xy=True).transform
PTS = {"A_range2": tf_(-110.9063, 52.7728), "B_road_head": tf_(-110.8996, 52.7705)}
idx = {k: (int((maxy - y) // RES), int((x - minx) // RES)) for k, (x, y) in PTS.items()}
yy, xx = np.mgrid[0:H, 0:W]; X = minx + (xx + .5) * RES; Y = maxy - (yy + .5) * RES
near = np.zeros((H, W), bool)
for x, y in PTS.values(): near |= np.hypot(X - x, Y - y) <= 600
# observed burned (Oct. 24 S2 dNBR, 10 m) -> 40 m (majority)
ex0, ey0, er, eh, ew = np.load(os.path.join(EDGE, "grid_meta.npy")); eh, ew = int(eh), int(ew)
ob10 = np.load(os.path.join(EDGE, "S2_20_m_dNBR_2026_10_24.npy")).astype("float32")
obs = np.full((H, W), np.nan, "float32")
reproject(ob10, obs, src_transform=from_origin(ex0, ey0, er, er), src_crs=CRS, dst_transform=T, dst_crs=CRS, resampling=Resampling.average, dst_nodata=np.nan)
obs_b = obs >= 0.5; obs_ok = np.isfinite(obs)
lab, n = ndimage.label(~obs_b & obs_ok & near)
i, j = idx["B_road_head"]
pocket = lab == lab[i, j] if lab[i, j] else lab == lab.flat[np.argmin(np.where(lab > 0, np.hypot(X - PTS["B_road_head"][0], Y - PTS["B_road_head"][1]), np.inf))]
A_scar = scar_m.sum()
rows = []
import glob
for case in sorted(os.path.basename(p)[len(os.path.basename(P4)):] for p in glob.glob(P4 + "*") if os.path.isdir(p)):
    W4 = P4 + case
    m = np.load(os.path.join(W4, "meta.npy")); assert np.allclose(m, [minx, maxy, RES, H, W]), "grid mismatch"
    hull_m = np.load(os.path.join(W4, "start316.npy"))          # run() starts from the global hull_m
    for lbname, lb in (("steady", LB), ("gusty", 3.0)):
        EE = math.sqrt(1 - 1 / lb ** 2)
        for s in ["S0_fixed306", "S1_stoic", "S2_station_veer", "S3_fast_veer", "S4_fixed315"]:
            for ros in (4.4, 8.0, 12.0):
                A = run(schedule(s, mdt("15:16")), mdt("15:16"), ros, fuel_free, t_end=mdt("19:00"), EE=EE)
                fin = np.sort(A[np.isfinite(A)].ravel())
                if len(fin) < A_scar: t_stop = np.inf; burned = np.isfinite(A)
                else: t_stop = fin[int(A_scar) - 1]; burned = A <= t_stop
                inter = (burned & scar_m).sum(); uni = (burned | scar_m).sum()
                rows.append(dict(case=case, schedule=s, ros=ros, gust=lbname, run=f"{s}_{ros}_{lbname}",
                                 jaccard=round(inter / uni, 3), edge_agree=round(float((burned[near & obs_ok] == obs_b[near & obs_ok]).mean()), 3),
                                 pocket_burned=round(float(burned[pocket].mean()), 3), stop_time_min=round(float(t_stop), 1),
                                 arr_A=round(float(A[idx["A_range2"]]), 1), arr_B=round(float(A[idx["B_road_head"]]), 1)))
                print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(os.path.join(OUTD, "fit_post_all.csv"), index=False)
print("pocket cells", int(pocket.sum()), "ha", pocket.sum() * RES * RES / 1e4)
