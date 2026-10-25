"""Graphic: every satellite-detected fire at CFB Wainwright from Sept. 16 to Oct. 17, 2026, boxed on an overview map, with a zoomed panel
for each and a comparison row. Usage: python3 scripts/maps/g36_fires_overview.py"""
import sys, glob, json, os; sys.path.insert(0, "scripts/maps")
from v4fig import *
import numpy as np, geopandas as gpd, pandas as pd, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from pyproj import Transformer
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle
tf = Transformer.from_crs(4326, 3400, always_xy=True).transform
FC = REPO + "data/fire_compare/"
F = pd.read_csv(REPO + "data/firms/history_2012-2026/all_detections_merged.csv"); F = F[F.source.str.contains("VIIRS|LANDSAT") & (F.acq_date >= "2026-09-16") & (F.acq_date <= "2026-10-17")]
F["mdt"] = pd.to_datetime(F.acq_date + " " + F.acq_time.astype(str).str.zfill(4)) - pd.Timedelta(hours=6)
s17 = gpd.read_file(REPO + "data/infrastructure/scar_patches_revised.geojson").to_crs(3400); s17 = s17[s17.patch == "main Oct 17 run"]
o = gpd.read_file(REPO + "data/infrastructure/osm_infrastructure_ODbL.geojson").to_crs(3400); pda2 = o[o.name == "Permanent Danger Area 2"]
RG = o[(o.military == "range") & o.name.fillna("").ne("")].copy(); RG["short"] = RG.name.str.replace(r" \(.*\)", "", regex=True).str.replace("AFV Battle Run", "AFV Battle Run")
def scar(f):
    p = FC + f + "/scar.geojson"; return gpd.read_file(p).to_crs(3400) if os.path.exists(p) else None
def summ(f):
    p = FC + f + "/summary.json"; return json.load(open(p)) if os.path.exists(p) else None
FIRES = [  # id, label, date filter, colour, box half-size (m)
    ("aug27_28", "A", "Aug. 27-28, Sept. 21", ["2026-08-27", "2026-08-28", "2026-09-21"], (200, 120, 200), 2400),
    ("sept16", "B", "Sept. 16", ["2026-09-16"], (150, 200, 120), 900),
    ("sept18_20", "C", "Sept. 18-20", ["2026-09-18", "2026-09-19", "2026-09-20"], (214, 140, 60), 2600),
    ("oct14", "D", "Oct. 14", ["2026-10-14"], RED, 1200),
    ("oct17", "E", "Oct. 17", ["2026-10-17"], CREAM, 3000)]
x0, y0 = tf(-111.10, 52.845); x1, y1 = tf(-110.82, 52.695); RES = 20; W_, H_ = int((x1 - x0) / RES), int((y0 - y1) / RES); T = from_origin(x0, y0, RES, RES)
L = glob.glob("/home/claude/cfb-wainwright-landsat-8-9/landsat/2026-10-16/*/*B7.TIF")[0].replace("B7.TIF", "B%s.TIF")
def rp(b):
    with rasterio.open(L % b) as r:
        d = np.zeros((H_, W_), "float32"); reproject(r.read(1).astype("float32") * 2e-5 - 0.1, d, src_transform=r.transform, src_crs=r.crs, dst_transform=T, dst_crs="EPSG:3400", resampling=Resampling.bilinear); return d
rgb = np.dstack([rp(b) for b in "765"]); lo, hi = np.percentile(rgb, 2, axis=(0, 1)), np.percentile(rgb, 98, axis=(0, 1)); rgb = np.clip((rgb - lo) / (hi - lo), 0, 1) * 0.72
EXT = [x0, x0 + W_ * RES, y0 - H_ * RES, y0]
st = lambda c, s=13: dict(color=hx(c), fontsize=s, weight="bold", path_effects=[pe.withStroke(linewidth=3.5, foreground=hx(INK))])
def draw(ax, focus=None):
    ax.imshow(rgb, extent=EXT); pda2.boundary.plot(ax=ax, color=hx(GOLD), lw=1.4, ls="--")
    RG.plot(ax=ax, facecolor="none", edgecolor="white", lw=1.0)
    for nm, g in zip(RG.short, RG.geometry):
        c = g.representative_point(); ax.annotate(nm, (c.x, c.y), (4, 4), textcoords="offset points", **st(CREAM, 9 if focus is None else 11))
    for fid, lab, nm, dates, col, half in FIRES:
        g = s17 if fid == "oct17" else scar(fid)
        if g is not None: g.boundary.plot(ax=ax, color=hx(col), lw=2.0 if focus == fid else 1.3)
        d = F[F.acq_date.isin(dates)]
        if fid == "oct17": d = d[d.mdt.dt.hour < 15]
        else:
            c = {"aug27_28": (52.728, -111.04), "sept16": (52.825, -110.858), "sept18_20": (52.73, -110.91), "oct14": (52.7549, -110.9389)}[fid]
            d = d[np.hypot((d.latitude - c[0]) * 111, (d.longitude - c[1]) * 67.4) < 4]
        px, py = tf(d.longitude.values, d.latitude.values); ax.plot(px, py, "^", ms=5 if focus is None else 8, mfc=hx(col), mec=hx(INK), mew=0.6)
CENT = {}
for fid, lab, nm, dates, col, half in FIRES:
    g = s17 if fid == "oct17" else scar(fid)
    if g is not None and len(g): c = g.geometry.union_all().centroid; CENT[fid] = (c.x, c.y)
    else: CENT[fid] = tf(-110.858, 52.825)
