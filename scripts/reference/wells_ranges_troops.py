"""Full-bleed well + range + troop-area maps (public: road head and 500 m zone; --private adds the source circle, never commit that output publicly).
Based on wells_fullbleed_sumerian.py. Full-bleed well maps on pre-fire (Oct. 4) and post-fire (Oct. 19) Sentinel-2, Sumerian Oil & Gas highlighted.
Usage: python3 wells_ranges_troops.py ARCHIVE_1 ARCHIVE_2 OUT_DIR [--private]"""
import sys, os
import numpy as np, pandas as pd, geopandas as gpd, rasterio, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from rasterio.windows import from_bounds
from pyproj import Transformer
A1, A2, OUT = sys.argv[1:4]; PRIV = '--private' in sys.argv; os.makedirs(OUT, exist_ok=True)
U = "EPSG:32612"; T = Transformer.from_crs(4326, 32612, always_xy=True)
cx, cy = T.transform(-110.9210, 52.7767)
VIEWS = {"12km": (cx - 12500, cx + 12500, cy - 9500, cy + 9500, 2500, 1900, 1.0),
         "ranges": (*[T.transform(-110.99, 52.735)[0], T.transform(-110.855, 52.735)[0]], T.transform(-110.9, 52.737)[1], T.transform(-110.9, 52.806)[1], None, 2000, 1.35)}
