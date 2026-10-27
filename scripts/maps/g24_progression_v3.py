import sys; sys.path.insert(0, "vis")
from pr import *
import json
from shapely.geometry import shape
from pyproj import Geod, Transformer
from rasterio.warp import reproject
G = Geod(ellps="WGS84")
m = Map(-110.990, -110.870, 52.748, 52.792, 190)
TOP, L = 196, 48
Wc, Hc = m.w + 2 * L, TOP + m.h + 24 + 140
im, d = canvas(Wc, Hc, "CFB WAINWRIGHT FIRE · OCT. 17, 2026 · WORKING MODEL V3",
               "How the fire grew before the wind turned (v3)",
               "Now fitted to the burned area Landsat 8 photographed at 12:17 p.m. Same start: rounds landing 1.4-2.2 km east of Range 11, about 7 a.m. (3:30-7 a.m. by morning pace).\nOn the Range 2 side, the 3:16 p.m. edge is set by where satellites saw fire at 2:49 p.m. (straight yellow line), unchanged from v2.1.")
base = m.base(date="2026-10-04", bright=0.8)
# arrival raster (hours since midnight) resampled to map pixels
src = rasterio.open(REPO + "data/authentic-stoic-stress-test/model_v3/arrival_prefront_v3c_3x_lb2.5_0700.tif")
arr = np.full((m.h, m.w), np.nan, "float32")
from rasterio.transform import from_bounds
reproject(src.read(1), arr, src_transform=src.transform, src_crs=src.crs, dst_transform=from_bounds(m.W, m.S, m.E, m.N, m.w, m.h), dst_crs="EPSG:4326", resampling=rasterio.enums.Resampling.nearest)
cols = [(255, 236, 140), (255, 205, 90), (255, 165, 60), (245, 120, 50), (225, 75, 45), (190, 40, 40), (140, 20, 40)]
edges = [7.0, 9, 10, 11, 12, 13, 14, 15.27]
ov = np.zeros((m.h, m.w, 4), "uint8")
for k in range(len(edges) - 1):
    sel = (arr >= edges[k]) & (arr < edges[k + 1]); ov[sel, :3] = cols[k]; ov[sel, 3] = 175
base = Image.alpha_composite(base, Image.fromarray(ov, "RGBA"))
o = ImageDraw.Draw(base)
# isochrone lines at 12:17 and 3:16
from scipy import ndimage
import geopandas as gpd
from rasterio import features as _f
_tr = from_bounds(m.W, m.S, m.E, m.N, m.w, m.h)
_hull = preshift_hull(); HULL = _f.rasterize([(_hull, 1)], out_shape=(m.h, m.w), transform=_tr).astype(bool)
_ls = rasterio.open(REPO + "data/authentic-stoic-stress-test/part8c_landsat_constraint/burned_1217_classes.tif"); LS = np.zeros((m.h, m.w), "uint8")
reproject(_ls.read(1), LS, src_transform=_ls.transform, src_crs=_ls.crs, dst_transform=_tr, dst_crs="EPSG:4326", resampling=rasterio.enums.Resampling.nearest)
for t, col, w in [(12 + 17 / 60, (255, 255, 255), 2), (15 + 16 / 60, YEL, 4), ("landsat", (0, 230, 255), 2)]:
    if t == "landsat": BB = LS >= 1
    elif t > 15: BB = (np.nan_to_num(arr, nan=99) <= t) | HULL
    else: BB = np.nan_to_num(arr, nan=99) <= t
    edge = BB & ~ndimage.binary_erosion(BB, iterations=2)
    ys, xs = np.nonzero(edge); base_np = np.array(base); base_np[ys, xs, :3] = col; base = Image.fromarray(base_np); o = ImageDraw.Draw(base)
osmf = json.load(open(REPO + "data/infrastructure/osm_infrastructure_ODbL.geojson"))["features"]
pda2 = [shape(f["geometry"]) for f in osmf if f["properties"].get("name") == "Permanent Danger Area 2"][0]
m.outline(o, pda2, (255, 214, 0, 160), width=2, dash=(12, 10))
for f in json.load(open(REPO + "data/reference/aer_pipelines_near_site.geojson"))["features"]:
    if f["properties"]["SEG_STATUS"] != "Operating": continue
    g = shape(f["geometry"])
    for gg in getattr(g, "geoms", [g]): o.line([m.P(y, x) for x, y in gg.coords], fill=(150, 170, 255), width=2)
