"""Working model v4, H1/H6 test: do straight edges of the burn scar line up with mapped roads, tracks and pipeline rights-of-way,
or are there straight edges nothing on the map explains (possible fireguards or containment lines)?
Usage: python3 fireguards.py REPO COPERNICUS_REPO
Scar: dNBR >= 0.27, Sentinel-2 Oct. 4 -> Oct. 24 (B8A/B12, 20 m bands at 10 m), largest connected patch, outline simplified to 15 m.
Straight edge: a run of simplified outline vertices within 15 m of a straight line, at least 250 m long.
Each straight edge is compared with OSM roads/tracks (ODbL), CanVec 1:50k transport and AER pipelines: 'mapped' if at least 70% of
it lies within 60 m of one of them (20 m pixels, map offsets). For unexplained edges, pre-fire (Oct. 4) NDVI on a 20 m strip along the edge vs 50-100 m
either side: a ploughed or disced guard reads bare (lower NDVI) before the fire. A guard cut during the fire would not show
before it, so the same strip is also compared after it (Oct. 19, B12 shortwave infrared: bare soil is brighter than both
blackened and unburned grass)."""
import sys, os, json, numpy as np, rasterio, geopandas as gpd, pandas as pd
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from rasterio import features
from scipy import ndimage
from shapely.geometry import shape, LineString, Point
from shapely.ops import unary_union
REPO, CP = sys.argv[1], sys.argv[2] + "/sentinel-2/"
M = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4"); CRS = "EPSG:3400"
ref = gpd.read_file(os.path.join(REPO, "data/copernicus/burn_scar.geojson")).to_crs(CRS)
x0, y0, x1, y1 = ref.total_bounds; x0 -= 800; y0 -= 800; x1 += 800; y1 += 800; R = 10
W, H = int((x1 - x0) / R), int((y1 - y0) / R); T = from_origin(x0, y1, R, R)
def get(d, b):
    s = rasterio.open(f"{CP}{d}/L2A_tiff/{d}-00_00_{d}-23_59_Sentinel-2_L2A_{b}_(Raw).tiff"); o = np.full((H, W), np.nan, "float32")
    reproject(rasterio.band(s, 1), o, dst_transform=T, dst_crs=CRS, resampling=Resampling.bilinear, dst_nodata=np.nan); return o
nbr = lambda d: (lambda n, s: (n - s) / (n + s))(get(d, "B8A"), get(d, "B12"))
burn = (nbr("2026-10-04") - nbr("2026-10-24")) >= 0.27
burn = ndimage.binary_opening(ndimage.binary_closing(burn, iterations=2), iterations=1)
lab, n = ndimage.label(burn); big = lab == (np.argmax(ndimage.sum(burn, lab, range(1, n + 1))) + 1)
poly = max((shape(g) for g, v in features.shapes(big.astype("uint8"), mask=big, transform=T) if v == 1), key=lambda p: p.area)
ring = np.array(poly.exterior.simplify(15).coords)
# greedy straight runs
segs, i = [], 0
while i < len(ring) - 1:
    j = i + 1; best = None
    while j < len(ring):
        a, b = ring[i], ring[j]; L = np.hypot(*(b - a))
        if L > 0:
            pts = ring[i:j + 1]; v = b - a; q = pts - a; d = np.abs(v[0] * q[:, 1] - v[1] * q[:, 0]) / L
            if d.max() <= 15: best = j; j += 1; continue
        break
    if best is not None and np.hypot(*(ring[best] - ring[i])) >= 250: segs.append(LineString([ring[i], ring[best]])); i = best
    else: i += 1
lines = []
for f, kind in (("data/infrastructure/osm_infrastructure_ODbL.geojson", "OSM"), ("data/reference/canvec50k_transport_near_site.geojson", "CanVec transport"), ("data/reference/aer_pipelines_near_site.geojson", "pipeline")):
    g = gpd.read_file(os.path.join(REPO, f)).to_crs(CRS); g = g[g.geom_type.isin(["LineString", "MultiLineString"])]
    lines.append((kind, unary_union(list(g.geometry))))
ndvi = (lambda n, r: (n - r) / (n + r))(get("2026-10-04", "B8A"), get("2026-10-04", "B04"))
def strip_ndvi(seg, lo, hi):
    zone = seg.buffer(hi, cap_style=2).difference(seg.buffer(lo, cap_style=2)) if lo else seg.buffer(hi, cap_style=2)
    m = features.rasterize([(zone, 1)], out_shape=(H, W), transform=T, fill=0).astype(bool); return float(np.nanmedian(ndvi[m]))
b12p = get("2026-10-19", "B12")
def strip_b12(seg, lo, hi):
    zone = seg.buffer(hi, cap_style=2).difference(seg.buffer(lo, cap_style=2)) if lo else seg.buffer(hi, cap_style=2)
    m = features.rasterize([(zone, 1)], out_shape=(H, W), transform=T, fill=0).astype(bool); return float(np.nanmedian(b12p[m]))
rows = []
for k, s in enumerate(segs):
    pts = [s.interpolate(t, normalized=True) for t in np.linspace(0, 1, 25)]
    best = max(((kind, float(np.mean([geom.distance(p) <= 60 for p in pts]))) for kind, geom in lines), key=lambda x: x[1])
    mid = s.interpolate(0.5, normalized=True)
    lon, lat = gpd.GeoSeries([mid], crs=CRS).to_crs(4326).iloc[0].coords[0]
    rows.append(dict(id=k, length_m=round(s.length), mid_lat=round(lat, 5), mid_lon=round(lon, 5), bearing=round(float(np.degrees(np.arctan2(*(np.array(s.coords[1]) - np.array(s.coords[0])))) % 180)),
                     best_match=best[0], share_within_60m=round(best[1], 2), mapped=best[1] >= 0.7,
                     prefire_ndvi_on_edge=round(strip_ndvi(s, 0, 10), 3), prefire_ndvi_50_100m=round(strip_ndvi(s, 50, 100), 3),
                     oct19_b12_on_edge=round(strip_b12(s, 0, 10), 4), oct19_b12_50_100m=round(strip_b12(s, 50, 100), 4)))
df = pd.DataFrame(rows); df["edge_minus_sides"] = (df.prefire_ndvi_on_edge - df.prefire_ndvi_50_100m).round(3)
df.to_csv(os.path.join(M, "fireguards_straight_edges.csv"), index=False)
summ = dict(perimeter_km=round(poly.exterior.length / 1000, 1), straight_edges=len(df), straight_km=round(df.length_m.sum() / 1000, 2),
            mapped_km=round(df[df.mapped].length_m.sum() / 1000, 2), unexplained_km=round(df[~df.mapped].length_m.sum() / 1000, 2),
            unexplained_with_bare_strip_before=int(((~df.mapped) & (df.edge_minus_sides <= -0.05)).sum()),
            unexplained_with_bright_strip_after=int(((~df.mapped) & (df.oct19_b12_on_edge >= 1.15 * df.oct19_b12_50_100m)).sum()))
json.dump(summ, open(os.path.join(M, "fireguards_summary.json"), "w"), indent=1)
gpd.GeoDataFrame(df, geometry=segs, crs=CRS).to_crs(4326).to_file(os.path.join(M, "fireguards_straight_edges.geojson"), driver="GeoJSON")
pd.set_option("display.width", 220); print(json.dumps(summ)); print(df.to_string(index=False))
