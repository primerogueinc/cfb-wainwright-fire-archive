"""Working model v4, H0 loose end: did the fire's head run into water or a clearing between 12:17 and 2:49 p.m.?
Usage: python3 pond_stall.py REPO COPERNICUS_REPO
From the Landsat 12:17 north-east tip, along bearings 30-60 deg (the head's direction of travel), distance to the first
pre-fire (Oct. 4 Sentinel-2) water (NDWI > 0.05) or bare ground (NDVI < 0.20) at least 30 m wide. If the barrier is about as far as
the measured advance (1.08 km), the head was stopped and 0.43 km/h is a lower bound on its speed; the fire-energy check (h0_speed_check)
then carries the H0 test. Also: at the standard rate (2.5 km/h) the head would reach the barrier in N minutes."""
import sys, os, json, numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from pyproj import Transformer, Geod
REPO, CP = sys.argv[1], sys.argv[2] + "/sentinel-2/"; G = Geod(ellps="WGS84")
tf = Transformer.from_crs(4326, 3400, always_xy=True).transform
tip = (-110.91173, 52.78011); tx, ty = tf(*tip); R = 10; HALF = 3000
T = from_origin(tx - HALF, ty + HALF, R, R); N = 2 * HALF // R
def get(b):
    s = rasterio.open(f"{CP}2026-10-04/L2A_tiff/2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L2A_{b}_(Raw).tiff"); o = np.full((N, N), np.nan, "float32")
    reproject(rasterio.band(s, 1), o, dst_transform=T, dst_crs="EPSG:3400", resampling=Resampling.bilinear, dst_nodata=np.nan); return o
g3, n8, r4 = get("B03"), get("B8A"), get("B04")
barrier = ((g3 - n8) / (g3 + n8) > 0.05) | ((n8 - r4) / (n8 + r4) < 0.20)
rows = {}
for b in range(30, 61, 5):
    run = 0; dist = None
    for d in np.arange(0, 2900, R):
        x = tx + d * np.sin(np.radians(b)); y = ty + d * np.cos(np.radians(b)); i, j = int((ty + HALF - y) // R), int((x - (tx - HALF)) // R)
        run = run + R if barrier[i, j] else 0
        if run >= 30: dist = int(d - run + R); break
    rows[str(b)] = dict(first_barrier_m=dist, minutes_at_standard_2p5kmh=None if dist is None else round(dist / 2500 * 60), minutes_at_measured_0p43=None if dist is None else round(dist / 430 * 60))
out = dict(measured_advance_along_axis_m=1081, by_bearing_deg=rows)
json.dump(out, open(os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4/pond_stall.json"), "w"), indent=1); print(json.dumps(out, indent=1))
