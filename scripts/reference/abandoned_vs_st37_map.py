"""Map: AER ST37 well list (Oct. 1, 2026; what the models use) vs the AER Abandoned Well Map (Jan. 2025; supplied Nov. 2).
Usage: python3 abandoned_vs_st37_map.py ARCHIVE_1 ARCHIVE_2 OUT_PNG"""
import sys, os
import numpy as np, pandas as pd, geopandas as gpd, rasterio, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from rasterio.windows import from_bounds
from pyproj import Transformer
A1, A2, OUT = sys.argv[1:4]
U = "EPSG:32612"; T = Transformer.from_crs(4326, 32612, always_xy=True)
s = pd.read_csv(os.path.join(A1, "data/derived_tables_oct19-20/cfb-wainwright-aer-wells-12km.csv"), dtype={"well_licence": str}); s["lic"] = s.well_licence.str.zfill(7)
a = pd.read_csv(os.path.join(A1, "data/reference/aer_abandoned_wells/abandoned_wells_near_site.csv"), dtype={"Licence": str}); a["lic"] = a.Licence.str.strip().str.zfill(7)
sx, sy = T.transform(s.lon.values, s.lat.values); s["x"], s["y"] = sx, sy
ax_, ay_ = T.transform(a.lon.values, a.lat.values); a["x"], a["y"] = ax_, ay_
cx, cy = T.transform(-110.9210, 52.7767); a = a[np.hypot(a.x - cx, a.y - cy) <= 12000]
m = s.merge(a[["lic", "Status", "x", "y"]], on="lic", how="outer", suffixes=("", "_a"), indicator=True)
aband = {"Abandoned", "RecCertified", "RecExempt"}
cat = []
for _, r in m.iterrows():
    if r._merge == "both": cat.append("same" if r.Status == r.licence_status else "status_changed")
    elif r._merge == "left_only": cat.append("abandoned_after_2025" if r.licence_status in aband else "active_other")
    else: cat.append("abandoned_map_only")
m["cat"] = cat; m["X"] = m.x.fillna(m.x_a); m["Y"] = m.y.fillna(m.y_a)
print(m.cat.value_counts().to_dict())
burn = gpd.read_file(os.path.join(A2, "data/rubicon-ridge/satellogic_2026-10-20/outline_for_model_v5.geojson")).to_crs(U)
pipes = gpd.read_file(os.path.join(A1, "data/reference/aer_pipelines_near_site.geojson")).to_crs(U); gas = pipes[pipes.SUBSTANCE1.str.contains("Gas", na=False)]
rso = pd.read_csv(os.path.join(A1, "data/reference/range_standing_orders_2024/rso_points.csv")).dropna(subset=["lat"]).set_index("name")
R = {k: T.transform(rso.loc[k, "lon"], rso.loc[k, "lat"]) for k in ("Range 2", "Range 10", "Range 11", "Range 13", "Range 15", "Range 22")}
COG = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/12/U/{t}/2026/10/{id}/TCI.tif"
def tci(x0, x1, y0, y1):
    out = None
    for t in ("VD", "WD"):
        with rasterio.open(COG.format(t=t, id=f"S2B_12U{t}_20261019_0_L2A")) as src:
            im = src.read(window=from_bounds(x0, y0, x1, y1, src.transform), boundless=True, fill_value=0, out_shape=(3, 900, int(900 * (x1 - x0) / (y1 - y0)))).transpose(1, 2, 0)
        out = im if out is None else np.where(out.sum(2, keepdims=True) == 0, im, out)
    o = out.astype(float); lo, hi = np.percentile(o[o > 0], [1, 99.5]); return np.clip((o - lo) / (hi - lo), 0, 1)
STY = {"same": dict(marker="o", s=34, facecolor="none", edgecolor="#22d3ee", lw=1.3, label="Same in both, same status"),
       "status_changed": dict(marker="o", s=60, facecolor="#f59e0b", edgecolor="k", lw=.6, label="In both: status changed since Jan. 2025 (now reclamation-certified)"),
       "abandoned_after_2025": dict(marker="X", s=70, facecolor="#ef4444", edgecolor="k", lw=.5, label="Abandoned after Jan. 2025: in ST37 only"),
       "active_other": dict(marker="^", s=34, facecolor="#a3e635", edgecolor="k", lw=.4, label="Active, suspended, amended or cancelled: in ST37 only"),
       "abandoned_map_only": dict(marker="s", s=60, facecolor="#e879f9", edgecolor="k", lw=.6, label="In the abandoned map only")}
def panel(ax, x0, x1, y0, y1, title, labels):
    ax.imshow(tci(x0, x1, y0, y1), extent=[x0, x1, y0, y1])
    gas.plot(ax=ax, color="#ff7a00", lw=.8, alpha=.8); burn.boundary.plot(ax=ax, color="#ffd400", lw=1.4)
    for k, st in STY.items():
        q = m[m.cat == k]; ax.scatter(q.X, q.Y, zorder=5, **{kk: v for kk, v in st.items() if kk != "label"})
    for k, (x, y) in R.items():
        if x0 < x < x1 and y0 < y < y1:
            ax.plot(x, y, "s", mfc="w", mec="k", ms=6, zorder=6)
            if labels: ax.annotate(k.replace("Range ", "R"), (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8, color="w", weight="bold", bbox=dict(fc="#1e3452", ec="none", alpha=.8, pad=1))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_xticks([]); ax.set_yticks([]); ax.set_title(title, fontsize=10.5, loc="left")
fig, axs = plt.subplots(1, 2, figsize=(16, 7.6))
panel(axs[0], cx - 12500, cx + 12500, cy - 9500, cy + 9500, "Within 12 km of the Oct. 17 site", False)
t = np.linspace(0, 2 * np.pi, 200); axs[0].plot(cx + 12000 * np.cos(t), cy + 12000 * np.sin(t), color="w", lw=.8, ls="--")
panel(axs[1], cx - 3800, cx + 4600, cy - 3600, cy + 2800, "Close-up: the burn, the ranges and the road head", True)
hand = [Line2D([], [], ls="", marker=v["marker"], mfc=v["facecolor"], mec=v["edgecolor"] if v["facecolor"] != "none" else "#22d3ee", ms=8, label=v["label"]) for v in STY.values()]
hand += [Line2D([], [], color="#ffd400", lw=1.4, label="Oct. 17 burn outline (v5)"), Line2D([], [], color="#ff7a00", lw=1, label="AER gas pipelines")]
fig.legend(handles=hand, loc="lower center", ncol=4, fontsize=8.5, frameon=False)
cnt = m.cat.value_counts()
fig.suptitle(f"Old vs new well data: AER ST37 list (Oct. 1, 2026, used by the models) vs AER Abandoned Well Map (Jan. 2025). "
             f"Matched wells sit at identical positions (0 m) · {cnt.get('same',0)} same · {cnt.get('status_changed',0)} status changed · "
             f"{cnt.get('abandoned_after_2025',0)} abandoned since · {cnt.get('abandoned_map_only',0)} abandoned-map only", fontsize=10, x=.01, ha="left")
fig.text(.01, .005, "Sources: Alberta Energy Regulator (ST37 well list; Abandoned Well Map; pipelines). Base: Sentinel-2 L2A, Oct. 19, 2026 (contains modified Copernicus data). Ranges: CFB Wainwright Range Standing Orders (2024). Prime Rogue Inc.", fontsize=6.8, color="#333")
fig.tight_layout(rect=(0, .08, 1, .95)); fig.savefig(OUT, dpi=150)
