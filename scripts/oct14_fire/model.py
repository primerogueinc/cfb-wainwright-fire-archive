"""Oct. 14 fire: free-burning grass-fire model (CFFDRS FBP O-1a, 95% curing, corrected ISI), Huygens ellipse spread on the 30 m grid
from layers.py, hourly CZWN weather Oct. 13 noon to Oct. 15 noon (FFMC from the CWFIS daily 80.5 on Oct. 13, hourly Van Wagner 1977).
Water and ground burned before Oct. 4 (the Sept. 20 burn) do not burn. Fire runs freely until TEND (hours from 00:00 Oct. 14; default 34 = 10:00 Oct. 15) or until it stops. Env: TEND, TAG, KS (rate factors).
Usage: python3 model.py REPO OUTDIR [SPACING_M]
For every ignition cell (on a SPACING grid inside the mapped Oct. 14 burn, plus cells up to 600 m outside) x ignition time
(06:00-14:30, 30 min) x rate factor K (1.0 = standard; 0.5; 0.17 = the factor the Oct. 17 fire ran at before its wind shift):
- burned area at 14:51 and whether the fire is burning inside the 375 m VIIRS pixel at 14:51 (any cell reached 14:21-14:51);
- final area, overlap with the mapped burn (Jaccard), and when the fire stops growing (95% of final area).
A second set of runs adds OSM roads as barriers (sensitivity)."""
import sys, os, math, json, heapq, numpy as np, pandas as pd
from multiprocessing import Pool
from rasterio.transform import Affine
REPO, OUT = sys.argv[1], sys.argv[2]; SP = float(sys.argv[3]) if len(sys.argv) > 3 else 120
z = np.load(os.path.join(OUT, "layers.npz")); T = Affine(*z["T"]); RES = 30
water, old, b14, roads = z["water"], z["oldburn"], z["burn14"], z["roads"]; N = b14.shape[0]; vr, vc = z["viirs"]
c = pd.read_csv(os.path.join(REPO, "data/weather_exports/3_climate_hourly_czwn_oct2026.csv"))
c["t"] = (pd.to_datetime(c["time_mdt_local_clock_utc-6"]) - pd.Timestamp("2026-10-14")).dt.total_seconds() / 3600  # hours from 00:00 Oct. 14
c = c[(c.t >= -12) & (c.t <= 36)].sort_values("t")
def hffmc(f0, temp, rh, ws):
    mo = 147.27723 * (101 - f0) / (59.5 + f0)
    ed = 0.942 * rh ** 0.679 + 11 * math.exp((rh - 100) / 10) + 0.18 * (21.1 - temp) * (1 - math.exp(-0.115 * rh))
    ew = 0.618 * rh ** 0.753 + 10 * math.exp((rh - 100) / 10) + 0.18 * (21.1 - temp) * (1 - math.exp(-0.115 * rh))
    if mo > ed: a = rh / 100; k = (0.424 * (1 - a ** 1.7) + 0.0694 * ws ** 0.5 * (1 - a ** 8)) * 0.0579 * math.exp(0.0365 * temp); m = ed + (mo - ed) * 10 ** (-k)
    elif mo < ew: a = (100 - rh) / 100; k = (0.424 * (1 - a ** 1.7) + 0.0694 * ws ** 0.5 * (1 - a ** 8)) * 0.0579 * math.exp(0.0365 * temp); m = ew - (ew - mo) * 10 ** (-k)
    else: m = mo
    return 59.5 * (250 - m) / (147.27723 + m)
def isi(ffmc, ws):  # corrected: 19.115 already includes 0.208
    fm = 147.27723 * (101 - ffmc) / (59.5 + ffmc); sf = 19.115 * math.exp(-0.1386 * fm) * (1 + fm ** 5.31 / 4.93e7)
    fw = math.exp(0.05039 * ws) if ws < 40 else 12 * (1 - math.exp(-0.0818 * (ws - 28))); return fw * sf
ff = 80.5; rows = []
for _, r in c.iterrows():
    ff = hffmc(ff, r["Temp (°C)"], r["Rel Hum (%)"], r["Wind Spd (km/h)"])
    rows.append(dict(t=r.t, ffmc=ff, ws=r["Wind Spd (km/h)"], wd=r.wind_dir_deg, rh=r["Rel Hum (%)"], temp=r["Temp (°C)"], isi=isi(ff, r["Wind Spd (km/h)"])))
