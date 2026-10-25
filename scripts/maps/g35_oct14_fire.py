"""Graphic: the fires before Oct. 17 in permanent danger area 2 (Sept. 20, Oct. 14) and the Oct. 14 fire model.
Usage (repo root): python3 scripts/maps/g35_oct14_fire.py"""
import sys, glob, json; sys.path.insert(0, "scripts/maps")
from v4fig import *
import numpy as np, geopandas as gpd, pandas as pd, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from pyproj import Transformer
import matplotlib.patheffects as pe
tf = Transformer.from_crs(4326, 3400, always_xy=True).transform
BR = gpd.read_file(REPO + "data/oct14_fire/burns.geojson").to_crs(3400)
scar = gpd.read_file(REPO + "data/infrastructure/scar_patches_revised.geojson").to_crs(3400); s17 = scar[scar.patch == "main Oct 17 run"]
o = gpd.read_file(REPO + "data/infrastructure/osm_infrastructure_ODbL.geojson").to_crs(3400); pda2 = o[o.name == "Permanent Danger Area 2"]
F = pd.read_csv(REPO + "data/firms/history_2012-2026/all_detections_merged.csv"); F = F[F.acq_date.isin(["2026-09-20"])]
fit = json.load(open(REPO + "data/oct14_fire/fit_summary.json"))
x0, y0 = tf(-110.985, 52.800); x1, y1 = tf(-110.865, 52.712); RES = 15; W_, H_ = int((x1 - x0) / RES), int((y0 - y1) / RES); T = from_origin(x0, y0, RES, RES)
L = glob.glob("/home/claude/cfb-wainwright-landsat-8-9/landsat/2026-10-16/*/*B7.TIF")[0].replace("B7.TIF", "B%s.TIF")
def rp(b):
    with rasterio.open(L % b) as r:
        d = np.zeros((H_, W_), "float32"); reproject(r.read(1).astype("float32") * 2e-5 - 0.1, d, src_transform=r.transform, src_crs=r.crs, dst_transform=T, dst_crs="EPSG:3400", resampling=Resampling.bilinear); return d
rgb = np.dstack([rp(b) for b in "765"]);
from scipy import ndimage
from rasterio import features as _ft
from shapely.geometry import shape as _shape
S2 = REPO + "data/copernicus/manual_exports/2026-10-04/2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L2A_%s_(Raw).tiff"
def rs(b):
    with rasterio.open(S2 % b) as r:
        d = np.zeros((H_, W_), "float32"); reproject(r.read(1).astype("float32"), d, src_transform=r.transform, src_crs=r.crs, dst_transform=T, dst_crs="EPSG:3400", resampling=Resampling.average); return d
