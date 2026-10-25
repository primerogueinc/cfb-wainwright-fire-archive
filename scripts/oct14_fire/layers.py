"""Oct. 14 fire: build the layers. Burn new between Sentinel-2 (Oct. 4, L2A) and Landsat 9 (Oct. 16, L1TP TOA), water, older burns, roads.
Usage: python3 layers.py REPO LANDSAT_DIR OUTDIR
NBR = (NIR - SWIR2)/(NIR + SWIR2): Sentinel-2 B8A/B12, Landsat 9 B5/B7 (TOA reflectance, MTL scaling 2e-5, -0.1).
The two sensors differ, so each date is thresholded on its own (burned: Oct. 4 NBR < -0.05; Oct. 16 NBR < 0.06; sensitivity
-0.08/0.05 and -0.02/0.07) and the new burn is burned on Oct. 16 but not within 30 m of ground burned on Oct. 4. The component(s)
within 500 m of the Oct. 14 VIIRS detection are the Oct. 14 burn."""
import sys, os, glob, json, numpy as np, rasterio, geopandas as gpd
from rasterio import features
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from pyproj import Transformer
from scipy import ndimage
REPO, LDIR, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
CRS = "EPSG:3400"; tf = Transformer.from_crs(4326, CRS, always_xy=True).transform
VI = (-110.93891, 52.75486)  # NOAA-21 VIIRS, 14:51 MDT Oct. 14
cx, cy = tf(-110.945, 52.752); RES = 30; N = 240  # 7.2 km window
T = from_origin(cx - N * RES / 2, cy + N * RES / 2, RES, RES)
def rp(path, scale=1.0, add=0.0):
    with rasterio.open(path) as r:
        d = np.zeros((N, N), "float32")
        reproject(r.read(1).astype("float32") * scale + add, d, src_transform=r.transform, src_crs=r.crs, dst_transform=T, dst_crs=CRS, resampling=Resampling.average)
    return d
L = glob.glob(os.path.join(LDIR, "*B7.TIF"))[0].replace("B7.TIF", "B%s.TIF")
S = os.path.join(REPO, "data/copernicus/manual_exports/2026-10-04/2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L2A_%s_(Raw).tiff")
nb = lambda n, s: (n - s) / np.maximum(n + s, 1e-6)
n4 = nb(rp(S % "B8A"), rp(S % "B12")); n16 = nb(rp(L % "5", 2e-5, -0.1), rp(L % "7", 2e-5, -0.1))
g, n = rp(S % "B03"), rp(S % "B08"); water = ndimage.binary_opening((g - n) / np.maximum(g + n, 1e-6) > 0.05)
yy, xx = np.mgrid[0:N, 0:N]; vx, vy = tf(*VI); vc, vr = ~T * (vx, vy)
near = np.hypot(yy - vr, xx - vc) * RES <= 500
res = {}
for nm, t4, t16 in (("central", -0.05, 0.06), ("strict", -0.08, 0.05), ("loose", -0.02, 0.07)):
    old = n4 < t4; new = (n16 < t16) & ~ndimage.binary_dilation(old) & ~water
    new = ndimage.binary_opening(new); lab, _ = ndimage.label(new)
    ids = list(set(np.unique(lab[near & new])) - {0}); comp = np.isin(lab, ids)
    res[nm] = dict(km2=round(comp.sum() * RES * RES / 1e6, 3))
    if nm == "central": burn14, oldburn = comp, ndimage.binary_opening(old) & ~water
p = gpd.read_file(os.path.join(REPO, "data/infrastructure/scar_patches_revised.geojson")).to_crs(CRS)
s2 = features.rasterize([(p[p.patch == "possible Oct 14 burn"].geometry.iloc[0], 1)], out_shape=(N, N), transform=T).astype(bool)
o = gpd.read_file(os.path.join(REPO, "data/infrastructure/osm_infrastructure_ODbL.geojson")).to_crs(CRS)
rd = o[o.kind.isin(["road", "track"]) | o.highway.notna()]
roads = features.rasterize([(gg, 1) for gg in rd.geometry if gg is not None and not gg.is_empty], out_shape=(N, N), transform=T, all_touched=True).astype(bool)
res["s2_oct19_patch_km2"] = round(s2.sum() * 900 / 1e6, 3); res["s2_patch_within_landsat_burn"] = round(float((s2 & burn14).sum() / s2.sum()), 2)
res["oct14_burn_on_old_burn_edge_share"] = round(float((ndimage.binary_dilation(burn14, iterations=2) & oldburn).sum() > 0), 0)
per = burn14 & ~ndimage.binary_erosion(burn14)
d_old = ndimage.distance_transform_edt(~oldburn) * RES; d_w = ndimage.distance_transform_edt(~water) * RES; d_r = ndimage.distance_transform_edt(~roads) * RES
res["perimeter_share_within_60m"] = dict(old_burn=round(float((d_old[per] <= 60).mean()), 2), water=round(float((d_w[per] <= 60).mean()), 2), road_or_track=round(float((d_r[per] <= 60).mean()), 2),
                                         any=round(float(((d_old[per] <= 60) | (d_w[per] <= 60) | (d_r[per] <= 60)).mean()), 2))
np.savez_compressed(os.path.join(OUT, "layers.npz"), n4=n4, n16=n16, water=water, oldburn=oldburn, burn14=burn14, s2patch=s2, roads=roads, T=np.array(T)[:6], viirs=np.array([vr, vc]))
json.dump(res, open(os.path.join(OUT, "layers_summary.json"), "w"), indent=1); print(json.dumps(res, indent=1))
