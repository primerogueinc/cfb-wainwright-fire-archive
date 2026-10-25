"""Working model v4: the full ensemble, every variation used since part 1. Usage: python3 ensemble_summary.py REPO
4 pre-front cases (start 4:00-6:30 a.m., morning speed 1.5-3x, width 1.5-3x) x front reaching the fire at 3:16 or 3:25 x 5 wind
schedules (fixed 306, fixed 315, fast veer, station veer, slow 'authentic stoic' veer) x head speed 4.4 / 8 / 12 km/h x steady or gusty
shape = 240 post-front fires. For each fire: arrival at the Range 2 point and road head (minutes after the front reaches the fire),
escape (jogging, best route) at the gust / +3 / +7 min, overlap with the final scar. Summaries: overall (equal and scar-fit weights),
and by each dimension."""
import sys, os, json, numpy as np, pandas as pd
REPO = sys.argv[1]; M = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4")
rows = []
for tag, front in (("", "3:16"), ("f325", "3:25")):
    sfx = f"_{tag}" if tag else ""; fit = pd.read_csv(os.path.join(M, f"fit_post{sfx}/fit_post_all.csv"))
    for case in fit.case.unique():
        d = pd.read_csv(os.path.join(M, case + sfx, "escape_clock.csv")); g = d.grid.str.extract(r"\('(\w+)', ([\d.]+), '(\w+)'\)")
        d["schedule"], d["ros"], d["gust"] = g[0], g[1].astype(float), g[2]; d = d[d.speed == "jog in kit (8 km/h)"]
        pm = pd.read_csv(os.path.join(M, case + sfx, "escape_perm.csv.gz")); pm = pm[pm.cue != "FAN"].drop_duplicates(["point", "schedule", "ros", "gust"])
        for _, f in fit[fit.case == case].iterrows():
            r = dict(case=case, front=front, schedule=f.schedule, ros=f.ros, shape=f.gust, jaccard=f.jaccard)
            for k, nm in (("A", "range2"), ("B", "roadhead")):
                a = pm[(pm.point == k) & (pm.schedule == f.schedule) & (pm.ros == f.ros) & (pm.gust == f.gust)].arrival
                r[f"arrival_{nm}_min"] = float(a.iloc[0]) - 16 if len(a) else np.nan
                for t, t0 in (("gust", 16), ("p3", 19), ("p7", 23)):
                    x = d[(d.point == k) & (d.t0 == t0) & (d.schedule == f.schedule) & (d.ros == f.ros) & (d.gust == f.gust)].optimal
                    r[f"escape_{nm}_{t}"] = float(x.iloc[0]) if len(x) else np.nan
            rows.append(r)
E_ = pd.DataFrame(rows); E_["w"] = np.exp((E_.jaccard - E_.jaccard.max()) / 0.05)
E_.to_csv(os.path.join(M, "ensemble_all.csv"), index=False)
cols = ["arrival_range2_min", "arrival_roadhead_min", "escape_range2_gust", "escape_range2_p3", "escape_range2_p7", "escape_roadhead_gust", "escape_roadhead_p3", "escape_roadhead_p7"]
def summ(df, w=None):
    o = {}
    for c in cols:
        v = df[c].values; ww = np.ones(len(v)) if w is None else df[w].values; m = np.isfinite(v)
        if c.startswith("arrival"):
            vv, wv = v[m], ww[m]; k = np.argsort(vv); cw = np.cumsum(wv[k]) / wv.sum()
            o[c] = dict(median=round(float(vv[k][np.searchsorted(cw, .5)]), 1), p10=round(float(vv[k][np.searchsorted(cw, .1)]), 1), p90=round(float(vv[k][min(np.searchsorted(cw, .9), len(vv) - 1)]), 1))
        else: o[c] = round(float(np.average(v[m], weights=ww[m])) * 100)
    return o
out = {"n_fires": len(E_), "overall_equal": summ(E_), "overall_scar_weighted": summ(E_, "w"), "by": {}}
for dim in ("case", "front", "schedule", "ros", "shape"):
    out["by"][dim] = {str(k): summ(g) for k, g in E_.groupby(dim)}
json.dump(out, open(os.path.join(M, "ensemble_summary.json"), "w"), indent=1); print(json.dumps({k: out[k] for k in ("n_fires", "overall_equal", "overall_scar_weighted")}, indent=1))