n8, n12 = rs("B8A"), rs("B12"); ob = ndimage.binary_opening((n8 - n12) / np.maximum(n8 + n12, 1e-6) < -0.05, iterations=2)
lab, _ = ndimage.label(ob); fx0, fy0 = tf(F.longitude.values, F.latitude.values); cc, rr = (~T) * (fx0, fy0)
ids = set(lab[np.clip(rr.astype(int), 0, H_ - 1), np.clip(cc.astype(int), 0, W_ - 1)]) - {0}; sept = np.isin(lab, list(ids))
SEPT_KM2 = sept.sum() * RES * RES / 1e6; print("sept20 km2 in window", round(SEPT_KM2, 2))
SEPT = gpd.GeoSeries([_shape(g) for g, v in _ft.shapes(sept.astype("uint8"), mask=sept, transform=T) if v == 1], crs=3400)
lo, hi = np.percentile(rgb, 2, axis=(0, 1)), np.percentile(rgb, 98, axis=(0, 1)); rgb = np.clip((rgb - lo) / (hi - lo), 0, 1) * 0.75
f, ax = fig(860, 860); ax.imshow(rgb, extent=[x0, x0 + W_ * RES, y0 - H_ * RES, y0])
pda2.boundary.plot(ax=ax, color=hx(GOLD), lw=1.6, ls="--")
s17.boundary.plot(ax=ax, color=hx(CREAM), lw=1.2)
SEPT.plot(ax=ax, color=hx((214, 140, 60)), alpha=0.5, lw=0); SEPT.boundary.plot(ax=ax, color=hx((214, 140, 60)), lw=1.0)
BR[BR.name == "oct14_burn"].plot(ax=ax, color=hx(RED), alpha=0.75, lw=0); BR[BR.name == "oct14_burn"].boundary.plot(ax=ax, color=hx(RED), lw=1.5)
fx, fy = tf(F.longitude.values, F.latitude.values); ax.plot(fx, fy, "^", ms=6, mfc="none", mec=hx(YEL), mew=1.4)
vx, vy = tf(-110.93891, 52.75486); ax.plot(vx, vy, "^", ms=12, mfc=hx(YEL), mec=hx(INK), mew=1.2)
ig = fit["_sunset"]["top15"][:6]; ix, iy = tf([p["lon"] for p in ig], [p["lat"] for p in ig]); ax.plot(ix, iy, "x", ms=9, mew=2.4, color="white")
st = dict(color=hx(CREAM), fontsize=13, weight="bold", path_effects=[pe.withStroke(linewidth=3.5, foreground=hx(INK))])
for nm, (lo_, la_), off in (("Range 11", (-110.9577, 52.7678), (-70, 8)), ("Range 13", (-110.94249, 52.75627), (-82, 2)), ("Range 2", (-110.9063, 52.7728), (8, 6))):
    x, y = tf(lo_, la_); ax.plot(x, y, "o", ms=8, mfc="white", mec="k"); ax.annotate(nm, (x, y), off, textcoords="offset points", **st)
for txt, (lo_, la_), c in (("Oct. 17 burn", (-110.905, 52.792), CREAM), ("Sept. 20 burn", (-110.905, 52.733), (240, 170, 90)), ("Oct. 14 burn", (-110.975, 52.742), RED), ("Permanent Danger Area 2\n(OpenStreetMap)", (-110.982, 52.792), GOLD)):
    x, y = tf(lo_, la_); ax.text(x, y, txt, color=hx(c), fontsize=14, weight="bold", path_effects=[pe.withStroke(linewidth=3.5, foreground=hx(INK))])
ax.set_xlim(x0, x1); ax.set_ylim(y1, y0); ax.set_axis_off(); f.subplots_adjust(0, 0, 1, 1); mp = to_img(f)
# right panel: how big it should have been
f2, a2 = fig(600, 420)
cats = ["Observed\n(Landsat, Oct. 16)", "Standard rate,\nout by dusk", "Standard rate,\nburning overnight"]
mid = [1.06, fit["_sunset"]["standard_rate_final_km2_range_viirs_consistent"][1], fit["free_to_10am"]["standard_rate_final_km2_range_viirs_consistent"][1]]
lo_ = [0.91, fit["_sunset"]["standard_rate_final_km2_range_viirs_consistent"][0], fit["free_to_10am"]["standard_rate_final_km2_range_viirs_consistent"][0]]
hi_ = [1.13, fit["_sunset"]["standard_rate_final_km2_range_viirs_consistent"][2], fit["free_to_10am"]["standard_rate_final_km2_range_viirs_consistent"][2]]
a2.errorbar(range(3), mid, yerr=[np.subtract(mid, lo_), np.subtract(hi_, mid)], fmt="o", ms=11, color=hx(GOLD), ecolor=hx(GOLD), elinewidth=3, capsize=8)
a2.plot(0, 1.06, "o", ms=12, color=hx(RED))
for k, (m, h) in enumerate(zip(mid, hi_)): a2.text(k + 0.12, m, f"{m:.1f} km²", color=hx(CREAM), fontsize=13, weight="bold", va="center")
a2.set_xticks(range(3)); a2.set_xticklabels(cats, color=hx(CREAM), fontsize=12); a2.set_ylabel("Area burned (km²)", color=hx(CREAM), fontsize=13); a2.set_xlim(-0.4, 2.7); a2.set_ylim(0, 13.5)
a2.grid(axis="y", color=hx(GRIDC)); f2.subplots_adjust(0.12, 0.2, 0.98, 0.97); ch = to_img(f2)
W, H = 1600, 1290
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · BEFORE OCT. 17 · PERMANENT DANGER AREA 2",
               "Two fires in the same danger area in the four weeks before Oct. 17",
               f"Sept. 20: a fire of about {SEPT_KM2:.0f} km², first seen by satellite at 3:07 a.m. Oct. 14: a fire of about 1 km², seen once at 2:51 p.m.\n"
               "Both burned inside Permanent Danger Area 2, the danger area the Provost Marshal says the Oct. 17 fire stayed in before the wind shift. Background: Landsat 9, Oct. 16.")