f, ax = fig(980, 760); draw(ax)
for fid, lab, nm, dates, col, half in FIRES:
    cx, cy = CENT[fid]; ax.add_patch(Rectangle((cx - half, cy - half), 2 * half, 2 * half, fill=False, ec=hx(col), lw=2.2))
    ax.text(cx - half + 120, cy + half - 420, lab, **st(col, 22))
x, y = tf(-110.99, 52.83); ax.text(x, y, "Permanent Danger Area 2 (dashed, OpenStreetMap)", **st(GOLD, 12))
xb = EXT[1] - 2600; yb = EXT[2] + 500; ax.plot([xb, xb + 2000], [yb, yb], color=hx(CREAM), lw=3); ax.text(xb, yb + 150, "2 km", **st(CREAM, 11))
ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_axis_off(); f.subplots_adjust(0, 0, 1, 1); OV = to_img(f)
PAN = []
for fid, lab, nm, dates, col, half in FIRES:
    f, ax = fig(300, 300); draw(ax, focus=fid); cx, cy = CENT[fid]
    ax.set_xlim(cx - half, cx + half); ax.set_ylim(cy - half, cy + half); ax.set_axis_off()
    for sp in ("left", "right", "top", "bottom"): pass
    sb = half * 0.5; sb = 500 if half < 1500 else 1000
    ax.plot([cx + half * 0.9 - sb, cx + half * 0.9], [cy - half * 0.88] * 2, color=hx(CREAM), lw=3); ax.text(cx + half * 0.9 - sb, cy - half * 0.82, f"{sb/1000:g} km", **st(CREAM, 10))
    f.subplots_adjust(0, 0, 1, 1); PAN.append(to_img(f))
W, H = 1600, 1560
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · EVERY FIRE SATELLITES SAW, AUG. 27-OCT. 17, 2026",
               "Five fires in seven weeks, all but one inside permanent danger areas",
               "Boxes A-E on the overview map are shown up close below. Outlines: burn scars from Sentinel-2 (Oct. 4) and Landsat 9 (Oct. 16); triangles: NASA VIIRS fire detections.\n"
               "Background: Landsat 9 shortwave infrared, Oct. 16 (before the Oct. 17 fire; its outline is the final scar).")
im.paste(OV, (54, 205)); d = ImageDraw.Draw(im)
# right column: comparison list
xr = 54 + 980 + 30; y = 205
d.text((xr, y), "How each fire behaved", font=B(22), fill=GOLD); y += 40
def fmt(fid):
    s = summ(fid)
    if fid == "oct17": return ["Burned 10.8 km²; crept at about a sixth", "of the standard rate all day, then ran", "4.4-12 km/h after the 3:16 p.m. front.", "FWI 30.8 (Extreme). Four killed."]
    if s is None: return ["(model running)"]
    fw = ", ".join(f"{c['fwi']:.0f}" for c in s["cwfis_days"]); sc = s["scar_km2"]; out = []
    out.append(f"Burn: {'too small to map' if sc < 0.05 else f'{sc:.1f} km²'}. FWI {fw}.")
    out.append(f"Seen on {len(s['passes_mdt'])} passes, {s['passes_mdt'][0]}-{s['passes_mdt'][-1]}" + (f"; {s['night_detections']} at night" if s["night_detections"] else "") + ".")
    v = s.get("dusk")
    if v and v.get("standard_rate_km2_p10_p50_p90"):
        p = v["standard_rate_km2_p10_p50_p90"]; out.append(f"Standard rate, out by dusk: {p[0]:.1f}-{p[2]:.1f} km²" + (f" ({v['ratio_standard_to_observed']:.1f}x)" if v.get("ratio_standard_to_observed") else "") + ".")
    if fid == "aug27_28": out.append("Seen again Sept. 21, 1:42-3:23 p.m., same scar.")
    return out
for fid, lab, nm, dates, col, half in FIRES:
    d.text((xr, y), f"{lab}  {nm}", font=B(19), fill=col); y += 28
    for l in fmt(fid): d.text((xr + 30, y), l, font=M(15), fill=CREAM); y += 23
    y += 12
# panels
py = 205 + 760 + 30
for k, ((fid, lab, nm, dates, col, half), p) in enumerate(zip(FIRES, PAN)):
    px = 54 + k * 302; im.paste(p, (px, py)); d.rectangle([px, py, px + 299, py + 299], outline=col, width=3)
    label(d, (px + 8, py + 8), f"{lab}  {nm}", col=col, size=17)
footer(im, ["Scars: NBR < -0.05 on Sentinel-2 Oct. 4 touching each fire's detections (A-C; older scars touching them would be included);",
            "D: Sentinel-2 Oct. 4 vs Landsat 9 Oct. 16; E: Sentinel-2 Oct. 19. Standard rate: FBP O-1a grass, 95% curing, station weather, runs matching every pass.",
            "Detections: NASA FIRMS (VIIRS S-NPP, NOAA-20, NOAA-21; Landsat). White outlines: ranges as mapped on OpenStreetMap; names and PDA 2: OpenStreetMap contributors (ODbL), not official.", SRC], fh=175)
im.convert("RGB").save(REPO + "data/graphics_published/oct25_oct14_fire/cfb-wainwright-all-fires-sept16-oct17.jpg", quality=92); print("ok")
