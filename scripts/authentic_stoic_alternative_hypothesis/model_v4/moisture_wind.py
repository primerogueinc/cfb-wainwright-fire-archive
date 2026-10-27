"""Working model v4, H4 test: how much damper fuel or lighter wind would it take for the standard grass model (FBP O-1a, 95% curing,
correct ISI) to give the measured 0.43 km/h head advance between 12:17 and 2:49 p.m.?
Usage: python3 moisture_wind.py REPO
Hourly FFMC, wind and humidity from part 8b (CZWN), with the v4 ISI fix. We lower FFMC by 0-15 points (damper fine fuel) and scale
the 10 m wind by 1.0-0.3 (wind at grass height, sheltering) and report the mean head spread 12:17-2:49 p.m. for each combination.
For scale: FFMC 2-3 points below the hourly value is ordinary local variation; wind at 2 m over open grass is roughly 0.6-0.7 of
the 10 m wind; the FBP system already uses the 10 m open wind, so scaling it is a deliberate departure."""
import sys, os, math, json, numpy as np, pandas as pd
REPO = sys.argv[1]
wx = pd.read_csv(os.path.join(REPO, "data/authentic-stoic-stress-test/part8b_ignition/weather_hourly_model.csv"))
def isi(ffmc, ws):
    fm = 147.27723 * (101 - ffmc) / (59.5 + ffmc); sf = 19.115 * math.exp(-0.1386 * fm) * (1 + fm ** 5.31 / 4.93e7)
    fw = math.exp(0.05039 * ws) if ws < 40 else 12 * (1 - math.exp(-0.0818 * (ws - 28))); return fw * sf
CF = 0.176 + 0.02 * (95 - 58.8)
ros = lambda I: 190 * (1 - math.exp(-0.0310 * I)) ** 1.4 * CF * 0.06       # km/h
ts = np.arange(12 + 17 / 60, 14 + 49 / 60, 1 / 60)
f_ = lambda t, c: float(np.interp(t, wx.t, wx[c]))
rows = []
for dF in (0, 2, 4, 6, 8, 10, 12, 15):
    for k in (1.0, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3):
        v = np.mean([ros(isi(f_(t, "ffmc") - dF, f_(t, "ws") * k)) for t in ts]); rows.append(dict(ffmc_minus=dF, wind_factor=k, head_kmh=round(v, 2)))
df = pd.DataFrame(rows); tab = df.pivot(index="ffmc_minus", columns="wind_factor", values="head_kmh")
df.to_csv(os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4/moisture_wind.csv"), index=False)
print("mean FFMC 12:17-2:49:", round(np.mean([f_(t, 'ffmc') for t in ts]), 1), " mean wind:", round(np.mean([f_(t, 'ws') for t in ts]), 1), "km/h")
print("head spread km/h (target 0.43):"); print(tab.to_string())
