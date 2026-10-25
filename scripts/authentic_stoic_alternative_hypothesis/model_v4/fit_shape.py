"""Working model v4, step 1 (v3 step 1 with the ISI fix): fit the fire's shape, start and timing to Landsat 8's 12:17 p.m. burned area.
Usage: python3 fit_shape.py REPO [NPROC]

Same model as part 8b (ignition_backcalc.py, 40 m grid), with one new parameter: LBM, a multiplier on the length-to-breadth
ratio of the spreading ellipse (LB = LBM * 1.1 * WS^0.464). Part 8c found the model's fire too wide at 12:17 (1.0-1.3 km^2
against 0.44 km^2 observed, length-to-breadth 3-4 against 6-8 observed). Head spread rate is unchanged (afternoon still
calibrated to the measured 0.43 km/h), so LBM only narrows the fire. Fit target and misfit as part 8c.
Candidates: lines of starts from Range 11 (bearings 72-88 deg; 1.0-2.2, 1.2-2.0, 1.4-2.2 km) and the 15 best single points
from part 8c; morning spread multiplier 1, 1.5, 2, 3; LBM 1, 1.5, 2, 2.5, 3; start every 30 min, 10 p.m. Oct 16 to 11:30 a.m.
"""
import sys, os, json
import numpy as np, pandas as pd, rasterio
from rasterio.warp import reproject, Resampling
from multiprocessing import Pool
REPO = sys.argv[1]; NP = int(sys.argv[2]) if len(sys.argv) > 2 else 2
src = open(os.path.join(REPO, "scripts/authentic_stoic_alternative_hypothesis/part8/ignition_backcalc.py")).read().split("# candidates:")[0]
src = src.replace("return 0.208 * fw * sf", "return fw * sf")  # v4: ISI bug fix (19.115 already includes 0.208)
assert "return fw * sf" in src
src = src.replace("lb = 1.1 * max(ws, 1) ** 0.464", "lb = max(1.0, LBM * 1.1 * max(ws, 1) ** 0.464)")
assert "LBM * 1.1" in src
LBM = 1.0
sys.argv = ["x", REPO, "40", "240"]; exec(src)
OUTD = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4"); os.makedirs(OUTD, exist_ok=True)
with rasterio.open(os.path.join(REPO, "data/authentic-stoic-stress-test/part8c_landsat_constraint/burned_1217_classes.tif")) as r:
    cls = np.zeros((H, W), "uint8")
    reproject(r.read(1), cls, src_transform=r.transform, src_crs=r.crs, dst_transform=T, dst_crs=CRS, resampling=Resampling.mode)
OBS = {"loose": cls >= 1, "central": cls >= 2, "tight": cls >= 3}
EDT = {k: ndimage.distance_transform_edt(~m) * RES for k, m in OBS.items()}
PER = {k: m & ~ndimage.binary_erosion(m) for k, m in OBS.items()}
def fit(A):
    B = A <= TL
    if not B.any(): return dict(misfit_m=9999)
    DB = ndimage.distance_transform_edt(~B) * RES; pb = B & ~ndimage.binary_erosion(B)
    out = {}
    for k in OBS:
        out[f"outline_{k}_m"] = round((float(DB[PER[k]].mean()) + float(EDT[k][pb].mean())) / 2)
        out[f"iou_{k}"] = round(float((B & OBS[k]).sum() / (B | OBS[k]).sum()), 3)
    v1, v2 = chamfer(A <= TV, Vany, D_to_V, Vmask)
    out["viirs_misfit_m"] = round(v1 + v2); out["misfit_m"] = round(out["outline_central_m"] + 0.5 * (v1 + v2) / 2)
    out["area_km2_1217"] = round(float(B.sum()) * RES * RES / 1e6, 3); out["area_km2_1449"] = round(float((A <= TV).sum()) * RES * RES / 1e6, 3)
    return out
def hm(t): return f"{int(t % 24):02d}:{int(round((t % 1) * 60)) % 60:02d}" + (" Oct 16" if t < 0 else "")
times = np.arange(-2, 11.51, 0.5)
starts = []
for b in range(72, 89, 4):
    for d1, d2 in [(1.0, 2.2), (1.2, 2.0), (1.4, 2.2)]:
        st = set()
        for dd in np.arange(d1, d2 + 1e-6, RES / 2000):
            lo, la, _ = G.fwd(R11[0], R11[1], b, dd * 1000); i, j = cell(*tf(lo, la))
            if 0 <= i < H and 0 <= j < W and fuel[i, j]: st.add((i, j))
        if st: starts.append(("line", f"bearing {b} deg, {d1}-{d2} km", sorted(st)))
pb_ = pd.read_csv(os.path.join(REPO, "data/authentic-stoic-stress-test/part8c_landsat_constraint/fit_best.csv"))
for key in pb_[pb_.kind == "point"].key.drop_duplicates().head(15):
    lo, la = map(float, key.split(",")[:2]); starts.append(("point", key, [cell(*tf(lo, la))]))
jobs = [(k, key, st, m, l) for k, key, st in starts for m in (1.0, 1.5, 2.0, 3.0) for l in (1.0, 1.5, 2.0, 2.5, 3.0)]
def job(a):
    kind, key, st, mult, lbm = a
    global MORNING_MULT, LBM
    MORNING_MULT, LBM = mult, lbm
    return [dict(kind=kind, key=key, ros_multiplier=mult, lb_multiplier=lbm, t0=float(t0), ignition_mdt=hm(t0), **fit(run(0, 0, t0, starts=st))) for t0 in times]
print(len(starts), "starts;", len(jobs), "jobs", flush=True)
with Pool(NP) as p: res = [r for rr in p.imap_unordered(job, jobs, chunksize=2) for r in rr]
df = pd.DataFrame(res); df.to_csv(os.path.join(OUTD, "fit_shape_all.csv.gz"), index=False)
best = df.sort_values("misfit_m").groupby(["kind", "key", "ros_multiplier", "lb_multiplier"]).head(1).sort_values("misfit_m")
best.to_csv(os.path.join(OUTD, "fit_shape_best.csv"), index=False)
print(best.head(30).to_string())
print(df.groupby("lb_multiplier").misfit_m.min())