VIEWS = {k: (a, b, c, d, w or int(round(h * (b - a) / (d - c))), h, s) for k, (a, b, c, d, w, h, s) in VIEWS.items()}
RH = T.transform(-110.89965, 52.77045)   # road head (public, v5.3 / fire-behaviour set)
CIRC = {"c": ((-110.8775, 52.7521), 300.0, 450.0), "alt": ((-110.8800, 52.7532), 450.0)}
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
def tci(sat, day, X0, X1, Y0, Y1, W, H):
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
def draw(img, title, fn, X0, X1, Y0, Y1, W, H, S, dpi=100):
    fig = plt.figure(figsize=(W / dpi, H / dpi), dpi=dpi); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)
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
    rr = rso[~rso.index.str.contains("barrier")]
    for n, r in rr.iterrows():
        x, y = T.transform(r.lon, r.lat); agl = n == "Range 11"
        if agl:
            ax.plot(x, y, "s", mfc="#22d3ee", mec="w", mew=2, ms=15 * S, zorder=11)
            for rad in (500, 1000): ax.add_patch(plt.Circle((x, y), rad, fill=False, ec="#22d3ee", lw=1.4, ls=(0, (4, 3)), zorder=5))
        else:
            ax.plot(x, y, "s", mfc="white", mec="k", ms=8 * S, zorder=9)
        lab = n.replace("Range ", "R") + ("  " + r.description.split(" (")[0] if S > 1 else "")
        if agl: lab = "R11 AGL range (AGLS / M203)" if S > 1 else "R11 AGL"
        dy = {"Range 15": -16, "Range 14": -16, "Range 19": 6}.get(n, 6) * S
        ax.annotate(lab, (x, y), xytext=(8 * S, dy), textcoords="offset points", fontsize=(12.5 if agl else 10.5) * S ** .5,
                    color="#22d3ee" if agl else "w", weight="bold", path_effects=halo, zorder=12)
    # troop-area hypotheses (public)
    ax.add_patch(plt.Circle(RH, 500, fc="#ef4444", alpha=.16, ec="none", zorder=4))
    ax.add_patch(plt.Circle(RH, 500, fill=False, ec="#ef4444", lw=2.2, zorder=10))
    ax.plot(*RH, marker="*", ms=17 * S, mfc="#ef4444", mec="w", mew=1.2, zorder=13)
    ax.annotate("Road head (v5.3)\n500 m troop-area zone", RH, xytext=(-150 * S, -40 * S), textcoords="offset points", fontsize=11 * S ** .5, color="#fecaca", weight="bold", path_effects=halo, zorder=13)
    if PRIV:
        (lo, la), r1, r2 = CIRC["c"]; px, py = T.transform(lo, la)
        ax.add_patch(plt.Circle((px, py), r1, fc="#a855f7", alpha=.2, ec="#a855f7", lw=2.4, zorder=10))
        ax.add_patch(plt.Circle((px, py), r2, fill=False, ec="#a855f7", lw=1.4, ls="--", zorder=10))
        (lo, la), r3 = CIRC["alt"]; qx, qy = T.transform(lo, la)
        ax.add_patch(plt.Circle((qx, qy), r3, fill=False, ec="#d8b4fe", lw=1.2, ls=":", zorder=10))
        ax.annotate("PRIVATE: source circle\n300 m (450 m dashed; alt. dotted)", (px, py), xytext=(30 * S, -30 * S), textcoords="offset points", fontsize=11 * S ** .5, color="#e9d5ff", weight="bold", path_effects=halo, zorder=13)
    t = np.linspace(0, 2 * np.pi, 400); ax.plot(cx + 12000 * np.cos(t), cy + 12000 * np.sin(t), color="w", lw=.8, ls=(0, (6, 6)), alpha=.6)
    wx, wy = T.transform(-110.857, 52.835)
    if X0 < wx < X1 and Y0 < wy < Y1: ax.annotate("Wainwright", (wx, wy), fontsize=12, color="w", style="italic", path_effects=halo)
    ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)
    hand = [Line2D([], [], ls="", marker=m, mfc=c, mec="k", ms=8, label=l) for m, c, l in MK.values()]
    hand += [Line2D([], [], ls="", marker="s", mfc="#22d3ee", mec="w", ms=10, label="R11 AGL range, 500 m and 1 km rings"),
             Line2D([], [], ls="", marker="*", mfc="#ef4444", mec="w", ms=13, label="Road head; red zone = 500 m troop area (v5.3)")]
    if PRIV: hand += [Line2D([], [], color="#a855f7", lw=2.4, label="PRIVATE source circle (300 m / 450 m)")]
    hand += [Line2D([], [], ls="", marker="o", mfc="none", mec=SUMC, mew=2.2, ms=13, label=f"Sumerian Oil & Gas well ({int(s['sum'].sum())} of {len(s)})"),
             Line2D([], [], color=SUMC, lw=1.8, label="Sumerian gas pipeline, operating"), Line2D([], [], color=SUMC, lw=1, ls="--", label="Sumerian pipeline, abandoned / discontinued"),
             Line2D([], [], color="#fb923c", lw=1, label="Other operators' pipelines"), Line2D([], [], color="#ffd400", lw=1.6, label="Oct. 17 burn outline"),
             Line2D([], [], ls="", marker="s", mfc="w", mec="k", ms=8, label="Other ranges (2024 Range Standing Orders)")]
    lg = ax.legend(handles=hand, loc="lower left", fontsize=10 * S ** .5, framealpha=.82, facecolor="#111", edgecolor="none", labelcolor="w", borderpad=.9)
    ax.text(.008, .988, title, transform=ax.transAxes, fontsize=15 * S ** .5, color="w", weight="bold", va="top", path_effects=halo)
    ax.text(.992, .008, ("Wells within 12 km (dashed circle) of the Oct. 17 site. " if S == 1 else "") + " AER ST37 well list (Oct. 1, 2026) and AER pipelines. Sentinel-2 L2A, 10 m (contains modified Copernicus data).\n"
            "Ranges: CFB Wainwright Range Standing Orders (2024). Burn outline: Prime Rogue v5. Prime Rogue Inc.", transform=ax.transAxes, fontsize=8.5, color="w", ha="right", va="bottom", path_effects=halo)
    sb = 2000 if S == 1 else 1000; ax.plot([X1 - 600 - sb, X1 - 600], [Y1 - 700] * 2, color="w", lw=4, path_effects=halo); ax.text(X1 - 600 - sb / 2, Y1 - 600, f"{sb // 1000} km", color="w", ha="center", fontsize=11, weight="bold", path_effects=halo)
    fig.savefig(os.path.join(OUT, fn), dpi=dpi, pad_inches=0); plt.close(fig)
from PIL import Image
tag = "PRIVATE_" if PRIV else ""
for v, (X0, X1, Y0, Y1, W, H, S) in VIEWS.items():
    for sat, day, word in (("S2C", "04", "BEFORE"), ("S2B", "19", "AFTER")):
        img = tci(sat, day, X0, X1, Y0, Y1, W, H)
        what = "ranges, AGL range, troop area, wells and pipelines" + (" + PRIVATE circle" if PRIV else "")
        draw(img, f"{word} · Sentinel-2, Oct. {int(day)}, 2026 · {what} · Sumerian in magenta", f"{tag}ranges_troops_{v}_{word.lower()}_oct{day}.png", X0, X1, Y0, Y1, W, H, S)
    a = Image.open(os.path.join(OUT, f"{tag}ranges_troops_{v}_before_oct04.png")).convert("RGB"); b = Image.open(os.path.join(OUT, f"{tag}ranges_troops_{v}_after_oct19.png")).convert("RGB")
    c = Image.new("RGB", (a.width * 2 + 12, a.height), "white"); c.paste(a, (0, 0)); c.paste(b, (a.width + 12, 0)); c.save(os.path.join(OUT, f"{tag}ranges_troops_{v}_before_after.jpg"), quality=88)
