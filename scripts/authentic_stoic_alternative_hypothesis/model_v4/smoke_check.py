"""Where was the smoke at 12:17 p.m.? Landsat 8 (Oct. 17) check of the smoke model's direction.
Usage: python3 smoke_check.py LANDSAT_REPO OUT_DIR
Smoke scatters red light (B4) but is nearly transparent at 1.6 um (B6); cloud is bright in both. So
smoke index = B4 - a*B6, with a fitted over the scene so that cloud/ground cancel (least squares), and we compare it in
30-degree sectors 0.5-4 km from the fire's middle. If the model is right the excess sits to the northeast (downwind of
a ~200-220 deg wind), not to the southeast where Range 2 is."""
import sys, os, re, json
import numpy as np, rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer
LS, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
P = f"{LS}/landsat/2026-10-17/LC08_L1TP_040023_20261017_20261021_02_T1/LC08_L1TP_040023_20261017_20261021_02_T1_"
mtl = open(P + "MTL.txt").read(); g = lambda k: float(re.search(k + r" = ([-\d.E+]+)", mtl).group(1))
se = np.radians(g("SUN_ELEVATION"))
r = rasterio.open(P + "B4.TIF"); tf = Transformer.from_crs(4326, r.crs, always_xy=True).transform
cx, cy = tf(-110.926, 52.775)                                  # middle of the 12:17 burned strip
w = from_bounds(cx - 8000, cy - 8000, cx + 8000, cy + 8000, r.transform); tr = rasterio.windows.transform(w, r.transform)
def refl(n):
    a = rasterio.open(P + f"B{n}.TIF").read(1, window=w).astype(float); a[a == 0] = np.nan
    return (a * g(f"REFLECTANCE_MULT_BAND_{n}") + g(f"REFLECTANCE_ADD_BAND_{n}")) / np.sin(se)
b4, b6, b7, b5 = refl(4), refl(6), refl(7), refl(5)
ny, nx = b4.shape; yy, xx = np.mgrid[0:ny, 0:nx]; X = tr.c + (xx + .5) * tr.a; Y = tr.f + (yy + .5) * tr.e
d = np.hypot(X - cx, Y - cy); az = (np.degrees(np.arctan2(X - cx, Y - cy)) + 360) % 360
fire = (b7 / b5 > 1.5)
bg = (d > 4000) & np.isfinite(b4) & np.isfinite(b6)
a = np.linalg.lstsq(np.c_[b6[bg], np.ones(bg.sum())], b4[bg], rcond=None)[0]
si = b4 - (a[0] * b6 + a[1])
ring = (d >= 500) & (d <= 4000) & ~fire & np.isfinite(si)
out = {f"{s}-{s+30}": round(float(np.nanmedian(si[ring & (az >= s) & (az < s + 30)])) * 1000, 2) for s in range(0, 360, 30)}
# remove the ground: same index on the clear Oct. 24 scene (path 41), reprojected; exclude the final scar (ground changed)
from rasterio.warp import reproject, Resampling
import geopandas as gpd
from rasterio.features import geometry_mask
P2 = f"{LS}/landsat/2026-10-24/LC08_L1TP_041023_20261024_20261024_02_RT/LC08_L1TP_041023_20261024_20261024_02_RT_"
mtl2 = open(P2 + "MTL.txt").read(); g2 = lambda k: float(re.search(k + r" = ([-\d.E+]+)", mtl2).group(1))
def refl2(n):
    s_ = rasterio.open(P2 + f"B{n}.TIF"); a_ = s_.read(1).astype("float32"); a_[a_ == 0] = np.nan
    a_ = (a_ * g2(f"REFLECTANCE_MULT_BAND_{n}") + g2(f"REFLECTANCE_ADD_BAND_{n}")) / np.sin(np.radians(g2("SUN_ELEVATION")))
    o = np.full(b4.shape, np.nan, "float32"); reproject(a_, o, src_transform=s_.transform, src_crs=s_.crs, dst_transform=tr, dst_crs=r.crs, resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan); return o
c4, c6 = refl2(4), refl2(6)
bg2 = bg & np.isfinite(c4) & np.isfinite(c6)
a2 = np.linalg.lstsq(np.c_[c6[bg2], np.ones(bg2.sum())], c4[bg2], rcond=None)[0]
si24 = c4 - (a2[0] * c6 + a2[1])
scar = gpd.read_file(os.path.join(os.path.dirname(__file__), "../../../data/copernicus/burn_scar.geojson")).to_crs(r.crs)
inscar = ~geometry_mask(list(scar.buffer(200).geometry), b4.shape, tr)
dsi = si - si24
ring2 = (d >= 500) & (d <= 4000) & ~fire & ~inscar & np.isfinite(dsi)
out2 = {f"{s}-{s+30}": round(float(np.nanmedian(dsi[ring2 & (az >= s) & (az < s + 30)])) * 1000, 2) for s in range(0, 360, 30)}
res = dict(fit_oct24=[round(float(v), 4) for v in a2], smoke_minus_ground_x1000_by_sector_0p5_4km_outside_scar=out2,
           n_pixels={f"{s}-{s+30}": int((ring2 & (az >= s) & (az < s + 30)).sum()) for s in range(0, 360, 30)}, fit=[round(float(v), 4) for v in a], smoke_index_x1000_by_sector_0p5_4km=out,
           note="positive = more red light than the cloud/ground relationship predicts (smoke); Range 2 lies ~100-120 deg from the strip's middle")
json.dump(res, open(os.path.join(OUT, "smoke_check_landsat_1217.json"), "w"), indent=1); print(json.dumps(res, indent=1))
np.save(os.path.join(OUT, "smoke_index_1217.npy"), si.astype("float32")); np.save(os.path.join(OUT, "smoke_index_1217_transform.npy"), np.array(tr)[:6])
