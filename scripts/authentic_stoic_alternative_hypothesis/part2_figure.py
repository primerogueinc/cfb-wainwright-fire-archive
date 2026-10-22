"""Part 2 figure: 20 small maps (4 references x 5 distance bands), each showing the ground that is
in the band for all 12 winds, coloured by ACH zone. Run after part2_distance.py."""
import os, sys
import numpy as np, pandas as pd, geopandas as gpd, shapely
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
REPO = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = os.path.join(REPO, "data/authentic-stoic-stress-test/part2")
FD = "/usr/share/fonts/opentype/inter/"
for f in ("Inter-Medium.otf", "Inter-Bold.otf"):
    if os.path.exists(FD + f): fm.fontManager.addfont(FD + f)
plt.rcParams["font.family"] = "Inter" if os.path.exists(FD + "Inter-Medium.otf") else "DejaVu Sans"
BG, CREAM, MUTED, GOLD, TEAL, RED, YEL = "#1c140f", "#eee6d6", "#a99b84", "#d4af68", "#40e0d0", "#e0603c", "#ffd600"
ZC = {"H1": TEAL, "H4": "#c98bff", "H6": RED, "H2": "#8899aa", "H3": "#8899aa"}
C = "EPSG:3400"
sys.argv = [sys.argv[0], REPO]
exec(open(os.path.join(REPO, "scripts/authentic_stoic_alternative_hypothesis/part2_distance.py")).read().split("rows, cores = [], {}")[0])
res = pd.read_csv(os.path.join(OUT, "part2_results.csv"))
RL = {"edge_all": "Fire's edge (both passes)\n= part 1", "edge_viirs": "Edge at 2:49 p.m.\n(VIIRS only)",
      "edge_landsat": "Edge at 12:17 p.m.\n(Landsat only)", "main_body": "Fire's main body\n(edge minus 300 m)"}
fig, axs = plt.subplots(4, 5, figsize=(20, 17.5), facecolor=BG)
minx, miny, maxx, maxy = scar.bounds
for i, (rn, ref) in enumerate(REFS.items()):
    D = downwind_dist(ref)
    for j, (bn, (lo, hi)) in enumerate(BANDS.items()):
        ax = axs[i, j]; ax.set_facecolor(BG)
        n = np.array([(D[w] >= lo) & (D[w] <= hi) for w in DIRS]).sum(0)
        gpd.GeoSeries([scar], crs=C).plot(ax=ax, color="#3a2a20", edgecolor="#6b5a48", linewidth=0.6)
        gpd.GeoSeries([ref], crs=C).plot(ax=ax, color=YEL, alpha=0.35, edgecolor=YEL, linewidth=0.8)
        m = n == 12
        ax.scatter(X[m], Y[m], s=3.2, marker="s", c=[ZC.get(z, "#888") for z in g.zone[m]], linewidths=0)
        for nm, mk in (("Range2 centroid (OSM)", "o"), ("Road dead end (CanVec)", "s")):
            p = cp[nm]; ax.plot(p.x, p.y, mk, ms=5, mfc="none", mec=CREAM, mew=1.2)
        r = res[(res.reference == rn) & (res.band_km == bn)].iloc[0]
        ax.text(0.03, 0.03, f"{r.core_km2:.2f} km²\nRange 2 zone {int(round(r.core_share_range2_zone * 100))}%", transform=ax.transAxes,
                color=CREAM, fontsize=10.5, va="bottom")
        ax.set_xlim(minx + 1500, maxx - 1500); ax.set_ylim(miny + 1800, maxy - 300)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
        for sp in ax.spines.values(): sp.set_color(GOLD if (rn == "edge_all" and j == 1) else "#35281f"); sp.set_linewidth(2.5 if (rn == "edge_all" and j == 1) else 1)
        if i == 0: ax.set_title(f"{bn} km", color=CREAM, fontsize=14, fontweight="bold")
        if j == 0: ax.set_ylabel(RL[rn], color=CREAM, fontsize=12, fontweight="bold")
fig.suptitle("The Authentic Stoic Stress Test, part 2: what does \"about a kilometre\" mean?", color=GOLD, fontsize=24, fontweight="bold", x=0.02, ha="left", y=0.995)
fig.text(0.02, 0.962, "Each map: ground in the band for all 12 winds (270–325°). Rows: what the kilometre is measured from (yellow). Columns: how loosely \"about a kilometre\" is read. Gold frame = part 1.",
         color=MUTED, fontsize=12.5, ha="left")
fig.text(0.02, 0.945, "Colour = analysis zone:  teal  Range 2 area (H1)    purple  strip north of Jamieson Lake (H4b)    red  south-central run (H6).   ○ Range 2   □ road's end",
         color=CREAM, fontsize=12.5, ha="left")
fig.text(0.02, 0.006, "Data: NASA FIRMS, Copernicus Sentinel-2. Method and data: github.com/primerogueinc/cfb-wainwright-fire-archive. Graphic: Prime Rogue Inc.", color=MUTED, fontsize=11, ha="left")
plt.subplots_adjust(left=0.08, right=0.99, top=0.925, bottom=0.025, wspace=0.03, hspace=0.06)
fig.savefig(os.path.join(OUT, "part2_grid.png"), dpi=100, facecolor=BG)
print("ok")
