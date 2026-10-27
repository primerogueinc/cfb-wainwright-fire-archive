"""Sentinel-1 change, Oct. 14 (pre-fire) vs Oct. 19 (post-fire), VV and VH, on the 10 m severity grid.
Usage: python3 change_oct14_oct19.py S1_REPO ARCHIVE_REPO"""
import sys, os, glob, json
import numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from scipy import ndimage
from pyproj import Transformer
S1, AR = sys.argv[1], sys.argv[2]
OUT = os.path.join(AR, "data/sentinel1/change_oct14_oct19"); os.makedirs(OUT, exist_ok=True)
sev = rasterio.open(os.path.join(AR, "data/copernicus/severity_matched_10m/dnbr_10m_oct04_oct19.tif")); d = sev.read(1)
def get(date, p):
    f = glob.glob(f"{S1}/sentinel-1/{date}/IW_VV_VH/*_{p}_(Raw).tiff")[0]; s = rasterio.open(f)
    o = np.full(d.shape, np.nan, "float32")
    reproject(s.read(1), o, src_transform=s.transform, src_crs=s.crs, dst_transform=sev.transform, dst_crs=sev.crs,
              resampling=Resampling.average, src_nodata=0, dst_nodata=np.nan)
    return o
res = {"note": "dB change = 10*log10(post/pre); 3x3 mean filter before ratio to reduce speckle. Burn mask from Sentinel-2 matched dNBR (>=0.27 burned, <0.05 unburned).", "bands": {}}
burn, unb = d >= 0.27, d < 0.05
ch = {}
for p in ["VV", "VH"]:
    pre, post = get("2026-10-14", p), get("2026-10-19", p)
    pre_f, post_f = ndimage.uniform_filter(np.nan_to_num(pre), 3), ndimage.uniform_filter(np.nan_to_num(post), 3)
    c = 10 * np.log10(post_f / pre_f); c[~np.isfinite(c)] = np.nan; ch[p] = c
    res["bands"][p] = {k: {"pre_dB": round(float(np.nanmedian(10 * np.log10(pre[m]))), 2), "post_dB": round(float(np.nanmedian(10 * np.log10(post[m]))), 2),
                           "change_dB": round(float(np.nanmedian(c[m])), 2)} for k, m in [("burned", burn), ("unburned", unb)]}
    prof = dict(driver="GTiff", height=d.shape[0], width=d.shape[1], count=1, dtype="float32", crs=sev.crs, transform=sev.transform, compress="deflate", nodata=np.nan)
    with rasterio.open(os.path.join(OUT, f"s1_{p.lower()}_change_db_oct14_oct19.tif"), "w", **prof) as o: o.write(c.astype("float32"), 1)
tf = Transformer.from_crs(4326, sev.crs, always_xy=True)
res["points"] = {}
for k, (lo, la) in {"origin": (-110.9214, 52.7764), "A_range2": (-110.90632, 52.77279), "B_road_head": (-110.89965, 52.77045)}.items():
    x, y = tf.transform(lo, la); i, j = sev.index(x, y); w = np.s_[i - 1:i + 2, j - 1:j + 2]
    res["points"][k] = {p: round(float(np.nanmean(ch[p][w])), 2) for p in ch}
# agreement: radar-darkened (VH change <= -1.5 dB) vs optical burn
rad = ch["VH"] <= -1.5
res["agreement"] = {"optical_burned_also_radar_darkened_pct": round(float(np.nanmean(rad[burn])) * 100, 1),
                    "optical_unburned_radar_darkened_pct": round(float(np.nanmean(rad[unb])) * 100, 1)}
json.dump(res, open(os.path.join(OUT, "summary.json"), "w"), indent=1); print(json.dumps(res, indent=1))
