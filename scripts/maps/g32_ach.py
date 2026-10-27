"""v4 graphic: analysis of competing hypotheses, both questions. Usage: python3 scripts/maps/g32_ach.py"""
import sys; sys.path.insert(0, "scripts/maps")
from v4fig import *
import json, re, pandas as pd
AD = REPO + "data/authentic-stoic-stress-test/model_v4/ach/"
S = json.load(open(AD + "ach_summary.json"))
COL = {"CC": (46, 125, 80), "C": (70, 105, 70), "N": (60, 52, 46), "I": (150, 80, 50), "II": (200, 70, 50)}
TXT = {"CC": "++", "C": "+", "N": "", "I": "-", "II": "--"}
SHORT1 = {"H0": "Not really slow\n(measurement)", "H1": "Firefighting\nheld it", "H1b": "Boundary guards\nor roads (PDA 2)", "H2": "Patchy ground\n(10 m+)",
          "H2b": "Fine-scale fuel\n(grazing, craters)", "H3": "Grass still\ngreen", "H4": "Damper fuel,\nlighter wind"}
SHORT2 = {"L1": "Range 2 / road head\nabout 3:20-3:35", "L2": "Further SE, 2-3 km\nabout 3:40-3:55", "L3": "On the flank, both\nstatements literal", "L4": "Front reached the\nfire about 3:45"}
EV1 = ["Speed re-measured: 0.33-0.52 km/h", "Fire energy: burning 0.2-0.4 km2/h", "No barrier ahead of the head", "Provost Marshal: suppression restricted",
       "Provost Marshal: stayed in PDA 2", "No guard lines visible (10-20 m)", "Morning path: no bare/old-burn/gaps", "Morning path not greener",
       "Curing would need to be ~57%", "Station: FWI 30.8 Extreme, RH 16-23%", "Moisture/wind: big stretch needed", "Same grass ran at full speed after", "Lower severity before the shift"]
EV2 = ["Rutland Oct. 18: a km away at the shift", "Rutland Oct. 22: just before 4:00", "DND releases Oct. 18: about 4 p.m.", "Station front 3:16 (fire 3:16-3:25)", "GOES: run in full force by 3:30",
       "Model: Range 2 3:21-3:30, road head 3:26-3:34", "Model: 'both true' ground 0-3%", "Part 2: '1 km' lands on Range 2 area", "Commander: fire suddenly on top", "Terrain: rise hides the fire"]


def table(d, x, y, df, H, short, ev, score, colw, roww=34, labw=420):
    for j, h in enumerate(H):
        for k, line in enumerate(short[h].split("\n")):
            d.text((x + labw + j * colw + colw / 2, y + k * 20), line, font=B(15), fill=CREAM, anchor="ma")
    y0 = y + 52
    for i, (r, e) in enumerate(zip(df.itertuples(), ev)):
        yy = y0 + i * roww
        d.text((x, yy + 8), e, font=M(15), fill=CREAM)
        for j, h in enumerate(H):
            v = getattr(r, h); d.rectangle([x + labw + j * colw + 3, yy + 2, x + labw + (j + 1) * colw - 3, yy + roww - 2], fill=COL[v])
            d.text((x + labw + j * colw + colw / 2, yy + roww / 2), TXT[v], font=B(18), fill=CREAM, anchor="mm")
    yy = y0 + len(df) * roww + 6
    d.text((x, yy + 6), "Weighted evidence against", font=B(16), fill=GOLD)
    for j, h in enumerate(H):
        d.text((x + labw + j * colw + colw / 2, yy + 6), f"{score[h]['weighted_inconsistency']:.1f}", font=B(18), fill=GOLD, anchor="ma")
    return yy + 40


W, H = 1600, 1560
im, d = canvas(W, H, "CFB WAINWRIGHT FIRE · WORKING MODEL V4 · COMPETING HYPOTHESES",
               "What the evidence rules out, and what it doesn't",
               "Each item of evidence rated against each explanation (++ strongly consistent ... -- strongly inconsistent), weighted by credibility.\nFollowing Heuer's method, explanations are ranked by the evidence AGAINST them: the closer to 0, the less the evidence contradicts it.")
y = 205
for key, short, ev, colw in (("slow_fire", SHORT1, EV1, 150), ("timeline_location", SHORT2, EV2, 262)):
    q = S[key]; df = pd.read_csv(AD + f"ach_{key}.csv"); Hs = list(q["scores"])
    assert len(df) == len(ev), (key, len(df), len(ev))
    d.text((54, y), q["question"].upper(), font=B(19), fill=GOLD); y += 36
    y = table(d, 54, y, df, Hs, short, ev, q["scores"], colw=colw)
    nm = lambda h: re.sub(r"\s*\(.*?\)", "", short[h].replace("\n", " ")).strip(); rk = q["ranking_least_contradicted_first"]
    d.text((54, y), "Least contradicted: " + " > ".join(nm(h) for h in rk[:3]) + ".   Most contradicted: " + nm(rk[-1]) + ".", font=M(16), fill=CREAM); y += 50
for l in ["Caution: an explanation our data cannot test is never contradicted. 'Fine-scale fuel' (grazing, craters) scores best on the first",
          "question partly for that reason; DND's answer on grazing, or sub-metre imagery, could rule it in or out. Ratings are our judgements."]:
    d.text((54, y), l, font=M(17), fill=MUTED); y += 26
footer(im, ["Method: Heuer (1999), Psychology of Intelligence Analysis, ch. 8. Ratings, credibility and sources for every cell: model_v4/ach/ in the archive (ach.py).",
            "Working model v4: 240 post-front fires; Sentinel-2 and Landsat 8 (Oct. 4-24); VIIRS, GOES-18; ECCC and CWFIS weather; DND releases and briefings Oct. 18 and 22.", SRC], fh=145)
im.convert("RGB").save(OUTD + "cfb-wainwright-competing-hypotheses.jpg", quality=92); print("ok", y)
