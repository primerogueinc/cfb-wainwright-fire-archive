"""v4 graphic: escape odds from the Range 2 area across every variation in the ensemble. Usage: python3 scripts/maps/g31_ensemble.py"""
import sys; sys.path.insert(0, "scripts/maps")
from v4fig import *
import json
MD = REPO + "data/authentic-stoic-stress-test/model_v4/"
E = json.load(open(MD + "ensemble_summary.json")); S = json.load(open(MD + "weighting_sensitivity.json"))
rows = [("All 240 fires, equal weight", E["overall_equal"]), ("All 240, weighted by fit to the scar", E["overall_scar_weighted"])]
lab = {"S0_fixed306": "Wind fixed from 306 deg", "S4_fixed315": "Wind fixed from 315 deg", "S3_fast_veer": "Wind veers fast (by 3:30)", "S2_station_veer": "Wind veers as station (by 3:50)", "S1_stoic": "Slow veer (by 4:20)"}
groups = [("FRONT REACHES FIRE", [(f"at {k}", v) for k, v in E["by"]["front"].items()]),
          ("WIND AFTER THE FRONT", [(lab[k], E["by"]["schedule"][k]) for k in ("S4_fixed315", "S0_fixed306", "S3_fast_veer", "S2_station_veer", "S1_stoic")]),
          ("FIRE SPEED AFTER THE FRONT", [(f"{float(k):g} km/h", v) for k, v in sorted(E["by"]["ros"].items(), key=lambda x: float(x[0]))]),
          ("FIRE SHAPE", [("Gusty (wider)", E["by"]["shape"]["gusty"]), ("Steady (narrower)", E["by"]["shape"]["steady"])]),
          ("MORNING FIRE (START CASE)", [(k.split("_")[0] + " " + k.split("_")[-1][:2] + ":" + k.split("_")[-1][2:] + " a.m.", v) for k, v in E["by"]["case"].items()])]
W, H = 1600, 1180
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · WORKING MODEL V4 · 240 FIRES",
               "In every variation, minutes decided who got out",
               "Share of modelled fires a soldier jogging in kit from the Range 2 area escapes, by when they start moving: at the gust, 3 minutes later, 7 minutes later.\nEach row changes one thing and keeps every other variation in the mix.")
f, ax = fig(1480, 820)
allrows = [("OVERALL", rows)] + groups; y = 0; yt, yl = [], []
for g, rs in allrows:
    y -= 0.6; ax.text(-2, y, g, color=hx(GOLD), fontsize=12, weight="bold", va="center"); y -= 0.9
    for name, v in rs:
        a, b, c = v["escape_range2_gust"], v["escape_range2_p3"], v["escape_range2_p7"]
        ax.plot([c, a], [y, y], color=hx(MUTED), lw=1.5, zorder=1)
        for val, col in ((a, TEAL), (b, GOLD), (c, RED)): ax.plot(val, y, "o", ms=11, color=hx(col), zorder=3)
        yt.append(y); yl.append(name); y -= 1
ax.set_yticks(yt); ax.set_yticklabels(yl, color=hx(CREAM), fontsize=12); ax.set_xlim(-2, 102); ax.set_ylim(y, 0.2)
ax.set_xticks(range(0, 101, 20)); ax.set_xticklabels([f"{v}%" for v in range(0, 101, 20)]); ax.grid(axis="x", color=hx(GRIDC), lw=1)
for s in ("right", "top", "left"): ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
f.subplots_adjust(left=0.2, right=0.98, top=0.99, bottom=0.04)
im.paste(to_img(f), (40, 215))
ly = 222; lx = 760
for col, t in ((TEAL, "Leave at the gust"), (GOLD, "Leave 3 minutes later"), (RED, "Leave 7 minutes later")):
    d.ellipse([lx, ly, lx + 18, ly + 18], fill=col); d.text((lx + 28, ly - 2), t, font=M(18), fill=CREAM); lx += 270
ws = S["s0.02"]["Range 2 area"], S["equal"]["Range 2 area"], S["s0.20"]["Range 2 area"]
footer(im, ["Weighting by fit to the scar (strict to loose) changes the overall figures only within: at the gust 68-81%, +3 min 36-48%, +7 min 2-11%. Fire speed matters most.",
            "Escape: part 4 model (8 km/h, best route, 3-minute safety margin, no smoke slowing). 'Range 2 area' = the Range 2 point. Model, not observation.", SRC], fh=145)
im.convert("RGB").save(OUTD + "cfb-wainwright-escape-robustness.jpg", quality=92); print("ok")
