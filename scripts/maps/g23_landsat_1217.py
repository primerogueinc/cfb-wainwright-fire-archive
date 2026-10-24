import sys, json; sys.path.insert(0, "vis")
from pr import *
from affine import Affine
from shapely.geometry import shape
from pyproj import Transformer
LS = "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/ls/"
d = np.load(LS + "crop.npz"); T = Affine(*json.load(open(LS + "T.json"))); fire = np.load(LS + "fire.npy")
def st(a, lo, hi): return np.clip((a - lo) / (hi - lo), 0, 1)
rgb = np.dstack([st(d["B7"], 0.17, 0.40), st(d["B6"], 0.20, 0.33), st(d["B5"], 0.25, 0.40)])
SC = 4
img = Image.fromarray((np.nan_to_num(rgb) * 255).astype("uint8")).resize((rgb.shape[1] * SC, rgb.shape[0] * SC), Image.BILINEAR).convert("RGBA")
tf = Transformer.from_crs(4326, 32612, always_xy=True).transform; Ti = ~T
def PX(lon, lat):
    c, r = Ti * tf(lon, lat); return (c * SC, r * SC)
dd = ImageDraw.Draw(img)
for f in json.load(open(REPO + "data/reference/aer_pipelines_near_site.geojson"))["features"]:
    if f["properties"]["SEG_STATUS"] != "Operating": continue
    g = shape(f["geometry"])
    for gg in getattr(g, "geoms", [g]):
        xy = [PX(*c) for c in gg.coords]; dd.line(xy, fill=INK, width=6); dd.line(xy, fill=(255, 214, 0), width=3)
for f in json.load(open(REPO + "data/copernicus/burn_scar.geojson"))["features"]:
    g = shape(f["geometry"])
    for gg in getattr(g, "geoms", [g]):
        dashed(dd, [PX(*c) for c in gg.exterior.coords], CREAM, 2, (8, 6))
from scipy import ndimage
area = np.load(LS + "area1217.npy"); edge = area & ~ndimage.binary_erosion(area)
for i, j in zip(*np.where(edge)):
    x, y = (j + 0.5) * SC, (i + 0.5) * SC; dd.rectangle([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=(255, 150, 60))
ii, jj = np.where(fire)
for i, j in zip(ii, jj):
    x, y = (j + 0.5) * SC, (i + 0.5) * SC; dd.rectangle([x - SC * 0.6, y - SC * 0.6, x + SC * 0.6, y + SC * 0.6], outline=(255, 255, 255), width=2)
def dot(p, col, r=10): dd.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col, outline=INK, width=3)
P = {k: PX(*v) for k, v in {"R11": (-110.9577, 52.7678), "R2": (-110.90632, 52.77279), "RH": (-110.89965, 52.77045)}.items()}
dot(P["R11"], TEAL); dot(P["R2"], CREAM); dot(P["RH"], CREAM)
x, y = PX(-110.92626, 52.77079); dd.line([x - 12, y - 12, x + 12, y + 12], fill=TEAL, width=5); dd.line([x - 12, y + 12, x + 12, y - 12], fill=TEAL, width=5)
label(dd, (P["R11"][0], P["R11"][1] + 24), "RANGE 11", col=TEAL, size=17, anchor="ma")
label(dd, (x - 20, y + 22), "Modelled start", col=TEAL, size=15, anchor="ra")
label(dd, (P["R2"][0] + 18, P["R2"][1] - 46), "RANGE 2", size=16)
label(dd, (P["RH"][0] + 18, P["RH"][1] + 14), "ROAD HEAD", size=16)
fx, fy = (jj.mean() + 0.5) * SC, (ii.min() + 0.5) * SC
label(dd, (fx - 330, fy - 130), "AT 12:17 P.M.: flames (white) around a burned\nstrip ~2 km long. Its back (southwest) end is\n1.2-1.5 km east of Range 11.", col=(255, 150, 80), size=17)
label(dd, (P["R2"][0] + 120, P["R2"][1] - 130), "Gas lines: no heat above background\nwithin 600 m. Nearest flames 0.86 km.", col=(255, 214, 0), size=16)
lx, ly = 16, img.size[1] - 150
ly2 = ly - 30
dd.rounded_rectangle([lx, ly - 30, lx + 470, ly + 134], radius=8, fill=INK)
for k, (kind, c, t) in enumerate([("sq", (255, 255, 255), "Active fire pixel (Landsat 8, 12:17 p.m.)"), ("edge", (255, 150, 60), "Burned and burning at 12:17 p.m."), ("gas", (255, 214, 0), "Gas line, operating (AER)"), ("dash", CREAM, "Final burn scar (Sentinel-2, Oct. 19)"), ("x", TEAL, "Working-model start (v2.1)")]):
    yy = ly2 + 16 + k * 29
    if kind == "edge": dd.line([lx + 10, yy + 9, lx + 38, yy + 9], fill=c, width=4)
    elif kind == "sq": dd.rectangle([lx + 16, yy + 2, lx + 30, yy + 16], outline=c, width=2)
    elif kind == "gas": dd.line([lx + 10, yy + 9, lx + 38, yy + 9], fill=c, width=4)
    elif kind == "dash": dashed(dd, [(lx + 8, yy + 9), (lx + 38, yy + 9)], c, 2, (6, 4))
    else: dd.line([lx + 16, yy + 2, lx + 30, yy + 16], fill=c, width=4); dd.line([lx + 16, yy + 16, lx + 30, yy + 2], fill=c, width=4)
    dd.text((lx + 50, yy), t, font=M(16), fill=CREAM)
sx = img.size[0] - 330; sy = img.size[1] - 40; Lk = 1000 / 30 * SC
dd.rectangle([sx, sy, sx + Lk, sy + 10], fill=CREAM); dd.text((sx + Lk / 2, sy - 26), "1 km", font=B(17), fill=CREAM, anchor="ma")
TOP, L = 196, 48
im, d0 = canvas(img.size[0] + 2 * L, TOP + img.size[1] + 24 + 140, "CFB WAINWRIGHT FIRE · LANDSAT 8 · OCT. 17, 2026, 12:17 P.M. MDT",
                "The only close-up of the fire while it burned",
                "Landsat 8 shortwave infrared (bands 7, 6, 5) through thin, cold cloud. By 12:17 p.m. the fire had burned a strip about 2 km long, pushed northeast by a southwest wind,\nfrom a back end 1.2-1.5 km east of Range 11. No gas line was hot: within 600 m of every operating line, readings sit at background.")
im.paste(img, (L, TOP))
footer(im, ["Landsat 8 OLI L1TP, scene LC08_L1TP_040023_20261017_20261021_02_T1, courtesy of the U.S. Geological Survey. Fire pixels: Schroeder et al. (2016) thresholds",
            "(B7/B5 > 2.5, B7 - B5 > 0.3, B7 > 0.5); 47 of NASA FIRMS' 59 detections fall within 45 m of them. Pipelines: AER licence data. Burn scar: Copernicus Sentinel-2.",
            "Graphic: Kevin Duska Jr. (Prime Rogue Inc.), CC BY-NC 4.0. Raw bands: github.com/primerogueinc/CFB-Wainwright-Landsat-8-9"], fh=140)
im.convert("RGB").save("vis/cfb-wainwright-landsat-1217.jpg", quality=92); print(im.size)
