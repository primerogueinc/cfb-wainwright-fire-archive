"""Part 8b sensitivity: best ignition time for the best-fitting start (point and gun-target line) if pre-front spread
was faster than the calibrated model (multipliers 0.75-3 on head rate of spread before 12:17 only). Usage: python3 ignition_sensitivity.py REPO"""
import sys, json, os
import numpy as np, pandas as pd
REPO = sys.argv[1]
src = open(os.path.join(REPO, "scripts/authentic_stoic_alternative_hypothesis/part8/ignition_backcalc.py")).read().split("# candidates:")[0]
sys.argv = ["x", REPO, "80", "240"]; exec(src)
K0 = K
pt = cell(*tf(-110.92626, 52.77079))
line = set()
for dd in np.arange(1.4, 2.2001, RES / 2000):
    lo, la, _ = G.fwd(R11[0], R11[1], 80, dd * 1000); i, j = cell(*tf(lo, la))
    if fuel[i, j]: line.add((i, j))
rows = []
for mult in (0.75, 1.0, 1.5, 2.0, 3.0):
    MORNING_MULT = mult
    for name, st in (("point 2.15 km at 81 deg", [pt]), ("line 1.4-2.2 km at 80 deg", list(line))):
        for t0 in np.arange(-8, 12.01, 0.25):
            l1, l2, s, v = score(run(0, 0, t0, starts=st))
            rows.append(dict(ros_multiplier=mult, start=name, t0=t0, misfit_m=s, landsat_to_fire_m=l1, fire_edge_to_landsat_m=l2, viirs_misfit_m=v))
df = pd.DataFrame(rows)
best = df.loc[df.groupby(["ros_multiplier", "start"]).misfit_m.idxmin()].copy()
def hm(t): return f"{int(t % 24):02d}:{int(round((t % 1) * 60)) % 60:02d}" + (" Oct 16" if t < 0 else "")
best["best_ignition_mdt"] = best.t0.map(hm)
# window: times within 20 m of the best misfit
win = df.merge(best[["ros_multiplier", "start", "misfit_m"]].rename(columns={"misfit_m": "mbest"}), on=["ros_multiplier", "start"])
win = win[win.misfit_m <= win.mbest + 20].groupby(["ros_multiplier", "start"]).t0.agg(["min", "max"]).reset_index()
best = best.merge(win, on=["ros_multiplier", "start"]); best["window_mdt"] = best["min"].map(hm) + " to " + best["max"].map(hm)
out = os.path.join(REPO, "data/authentic-stoic-stress-test/part8b_ignition")
df.to_csv(os.path.join(out, "sensitivity_all.csv"), index=False)
best[["ros_multiplier", "start", "best_ignition_mdt", "window_mdt", "misfit_m", "landsat_to_fire_m", "fire_edge_to_landsat_m", "viirs_misfit_m"]].to_csv(os.path.join(out, "sensitivity_best.csv"), index=False)
print(best[["ros_multiplier", "start", "best_ignition_mdt", "window_mdt", "misfit_m", "landsat_to_fire_m", "fire_edge_to_landsat_m", "viirs_misfit_m"]].to_string(index=False))
