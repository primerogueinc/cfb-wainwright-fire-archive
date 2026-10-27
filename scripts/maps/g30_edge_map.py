"""v4 graphic: the Range 2 point inside the burn, the road head on its edge (Sentinel-2, Oct. 24).
Usage: python3 scripts/maps/g30_edge_map.py EDGE_DIR  (edge_check.py output: grid_meta.npy, S2_20_m_dNBR_2026_10_24.npy)"""
import sys; sys.path.insert(0, "scripts/maps")
from v4fig import *
import json, numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from pyproj import Transformer
ED = sys.argv[1]; CP = "/home/claude/cfb-wainwright---full-satellite-data---copernicus-/sentinel-2/"
x0, y0, R, Hh, Ww = np.load(ED + "/grid_meta.npy"); Hh, Ww = int(Hh), int(Ww); T = from_origin(x0, y0, R, R)
burn = np.load(ED + "/S2_20_m_dNBR_2026_10_24.npy")
def band(d, b):
    s = rasterio.open(f"{CP}{d}/L2A_tiff/{d}-00_00_{d}-23_59_Sentinel-2_L2A_{b}_(Raw).tiff"); o = np.full((Hh, Ww), np.nan, "float32")
    reproject(rasterio.band(s, 1), o, dst_transform=T, dst_crs="EPSG:3400", resampling=Resampling.bilinear, dst_nodata=np.nan); return o
rgb = np.dstack([band("2026-10-24", b) for b in ("B04", "B03", "B02")]); rgb = np.clip(np.nan_to_num(rgb) / 0.16, 0, 1) ** (1 / 1.4)
q = json.load(open(REPO + "data/authentic-stoic-stress-test/model_v4/edge/edge_quadrants.json"))["S2_20_m_dNBR_2026_10_24"]
tf = Transformer.from_crs(4326, 3400, always_xy=True).transform
P = {"Range 2 point": tf(-110.9063, 52.7728), "Road head": tf(-110.8996, 52.7705)}
cx, cy = np.mean([p[0] for p in P.values()]), np.mean([p[1] for p in P.values()]); half = 900
f, ax = fig(1000, 640); ext = [x0, x0 + Ww * R, y0 - Hh * R, y0]
ax.imshow(rgb, extent=ext); X = x0 + (np.arange(Ww) + .5) * R; Y = y0 - (np.arange(Hh) + .5) * R
ax.contour(X, Y, burn.astype(float), [0.5], colors=hx(YEL), linewidths=2.2)
import matplotlib.patheffects as pe
for k, (x, y) in P.items():
    ax.plot(x, y, "o", ms=11, mfc="white", mec="k", zorder=4)
    ax.annotate(k, (x, y), (-120, 14) if k.startswith("Range") else (12, -24), textcoords="offset points", color=hx(CREAM), fontsize=15, weight="bold",
                path_effects=[pe.withStroke(linewidth=4, foreground=hx(INK))])
ax.set_xlim(cx - half * 1.3, cx + half * 1.3); ax.set_ylim(cy - half * 0.84, cy + half * 0.84); ax.set_xticks([]); ax.set_yticks([])
ax.plot([cx + half * 1.3 - 420, cx + half * 1.3 - 220], [cy - half * 0.84 + 90] * 2, color="white", lw=4); ax.text(cx + half * 1.3 - 420, cy - half * 0.84 + 120, "200 m", color="white", fontsize=12, path_effects=[pe.withStroke(linewidth=3, foreground="k")])
f.subplots_adjust(0, 0, 1, 1)
W, H = 1600, 1000
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · WORKING MODEL V4 · SENTINEL-2, OCT. 24",
               "The burn swept past Range 2 and ended at the road head",
               "Natural colour a week after the fire. Yellow line: edge of the burn (Sentinel-2 burn index, Oct. 4 vs Oct. 24), the same on Oct. 19 and in Landsat 8.")
im.paste(to_img(f), (54, 200))
r2, rh = q["Range 2 point"], q["Road head"]
tx = 1090; y = 215
for head, lines in (("RANGE 2 POINT", [f"Inside the burn: {r2['burned_pct_within_150m']}% of the ground within", "150 m burned, all of it to the south-west and", "north-west. A narrow unburned strip runs east", "from its pad along the track.", "Model: fire arrives about 3:21-3:30 p.m."]),
                    ("ROAD HEAD", [f"Exactly on the edge: {rh['burned_pct_30_150m_by_quadrant']['SW']}% burned to the", f"south-west, {rh['burned_pct_30_150m_by_quadrant']['NE']}% to the north-east.", "A 33-35 ha pocket north-east of it barely", "burned. Something local stopped the fire", "there: the track, fuel or people.", "Model: fire arrives about 3:26-3:34 p.m."]),
                    ("WHAT IT DOES NOT SHOW", ["That safety was within reach. Light", "burning in grass can read as unburned,", "pixels are 10-20 m, and who was where,", "when, is not public."])):
    d.text((tx, y), head, font=B(19), fill=GOLD); y += 32
    for l in lines: d.text((tx, y), l, font=M(18), fill=CREAM); y += 27
    y += 22
footer(im, ["Contains modified Copernicus Sentinel data [2026]. Burned = drop in normalized burn ratio (B8A/B12) of 0.27 or more; checked against Sentinel-2 Oct. 19 and Landsat 8 Oct. 24 (USGS).",
            "Points: Range 2 (OpenStreetMap), road head (end of the range road, CanVec). Model times: working model v4, front reaching the fire at 3:16 or 3:25 p.m.", SRC], fh=145)
im.convert("RGB").save(OUTD + "cfb-wainwright-edge-range2-road-head.jpg", quality=92); print("ok")
