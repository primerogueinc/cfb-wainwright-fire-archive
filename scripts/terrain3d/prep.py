"""Prepare layers for the 3D terrain scene of the Oct 17, 2026 CFB Wainwright fire.

Everything is resampled onto one grid in EPSG:3400 (Alberta 10-TM) so Blender
can treat it as a flat metric surface:

  height.npy     bare-earth elevation (m): NRCan HRDEM lidar where it exists,
                 NRCan MRDEM-30 elsewhere (offset-matched along the seam)
  canopy.npy     vegetation height (m), Meta/WRI global canopy height model
                 (only covers the inner part of the scene; 0 elsewhere)
  pre_tc.png     Sentinel-2 L2A true colour, Oct 4, 2026 (before the fire)
  dnbr.npy       Sentinel-2 dNBR, Oct 4 -> Oct 24 (burn severity)
  scar.png       burn-scar mask (dNBR >= 0.27 patches, from burn_scar.geojson)
  points.json    POV points, 12:17 Landsat and 14:49 VIIRS hotspots, in grid
                 coordinates (metres from the grid's lower-left corner)

Run: python3 scripts/terrain3d/prep.py OUTDIR
"""
import json, sys, os
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from rasterio.features import rasterize
from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform as shp_transform
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
D = lambda *p: os.path.join(ROOT, 'data', *p)

CRS = 'EPSG:3400'
RES = 10.0
to3400 = Transformer.from_crs('EPSG:4326', CRS, always_xy=True)

# Scene window: Range 13 / Range 14 in the south to the garrison (Denwood) in the north
LON0, LON1, LAT0, LAT1 = -110.975, -110.845, 52.733, 52.828
xs, ys = zip(*[to3400.transform(lo, la) for lo in (LON0, LON1) for la in (LAT0, LAT1)])
X0, X1 = np.floor(min(xs) / RES) * RES, np.ceil(max(xs) / RES) * RES
Y0, Y1 = np.floor(min(ys) / RES) * RES, np.ceil(max(ys) / RES) * RES
W, H = int((X1 - X0) / RES), int((Y1 - Y0) / RES)
T = from_origin(X0, Y1, RES, RES)
print(f'grid {W}x{H} at {RES} m, {W*RES/1000:.1f} x {H*RES/1000:.1f} km')


def warp(path, band=1, resampling=Resampling.bilinear, nodata_fill=np.nan, count=None):
    with rasterio.open(path) as src:
        bands = range(1, src.count + 1) if count else [band]
        out = []
        for b in bands:
            dst = np.full((H, W), np.nan, np.float32)
            reproject(rasterio.band(src, b), dst, dst_transform=T, dst_crs=CRS,
                      dst_nodata=np.nan, resampling=resampling)
            nd = src.nodata
            if nd is not None and not np.isnan(nd):
                dst[np.isclose(dst, nd)] = np.nan
            out.append(dst)
        return np.stack(out) if count else out[0]


# --- elevation ---------------------------------------------------------------
# HRDEM lidar only touches ~1% of this window (the 2024 survey edge), so the
# scene is effectively MRDEM-30 (30 m); HRDEM is used where it exists.
hr = warp(D('dem', 'hrdem-lidar_NRCAN-Lloydminster_South_2024-1m_dtm_native.tif'))
mr = warp(D('dem', 'mrdem30_dtm_native.tif'), resampling=Resampling.cubic)
hr[(hr < 300) | (hr > 2000)] = np.nan
both = ~np.isnan(hr) & ~np.isnan(mr)
offset = float(np.nanmedian(hr[both] - mr[both])) if both.any() else 0.0
mr_adj = mr + offset
# feather the seam over ~300 m so there is no step
from scipy.ndimage import distance_transform_edt
valid_hr = ~np.isnan(hr)
dist_in = distance_transform_edt(valid_hr) * RES
w = np.clip(dist_in / 300.0, 0, 1)
height = np.where(valid_hr, w * np.nan_to_num(hr) + (1 - w) * mr_adj, mr_adj)
height = np.where(np.isnan(height), np.nanmedian(height), height).astype(np.float32)
np.save(os.path.join(OUT, 'height.npy'), height)
print(f'elevation {height.min():.1f}-{height.max():.1f} m; HRDEM covers {valid_hr.mean()*100:.0f}% '
      f'(MRDEM offset {offset:+.2f} m)')

# --- canopy ------------------------------------------------------------------
chm = warp(D('visibility', 'meta_wri_chm_3400_10m.tif'), resampling=Resampling.average)
chm_valid = ~np.isnan(chm)
chm = np.clip(np.nan_to_num(chm), 0, 40).astype(np.float32)
np.save(os.path.join(OUT, 'canopy.npy'), chm)
np.save(os.path.join(OUT, 'canopy_valid.npy'), chm_valid)
print(f'canopy model covers {chm_valid.mean()*100:.0f}% of the scene; >2 m on '
      f'{(chm > 2).sum() / max(chm_valid.sum(),1) * 100:.0f}% of that')

# --- imagery -----------------------------------------------------------------
# The exported True_color.tiff is truncated, so build true colour from the
# L2A reflectance bands B04/B03/B02 (same Oct 4 scene, ~20 m pixels).
band = lambda b: D('copernicus', 'manual_exports', '2026-10-04',
                   f'2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L2A_{b}_(Raw).tiff')
