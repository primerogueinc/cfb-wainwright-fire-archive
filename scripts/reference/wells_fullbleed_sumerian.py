"""Full-bleed well maps on pre-fire (Oct. 4) and post-fire (Oct. 19) Sentinel-2, Sumerian Oil & Gas highlighted.
Usage: python3 wells_fullbleed_sumerian.py ARCHIVE_1 ARCHIVE_2 OUT_DIR"""
import sys, os
import numpy as np, pandas as pd, geopandas as gpd, rasterio, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from rasterio.windows import from_bounds
from pyproj import Transformer
A1, A2, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
U = "EPSG:32612"; T = Transformer.from_crs(4326, 32612, always_xy=True)
cx, cy = T.transform(-110.9210, 52.7767)
X0, X1, Y0, Y1 = cx - 12500, cx + 12500, cy - 9500, cy + 9500
W, H = 2500, 1900   # 10 m pixels, native Sentinel-2 resolution
s = pd.read_csv(os.path.join(A1, "data/derived_tables_oct19-20/cfb-wainwright-aer-wells-12km.csv"), dtype={"well_licence": str})
s["x"], s["y"] = T.transform(s.lon.values, s.lat.values)
s["sum"] = s.licensee.str.contains("Sumerian", na=False)
CL = {"Issued": "lic", "Amended": "lic", "Suspension": "sus", "Abandoned": "aban", "RecCertified": "aban", "RecExempt": "aban", "Cancelled": "can"}
s["cls"] = s.licence_status.map(CL).fillna("can")
burn = gpd.read_file(os.path.join(A2, "data/rubicon-ridge/satellogic_2026-10-20/outline_for_model_v5.geojson")).to_crs(U)
p = gpd.read_file(os.path.join(A1, "data/reference/aer_pipelines_near_site.geojson")).to_crs(U)
p["sum"] = p.COMP_NAME.str.contains("Sumerian", na=False); p["live"] = p.SEG_STATUS.eq("Operating")
rso = pd.read_csv(os.path.join(A1, "data/reference/range_standing_orders_2024/rso_points.csv")).dropna(subset=["lat"]).set_index("name")
COG = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/12/U/{t}/2026/10/{id}/TCI.tif"
def tci(sat, day):
    out = None
    for t in ("VD", "WD"):
        with rasterio.open(COG.format(t=t, id=f"{sat}_12U{t}_202610{day}_0_L2A")) as src:
            im = src.read(window=from_bounds(X0, Y0, X1, Y1, src.transform), boundless=True, fill_value=0, out_shape=(3, H, W)).transpose(1, 2, 0)
        out = im if out is None else np.where(out.sum(2, keepdims=True) == 0, im, out)
    o = out.astype(float); lo, hi = np.percentile(o[o > 0], [1, 99.6]); return np.clip((o - lo) / (hi - lo), 0, 1) ** 0.9
MK = {"lic": ("o", "#facc15", "Licensed (issued / amended)"), "sus": ("D", "#38bdf8", "Suspended"),
      "aban": ("X", "#f87171", "Abandoned / reclaimed"), "can": ("v", "#d4d4d4", "Cancelled")}
