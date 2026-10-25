"""v4 edge check: is the burn edge by Range 2 and the road head the same on three independent images?
Usage: python3 edge_check.py COPERNICUS_REPO LANDSAT_REPO OUT_DIR
Each image is classified burned/unburned on its own native grid, then resampled to a common 10 m grid (EPSG:3400):
  S2-20m: Sentinel-2 dNBR (B8A/B12, 20 m) Oct 4 -> Oct 19, and Oct 4 -> Oct 24; burned = dNBR >= 0.27 (the scar threshold)
  S2-10m: Sentinel-2 red-band darkening (B04, 10 m), Oct 4 -> date; burned = red reflectance fell by >= 30%
  L8-30m: Landsat 8 Oct 24 NBR (B5/B7, 30 m), burned = NBR <= -0.08 (midway between scar -0.27 and surroundings +0.11)
For each: is the Range 2 point / road head pixel burned, distance from each point to the nearest unburned ground
(within the pocket northeast of them), and the pocket's area (unburned, connected, within 600 m of the two points)."""
import sys, os, json, re
import numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from scipy import ndimage
from pyproj import Transformer
CP, LS, OUT = sys.argv[1] + "/sentinel-2/", sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
tf = Transformer.from_crs(4326, 3400, always_xy=True).transform
P = {"Range 2 point": tf(-110.9063, 52.7728), "Road head": tf(-110.8996, 52.7705)}
cx, cy = np.mean([p[0] for p in P.values()]), np.mean([p[1] for p in P.values()])
RES, HALF = 10, 1500; W = H = 2 * HALF // RES; T = from_origin(cx - HALF, cy + HALF, RES, RES)
def grid(path, rs=Resampling.bilinear, scale=None):
    s = rasterio.open(path); o = np.full((H, W), np.nan, "float32")
    src = s.read(1).astype("float32")
    if scale: src = scale(src)
    reproject(src, o, src_transform=s.transform, src_crs=s.crs, dst_transform=T, dst_crs="EPSG:3400", resampling=rs, src_nodata=np.nan); return o
s2 = lambda d, b: f"{CP}{d}/L2A_tiff/{d}-00_00_{d}-23_59_Sentinel-2_L2A_{b}.tiff"
def nbr_s2(d): n, s = grid(s2(d, "B8A_(Raw)")), grid(s2(d, "B12_(Raw)")); return (n - s) / (n + s)
pre_nbr, pre_red = nbr_s2("2026-10-04"), grid(s2("2026-10-04", "B04_(Raw)"))
maps = {}
for d in ("2026-10-19", "2026-10-24"):
    maps[f"S2 20 m dNBR {d}"] = (pre_nbr - nbr_s2(d)) >= 0.27
    maps[f"S2 10 m red darkening {d}"] = (grid(s2(d, "B04_(Raw)")) / pre_red) <= 0.70
L = f"{LS}/landsat/2026-10-24/LC08_L1TP_041023_20261024_20261024_02_RT/LC08_L1TP_041023_20261024_20261024_02_RT_"
mtl = open(L + "MTL.txt").read(); g = lambda k: float(re.search(k + r" = ([-\d.E+]+)", mtl).group(1))
def lref(n):
    m, a = g(f"REFLECTANCE_MULT_BAND_{n}"), g(f"REFLECTANCE_ADD_BAND_{n}")
    return grid(L + f"B{n}.TIF", Resampling.nearest, lambda x: np.where(x == 0, np.nan, x * m + a))
b5, b7 = lref(5), lref(7); maps["Landsat 30 m NBR 2026-10-24"] = ((b5 - b7) / (b5 + b7)) <= -0.08
yy, xx = np.mgrid[0:H, 0:W]; X = cx - HALF + (xx + .5) * RES; Y = cy + HALF - (yy + .5) * RES
near = np.hypot(X - cx, Y - cy) <= 600
res = {}
for k, burned in maps.items():
    unb = ~burned
    lab, n = ndimage.label(unb & near)
    r = {}
    for name, (px, py) in P.items():
        i, j = int((cy + HALF - py) // RES), int((px - (cx - HALF)) // RES)
        d = np.hypot(X - px, Y - py); d_unb = float(d[unb & near].min()) if (unb & near).any() else None
        r[name] = dict(burned=bool(burned[i, j]), nearest_unburned_m=round(d_unb) if d_unb is not None else None)
    # pocket: the unburned component touching the road head or nearest to it
    i, j = int((cy + HALF - P["Road head"][1]) // RES), int((P["Road head"][0] - (cx - HALF)) // RES)
    if lab[i, j] > 0: pk = lab == lab[i, j]
    else:
        dd = np.where(lab > 0, np.hypot(X - P["Road head"][0], Y - P["Road head"][1]), np.inf); pk = lab == lab.flat[np.argmin(dd)]
    r["pocket_ha_within_600m"] = round(float(pk.sum() * RES * RES / 1e4), 1)
    res[k] = r
    np.save(os.path.join(OUT, re.sub(r"\W+", "_", k) + ".npy"), burned)
json.dump(res, open(os.path.join(OUT, "edge_check.json"), "w"), indent=1); print(json.dumps(res, indent=1))
np.save(os.path.join(OUT, "grid_meta.npy"), np.array([cx - HALF, cy + HALF, RES, H, W]))
