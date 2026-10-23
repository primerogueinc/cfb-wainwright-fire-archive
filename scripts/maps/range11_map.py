"""Map: Range 11 (AGL range per standing orders), the fire's start and Range 2 / road head. Usage: python3 range11_map.py ARCHIVE DATA_REPO OUT.jpg"""
import sys, json, glob
import numpy as np, pandas as pd, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from pyproj import Transformer, Geod
from shapely.geometry import shape
from shapely.ops import transform as stx
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
AR, DR, OUT = sys.argv[1:4]
U = "EPSG:32612"; tf = Transformer.from_crs(4326, U, always_xy=True).transform; G = Geod(ellps="WGS84")
W, S, E, N = -111.000, 52.738, -110.860, 52.800
x0, y1 = tf(W, N); x1, y0 = tf(E, S); res = 10
Wd, Hd = int((x1 - x0) / res), int((y1 - y0) / res); T = from_origin(x0, y1, res, res)
f = glob.glob(f"{DR}/sentinel-2/2026-10-19/L2A_tiff/*True_color.tiff")[0]; s = rasterio.open(f)
img = np.zeros((3, Hd, Wd), "float32")
for b in range(3):
    reproject(s.read(b + 1).astype("float32"), img[b], src_transform=s.transform, src_crs=s.crs, dst_transform=T, dst_crs=U, resampling=Resampling.bilinear)
img = np.moveaxis(img, 0, -1); img = np.clip(img / np.percentile(img[img > 0], 99), 0, 1) ** 0.9
img = 0.55 * img + 0.45 * img.mean(axis=2, keepdims=True)  # tone down colour so overlays read
fig, ax = plt.subplots(figsize=(14, 9.2), dpi=150)
ax.imshow(img, extent=(x0, x1, y0, y1), origin="upper")
def poly(geom, **kw):
    g = stx(tf, geom)
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        xs, ys = p.exterior.xy; ax.plot(xs, ys, **kw)
osm = json.load(open(f"{AR}/data/infrastructure/osm_infrastructure_ODbL.geojson"))["features"]
pda2 = [shape(f["geometry"]) for f in osm if f["properties"].get("name") == "Permanent Danger Area 2"][0]
poly(pda2, color="#ffd23f", lw=1.6, ls=(0, (6, 4)))
for f in json.load(open(f"{AR}/data/copernicus/burn_scar.geojson"))["features"]:
    poly(shape(f["geometry"]), color="#ff4d2e", lw=1.8)
d = pd.read_csv(f"{AR}/data/firms/detections.csv"); d = d[(d.acq_date == "2026-10-17") & (abs(d.latitude - 52.77) < 0.08) & (abs(d.longitude + 110.92) < 0.12)]
l = d[d.source.str.contains("LANDSAT")]; v = d[d.source.str.contains("VIIRS")]
lx, ly = tf(l.longitude.values, l.latitude.values); vx, vy = tf(v.longitude.values, v.latitude.values)
ax.scatter(vx, vy, s=70, facecolors="none", edgecolors="#ff9f1c", lw=1.4, zorder=4, label="Fire detected by satellite, 2:49 p.m. (VIIRS, 375 m)")
ax.scatter(lx, ly, s=9, c="#ff2a00", zorder=5, label="Fire detected by satellite, 12:17 p.m. (Landsat, 30 m)")
P = {"Range 11\n(AGL range, per standing orders)": (-110.9577, 52.7678, "#00d1ff", (-1900, -950)),
     "Range 2 (hand grenade)": (-110.9063, 52.7728, "#ffffff", (450, 1500)),
     "Road head\n(end of range road)": (-110.89965, 52.77045, "#ffffff", (250, -900)),
     "Fire's start\n(our estimate)": (-110.9214, 52.7764, "#ff2a00", (-1650, 700))}
xy = {}
for k, (lo, la, c, off) in P.items():
    x, y = tf(lo, la); xy[k] = (x, y)
    ax.scatter([x], [y], s=150, marker="o" if "Fire" not in k else "*", c=c if "Fire" not in k else "#ffef00", edgecolors="#111", lw=1.3, zorder=7)
    ax.annotate(k, (x, y), xytext=(x + off[0], y + off[1]), color="#fff", fontsize=10.5, weight="bold", zorder=8,
                bbox=dict(boxstyle="round,pad=0.3", fc="#111c", ec="none"), arrowprops=dict(arrowstyle="-", color="#fff", lw=0.8))