W = pd.DataFrame(rows); CF = 0.176 + 0.02 * (95 - 58.8)
rsi = lambda I: 190 * (1 - math.exp(-0.0310 * I)) ** 1.4 * CF  # m/min
W["ros_std_kmh"] = [rsi(i) * 0.06 for i in W.isi]
def wx(t):
    ws = float(np.interp(t, W.t, W.ws)); I = float(np.interp(t, W.t, W.isi)); a = np.radians(W.wd.values)
    return ws, I, math.degrees(math.atan2(np.interp(t, W.t, np.sin(a)), np.interp(t, W.t, np.cos(a)))) % 360
NB = [(di, dj) for di in range(-2, 3) for dj in range(-2, 3) if (di, dj) != (0, 0) and math.gcd(abs(di), abs(dj)) == 1]
NBg = [(di, dj, RES * math.hypot(di, dj), math.degrees(math.atan2(dj, -di)) % 360) for di, dj in NB]
TEND = float(os.environ.get('TEND', 34.0)); TAG = os.environ.get('TAG', ''); KS = [float(k) for k in os.environ.get('KS', '1.0,0.5,0.17').split(',')]; TV = 14 + 51 / 60
yy, xx = np.mgrid[0:N, 0:N]; Vpix = (np.abs((yy - vr) * RES) <= 187.5) & (np.abs((xx - vc) * RES) <= 187.5)
def run(args):
    i0, j0, t0, K, barrier = args; fuel = ~water & ~old & (~roads if barrier else True)
    A = np.full((N, N), np.inf); A[i0, j0] = t0; pq = [(t0, i0, j0)]; cache = {}
    while pq:
        t, i, j = heapq.heappop(pq)
        if t > A[i, j] or t > TEND: continue
        key = round(t * 12)
        if key not in cache:
            ws, I, wd = wx(key / 12); R = max(K * rsi(I), 1e-3); lb = 1.1 * max(ws, 1) ** 0.464; e = math.sqrt(max(0, 1 - 1 / lb ** 2)); head = (wd + 180) % 360
            cache[key] = [(di, dj, d / (R * (1 - e) / (1 - e * math.cos(math.radians(brg - head)))) / 60) for di, dj, d, brg in NBg]
        for di, dj, dt in cache[key]:
            a, b = i + di, j + dj
            if 0 <= a < N and 0 <= b < N and fuel[a, b]:
                tn = t + dt
                if tn < A[a, b]: A[a, b] = tn; heapq.heappush(pq, (tn, a, b))
    B = A <= TEND; fin = A[B]
    t95 = float(np.quantile(fin, 0.95)) if fin.size else t0
    edge_hit = bool(B[0].any() or B[-1].any() or B[:, 0].any() or B[:, -1].any())
    return dict(i=i0, j=j0, t0=t0, K=K, barrier=barrier, area_1451_km2=round(float((A <= TV).sum()) * 900 / 1e6, 3),
                viirs_active=bool(((A > TV - 0.5) & (A <= TV) & Vpix).any()), final_km2=round(B.sum() * 900 / 1e6, 3),
                jaccard=round(float((B & b14).sum() / max((B | b14).sum(), 1)), 3), covers_obs=round(float((B & b14).sum() / b14.sum()), 3),
                t95=round(t95, 2), reached_grid_edge=edge_hit), A
def job(a): return run(a)[0]
if __name__ == "__main__":
    step = max(1, int(SP // RES)); from scipy import ndimage
    zone = ndimage.binary_dilation(b14, iterations=int(600 // RES)) & ~water & ~old
    cand = [(i, j) for i in range(0, N, step) for j in range(0, N, step) if zone[i, j]]
    times = np.arange(6, 14.5 + 1e-6, 0.5)
    jobs = [(i, j, t, K, False) for (i, j) in cand for t in times for K in KS]
    print(len(cand), "cells", len(jobs), "runs", flush=True)
    with Pool(2) as p: res = p.map(job, jobs, chunksize=20)
    df = pd.DataFrame(res); df.to_csv(os.path.join(OUT, f"runs{TAG}.csv.gz"), index=False)
    W.round(3).to_csv(os.path.join(OUT, "weather_oct14.csv"), index=False)
    ok = df[df.viirs_active]
    best = ok.sort_values("jaccard", ascending=False).groupby("K").head(5)
    print(best.to_string()); print(df.groupby("K").final_km2.describe())
