"""Shared helpers for the working model v4 graphics (house style from pr.py)."""
import io, sys
sys.path.insert(0, "scripts/maps")
from pr import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
hx = lambda c: "#%02x%02x%02x" % c
OUTD = REPO + "data/graphics_published/oct25_model_v4/"
def fig(w, h):
    f, ax = plt.subplots(figsize=(w / 100, h / 100), facecolor=hx(BG)); ax.set_facecolor(hx(BG))
    for s in ax.spines.values(): s.set_color(hx(MUTED))
    ax.tick_params(colors=hx(CREAM), labelsize=12); return f, ax
def to_img(f):
    buf = io.BytesIO(); f.savefig(buf, dpi=100, facecolor=hx(BG)); plt.close(f); buf.seek(0); return Image.open(buf).convert("RGBA")
SRC = "Data and code: github.com/primerogueinc/cfb-wainwright-fire-archive. Graphic: Kevin Duska Jr. (Prime Rogue Inc.), CC BY-NC 4.0."