im.paste(mp, (54, 200)); d = ImageDraw.Draw(im)
xr = 54 + 860 + 40
d.text((xr, 200), "Oct. 14: how big should it have been?", font=B(22), fill=GOLD)
im.paste(ch, (xr - 10, 236))
y = 236 + 420 + 14
for l, fnt, col in (("Free-burning at the standard grass-fire rate, a fire seen at", M(16), CREAM), ("2:51 p.m. grows to 2.8-6.7 km² by dusk, 4.8-12.5 by morning.", M(16), CREAM),
                    ("It stopped at about 1 km². The model fits best when it ran", M(16), CREAM), ("at a third to a sixth of the standard rate, as the Oct. 17", M(16), CREAM),
                    ("fire did before its wind shift, and started early, around", M(16), CREAM), ("6-8:30 a.m. (the earliest we tested). Or it was put out.", M(16), CREAM), ("", M(10), CREAM),
                    ("Satellite fire detections in the training area", B(18), GOLD),
                    ("Sept. 16  1:34 p.m.   north-east of the base", M(15), CREAM), ("Sept. 18  3:14 p.m.   PDA 2, about 5 km SE of the Oct. 14 burn", M(15), CREAM),
                    ("Sept. 20  3:07 a.m. to 2:55 p.m.   PDA 2 (31 detections)", B(15), (240, 170, 90)), ("Sept. 21  1:42 p.m.   PDA 3A F1, 9.5 km west", M(15), CREAM),
                    ("Oct. 14   2:51 p.m.   PDA 2, at Range 13", B(15), RED), ("Oct. 17   12:17 p.m. onward   PDA 2", B(15), CREAM)):
    d.text((xr, y), l, font=fnt, fill=col); y += 27
lx, ly = 70, 200 + 860 - 90
for sym, txt in (("▲", "VIIRS detections: Sept. 20 (open), Oct. 14 (filled)"), ("x", "Best-fit start points for the Oct. 14 fire (model)")):
    label(d, (lx, ly), f"{sym}  {txt}", col=CREAM, size=15); ly += 34
footer(im, ["Burns: Sentinel-2 Oct. 4 (L2A) vs Landsat 9 Oct. 16 (TOA), NBR thresholds per sensor (Oct. 14 burn 0.91-1.13 km² across thresholds); Sept. 20 burn as seen Oct. 4.",
            "Detections: NASA FIRMS (VIIRS S-NPP, NOAA-20, NOAA-21), MDT. Model: FBP O-1a, 95% curing, CZWN hourly weather, 9,180+ runs per variant.",
            "Range names and the PDA 2 outline: OpenStreetMap contributors (ODbL), not official.",
            SRC], fh=170)
im.convert("RGB").save(OUTD.replace("oct25_model_v4", "oct25_oct14_fire") + "cfb-wainwright-oct14-sept20-fires.jpg", quality=92); print("ok")