# texture at 5 m for a smoother drape
T5 = from_origin(X0, Y1, 5.0, 5.0)
rgb = np.zeros((3, H * 2, W * 2), np.float32)
for i, b in enumerate(['B04', 'B03', 'B02']):
    with rasterio.open(band(b)) as src:
        reproject(rasterio.band(src, 1), rgb[i], dst_transform=T5, dst_crs=CRS,
                  resampling=Resampling.cubic)
# simple reflectance stretch, same for all three bands so colours stay true
# soft shoulder so the alkaline lake margins don't clip to flat white
x = rgb * 3.0
img = np.where(x < 0.7, x, 0.7 + 0.3 * (1 - np.exp(-(x - 0.7) / 0.3)))
img = np.clip(img, 0, 1) ** (1 / 1.2)
Image.fromarray((img.transpose(1, 2, 0) * 255).astype(np.uint8)).save(os.path.join(OUT, 'pre_tc.png'))

dnbr = warp(D('copernicus', 'dnbr.tif'))
np.save(os.path.join(OUT, 'dnbr.npy'), np.nan_to_num(dnbr).astype(np.float32))

from_ll = lambda g: shp_transform(lambda x, y, z=None: to3400.transform(x, y), g)
scar = shape(json.load(open(D('copernicus', 'burn_scar.geojson')))['features'][0]['geometry'])
scar_m = from_ll(scar)
mask5 = rasterize([(mapping(scar_m), 255)], out_shape=(H * 2, W * 2), transform=T5, dtype=np.uint8)
Image.fromarray(mask5).save(os.path.join(OUT, 'scar.png'))

# --- points ------------------------------------------------------------------
def gxy(lon, lat):
    x, y = to3400.transform(lon, lat)
    return [x - X0, y - Y0]

def zat(gx, gy):
    c, r = int(gx / RES), int((Y1 - Y0 - gy) / RES)
    return float(height[np.clip(r, 0, H - 1), np.clip(c, 0, W - 1)])

POV = {  # lat, lon, source
    'Range 13':  (52.75627, -110.94249, 'OSM range polygon centroid (way/1240048253); range names not verified by DND'),
    'Range 2':   (52.77281, -110.90626, 'OSM "Range 2 (Grenade)" centroid (way/1240048250)'),
    'Roadhead':  (52.7705,  -110.8996,  'CanVec road dead end on the N-S collector road (location analysis)'),
    'Garrison':  (52.8197,  -110.8944,  'CGNDB "Denwood" (garrison area, north edge of the range)'),
}
pts = {'grid': {'crs': CRS, 'x0': X0, 'y0': Y0, 'res': RES, 'w': W, 'h': H}, 'pov': {}, 'hotspots': []}
for k, (la, lo, src) in POV.items():
    gx, gy = gxy(lo, la)
    pts['pov'][k] = {'lat': la, 'lon': lo, 'x': gx, 'y': gy, 'z': zat(gx, gy), 'source': src}

prog = json.load(open(D('copernicus', 'fire_progression.geojson')))
for f in prog['features']:
    p = f['properties']
    if f['geometry']['type'] != 'Point':
        continue
    lo, la = f['geometry']['coordinates'][:2]
    gx, gy = gxy(lo, la)
    if 0 <= gx <= W * RES and 0 <= gy <= H * RES:
        pts['hotspots'].append({'x': gx, 'y': gy, 'z': zat(gx, gy), 'source': p.get('source'),
                                'time_mdt': p.get('time_mdt')})
# 12:17 Landsat line centre = where the fire was at noon (look target for POVs)
ls = [h for h in pts['hotspots'] if h['source'] == 'LANDSAT_NRT' and '12:17' in (h['time_mdt'] or '')]
if ls:
    pts['noon_fire'] = {'x': float(np.mean([h['x'] for h in ls])), 'y': float(np.mean([h['y'] for h in ls]))}
    pts['noon_fire']['z'] = zat(pts['noon_fire']['x'], pts['noon_fire']['y'])
c = scar_m.centroid
pts['scar_centroid'] = {'x': c.x - X0, 'y': c.y - Y0}
pts['scar_centroid']['z'] = zat(c.x - X0, c.y - Y0)
pts['scar_outline'] = [[[x - X0, y - Y0] for x, y in poly.exterior.coords]
                       for poly in getattr(scar_m, 'geoms', [scar_m])]
# Range 11, the AGL range per the standing orders (as reported), and an illustrative
# impact-zone centre 2.2 km at 073 deg (the working model's best-fitting start zone)
import math
r11 = gxy(-110.95771, 52.76781)
pts['extra'] = {'Range 11': {'x': r11[0], 'y': r11[1], 'lat': 52.76781, 'lon': -110.95771,
                             'source': 'OSM way/1240048252; AGL range per standing orders as reported'},
                'agl_impact_centre': {'x': r11[0] + 2200 * math.sin(math.radians(73)),
                                      'y': r11[1] + 2200 * math.cos(math.radians(73)),
                                      'note': 'illustrative: 2.2 km at 073 deg from Range 11'}}
json.dump(pts, open(os.path.join(OUT, 'points.json'), 'w'), indent=1)
print(f"{len(pts['hotspots'])} hotspots in scene ({len(ls)} Landsat 12:17)")
for k, v in pts['pov'].items():
    print(f"  {k:9s} grid ({v['x']:.0f}, {v['y']:.0f}) elev {v['z']:.1f} m")