R11 = (52.7678, -110.9577)
pts = []
for az in range(0, 361, 2):
    lo, la, _ = G.fwd(R11[1], R11[0], az, 2200); pts.append(m.P(la, lo))
dashed(o, pts, TEAL, 3, (16, 9))
p1 = m.P(*G.fwd(R11[1], R11[0], 80, 1400)[1::-1]); p2 = m.P(*G.fwd(R11[1], R11[0], 80, 2200)[1::-1]); p0 = m.P(*R11)
dashed(o, [p0, p1], TEAL, 2, (8, 8)); o.line([p1, p2], fill=TEAL, width=9)
det = pd.read_csv(REPO + "data/firms/detections.csv"); det = det[(det.acq_date == "2026-10-17") & (abs(det.latitude - 52.77) < 0.08) & (abs(det.longitude + 110.92) < 0.12)]
for _, r in det[det.source.str.contains("VIIRS")].iterrows():
    x, y = m.P(r.latitude, r.longitude); o.ellipse([x - 14, y - 14, x + 14, y + 14], outline=(255, 159, 28), width=3)
for _, r in det[det.source.str.contains("LANDSAT")].iterrows():
    x, y = m.P(r.latitude, r.longitude); o.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255), outline=INK)
PA, PB = m.P(52.7728, -110.9063), m.P(52.77045, -110.89965)
for p in (PA, PB): o.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=CREAM, outline=INK, width=3)
o.ellipse([p0[0] - 11, p0[1] - 11, p0[0] + 11, p0[1] + 11], fill=TEAL, outline=INK, width=3)
label(o, (p0[0] + 18, p0[1] + 14), "RANGE 11 (AGL)", col=TEAL, size=17)
mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
label(o, (mid[0] - 40, mid[1] + 26), "Modelled start: rounds landing\n1.4-2.2 km out on the line of fire", col=TEAL, size=15)
label(o, (PA[0] + 18, PA[1] - 58), "RANGE 2\nedge ~590 m away at 3:16", size=15)
label(o, (PB[0] + 18, PB[1] + 12), "ROAD HEAD\nedge ~1.1 km away at 3:16", size=15)
label(o, m.P(52.7895, -110.948), "CYAN LINE: burned area Landsat saw at 12:17 p.m. (loosest outline)\nWHITE LINE: model's fire edge at 12:17 p.m.\nYELLOW LINE: fire edge at 3:16 p.m., when the wind turned\nBLUE LINES: operating gas lines (AER)", col=CREAM, size=15)
# legend: hour bands
lx, ly = 18, m.h - 92
o.rounded_rectangle([lx, ly, lx + 640, ly + 76], radius=8, fill=INK)
o.text((lx + 14, ly + 10), "Modelled time the fire reached each spot (MDT)", font=B(15), fill=CREAM)
labs = ["7-9 a.m.", "9-10", "10-11", "11-12", "12-1 p.m.", "1-2", "2-3:16"]
for k, (c_, t) in enumerate(zip(cols, labs)):
    x = lx + 14 + k * 88; o.rectangle([x, ly + 38, x + 26, ly + 58], fill=c_); o.text((x + 31, ly + 40), t, font=M(13), fill=CREAM)
dd2 = ImageDraw.Draw(base)
sx, sy = m.w - 330, m.h - 40
dd2.rectangle([sx, sy, sx + m.pxkm, sy + 10], fill=CREAM)
for i, t in enumerate(["0", "1 km"]): dd2.text((sx + i * m.pxkm, sy - 24), t, font=B(15), fill=CREAM, anchor="ma")
arrow(dd2, (m.w - 50, 110), (m.w - 50, 50), CREAM, width=6, head=18); dd2.text((m.w - 50, 118), "N", font=B(20), fill=CREAM, anchor="ma")
im.paste(base, (L, TOP))
footer(im, ["Prime Rogue working model v3: grass-fire spread (CFFDRS O-1a) on hourly base-station weather, pace calibrated to satellites, shape fitted to Landsat 8.",
            "A model, not an observation. White dots: Landsat 12:17 p.m.; rings: VIIRS 2:49 p.m. (NASA FIRMS). Landsat courtesy USGS. Pipelines: AER. Ranges: OpenStreetMap.",
            
            "Base: Sentinel-2, Oct. 4, modified Copernicus data [2026]. Graphic: Kevin Duska Jr. (Prime Rogue Inc.), CC BY-NC 4.0. Data: github.com/primerogueinc/cfb-wainwright-fire-archive"], fh=140)
im.convert("RGB").save("vis/cfb-wainwright-fire-progression-model-v3.jpg", quality=92); print(im.size)
