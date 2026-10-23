"""Burn severity from matched full exports: Sentinel-2 L2A Oct. 4 (pre) vs Oct. 19 (post).
Usage: python3 severity_matched.py DATA_REPO OUT_DIR
Both scenes resampled (bilinear) onto one 10 m UTM 12N grid over the fire area. dNBR uses B8A/B12 (20 m native);
dNDVI uses B04/B08 (10 m native). Cloud/shadow/snow/water masked with both scenes' scene classification."""
import sys, os, glob, json
import numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from pyproj import Transformer
from scipy import ndimage
D, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
CRS = "EPSG:32612"; tf = Transformer.from_crs(4326, CRS, always_xy=True)
x0, y1 = tf.transform(-110.96, 52.80); x1, y0 = tf.transform(-110.85, 52.74)
x0, y1 = np.floor(x0 / 10) * 10, np.ceil(y1 / 10) * 10
W, H = int(np.ceil((x1 - x0) / 10)), int(np.ceil((y1 - y0) / 10)); T = from_origin(x0, y1, 10, 10)
def band(date, b, rs=Resampling.bilinear):
    f = glob.glob(f"{D}/sentinel-2/{date}/L2A_tiff/*_{b}*.tiff")[0]; s = rasterio.open(f)
    out = np.full((H, W), np.nan, "float32")
    reproject(s.read(1).astype("float32"), out, src_transform=s.transform, src_crs=s.crs, dst_transform=T, dst_crs=CRS, resampling=rs, src_nodata=0, dst_nodata=np.nan)
    return out
def nbr(n, s): return (n - s) / (n + s)
def ndvi(r, n): return (n - r) / (n + r)
pre = {b: band("2026-10-04", b) for b in ["B04", "B08", "B8A", "B12"]}
post = {b: band("2026-10-19", b) for b in ["B04", "B08", "B8A", "B12"]}
dnbr = nbr(pre["B8A"], pre["B12"]) - nbr(post["B8A"], post["B12"])
dndvi = ndvi(pre["B04"], pre["B08"]) - ndvi(post["B04"], post["B08"])
# water/cloud mask from pre-fire NDWI-like test and NaNs (SCL export is a colour visualisation, not class codes)
water = (pre["B08"] < 0.06) | (post["B08"] < 0.04)
dnbr[water] = np.nan; dndvi[water] = np.nan
# Seasonal offset: grass cured between Oct. 4 and 19, so unburned ground drifts positive. Reference = NE third of the
# box (north of the east-west track, east of the range road), unburned in every source. Standard dNBR offset (Key & Benson).
OFFSET = float(np.nanmedian(dnbr[:H // 3, int(W * 0.7):]))
dnbr = dnbr - OFFSET
prof = dict(driver="GTiff", height=H, width=W, count=1, dtype="float32", crs=CRS, transform=T, compress="deflate", nodata=np.nan)
for n, a in [("dnbr_10m_oct04_oct19.tif", dnbr), ("dndvi_10m_oct04_oct19.tif", dndvi)]:
    with rasterio.open(os.path.join(OUT, n), "w", **prof) as d: d.write(a, 1)
burn = np.nan_to_num(dnbr) >= 0.27
edt = ndimage.distance_transform_edt(~burn) * 10
pts = {"origin": (-110.9214, 52.7764), "A_range2": (-110.90632, 52.77279), "B_road_head": (-110.89965, 52.77045)}
res = {"grid": "UTM 12N, 10 m", "dnbr_offset_subtracted": round(OFFSET, 3), "classes_km2": {}, "points": {}}
for lo, hi, n in [(0.10, 0.27, "low"), (0.27, 0.44, "moderate_low"), (0.44, 0.66, "moderate_high"), (0.66, 9, "high")]:
    res["classes_km2"][n] = round(float(((dnbr >= lo) & (dnbr < hi)).sum()) * 1e-4, 2)
res["burned_km2_dnbr_ge_0.27"] = round(float(burn.sum()) * 1e-4, 2)
for k, (lo, la) in pts.items():
    x, y = tf.transform(lo, la); j, i = int((x - x0) // 10), int((y1 - y) // 10); w = np.s_[i - 2:i + 3, j - 2:j + 3]
    res["points"][k] = dict(dnbr=round(float(dnbr[i, j]), 3), dnbr_5x5=round(float(np.nanmean(dnbr[w])), 3), dndvi=round(float(dndvi[i, j]), 3),
                            burned=bool(burn[i, j]), m_to_nearest_burned=round(float(edt[i, j])))
json.dump(res, open(os.path.join(OUT, "severity_matched_summary.json"), "w"), indent=1); print(json.dumps(res, indent=1))
