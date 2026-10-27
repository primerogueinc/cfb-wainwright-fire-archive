"""Four-panel comparison: modelled burn under each wind schedule (8 km/h head spread, front at 3:16)
against the mapped scar. Run after spread.py."""
import os, sys
import numpy as np, pandas as pd, geopandas as gpd, rasterio
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = os.path.join(REPO, "data/authentic-stoic-alternative-hypothesis")
FD = "/usr/share/fonts/opentype/inter/"
for f in ("Inter-Medium.otf", "Inter-Bold.otf"):
    if os.path.exists(FD + f): fm.fontManager.addfont(FD + f)
plt.rcParams["font.family"] = "Inter" if os.path.exists(FD + "Inter-Medium.otf") else "DejaVu Sans"
BG, CREAM, MUTED, GOLD, TEAL, RED = "#1c140f", "#eee6d6", "#a99b84", "#d4af68", "#40e0d0", "#e0603c"

CRS = "EPSG:3400"
scar = max(gpd.read_file(os.path.join(REPO, "data/infrastructure/scar_patches_revised.geojson")).to_crs(CRS).geometry, key=lambda g: g.area)
summ = pd.read_csv(os.path.join(OUT, "summary.csv"))
cand = pd.read_csv(os.path.join(REPO, "data/location_analysis/candidate_points.csv"))
cp = gpd.GeoSeries(gpd.points_from_xy(cand.lon, cand.lat), crs=4326).to_crs(CRS)
r2 = cp[cand.point == "Range2 centroid (OSM)"].iloc[0]

TITLE = {"S0_fixed306": "A. Fixed 306° (Oct. 21 analysis)",
         "S1_stoic": "B. Challenge: 269° → 288° at 4:09",
         "S2_station_veer": "C. 269° → 305° by 3:50",
         "S3_fast_veer": "D. 269° → 305° by 3:30"}
fig, axs = plt.subplots(2, 2, figsize=(14, 14), facecolor=BG)
for ax, s in zip(axs.flat, TITLE):
    with rasterio.open(os.path.join(OUT, f"arrival_{s}_unconstrained_8kmh_front316.tif")) as r:
        A = r.read(1); A = np.where(A < -9000, np.nan, A); b = r.bounds
    row = summ[(summ.schedule == s) & (summ.front == "3:16") & (summ.ros_kmh == 8.0)].iloc[0]
    h, m = map(int, row.stop_time.split(":")); tstop = (h - 15) * 60 + m
    ext = (b.left, b.right, b.bottom, b.top)
    show = np.where(A <= tstop, A, np.nan)
    ax.set_facecolor(BG)
    im = ax.imshow(show, extent=ext, cmap="inferno_r", vmin=16, vmax=tstop, alpha=0.9)
    ax.contour(np.flipud(show), levels=list(range(20, int(tstop) + 1, 10)), extent=ext, colors=BG, linewidths=0.6, origin="lower")
    gpd.GeoSeries([scar], crs=CRS).boundary.plot(ax=ax, color=TEAL, linewidth=2.2)
    ax.plot(r2.x, r2.y, "o", ms=9, mfc="none", mec=CREAM, mew=2)
    ax.annotate("Range 2", (r2.x, r2.y), xytext=(8, -14), textcoords="offset points", color=CREAM, fontsize=11)
    minx, miny, maxx, maxy = scar.bounds
    ax.set_xlim(minx - 1500, maxx + 3500); ax.set_ylim(miny - 1500, maxy + 1500)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
    for sp in ax.spines.values(): sp.set_color("#35281f")
    ax.set_title(TITLE[s], color=CREAM, fontsize=15, fontweight="bold", loc="left")
    ax.text(0.02, 0.03, f"Overlap with scar (Jaccard): {row.jaccard_vs_scar:.2f}\nEast/south reach: {row.east_to_south_ratio:.2f} (scar: 1.17)",
            transform=ax.transAxes, color=CREAM, fontsize=12, va="bottom",
            bbox=dict(facecolor=BG, edgecolor="none", alpha=0.85, pad=6))
fig.suptitle("Does a westerly wind after 3:16 p.m. fit the burn scar?", color=GOLD, fontsize=22, fontweight="bold", x=0.03, ha="left", y=0.99)
fig.text(0.03, 0.948, "Modelled burn (shaded by arrival time, 10-min contours) stopped when it equals the scar's area; teal = mapped scar. 8 km/h head spread, front at 3:16 p.m., no suppression.",
         color=MUTED, fontsize=11.5, ha="left")
fig.text(0.03, 0.012, "Model and data: github.com/primerogueinc/cfb-wainwright-fire-archive (authentic-stoic-alternative-hypothesis). Wind: ECCC CZWN swob, Oct. 17, 2026. Graphic: Prime Rogue Inc.",
         color=MUTED, fontsize=10, ha="left")
plt.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.04, wspace=0.03, hspace=0.07)
fig.savefig(os.path.join(OUT, "wind_schedule_comparison.png"), dpi=110, facecolor=BG)
print("ok")
