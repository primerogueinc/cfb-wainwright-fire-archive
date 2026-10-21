"""Grass fire behaviour for the Oct. 17 CFB Wainwright fire.

Models
  FBP  Canadian Forest Fire Behavior Prediction System (Forestry Canada 1992, ST-X-3;
       Wotton et al. 2009 updates), grass fuel types O-1a (matted) and O-1b (standing).
  CSIRO Cheney, Gould & Catchpole (1998) grassland spread model, natural and grazed pasture;
       moisture after Cheney et al.; curing after Cruz et al. (2015).
  Rule  Cruz, Alexander & Kilinc (2022): grassfire spread about 20% of the 10 m wind speed (very dry).
Outputs: head, flank and back spread, minutes to cover 1 km, fireline intensity, flame length.
"""
import math, json, itertools
import pandas as pd

def isi_fbp(ffmc, ws):
    m = 147.27723 * (101 - ffmc) / (59.5 + ffmc)
    ff = 91.9 * math.exp(-0.1386 * m) * (1 + m ** 5.31 / 4.93e7)
    fw = math.exp(0.05039 * ws) if ws <= 40 else 12 * (1 - math.exp(-0.0818 * (ws - 28)))
    return 0.208 * fw * ff, ff

def cf(c):
    return 0.005 * (math.exp(0.061 * c) - 1) if c < 58.8 else 0.176 + 0.02 * (c - 58.8)

def fbp(ffmc, ws, curing, ftype="O1b", gfl=0.35):
    a, b, c = {"O1a": (190, 0.0310, 1.4), "O1b": (250, 0.0350, 1.7)}[ftype]
    isi, ff = isi_fbp(ffmc, ws)
    ros = a * (1 - math.exp(-b * isi)) ** c * cf(curing)            # m/min
    bisi = 0.208 * math.exp(-0.05039 * ws) * ff
    bros = a * (1 - math.exp(-b * bisi)) ** c * cf(curing)
    lb = 1.1 * ws ** 0.464 if ws >= 1 else 1.0                       # grass LB (ST-X-3 eq. 80)
    fros = (ros + bros) / (2 * lb)
    I = 300 * gfl * ros                                              # kW/m (TFC = GFL for O-1)
    return dict(model=f"FBP {ftype}", isi=round(isi, 1), head_m_min=ros, flank_m_min=fros, back_m_min=bros, lb=lb, I=I)

def csiro(T, RH, ws, curing, pasture="natural", gfl=0.45):
    mc = 9.58 - 0.205 * T + 0.138 * RH
    if mc < 12: pm = math.exp(-0.108 * mc)
    elif ws <= 10: pm = 0.684 - 0.0342 * mc
    else: pm = 0.547 - 0.0228 * mc
    pc = 1.036 / (1 + 103.99 * math.exp(-0.0996 * (curing - 20)))
    if ws < 5:
        r = (0.054 + 0.269 * ws) if pasture == "natural" else (0.054 + 0.209 * ws)
    else:
        r = (1.4 + 0.838 * (ws - 5) ** 0.844) if pasture == "natural" else (1.1 + 0.715 * (ws - 5) ** 0.844)
    ros = r * pm * pc * 1000 / 60                                     # m/min
    I = 300 * gfl * ros  # approx: H*w*R with H=18000 kJ/kg -> 18000*w(kg/m2)*R(m/s) = 300*w*R(m/min)
    return dict(model=f"CSIRO {pasture}", mc=round(mc, 1), head_m_min=ros, I=I)

def rule(ws):
    return dict(model="Cruz 20% rule", head_m_min=0.2 * ws * 1000 / 60)

def flame(I):  # Byram (1959)
    return 0.0775 * I ** 0.46