SUMC = "#ff2bd6"
halo = [pe.withStroke(linewidth=3, foreground="black")]
def draw(img, title, fn, dpi=100):
    fig = plt.figure(figsize=(W / dpi, H / dpi), dpi=dpi); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    ax.imshow(img, extent=[X0, X1, Y0, Y1], interpolation="lanczos")
    p[~p["sum"]].plot(ax=ax, color="#fb923c", lw=.7, alpha=.55)
    p[p["sum"] & ~p.live].plot(ax=ax, color=SUMC, lw=1.0, alpha=.55, linestyle="--")
    p[p["sum"] & p.live].plot(ax=ax, color=SUMC, lw=1.7, alpha=.95)
    burn.boundary.plot(ax=ax, color="#ffffff", lw=2.6, alpha=.7); burn.boundary.plot(ax=ax, color="#ffd400", lw=1.4)
    for k, (m, c, _) in MK.items():
        q = s[(s.cls == k) & ~s["sum"]]; ax.scatter(q.x, q.y, marker=m, s=34, c=c, edgecolors="k", linewidths=.6, zorder=6)
        q = s[(s.cls == k) & s["sum"]]
        ax.scatter(q.x, q.y, marker="o", s=190, facecolors="none", edgecolors=SUMC, linewidths=2.2, zorder=7)
        ax.scatter(q.x, q.y, marker=m, s=46, c=c, edgecolors="k", linewidths=.7, zorder=8)
    for n in ("Range 2", "Range 10", "Range 11", "Range 13", "Range 15", "Range 22"):
        x, y = T.transform(rso.loc[n, "lon"], rso.loc[n, "lat"])
        ax.plot(x, y, "s", mfc="white", mec="k", ms=8, zorder=9)
        ax.annotate(n.replace("Range ", "R"), (x, y), xytext=(6, -14 if n == "Range 15" else 5), textcoords="offset points", fontsize=11, color="w", weight="bold", path_effects=halo, zorder=10)
    t = np.linspace(0, 2 * np.pi, 400); ax.plot(cx + 12000 * np.cos(t), cy + 12000 * np.sin(t), color="w", lw=.8, ls=(0, (6, 6)), alpha=.6)
    wx, wy = T.transform(-110.857, 52.835); ax.annotate("Wainwright", (wx, wy), fontsize=12, color="w", style="italic", path_effects=halo)
    ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)
    hand = [Line2D([], [], ls="", marker=m, mfc=c, mec="k", ms=8, label=l) for m, c, l in MK.values()]
    hand += [Line2D([], [], ls="", marker="o", mfc="none", mec=SUMC, mew=2.2, ms=13, label=f"Sumerian Oil & Gas well ({int(s['sum'].sum())} of {len(s)})"),
             Line2D([], [], color=SUMC, lw=1.8, label="Sumerian gas pipeline, operating"), Line2D([], [], color=SUMC, lw=1, ls="--", label="Sumerian pipeline, abandoned / discontinued"),
             Line2D([], [], color="#fb923c", lw=1, label="Other operators' pipelines"), Line2D([], [], color="#ffd400", lw=1.6, label="Oct. 17 burn outline"),
             Line2D([], [], ls="", marker="s", mfc="w", mec="k", ms=8, label="Range (2024 Range Standing Orders)")]
    lg = ax.legend(handles=hand, loc="lower left", fontsize=10, framealpha=.82, facecolor="#111", edgecolor="none", labelcolor="w", borderpad=.9)
    ax.text(.008, .988, title, transform=ax.transAxes, fontsize=15, color="w", weight="bold", va="top", path_effects=halo)
    ax.text(.992, .008, "Wells within 12 km (dashed circle) of the Oct. 17 site. AER ST37 well list (Oct. 1, 2026) and AER pipelines. Sentinel-2 L2A, 10 m (contains modified Copernicus data).\n"
            "Ranges: CFB Wainwright Range Standing Orders (2024). Burn outline: Prime Rogue v5. Prime Rogue Inc.", transform=ax.transAxes, fontsize=8.5, color="w", ha="right", va="bottom", path_effects=halo)
    sb = 2000; ax.plot([X1 - 600 - sb, X1 - 600], [Y1 - 700] * 2, color="w", lw=4, path_effects=halo); ax.text(X1 - 600 - sb / 2, Y1 - 600, "2 km", color="w", ha="center", fontsize=11, weight="bold", path_effects=halo)
    fig.savefig(os.path.join(OUT, fn), dpi=dpi, pad_inches=0); plt.close(fig)
pre = tci("S2C", "04"); post = tci("S2B", "19")
draw(pre, "BEFORE · Sentinel-2, Oct. 4, 2026 · wells and pipelines, Sumerian Oil & Gas highlighted", "wells_sumerian_before_oct04.png")
draw(post, "AFTER · Sentinel-2, Oct. 19, 2026 · wells and pipelines, Sumerian Oil & Gas highlighted", "wells_sumerian_after_oct19.png")
from PIL import Image
a = Image.open(os.path.join(OUT, "wells_sumerian_before_oct04.png")); b = Image.open(os.path.join(OUT, "wells_sumerian_after_oct19.png"))
c = Image.new("RGB", (a.width + b.width, a.height)); c.paste(a, (0, 0)); c.paste(b, (a.width, 0)); c.save(os.path.join(OUT, "wells_sumerian_before_after.jpg"), quality=90)
