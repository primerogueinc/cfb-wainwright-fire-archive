"""v4 graphic: the fire ran far below what the day's weather supported until the front. Usage: python3 scripts/maps/g28_held_back.py"""
import sys; sys.path.insert(0, "scripts/maps")
from v4fig import *
import pandas as pd, numpy as np
MD = REPO + "data/authentic-stoic-stress-test/model_v4/"
hs = pd.read_csv(MD + "danger/hourly_standard.csv"); hs["h"] = hs.hour_mdt.str[:2].astype(int)
hs = hs[(hs.h >= 6) & (hs.h <= 16)]
W, H = 1600, 1000
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · WORKING MODEL V4 · OCT. 17",
               "Held back all day, then unleashed",
               "Head-fire speed the day's weather could support (routine Canadian grass-fire calculation, hourly) against what the fire actually did.\nShaded bands: grass-fire suppression classes (Alexander, Heathcott & Schwanke 2013).")
f, ax = fig(1480, 640)
ax.axhspan(0.05, 1, color="#2e5b3a", alpha=0.45); ax.axhspan(1, 5, color="#6b5a20", alpha=0.45); ax.axhspan(5, 30, color="#6b2a1c", alpha=0.5)
for y, t, x in ((0.4, "Easy to suppress  (< 1 km/h)", 6.08), (2.2, "Challenging  (1-4.9 km/h)", 6.08), (7.5, "Beyond control  (5+ km/h)", 11.6)):
    ax.text(x, y, t, color=hx(CREAM), fontsize=13, va="center", alpha=0.9)
ax.plot(hs.h, hs.hfros_kmh, color=hx(GOLD), lw=3.5, marker="o", ms=7, label="What the weather could support (standard calculation)")
ax.plot([12 + 17 / 60, 14 + 49 / 60], [0.43, 0.43], color=hx(TEAL), lw=7, solid_capstyle="butt", label="What the fire did: 0.43 km/h (Landsat 12:17 to VIIRS 2:49)")
ax.fill_between([15 + 16 / 60, 16.6], [4.4, 4.4], [12, 12], color=hx(RED), alpha=0.85, label="After the 3:16 p.m. front: 4.4-12 km/h (model, fitted to the scar)")
ax.axvline(15 + 16 / 60, color=hx(CREAM), lw=1.5, ls="--"); ax.text(15 + 16 / 60 - 0.08, 22, "3:16 p.m. front\n82 km/h gust", color=hx(CREAM), fontsize=12, ha="right", va="top")
ax.annotate("about 6x below\nwhat the weather\ncould support", xy=(13.55, 0.43), xytext=(13.1, 0.13), color=hx(TEAL), fontsize=14, weight="bold",
            arrowprops=dict(arrowstyle="->", color=hx(TEAL)))
ax.set_yscale("log"); ax.set_ylim(0.08, 30); ax.set_xlim(6, 16.6)
ax.set_yticks([0.1, 0.25, 0.5, 1, 2, 5, 10, 20]); ax.set_yticklabels(["0.1", "0.25", "0.5", "1", "2", "5", "10", "20"])
ax.set_xticks(range(6, 17)); ax.set_xticklabels([f"{h if h <= 12 else h - 12} {'a.m.' if h < 12 else 'p.m.'}" for h in range(6, 17)])
ax.set_ylabel("Head-fire speed, km/h (log scale)", color=hx(CREAM), fontsize=13)
leg = ax.legend(loc="lower left", facecolor=hx(PANEL), edgecolor=hx(MUTED), labelcolor=hx(CREAM), fontsize=12, bbox_to_anchor=(0.0, 0.02))
f.subplots_adjust(left=0.07, right=0.98, top=0.97, bottom=0.08)
im.paste(to_img(f), (40, 200))
footer(im, ["Standard: FBP grass fuel O-1a, 95% curing, hourly ECCC CZWN weather (CWFIS rated Oct. 17 Extreme, FWI 30.8). Actual: satellite head advance; fire energy (VIIRS) agrees.",
            "Satellite fire power rose about 16-fold between 3:10 and 3:30 p.m. (GOES-18). The cause of the slow morning spread is not established.", SRC], fh=145)
im.convert("RGB").save(OUTD + "cfb-wainwright-held-back.jpg", quality=92); print("ok")