# ---------- scenarios from the record (CZWN; hourly FFMC computed from CWFIS noon value)
S = [
    ("Before the shift, 2:49-3:16 p.m.", dict(T=23.3, RH=17, ws=32, ffmc=92.9), "SW 236 deg, 10-min avg 32 km/h"),
    ("Before the shift, gusts", dict(T=23.3, RH=17, ws=50, ffmc=92.9), "gust 45-51 km/h in the hour"),
    ("Just after the front (drier edge)", dict(T=18, RH=25, ws=48, ffmc=92.6), "transition; mid values"),
    ("After the shift, 4 p.m. obs", dict(T=12.9, RH=43, ws=48, ffmc=92.3), "NW 307 deg, avg 47.6 km/h"),
    ("Peak gust 3:16 p.m.", dict(T=18, RH=25, ws=82, ffmc=92.6), "82 km/h from 269 deg"),
]
rows = []
for (name, w, note), curing in itertools.product(S, (90, 100)):
    for r in (fbp(w["ffmc"], w["ws"], curing, "O1b"), fbp(w["ffmc"], w["ws"], curing, "O1a", 0.30),
              csiro(w["T"], w["RH"], w["ws"], curing, "natural"), csiro(w["T"], w["RH"], w["ws"], curing, "grazed", 0.30), rule(w["ws"])):
        r.update(scenario=name, curing=curing, wind=w["ws"], note=note)
        r["head_km_h"] = round(r["head_m_min"] * 60 / 1000, 1)
        r["min_per_km"] = round(1000 / r["head_m_min"], 1)
        if "I" in r: r["flame_m"] = round(flame(r["I"]), 1); r["I"] = round(r["I"])
        for k in ("head_m_min", "flank_m_min", "back_m_min", "lb"):
            if k in r: r[k] = round(r[k], 1)
        rows.append(r)
df = pd.DataFrame(rows)
cols = ["scenario", "curing", "wind", "model", "head_km_h", "min_per_km", "flank_m_min", "lb", "I", "flame_m", "isi", "mc"]
df[cols].to_csv("/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/stress/fire_models.csv", index=False)
pd.set_option("display.width", 220)
print(df[cols].to_string(index=False))

# ---------- tests
post = df[(df.scenario.isin(["Just after the front (drier edge)", "After the shift, 4 p.m. obs"])) & (df.model != "Cruz 20% rule")]
pre = df[df.scenario == "Before the shift, 2:49-3:16 p.m."]
tests = {
  "post_shift_head_km_h_range": [float(post.head_km_h.min()), float(post.head_km_h.max())],
  "post_shift_min_per_km_range": [float(post.min_per_km.min()), float(post.min_per_km.max())],
  "gust82_head_km_h_range": [float(df[df.scenario == "Peak gust 3:16 p.m."].head_km_h.min()), float(df[df.scenario == "Peak gust 3:16 p.m."].head_km_h.max())],
  "rutland_1km_30_60s_requires_km_h": [60, 120],
  "pre_shift_free_head_km_h": [float(pre.head_km_h.min()), float(pre.head_km_h.max())],
  "pre_shift_flank_m_in_27min_FBP": [round(float(pre[pre.model.str.startswith("FBP")].flank_m_min.min()) * 27), round(float(pre[pre.model.str.startswith("FBP")].flank_m_min.max()) * 27)],
  "observed_pre_shift_growth_km_h": round(1.0 / (152 / 60), 2),
  "observed_run_km_h_if_4_8km_in_20_40min": [round(4.8 / (40 / 60), 1), round(4.8 / (20 / 60), 1)],
}
# arrival times at distances from the flank, front reaching the fire 3:20-3:30
for d in (0.25, 0.5, 1.0, 1.5, 4.8):
    lo, hi = tests["post_shift_head_km_h_range"]
    tests[f"minutes_to_{d}km"] = [round(d / hi * 60, 1), round(d / lo * 60, 1)]
json.dump(tests, open("/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/stress/fire_model_tests.json", "w"), indent=1)
print(json.dumps(tests, indent=1))
