"""Working model v4, step 4: arrival and escape odds with the 30 post-front fires weighted by how well each matches the final scar.
Usage: python3 weighted.py REPO
Weight per fire (per case) = exp((jaccard - best) / 0.05), from fit_post/fit_post_all.csv (overlap with the mapped scar when the
fire's area equals the scar's). 0.05 is about the spread between runs that differ only in spread rate; a fire 0.05 below the
best counts 37% as much, 0.10 below 14%. Unweighted figures (as in v3) are given alongside."""
import sys, os, json, numpy as np, pandas as pd
REPO = sys.argv[1]; M = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4")
fit = pd.read_csv(os.path.join(M, "fit_post/fit_post_all.csv"))
fit["w"] = np.exp((fit.jaccard - fit.jaccard.max()) / 0.05)
out = {"weights_by_schedule": fit.groupby("schedule").w.sum().div(fit.w.sum()).round(3).to_dict(),
       "weights_by_ros": fit.groupby("ros").w.sum().div(fit.w.sum()).round(3).to_dict(), "cases": {}}
def wq(v, w, q):
    o = np.argsort(v); v, w = np.asarray(v)[o], np.asarray(w)[o]; c = np.cumsum(w) / w.sum(); return float(v[np.searchsorted(c, q)])
rows = []
for case in sorted(fit.case.unique()):
    f = fit[fit.case == case][["schedule", "ros", "gust", "w"]]
    d = pd.read_csv(os.path.join(M, case, "escape_clock.csv"))
    g = d.grid.str.extract(r"\('(\w+)', ([\d.]+), '(\w+)'\)"); d["schedule"], d["ros"], d["gust"] = g[0], g[1].astype(float), g[2]
    d = d.merge(f, on=["schedule", "ros", "gust"])
    pm = pd.read_csv(os.path.join(M, case, "escape_perm.csv.gz")); pm = pm[pm.cue != "FAN"].drop_duplicates(["point", "schedule", "ros", "gust"]).merge(f, on=["schedule", "ros", "gust"])
    for k in "AB":
        x = d[(d.point == k) & (d.speed == "jog in kit (8 km/h)")]; a = pm[pm.point == k]
        r = dict(case=case, point=k)
        for lab, ww in (("unweighted", None), ("weighted", "w")):
            W_ = (lambda s: np.ones(len(s))) if ww is None else (lambda s: s.w.values)
            r[f"arrival_median_{lab}"] = round(wq(a.arrival - 16, W_(a), 0.5), 1)
            for t0, nm in ((16, "gust"), (19, "plus3"), (23, "plus7")):
                s = x[x.t0 == t0]; r[f"escape_{nm}_{lab}"] = round(float(np.average(s.optimal, weights=W_(s))) * 100)
        rows.append(r)
df = pd.DataFrame(rows); df.to_csv(os.path.join(M, "weighted_summary.csv"), index=False)
out["by_point_across_cases"] = {p: {c: [float(g[c].min()), float(g[c].max())] for c in g.columns if c not in ("case", "point")} for p, g in df.groupby("point")}
json.dump(out, open(os.path.join(M, "weighted_summary.json"), "w"), indent=1, default=str)
pd.set_option("display.width", 250); print(json.dumps({k: out[k] for k in ("weights_by_schedule", "weights_by_ros")}, indent=1)); print(df.to_string(index=False))
