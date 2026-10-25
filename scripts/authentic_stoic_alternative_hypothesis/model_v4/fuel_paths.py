"""Working model v4, H2/H3 test: was the ground the fire crept across before 3:16 p.m. patchier, barer or greener than the ground
it ran across after? Usage: python3 fuel_paths.py REPO COPERNICUS_REPO
Pre-fire Sentinel-2 L2A, Oct. 4 (clear), resampled to 10 m (EPSG:3400). Zones:
  morning   burned by 12:17 p.m. (Landsat central class)
  midday    burned 12:17-3:16 p.m. (v4 starting fire for the post-front runs, case v4b, minus the morning zone)
  afternoon burned after 3:16 p.m. (mapped final scar minus the above)
  unburned  within 1 km of the scar, outside it
Measures: NDVI (B8A/B04; green-ness), NBR (B8A/B12), share of bare ground (NDVI < 0.20), share of old burn (pre-fire NBR < 0.0
on vegetated ground, i.e. dark in shortwave infrared, as in the old scars visible on Oct. 4), and patchiness: the share of
100 x 100 m blocks in which more than 20% of pixels are bare or old burn (gaps a slow fire must cross)."""
import sys, os, json, numpy as np, rasterio, geopandas as gpd
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from rasterio.features import geometry_mask
REPO, CP = sys.argv[1], sys.argv[2] + "/sentinel-2/"
M = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4")
scar = gpd.read_file(os.path.join(REPO, "data/copernicus/burn_scar.geojson")).to_crs(3400)
x0, y0, x1, y1 = scar.total_bounds; x0 -= 1200; y0 -= 1200; x1 += 1200; y1 += 1200; R = 10
W, H = int((x1 - x0) / R), int((y1 - y0) / R); T = from_origin(x0, y1, R, R)
def get(path, rs=Resampling.bilinear):
    s = rasterio.open(path); o = np.full((H, W), np.nan, "float32")
    reproject(rasterio.band(s, 1), o, dst_transform=T, dst_crs="EPSG:3400", resampling=rs, dst_nodata=np.nan); return o
b = lambda n: get(f"{CP}2026-10-04/L2A_tiff/2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L2A_{n}_(Raw).tiff")
nir, red, sw2, grn = b("B8A"), b("B04"), b("B12"), b("B03")
ndvi = (nir - red) / (nir + red); nbr = (nir - sw2) / (nir + sw2); water = (grn - nir) / (grn + nir) > 0.05
morning = get("/home/claude/cfb-wainwright-landsat-8-9/analysis/2026-10-17/burned_1217_classes.tif", Resampling.nearest) >= 2
SP = os.path.join(os.environ.get("P4ROOT", "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/"), "p4_v4_v4b_2x_lb3.0_0500/")
mx, my, mr, mh, mw = np.load(SP + "meta.npy"); st = np.zeros((H, W), "float32")
reproject(np.load(SP + "start316.npy").astype("float32"), st, src_transform=from_origin(mx, my, mr, mr), src_crs="EPSG:3400", dst_transform=T, dst_crs="EPSG:3400", resampling=Resampling.nearest)
insc = ~geometry_mask(list(scar.geometry), (H, W), T); near = ~geometry_mask(list(scar.buffer(1000).geometry), (H, W), T) & ~insc
zones = {"morning (by 12:17)": morning & ~water, "midday (12:17-3:16)": (st > .5) & ~morning & ~water, "afternoon (after 3:16)": insc & ~(st > .5) & ~morning & ~water, "unburned (within 1 km)": near & ~water}
bare = ndvi < 0.20; old = (nbr < 0.0) & ~bare; gap = bare | old
# patchiness on 100 m blocks
k = 10; Hb, Wb = H // k, W // k
blk = lambda a: a[:Hb * k, :Wb * k].reshape(Hb, k, Wb, k).mean((1, 3))
gapb = blk(gap.astype(float)) > 0.20
out = {}
for name, z in zones.items():
    zb = blk(z.astype(float)) > 0.5
    out[name] = dict(km2=round(float(z.sum()) * R * R / 1e6, 2), ndvi_median=round(float(np.nanmedian(ndvi[z])), 3), nbr_median=round(float(np.nanmedian(nbr[z])), 3),
                     bare_pct=round(float(bare[z].mean()) * 100, 1), old_burn_pct=round(float(old[z].mean()) * 100, 1), patchy_blocks_pct=round(float(gapb[zb].mean()) * 100, 1))
json.dump(out, open(os.path.join(M, "fuel_paths.json"), "w"), indent=1); print(json.dumps(out, indent=1))
