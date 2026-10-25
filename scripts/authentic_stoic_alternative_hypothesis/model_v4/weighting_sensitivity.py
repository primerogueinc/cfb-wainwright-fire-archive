"""Working model v4: how much do the results depend on the weighting of post-front fires by fit to the final scar?
Usage: python3 weighting_sensitivity.py REPO [TAG]
Weight = exp((jaccard - best) / s) for s = 0.02, 0.05 (used), 0.10, 0.20, and equal weights. For each: share of weight by wind
schedule, and weighted escape odds (Range 2 area and road head, jogging, optimal route) at the gust, +3 and +7 minutes."""
import sys, os, json, numpy as np, pandas as pd
REPO = sys.argv[1]; TAG = sys.argv[2] if len(sys.argv) > 2 else ""; SFX = f"_{TAG}" if TAG else ""
M = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4"); fit = pd.read_csv(os.path.join(M, f"fit_post{SFX}/fit_post_all.csv"))
clk = []
for case in fit.case.unique():
    d = pd.read_csv(os.path.join(M, case + SFX, "escape_clock.csv")); g = d.grid.str.extract(r"\('(\w+)', ([\d.]+), '(\w+)'\)")
    d["schedule"], d["ros"], d["gust"], d["case"] = g[0], g[1].astype(float), g[2], case; clk.append(d)
clk = pd.concat(clk); clk = clk[clk.speed == "jog in kit (8 km/h)"]
out = {}
for lab, s in (("s0.02", .02), ("s0.05", .05), ("s0.10", .10), ("s0.20", .20), ("equal", None)):
    w = np.ones(len(fit)) if s is None else np.exp((fit.jaccard - fit.jaccard.max()) / s)
    f = fit.assign(w=w); x = clk.merge(f[["case", "schedule", "ros", "gust", "w"]], on=["case", "schedule", "ros", "gust"])
    r = {"schedule_share": f.groupby("schedule").w.sum().div(f.w.sum()).round(3).to_dict()}
    for k, nm in (("A", "Range 2 area"), ("B", "road head")):
        r[nm] = {t: round(float(np.average(x[(x.point == k) & (x.t0 == t0)].optimal, weights=x[(x.point == k) & (x.t0 == t0)].w)) * 100) for t, t0 in (("gust", 16), ("+3", 19), ("+7", 23))}
    out[lab] = r
json.dump(out, open(os.path.join(M, f"weighting_sensitivity{SFX}.json"), "w"), indent=1); print(json.dumps(out, indent=1))
