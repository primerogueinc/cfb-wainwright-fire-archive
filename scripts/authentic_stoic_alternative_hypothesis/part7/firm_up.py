"""Part 7d: bound the soft spots. (1) Front arrival at the fire from a planar fit to four stations' front
passage times. (2) Escape odds if the fire ran at 8-12 km/h only (the GOES southern-pixel constraint)."""
import os, sys, json
import numpy as np, pandas as pd
from pyproj import Transformer
REPO = sys.argv[1]; OUT = os.path.join(REPO, "data/authentic-stoic-stress-test/part7_briefing_check")
tf = Transformer.from_crs(4326, 3400, always_xy=True)
st = {"CYEG": (53.3097, -113.5797, "19:27"), "CYQF": (52.1822, -113.8944, "20:24"), "CZWN": (52.8300, -111.1000, "21:16"), "CYLL": (53.3092, -110.0725, "21:49")}
X = np.array([tf.transform(lo, la) for la, lo, _ in st.values()]) / 1000
T = np.array([int(t[:2]) * 60 + int(t[3:]) for *_, t in st.values()], float)
A = np.c_[np.ones(len(T)), X]; (t0, sx, sy), *_ = np.linalg.lstsq(A, T, rcond=None)
speed = 60 / np.hypot(sx, sy); heading = float(np.degrees(np.arctan2(sx, sy)) % 360)
fx, fy = np.array(tf.transform(-110.9214, 52.7764)) / 1000
pred = t0 + sx * fx + sy * fy
cz = np.array(tf.transform(-111.10, 52.83)) / 1000; u = np.array([np.sin(np.radians(heading)), np.cos(np.radians(heading))])
lag = ((np.array([fx, fy]) - cz) @ u) / speed * 60
front = dict(stations_utc={k: v[2] for k, v in st.items()}, fit_speed_kmh=round(float(speed)), fit_heading_deg=round(heading),
             fit_residuals_min=[round(float(r), 1) for r in A @ np.array([t0, sx, sy]) - T],
             planar_fit_arrival_at_fire_mdt=f"{int(pred // 60) - 6}:{int(pred % 60):02d}",
             czwn_plus_travel_time_mdt=f"3:{16 + round(float(lag)):02d}",
             note="Loose fit (residuals up to ~13 min). GOES-18 southern pixel burning by 3:30 favours an early arrival. Bracket: 3:16 to about 3:26.")
c = pd.read_csv(os.path.join(REPO, "data/authentic-stoic-stress-test/part4_escape/clock.csv"))
c["ros"] = c.grid.str.extract(r"'[^']+', ([0-9.]+)").astype(float); c = c[c.t0 % 1 == 0]
def tab(sub): return (sub.groupby(["point", "speed", "t0"]).optimal.mean() * 100).round().unstack("t0").to_dict("index")
odds = {"all_30_fires": {str(k): v for k, v in tab(c).items()}, "fast_8_12_kmh_20_fires": {str(k): v for k, v in tab(c[c.ros >= 8]).items()}}
res = dict(front_arrival=front, escape_odds_by_departure_minute=odds,
           rutland_km_in_30_60_s=dict(gust_front_speed_kmh=round(float(speed)), seconds_per_km_at_front_speed=round(3600 / float(speed)),
                                      note="Matches the speed of the wind front, not the modelled flame front (4.4-12 km/h: 5-14 min per km)."))
json.dump(res, open(os.path.join(OUT, "firm_up.json"), "w"), indent=1); print(json.dumps(front, indent=1))
