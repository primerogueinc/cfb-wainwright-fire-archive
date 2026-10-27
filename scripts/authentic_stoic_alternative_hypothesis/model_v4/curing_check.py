"""Working model v4, H3/H4: what curing would close the 6-times gap, and what does the national system's station data say?
Usage: python3 curing_check.py REPO
FBP grass curing factor (O-1a/O-1b): CF = 0.005 (e^(0.061 C) - 1) for C < 58.8%, else 0.176 + 0.02 (C - 58.8). The model uses 95%
(CF 0.90). The measured pace is about 1/5.8 of the standard rate, so we solve for the curing that gives CF = 0.90 / 5.8, all else equal.
Also the CWFIS daily values for the CFB Wainwright station on Oct. 17 (data/nrcan_cwfis), against the model's hourly FFMC."""
import sys, os, json, math, numpy as np, pandas as pd
REPO = sys.argv[1]
cf = lambda C: 0.005 * (math.exp(0.061 * C) - 1) if C < 58.8 else 0.176 + 0.02 * (C - 58.8)
target = cf(95) / 5.8
C = next(c / 10 for c in range(1000, 0, -1) if cf(c / 10) <= target)
st = pd.read_csv(os.path.join(REPO, "data/nrcan_cwfis/fwi_nearby_stations_oct10-18.csv"))
row = st[(st.REPDATE == 20261017) & st.NAME.str.contains("WAINWRIGHT")]
isi_st = float(row.ISI.iloc[0]); ros_st = 190 * (1 - math.exp(-0.0310 * isi_st)) ** 1.4 * cf(95) * 0.06
wx = pd.read_csv(os.path.join(REPO, "data/authentic-stoic-stress-test/part8b_ignition/weather_hourly_model.csv"))
out = dict(cf_used_95pct=round(cf(95), 3), cf_needed=round(target, 3), curing_needed_pct=C,
           note="for the gap to be curing alone, the grass would have had to be about this cured; mid-October prairie grass is normally 90-100% cured",
           cwfis_station_oct17=row[['NAME', 'REPDATE', 'TEMP', 'RH', 'WS', 'WDIR', 'FFMC', 'ISI', 'FWI', 'alberta_fire_danger_class']].to_dict('records'),
           standard_head_kmh_from_cwfis_noon_isi=round(ros_st, 2),
           note_isi='CWFIS noon ISI 11.6 is on the corrected scale (our corrected 1 p.m. ISI 7.9 with the model FFMC 89.0); the uncorrected part 8b table gave 1.6',
           model_hourly_ffmc_13h=float(wx[wx.t == 13].ffmc.iloc[0]))
json.dump(out, open(os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4/curing_check.json"), "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))
