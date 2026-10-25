"""Two maps for the 'just before 4:00' question (Oct. 23 briefing) against working model v4.
Usage: python3 maps_dnd_timing.py REPO SCRATCH_V4_DIR
Left: share of the 120 post-front fires (weighted by fit to the final scar) that reach each 40 m cell between 3:45 and 4:00 p.m.
Right: the same, only for ground 600-1,400 m from the fire's edge at 3:16 p.m. ('about a kilometre away when the wind shifted',
Oct. 18 briefing): where the pairs range would have to be if both statements are literally true."""
import sys, os, numpy as np, geopandas as gpd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pyproj import Transformer
REPO, SV = sys.argv[1], sys.argv[2]
g = np.load(os.path.join(SV, "truthful_reading.npz")); P, D = g["P"], g["D"]; minx, maxy, R, H, W = g["meta"]; H, W = int(H), int(W)
ext = [minx, minx + W * R, maxy - H * R, maxy]
scar = gpd.read_file(os.path.join(REPO, "data/copernicus/burn_scar.geojson")).to_crs(3400)
tf = Transformer.from_crs(4326, 3400, always_xy=True).transform
PTS = {"Range 2": (-110.9063, 52.7728), "Road head": (-110.8996, 52.7705), "Range 11": (-110.9577, 52.7678), "Track, 2 km S of road head": (-110.8990, 52.7530)}
BG, FG = "#1c140f", "#eee6d6"
fig, axs = plt.subplots(1, 2, figsize=(16, 8.4), facecolor=BG)
for ax, data, title in ((axs[0], P, "Where the fire was between 3:45 and 4:00 p.m."),
                        (axs[1], np.where((D >= 600) & (D <= 1400), P, np.nan), "…and was also about 1 km from the fire at 3:16 p.m.")):
    ax.set_facecolor(BG); scar.boundary.plot(ax=ax, color="#888", lw=0.8)
    im = ax.imshow(np.where(data > 0.02, data, np.nan), extent=ext, cmap="YlOrRd", vmin=0, vmax=0.6, zorder=2)
    for k, (lo, la) in PTS.items():
        x, y = tf(lo, la); ax.plot(x, y, "o", ms=7, mfc="white", mec="k", zorder=3); ax.annotate(k, (x, y), {"Range 2": (-62, 8), "Road head": (8, 6), "D": (8, -4), "Track, 2 km S of road head": (8, -4), "Range 11": (-28, 10)}[k], textcoords="offset points", color=FG, fontsize=11, weight="bold", zorder=3)
    b = scar.total_bounds; ax.set_xlim(b[0] - 2500, b[2] + 500); ax.set_ylim(b[1] - 500, b[3] + 800); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_title(title, color=FG, fontsize=14, loc="left")
    ax.plot([b[2] - 1500, b[2] - 500], [b[1] - 300] * 2, color=FG, lw=3); ax.text(b[2] - 1500, b[1] - 200, "1 km", color=FG, fontsize=10)
cb = fig.colorbar(im, ax=axs, shrink=0.6, pad=0.01); cb.set_label("Share of modelled fires (weighted by fit to the scar)", color=FG); cb.ax.tick_params(colors=FG)
fig.text(0.02, 0.95, "DND: overtaken \"just before 4:00\" (Oct. 23); fire \"about a kilometre away\" when the wind shifted (Oct. 18)", color=FG, fontsize=16, weight="bold")
fig.text(0.02, 0.03, "Working model v4: 4 pre-front cases x 30 post-front fires, weighted by overlap with the final Sentinel-2 scar. Grey: mapped final scar. "
         "Range 2 median arrival 3:21, road head 3:26 (0% and 4% of fires in 3:45-4:00).", color="#a99b84", fontsize=9.5)
out = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4/maps"); os.makedirs(out, exist_ok=True)
plt.savefig(os.path.join(out, "dnd_timing_test.png"), dpi=110, facecolor=BG); print("saved")
