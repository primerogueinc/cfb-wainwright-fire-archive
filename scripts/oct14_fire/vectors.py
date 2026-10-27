"""Polygonise the Oct. 14 burn and the Sept. 20 burn (ground already burned on Oct. 4, main component) from layers.npz; write GeoJSON (EPSG:4326)."""
import sys, os, numpy as np, geopandas as gpd
from rasterio import features
from rasterio.transform import Affine
from scipy import ndimage
from shapely.geometry import shape
OUT = sys.argv[1]; z = np.load(os.path.join(OUT, "layers.npz")); T = Affine(*z["T"])
lab, n = ndimage.label(z["oldburn"]); big = np.argmax(ndimage.sum(z["oldburn"], lab, range(1, n + 1))) + 1
rows = []
for nm, m, note in (("oct14_burn", z["burn14"], "burned between Oct. 4 (Sentinel-2) and Oct. 16 (Landsat 9); matches VIIRS 14:51 MDT Oct. 14"),
                    ("sept20_burn", lab == big, "already burned on Oct. 4 (Sentinel-2); matches VIIRS detections Sept. 20, 2026")):
    geoms = [shape(g) for g, v in features.shapes(m.astype("uint8"), mask=m, transform=T) if v == 1]
    g = gpd.GeoSeries(geoms, crs=3400).unary_union
    rows.append(dict(name=nm, area_km2=round(g.area / 1e6, 3), note=note, geometry=g))
gpd.GeoDataFrame(rows, crs=3400).to_crs(4326).to_file(os.path.join(OUT, "burns.geojson"), driver="GeoJSON")
print([(r["name"], r["area_km2"]) for r in rows])
