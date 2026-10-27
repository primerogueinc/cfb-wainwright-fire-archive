"""v4 graphic: when smoke and fire reached each point after the front (both front times). Usage: python3 scripts/maps/g29_smoke_timeline.py"""
import sys; sys.path.insert(0, "scripts/maps")
from v4fig import *
import json
MD = REPO + "data/authentic-stoic-stress-test/model_v4/"
a = json.load(open(MD + "smoke/smoke_summary.json"))["after_front"]; b = json.load(open(MD + "smoke_f325/smoke_summary.json"))["after_front"]
pre = json.load(open(MD + "smoke/smoke_summary.json"))["before_front"]
tm = lambda s: (int(s.split(":")[0]) - 3) * 60 + int(s.split(":")[1])
ROWS = [("Range 2 point", "Range 2 point"), ("Road head", "Road head"), ("D", "Track 900 m S of road head"), ("E", "Track 2 km S of road head")]
W, H = 1600, 990
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · WORKING MODEL V4 · SMOKE",
               "The smoke came with the fire, not before it",
               "After the wind shift: when haze (visibility under 1 km), thick smoke (under 100 m) and the fire reached each point. Weighted medians of the modelled fires.\nBefore 3:16 p.m. the smoke blew north-east, past them: visibility at the Range 2 point stayed above about 2.7 km until the front.")
f, ax = fig(1480, 520)
for i, (k, lab) in enumerate(ROWS):
    for j, (src, ft, dy, al) in enumerate(((a, 16, 0.16, 1.0), (b, 25, -0.16, 0.55))):
        y = len(ROWS) - i + dy; r = src[k]
        hz, dn, fi = tm(r["haze_lt_1km"]), tm(r["dense_lt_100m"]), tm(r["fire"])
        ax.plot([ft, hz], [y, y], color=hx(MUTED), lw=2, ls=":", alpha=al)
        ax.plot([hz, dn], [y, y], color="#b9a88f", lw=10, alpha=al, solid_capstyle="butt")
        ax.plot([dn, fi], [y, y], color="#6e6255", lw=10, alpha=al, solid_capstyle="butt")
        ax.plot([fi], [y], marker="o", ms=13, color=hx(RED), alpha=al)
        if j == 0: ax.text(fi + 0.6, y, f"fire {r['fire']}", color=hx(CREAM), fontsize=12, va="center")
        else: ax.text(fi + 0.6, y, f"{r['fire']} (front at 3:25)", color=hx(MUTED), fontsize=11, va="center")
    ax.text(15.3, len(ROWS) - i, lab, color=hx(CREAM), fontsize=13, ha="right", va="center", weight="bold")
for x, t in ((16, "3:16 front"), (25, "3:25")):
    ax.axvline(x, color=hx(CREAM), lw=1, ls="--", alpha=0.6); ax.text(x, len(ROWS) + 0.62, t, color=hx(CREAM), fontsize=11, ha="center")
ax.set_xlim(2, 58); ax.set_ylim(0.5, len(ROWS) + 0.8); ax.set_yticks([])
ax.set_xticks(range(15, 56, 5)); ax.set_xticklabels([f"3:{m:02d}" for m in range(15, 56, 5)])
for s in ("left", "right", "top"): ax.spines[s].set_visible(False)
f.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.08)
im.paste(to_img(f), (40, 215))
lx, ly = 60, 770
for c, t in (("#b9a88f", "Haze (visibility under 1 km)"), ("#6e6255", "Thick smoke (under 100 m)")):
    d.rectangle([lx, ly, lx + 40, ly + 16], fill=tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))); d.text((lx + 50, ly - 3), t, font=M(17), fill=CREAM); lx += 360
d.ellipse([lx, ly - 2, lx + 18, ly + 16], fill=RED); d.text((lx + 28, ly - 3), "Fire arrives", font=M(17), fill=CREAM)
d.text((lx + 200, ly - 3), "Faded rows: front reaching the fire at 3:25 instead of 3:16", font=M(17), fill=MUTED)
footer(im, ["Smoke model: plume from every modelled burning cell, ground-hugging (worst case for visibility), wind varied +/-20 deg. Modelled, not observed: NOAA mapped no plume (cloud).",
            "Working model v4: 240 post-front fires weighted by fit to the final Sentinel-2 scar. Times are medians; individual fires vary by several minutes.", SRC], fh=145)
im.convert("RGB").save(OUTD + "cfb-wainwright-smoke-vs-fire.jpg", quality=92); print("ok")
