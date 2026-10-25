"""Working model v4: where was the fire 'just before 4:00'? (Oct. 22 briefing: "Just before 4:00 local time, uncommonly high
winds took a pre-existing range fire towards the pairs range and it overtook their position.")
Usage: python3 overtaken_time.py REPO P4_DIR_PREFIX
For every post-front fire (4 cases x 30), weighted by its fit to the final scar (weighted.py), the share of fires reaching
each point, and the likely ground of part 2, in three windows: 3:16-3:30, 3:30-3:45, 3:45-4:00 p.m."""
import sys, os, glob, json, numpy as np, pandas as pd
from pyproj import Transformer
REPO, P4 = sys.argv[1], sys.argv[2]
M = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4")
fit = pd.read_csv(os.path.join(M, "fit_post/fit_post_all.csv")); fit["w"] = np.exp((fit.jaccard - fit.jaccard.max()) / 0.05)
tf = Transformer.from_crs(4326, 3400, always_xy=True).transform
PTS = {"Range 2 point": (-110.9063, 52.7728), "Road head": (-110.8996, 52.7705), "C": (-110.9160, 52.7640), "D": (-110.8995, 52.7628), "E": (-110.8990, 52.7530)}
zone = pd.read_csv(os.path.join(REPO, "data/authentic-stoic-stress-test/part2/part2_core_frequency.csv")); zone = zone[zone.n_scenarios_in_core > 0]
WIN = {"3:16-3:30": (16, 30), "3:30-3:45": (30, 45), "3:45-4:00": (45, 60), "after 4:00": (60, 1e9)}
rows, zrows, maps = [], [], {}
for d in sorted(glob.glob(P4 + "*")):
    case = os.path.basename(d)[len(os.path.basename(P4)):]
    minx, maxy, RES, H, W = np.load(os.path.join(d, "meta.npy")); H, W = int(H), int(W)
    idx = lambda lo, la: (int((maxy - tf(lo, la)[1]) // RES), int((tf(lo, la)[0] - minx) // RES))
    zi = np.array([idx(x, y) for x, y in zip(zone.x, zone.y)])
    for f in sorted(glob.glob(os.path.join(d, "arr_*.npy"))):
        run = os.path.basename(f)[4:-4]; A = np.load(f)
        w = float(fit[(fit.case == case) & (fit.run == run)].w.iloc[0])
        r = dict(case=case, run=run, w=w)
        for k, (lo, la) in PTS.items(): r[k] = float(A[idx(lo, la)])
        rows.append(r)
        za = A[zi[:, 0], zi[:, 1]]
        for lab, (a, b) in WIN.items():
            zrows.append(dict(case=case, run=run, w=w, window=lab, zone_share=float(np.average((za >= a) & (za < b), weights=zone.n_scenarios_in_core))))
        for lab, (a, b) in WIN.items():
            m = ((A >= a) & (A < b)).astype("float32") * w
            maps[lab] = maps.get(lab, 0) + m
        maps["_w"] = maps.get("_w", 0) + w
df = pd.DataFrame(rows); z = pd.DataFrame(zrows)
out = {"points_weighted_share_by_window": {}, "zone_weighted_share_by_window": {}}
for k in PTS:
    out["points_weighted_share_by_window"][k] = {lab: round(float(df.w[(df[k] >= a) & (df[k] < b)].sum() / df.w.sum()), 3) for lab, (a, b) in WIN.items()}
    o = np.argsort(df[k].values); c = np.cumsum(df.w.values[o]) / df.w.sum(); m = float(df[k].values[o][np.searchsorted(c, .5)])
    out["points_weighted_share_by_window"][k]["median_arrival_clock"] = f"3:{int(m):02d}" if m < 60 else f"4:{int(m - 60):02d}"   # weighted median
for lab in WIN: out["zone_weighted_share_by_window"][lab] = round(float(np.average(z[z.window == lab].zone_share, weights=z[z.window == lab].w)), 3)
json.dump(out, open(os.path.join(M, "overtaken_time.json"), "w"), indent=1); print(json.dumps(out, indent=1))
np.savez_compressed(os.path.join(os.path.dirname(P4), "v4", "overtaken_maps.npz"), **{k.replace(":", "").replace("-", "_").replace(" ", "_"): v for k, v in maps.items()}, meta=np.array([minx, maxy, RES, H, W]))
