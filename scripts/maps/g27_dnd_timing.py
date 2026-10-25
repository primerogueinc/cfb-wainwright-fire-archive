"""Branded version of model_v4/maps/dnd_timing_test.png: DND's 'about a kilometre' (Oct. 18) and 'just before 4:00' (Oct. 23)
against working model v4. Usage (repo root): python3 scripts/maps/g27_dnd_timing.py OUT.jpg"""
import sys, os, io
sys.path.insert(0, "scripts/maps")
from pr import *
import numpy as np, geopandas as gpd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pyproj import Transformer
OUT = sys.argv[1]
g = np.load(REPO + "data/authentic-stoic-stress-test/model_v4/maps/truthful_reading.npz"); P, D = g["P"], g["D"]
minx, maxy, R, H, W = g["meta"]; H, W = int(H), int(W); ext = [minx, minx + W * R, maxy - H * R, maxy]
scar = gpd.read_file(REPO + "data/copernicus/burn_scar.geojson").to_crs(3400)
tf = Transformer.from_crs(4326, 3400, always_xy=True).transform
PTS = {"Range 2": (-110.9063, 52.7728), "Road head": (-110.8996, 52.7705), "Range 11": (-110.9577, 52.7678), "E": (-110.8990, 52.7530)}
OFF = {"Range 2": (-64, 8), "Road head": (8, 6), "E": (9, -5), "Range 11": (-30, 10)}
hx = lambda c: "#%02x%02x%02x" % c
def panel(data):
    fig, ax = plt.subplots(figsize=(7.0, 6.2), facecolor=hx(BG)); ax.set_facecolor(hx(BG))
    scar.boundary.plot(ax=ax, color=hx(MUTED), lw=0.9)
    ax.imshow(np.where(data > 0.02, data, np.nan), extent=ext, cmap="YlOrRd", vmin=0, vmax=0.6, zorder=2)
    for k, (lo, la) in PTS.items():
        x, y = tf(lo, la); ax.plot(x, y, "o", ms=8, mfc="white", mec="k", zorder=3)
        ax.annotate(k, (x, y), OFF[k], textcoords="offset points", color=hx(CREAM), fontsize=12, weight="bold", zorder=3)
    b = scar.total_bounds; ax.set_xlim(b[0] - 2300, b[2] + 400); ax.set_ylim(b[1] - 400, b[3] + 600)
    ax.plot([b[2] - 1400, b[2] - 400], [b[1] - 250] * 2, color=hx(CREAM), lw=3); ax.text(b[2] - 1400, b[1] - 150, "1 km", color=hx(CREAM), fontsize=11)
    ax.set_axis_off(); fig.subplots_adjust(0, 0, 1, 1)
    buf = io.BytesIO(); fig.savefig(buf, dpi=100, facecolor=hx(BG)); plt.close(fig); buf.seek(0); return Image.open(buf).convert("RGBA")
left = panel(P); right = panel(np.where((D >= 600) & (D <= 1400), P, np.nan))
Wc, Hc = 1600, 1075
im, d = canvas(Wc, Hc, "CFB WAINWRIGHT FIRE · WORKING MODEL V4 · DND TIMELINE TEST",
               "\"About a kilometre away\" and \"just before 4:00\"",
               "DND, Oct. 18: the fire was about a kilometre away when the wind shifted. DND, Oct. 23: it overtook the pairs range just before 4:00 p.m.\n"
               "Shading: share of 120 modelled fires (weighted by fit to the final burn scar) reaching each spot in that window.")
y0 = 205
for i, (pnl, t) in enumerate(((left, "Where the fire was, 3:45-4:00 p.m."), (right, "...and about 1 km from the fire at 3:16 p.m."))):
    x = 54 + i * (pnl.size[0] + 40)
    d.text((x, y0), t, font=B(22), fill=GOLD); im.paste(pnl, (x, y0 + 38))
# legend bar
lx, ly = Wc - 54 - 22, y0 + 80
cm = plt.get_cmap("YlOrRd")
for k in range(300):
    c = tuple(int(255 * v) for v in cm(1 - k / 300)[:3]); d.line([(lx, ly + k), (lx + 22, ly + k)], fill=c)
d.text((lx - 8, ly), "60%", font=M(15), fill=CREAM, anchor="ra"); d.text((lx - 8, ly + 300), "0", font=M(15), fill=CREAM, anchor="rb")
label(d, (60, y0 + 38 + 630), "Range 2: median arrival 3:21 p.m. Road head: 3:26.\nOnly 0% and 4% of fires reach them 3:45-4:00.", col=CREAM, size=18)
label(d, (54 + left.size[0] + 46, y0 + 38 + 630), "If both statements are true: a thin strip south-east\nof the road head, on the fire's flank (10-20% of fires).", col=GOLD, size=18)
footer(im, ["Working model v4 (Prime Rogue): grass-fire spread fitted to Landsat 8 (12:17 p.m.), VIIRS (2:49 p.m.) and the final Sentinel-2 scar; wind from ECCC CZWN. Grey: final scar.",
            "Statements: DND briefings, Oct. 18 and Oct. 23, 2026. Data and code: github.com/primerogueinc/cfb-wainwright-fire-archive. Graphic: Kevin Duska Jr. (Prime Rogue Inc.), CC BY-NC 4.0."], fh=112)
im.convert("RGB").save(OUT, quality=92); print(OUT)
