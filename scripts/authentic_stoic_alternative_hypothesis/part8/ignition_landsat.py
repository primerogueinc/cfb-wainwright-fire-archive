"""Part 8c (working model v2.2): re-fit the fire's start to the burned-and-burning area Landsat 8 recorded at 12:17 p.m. MDT,
not only to its fire pixels. Usage: python3 ignition_landsat.py REPO [NPROC]

Uses the part 8b model unchanged (ignition_backcalc.py up to its candidate search). Target: burned_1217_classes.tif
(from github.com/primerogueinc/CFB-Wainwright-Landsat-8-9, analysis/2026-10-17/area.py): burned at burn ratio < 0.08 (central),
< 0.12 (loose), < 0.06 (tight). A start must lie inside the area burned by 12:17, so candidates are model cells within 120 m of
the loose outline. Misfit = mean distance between modelled and observed 12:17 outlines (both directions) + half the 2:49 p.m.
VIIRS misfit as in part 8b. Also reports overlap (intersection over union) with each outline.
"""
import sys, os, json
import numpy as np, pandas as pd, rasterio
from rasterio.warp import reproject, Resampling
from multiprocessing import Pool
REPO = sys.argv[1]; NP = int(sys.argv[2]) if len(sys.argv) > 2 else 4
src = open(os.path.join(REPO, "scripts/authentic_stoic_alternative_hypothesis/part8/ignition_backcalc.py")).read().split("# candidates:")[0]
sys.argv = ["x", REPO, "40", "240"]; exec(src)
OUTD = os.path.join(REPO, "data/authentic-stoic-stress-test/part8c_landsat_constraint")
with rasterio.open(os.path.join(OUTD, "burned_1217_classes.tif")) as r:
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
        d1 = float(DB[PER[k]].mean()); d2 = float(EDT[k][pb].mean())
        out[f"outline_{k}_m"] = round((d1 + d2) / 2); out[f"iou_{k}"] = round(float((B & OBS[k]).sum() / (B | OBS[k]).sum()), 3)
    v1, v2 = chamfer(A <= TV, Vany, D_to_V, Vmask)
    out["viirs_misfit_m"] = round(v1 + v2); out["misfit_m"] = round(out["outline_central_m"] + 0.5 * (v1 + v2) / 2)
    out["area_ha_model_1217"] = round(float(B.sum()) * RES * RES / 1e4, 1)
    return out
near = ndimage.binary_dilation(OBS["loose"], iterations=3) & fuel
cand = [(i, j) for i, j in zip(*np.where(near)) if i % 2 == 0 and j % 2 == 0]  # every other 40 m cell = 80 m spacing
times = np.arange(-8, 12.01, 0.5)
inv = Transformer.from_crs(CRS, 4326, always_xy=True).transform
def hm(t): return f"{int(t % 24):02d}:{int(round((t % 1) * 60)) % 60:02d}" + (" Oct 16" if t < 0 else "")
def job(args):
    kind, key, st, mult = args
    global MORNING_MULT
    MORNING_MULT = mult; rows = []
    for t0 in times:
        rows.append(dict(kind=kind, key=key, ros_multiplier=mult, t0=float(t0), ignition_mdt=hm(t0), **fit(run(0, 0, t0, starts=st))))
    return rows
MULTS = (1.0, 2.0, 3.0)  # morning spread multipliers, as in part 8b
jobs = []
for (i, j) in cand:
    lo, la = inv(*cxy(i, j)); az, _, dist = G.inv(R11[0], R11[1], lo, la)
    for mult in MULTS: jobs.append(("point", f"{lo:.5f},{la:.5f},{dist/1000:.2f}km,{az%360:.0f}deg", [(i, j)], mult))
for b in range(60, 101, 4):
    for d1, d2 in [(0.8, 1.6), (1.0, 1.6), (1.0, 2.2), (1.2, 2.0), (1.4, 2.2)]:
        st = set()
        for dd in np.arange(d1, d2 + 1e-6, RES / 2000):
            lo, la, _ = G.fwd(R11[0], R11[1], b, dd * 1000); i, j = cell(*tf(lo, la))
            if 0 <= i < H and 0 <= j < W and fuel[i, j]: st.add((i, j))
        if st:
            for mult in MULTS: jobs.append(("line", f"bearing {b} deg, {d1}-{d2} km", list(st), mult))
print(len(cand), "point candidates;", len(jobs), "jobs", flush=True)
with Pool(NP) as p: res = [r for rr in p.map(job, jobs, chunksize=4) for r in rr]
df = pd.DataFrame(res); df.to_csv(os.path.join(OUTD, "fit_all.csv"), index=False)
best = df.sort_values("misfit_m").groupby(["kind", "key", "ros_multiplier"]).head(1).sort_values("misfit_m")
best.head(40).to_csv(os.path.join(OUTD, "fit_best.csv"), index=False)
print(best.head(25).to_string())
json.dump(dict(model="part 8b (ignition_backcalc.py), unchanged", K=round(K, 4), res_m=RES, n_point_candidates=len(cand), n_jobs=len(jobs)), open(os.path.join(OUTD, "run.json"), "w"), indent=1)
