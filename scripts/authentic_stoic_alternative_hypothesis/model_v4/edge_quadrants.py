"""Working model v4: burned share by direction around the Range 2 point and the road head, for each edge_check.py classifier.
Usage: python3 edge_quadrants.py EDGE_DIR OUT_DIR. Ring 30-150 m, quadrants NE/SE/SW/NW; plus share burned within 150 m."""
import sys, os, glob, json, numpy as np
from pyproj import Transformer
ED, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
tf = Transformer.from_crs(4326, 3400, always_xy=True).transform
x0, y0, R, H, W = np.load(os.path.join(ED, "grid_meta.npy")); H, W = int(H), int(W)
yy, xx = np.mgrid[0:H, 0:W]; X = x0 + (xx + .5) * R; Y = y0 - (yy + .5) * R
P = {"Range 2 point": tf(-110.9063, 52.7728), "Road head": tf(-110.8996, 52.7705)}
out = {}
for f in sorted(glob.glob(os.path.join(ED, "*_20*.npy"))):
    b = np.load(f); r = {}
    for k, (px, py) in P.items():
        d = np.hypot(X - px, Y - py); az = (np.degrees(np.arctan2(X - px, Y - py)) + 360) % 360; ring = (d >= 30) & (d <= 150)
        r[k] = dict(burned_pct_30_150m_by_quadrant={n: round(float(b[ring & (az >= a) & (az < a + 90)].mean() * 100)) for n, a in (("NE", 0), ("SE", 90), ("SW", 180), ("NW", 270))},
                    burned_pct_within_150m=round(float(b[d <= 150].mean() * 100)))
    out[os.path.basename(f)[:-4]] = r
json.dump(out, open(os.path.join(OUT, "edge_quadrants.json"), "w"), indent=1); print(json.dumps(out)[:400])
