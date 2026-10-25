"""Summarise smoke.py output: smoke before the front at the points and likely ground; after the front, when haze (<1 km)
and dense smoke (<100 m) arrive at each point against when the fire arrives (fires weighted by fit to the final scar).
Usage: python3 smoke_summary.py REPO P4_DIR_PREFIX SMOKE_DIR"""
import sys, os, json, numpy as np, pandas as pd
from pyproj import Transformer
REPO, P4, SD = sys.argv[1:4]; M = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4"); OUT = os.path.join(M, "smoke"); os.makedirs(OUT, exist_ok=True)
d = pd.read_csv(os.path.join(SD, "smoke_receptors.csv.gz"))
fit = pd.read_csv(os.path.join(M, "fit_post/fit_post_all.csv")); fit["w"] = np.exp((fit.jaccard - fit.jaccard.max()) / 0.05)
tf = Transformer.from_crs(4326, 3400, always_xy=True).transform
PTS = {"Range 2 point": (-110.9063, 52.7728), "Road head": (-110.8996, 52.7705), "C": (-110.9160, 52.7640), "D": (-110.8995, 52.7628), "E": (-110.8990, 52.7530)}
clock = lambda m: None if m is None or not np.isfinite(m) else f"{3 + int(m // 60)}:{int(m % 60):02d}"
out = {"before_front": {}, "after_front": {}}
pre = d[d.phase == "pre"]
for k in PTS:
    s = pre[pre.rec == k].groupby(["time_min", "off"]).vis_m.median().unstack()
    out["before_front"][k] = {f"min_visibility_m_wind{o:+d}": round(float(s[o].min())) for o in s.columns}
z = pre[pre.kind == "zone"]
zz = z.groupby(["case", "time_min", "off"]).apply(lambda x: np.average(x.vis_m < 1000, weights=x.w)).groupby(["time_min", "off"]).median()
out["before_front"]["likely_ground_max_share_in_smoke_vis_lt_1km"] = round(float(zz.max()), 3)
post = d[(d.phase == "post") & (d.off == 0)]
rows = []
for (case, run), g in post.groupby(["case", "run"]):
    dd = P4 + case; minx, maxy, R, H, W = np.load(dd + "/meta.npy"); A = np.load(f"{dd}/arr_{run}.npy")
    w = float(fit[(fit.case == case) & (fit.run == run)].w.iloc[0])
    for k, (lo, la) in PTS.items():
        x, y = tf(lo, la); fa = float(A[int((maxy - y) // R), int((x - minx) // R)]); s = g[g.rec == k]
        rows.append(dict(case=case, run=run, w=w, point=k, fire=fa, haze=s[s.vis_m < 1000].time_min.min(), dense=s[s.vis_m < 100].time_min.min()))
r = pd.DataFrame(rows); r.to_csv(os.path.join(OUT, "smoke_vs_fire_points.csv"), index=False)
def wmed(x, w):
    x, w = np.asarray(x, float), np.asarray(w, float); m = np.isfinite(x); x, w = x[m], w[m]
    if not len(x): return None
    o = np.argsort(x); return float(x[o][np.searchsorted(np.cumsum(w[o]) / w.sum(), .5)])
for k in PTS:
    s = r[r.point == k]
    out["after_front"][k] = dict(fire=clock(wmed(s.fire, s.w)), haze_lt_1km=clock(wmed(s.haze, s.w)), dense_lt_100m=clock(wmed(s.dense, s.w)),
                                 haze_lead_min=round(wmed(s.fire - s.haze, s.w), 1), dense_lead_min=round(wmed(s.fire - s.dense, s.w), 1))
for f in ("convection_number_by_hour.csv", "smoke_check_landsat_1217.json"):
    if os.path.exists(os.path.join(SD, f)): open(os.path.join(OUT, f), "wb").write(open(os.path.join(SD, f), "rb").read())
json.dump(out, open(os.path.join(OUT, "smoke_summary.json"), "w"), indent=1); print(json.dumps(out, indent=1))