def line(a, b, lab, dy):
    (xa, ya), (xb, yb) = xy[a], xy[b]
    ax.plot([xa, xb], [ya, yb], color="#ffffff", lw=1.3, ls=(0, (3, 2)), zorder=6)
    lo1, la1 = Transformer.from_crs(U, 4326, always_xy=True).transform(xa, ya); lo2, la2 = Transformer.from_crs(U, 4326, always_xy=True).transform(xb, yb)
    km = G.inv(lo1, la1, lo2, la2)[2] / 1000
    if lab is None: return
    ax.text((xa + xb) / 2, (ya + yb) / 2 + dy, f"{lab}{km:.1f} km", color="#111", fontsize=10, weight="bold", ha="center", zorder=9,
            bbox=dict(boxstyle="round,pad=0.25", fc="#fffc", ec="none"))
k11, k2, kb, kf = list(P)
line(k11, k2, "", -330); line(k11, kf, "", 260); line(kf, k2, None, 0); line(kf, kb, None, 0)
xa, ya = xy[kf]; xb, yb = xy[kb]
ax.text((xa + xb) / 2 - 150, (ya + yb) / 2 - 900, "1.1 km to Range 2\n1.6 km to road head", color="#111", fontsize=10, weight="bold", ha="center", zorder=9,
        bbox=dict(boxstyle="round,pad=0.25", fc="#fffc", ec="none"))
# wind arrows
for (sx, sy, dx, dy, lab, c) in [(x0 + 600, y1 - 3900, 900, 900, "Wind before 3:16 p.m.\nsouthwest, ~30 km/h", "#9ad1ff"),
                                 (x0 + 2700, y1 - 1300, 1000, -900, "Wind from 3:16 p.m.\nnorthwest, gusts 82 km/h", "#ff8a8a")]:
    ax.add_patch(FancyArrowPatch((sx, sy), (sx + dx, sy + dy), arrowstyle="-|>", mutation_scale=28, lw=3.5, color=c, zorder=6))
    ax.text(sx - 200, sy + dy + 250 if dy > 0 else sy + 330, lab, color="#fff", fontsize=9.5, weight="bold", bbox=dict(boxstyle="round,pad=0.3", fc="#111c", ec="none"))
# scale bar and north
bx, by = x1 - 3300, y0 + 600
ax.plot([bx, bx + 2000], [by, by], color="#fff", lw=5, solid_capstyle="butt"); ax.plot([bx, bx + 1000], [by, by], color="#111", lw=5, solid_capstyle="butt")
ax.text(bx + 1000, by + 220, "2 km", color="#fff", ha="center", fontsize=10, weight="bold")
ax.annotate("N", (x1 - 500, y1 - 1300), xytext=(x1 - 500, y1 - 2300), color="#fff", ha="center", fontsize=14, weight="bold",
            arrowprops=dict(arrowstyle="-|>", color="#fff", lw=2.5))
from matplotlib.lines import Line2D
h, labs = ax.get_legend_handles_labels()
h += [Line2D([], [], color="#ff4d2e", lw=2), Line2D([], [], color="#ffd23f", lw=1.6, ls=(0, (6, 4)))]
labs += ["Burn scar (Sentinel-2, Oct. 19)", "Permanent Danger Area 2 (as publicly mapped)"]
ax.legend(h, labs, loc="lower left", fontsize=9, framealpha=0.85, facecolor="#111", labelcolor="#fff", edgecolor="none", bbox_to_anchor=(0.005, 0.005))
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_xticks([]); ax.set_yticks([])
ax.set_title("CFB Wainwright, Oct. 17, 2026: the AGL range, where the fire started, and where it caught C Company", fontsize=13.5, weight="bold", loc="left")
fig.text(0.01, 0.012, "Range positions: OpenStreetMap contributors (volunteer-mapped, not official). Fire's start and C Company's location are Prime Rogue estimates from public data; DND has not confirmed them.\n"
         "Imagery: contains modified Copernicus Sentinel data [2026]. Detections: NASA FIRMS. Weather: Environment and Climate Change Canada. Map: Kevin Duska Jr. (Prime Rogue Inc.), CC BY-NC 4.0.",
         fontsize=8, color="#333")
plt.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.06)
plt.savefig(OUT, dpi=150, pil_kwargs={"quality": 90}); print(OUT)
