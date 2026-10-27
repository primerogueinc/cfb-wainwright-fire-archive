"""Map and model one earlier 2026 fire at CFB Wainwright, the same way for each, so they can be compared with Oct. 17.
Usage: python3 model_fire.py REPO FIRE_ID [SPACING_M]
FIRE_ID: aug27_28 (night detections only), sept16, sept18_20 (one fire, Sept. 18-20), sept21 (scar from Sentinel-2 Oct. 4) or oct14 (scar from scripts/oct14_fire/layers.py).
Scar: ground with NBR < -0.05 on Sentinel-2 Oct. 4 (B8A/B12, L2A), in components touching a 375 m VIIRS pixel of that fire's detections.
There is no clear pre-fire image in the archive for September, so an older scar touching the same pixels would be counted too.
Weather: ECCC hourly, Wainwright CFB Airfield 21 (301S001), published in LST (UTC-7), converted to MDT (UTC-6); FFMC run hourly
(Van Wagner 1977) from the CWFIS daily FFMC at the station the day before. Fuel: FBP O-1a, 95% curing, corrected ISI; L:B 1.1 WS^0.464.
Spread: Huygens ellipse (rear focus) on a 30 m grid (Dijkstra). Water (NDWI > 0.05 on Oct. 4) does not burn; other scars do burn.
Sweep: ignition at every SPACING cell within 600 m of the first detection pass's 375 m pixels x every 30 min from 12 h before the first detection to the first detection
x rate factor K (1 standard, 0.5, 0.3, 0.17). A run is kept only if the fire is burning inside the 375 m pixel of every detection pass
(modelled arrival within 45 min before the pass). Stop variants: dusk (sunset +20 min), humidity 60%, or free-burning 24 h after
the last detection. Outputs: data/fire_compare/<fire>/ (scar.geojson, runs_<variant>.csv.gz, summary.json)."""
import sys, os, math, json, heapq, numpy as np, pandas as pd, geopandas as gpd, rasterio
from multiprocessing import Pool
from rasterio import features
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin, Affine
from pyproj import Transformer
from scipy import ndimage
from shapely.geometry import shape
REPO, FIRE = sys.argv[1], sys.argv[2]; SP = float(sys.argv[3]) if len(sys.argv) > 3 else 150
OUT = os.path.join(REPO, "data/fire_compare", FIRE); os.makedirs(OUT, exist_ok=True)
CRS = "EPSG:3400"; tf = Transformer.from_crs(4326, CRS, always_xy=True).transform; RES = 30
DATES = {"aug27_28": ["2026-08-27", "2026-08-28"], "sept16": ["2026-09-16"], "sept18_20": ["2026-09-18", "2026-09-19", "2026-09-20"], "sept21": ["2026-09-21"], "oct14": ["2026-10-14"]}[FIRE]
DAY = DATES[0]
SUNSET_LAST = {"2026-08-28": 20.93, "2026-09-16": 19.75, "2026-09-20": 19.62, "2026-09-21": 19.58, "2026-10-14": 18.67}[DATES[-1]]  # local MDT, approx., 52.75 N 110.9 W
SUNSET = SUNSET_LAST + 24 * (len(DATES) - 1)
# ---------- detections
F = pd.read_csv(os.path.join(REPO, "data/firms/history_2012-2026/all_detections_merged.csv"))
F = F[F.source.str.contains("VIIRS") & F.acq_date.isin(DATES)].copy()
F["t_mdt"] = pd.to_datetime(F.acq_date + " " + F.acq_time.astype(str).str.zfill(4), format="%Y-%m-%d %H%M") - pd.Timedelta(hours=6)
CLUSTER = {"aug27_28": (52.73, -111.048), "sept16": (52.825, -110.858), "sept18_20": (52.73, -110.91), "sept21": (52.723, -111.032), "oct14": (52.7549, -110.9389)}[FIRE]
F = F[(np.hypot((F.latitude - CLUSTER[0]) * 111, (F.longitude - CLUSTER[1]) * 67.4) < 4.0)]
T0D = pd.Timestamp(DAY)
F["t"] = (F.t_mdt - T0D).dt.total_seconds() / 3600
passes = sorted(F.t.round(3).unique())
# ---------- grid
cx, cy = tf(F.longitude.mean(), F.latitude.mean()); N = 260; T = from_origin(cx - N * RES / 2, cy + N * RES / 2, RES, RES)
S2 = os.path.join(REPO, "data/copernicus/manual_exports/2026-10-04/2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L2A_%s_(Raw).tiff")
def rp(b):
    with rasterio.open(S2 % b) as r:
        d = np.zeros((N, N), "float32"); reproject(r.read(1).astype("float32"), d, src_transform=r.transform, src_crs=r.crs, dst_transform=T, dst_crs=CRS, resampling=Resampling.average); return d
n8, n12, g3, n08 = rp("B8A"), rp("B12"), rp("B03"), rp("B08")
water = ndimage.binary_opening((g3 - n08) / np.maximum(g3 + n08, 1e-6) > 0.05)
yy, xx = np.mgrid[0:N, 0:N]
fx, fy = tf(F.longitude.values, F.latitude.values); fc, fr = (~T) * (fx, fy)
pix = [(np.abs((yy - r) * RES) <= 187.5) & (np.abs((xx - c) * RES) <= 187.5) for r, c in zip(fr, fc)]
pass_pix = {p: np.any([m for m, t in zip(pix, F.t.round(3)) if t == p], axis=0) for p in passes}
anypix = np.any(pix, axis=0)
if FIRE == "oct14":
    z = np.load(os.path.join(REPO, "data/oct14_fire/layers.npz")); Tz = Affine(*z["T"]); scar = np.zeros((N, N), bool)
    reproject(z["burn14"].astype("float32"), (s := np.zeros((N, N), "float32")), src_transform=Tz, src_crs=CRS, dst_transform=T, dst_crs=CRS, resampling=Resampling.nearest); scar = s > 0.5
    old = np.zeros((N, N), "float32"); reproject(z["oldburn"].astype("float32"), old, src_transform=Tz, src_crs=CRS, dst_transform=T, dst_crs=CRS, resampling=Resampling.nearest); barrier = old > 0.5
else:
    burned = ndimage.binary_opening(((n8 - n12) / np.maximum(n8 + n12, 1e-6) < -0.05) & ~water)
    lab, _ = ndimage.label(burned); ids = set(np.unique(lab[anypix & burned])) - {0}; scar = np.isin(lab, list(ids)); barrier = np.zeros((N, N), bool)
scar_km2 = scar.sum() * RES * RES / 1e6
if scar.any():
    gs = gpd.GeoSeries([shape(g) for g, v in features.shapes(scar.astype("uint8"), mask=scar, transform=T) if v == 1], crs=CRS).union_all()
    gpd.GeoDataFrame(dict(fire=[FIRE], area_km2=[round(scar_km2, 3)]), geometry=[gs], crs=CRS).to_crs(4326).to_file(os.path.join(OUT, "scar.geojson"), driver="GeoJSON")
edge_hit = bool(scar[0].any() or scar[-1].any() or scar[:, 0].any() or scar[:, -1].any())
# ---------- weather
H = os.path.join(REPO, "data/eccc/climate_hourly/history")
mo = sorted({(T0D + pd.Timedelta(days=d)).strftime("%Y-%m") for d in (-1, 0, 1, 2, 3)})
w = pd.concat([pd.read_csv(os.path.join(H, f"301S001_{m}_LST.csv")) for m in mo])
w["t"] = (pd.to_datetime(w["Date/Time (LST)"]) + pd.Timedelta(hours=1) - T0D).dt.total_seconds() / 3600
w = w[(w.t >= -36) & (w.t <= 110)].dropna(subset=["Temp (°C)", "Rel Hum (%)", "Wind Spd (km/h)"]).sort_values("t")
w["wd"] = w["Wind Dir (10s deg)"].fillna(0) * 10
cw = pd.read_csv(os.path.join(REPO, "data/nrcan_cwfis/history/cwfis_fwi_2026_wainwright.csv"), skipinitialspace=True).drop_duplicates()
cw.columns = [c.strip().lower() for c in cw.columns]
cw["d"] = pd.to_datetime(cw.repdate.astype(str).str.strip(), format="%Y%m%d")
prev = cw[cw.d == T0D - pd.Timedelta(days=1)]; today = cw[cw.d == T0D]
ff0 = float(prev.ffmc.iloc[0]) if len(prev) else 85.0
def hffmc(f0, temp, rh, ws, rain=0.0):
    mo_ = 147.27723 * (101 - f0) / (59.5 + f0)
    if rain > 0.5: mo_ = min(250.0, mo_ + 42.5 * (rain - 0.5) * math.exp(-100 / (251 - mo_)) * (1 - math.exp(-6.93 / (rain - 0.5))))
    ed = 0.942 * rh ** 0.679 + 11 * math.exp((rh - 100) / 10) + 0.18 * (21.1 - temp) * (1 - math.exp(-0.115 * rh))
    ew = 0.618 * rh ** 0.753 + 10 * math.exp((rh - 100) / 10) + 0.18 * (21.1 - temp) * (1 - math.exp(-0.115 * rh))
    if mo_ > ed: a = rh / 100; k = (0.424 * (1 - a ** 1.7) + 0.0694 * ws ** 0.5 * (1 - a ** 8)) * 0.0579 * math.exp(0.0365 * temp); m = ed + (mo_ - ed) * 10 ** (-k)
    elif mo_ < ew: a = (100 - rh) / 100; k = (0.424 * (1 - a ** 1.7) + 0.0694 * ws ** 0.5 * (1 - a ** 8)) * 0.0579 * math.exp(0.0365 * temp); m = ew - (ew - mo_) * 10 ** (-k)
    else: m = mo_
    return 59.5 * (250 - m) / (147.27723 + m)
def isi(ffmc, ws):
    fm = 147.27723 * (101 - ffmc) / (59.5 + ffmc); sf = 19.115 * math.exp(-0.1386 * fm) * (1 + fm ** 5.31 / 4.93e7)
    fw = math.exp(0.05039 * ws) if ws < 40 else 12 * (1 - math.exp(-0.0818 * (ws - 28))); return fw * sf
ff = ff0; rows = []
for _, r in w[w.t >= -11].iterrows():  # from 13:00 MDT the day before (CWFIS noon LST)
    ff = hffmc(ff, r["Temp (°C)"], r["Rel Hum (%)"], r["Wind Spd (km/h)"], float(r.get("Precip. Amount (mm)", 0) or 0))
    rows.append(dict(t=r.t, ffmc=ff, ws=r["Wind Spd (km/h)"], wd=r.wd, rh=r["Rel Hum (%)"], temp=r["Temp (°C)"], isi=isi(ff, r["Wind Spd (km/h)"])))
W = pd.DataFrame(rows); CF = 0.176 + 0.02 * (95 - 58.8)
rsi = lambda I: 190 * (1 - math.exp(-0.0310 * I)) ** 1.4 * CF
W["ros_std_kmh"] = [rsi(i) * 0.06 for i in W.isi]; W.round(3).to_csv(os.path.join(OUT, "weather_model.csv"), index=False)
def wx(t):
    ws = float(np.interp(t, W.t, W.ws)); I = float(np.interp(t, W.t, W.isi)); a = np.radians(W.wd.values)
    return ws, I, math.degrees(math.atan2(np.interp(t, W.t, np.sin(a)), np.interp(t, W.t, np.cos(a)))) % 360
NB = [(di, dj) for di in range(-2, 3) for dj in range(-2, 3) if (di, dj) != (0, 0) and math.gcd(abs(di), abs(dj)) == 1]
NBg = [(di, dj, RES * math.hypot(di, dj), math.degrees(math.atan2(dj, -di)) % 360) for di, dj in NB]
rh = W.set_index("t").rh; last = max(passes)
t_rh60 = next((t for t in W.t if t > last and W.set_index("t").rh[t] >= 60), last + 12)
VARS = {"dusk": max(SUNSET + 0.33, last + 0.1), "rh60": t_rh60, "free24h": last + 24}
fuel = ~water & ~barrier
def run(args):
    i0, j0, t0, K, tend = args
    A = np.full((N, N), np.inf); A[i0, j0] = t0; pq = [(t0, i0, j0)]; cache = {}
    while pq:
        t, i, j = heapq.heappop(pq)
        if t > A[i, j] or t > tend: continue
        key = round(t * 12)
        if key not in cache:
            ws, I, wd = wx(key / 12); R = max(K * rsi(I), 1e-3); lb = 1.1 * max(ws, 1) ** 0.464; e = math.sqrt(max(0, 1 - 1 / lb ** 2)); head = (wd + 180) % 360
            cache[key] = [(di, dj, d / (R * (1 - e) / (1 - e * math.cos(math.radians(brg - head)))) / 60) for di, dj, d, brg in NBg]
        for di, dj, dt in cache[key]:
            a, b = i + di, j + dj
            if 0 <= a < N and 0 <= b < N and fuel[a, b]:
                tn = t + dt
                if tn < A[a, b]: A[a, b] = tn; heapq.heappush(pq, (tn, a, b))
    return A
def job(args):
    i0, j0, t0, K = args; out = []
    A = run((i0, j0, t0, K, max(VARS.values())))
    ok = all(((A > p - 0.75) & (A <= p) & pass_pix[p]).any() for p in passes)
    for v, te in VARS.items():
        B = A <= te
        out.append(dict(i=i0, j=j0, t0=t0, K=K, variant=v, ok=ok, final_km2=round(B.sum() * RES * RES / 1e6, 3),
                        jaccard=round(float((B & scar).sum() / max((B | scar).sum(), 1)), 3), grid_edge=bool(B[0].any() or B[-1].any() or B[:, 0].any() or B[:, -1].any())))
    return out
if __name__ == "__main__":
    firstpix = pass_pix[min(passes)]
    zone = ndimage.binary_dilation(firstpix, iterations=int(600 // RES)) & fuel  # the fire started near its first detection
    step = max(1, int(SP // RES)); cand = [(i, j) for i in range(0, N, step) for j in range(0, N, step) if zone[i, j]]
    first = min(passes); times = np.arange(first - 12, first + 1e-6, 0.5)
    jobs = [(i, j, t, K) for (i, j) in cand for t in times for K in (1.0, 0.5, 0.3, 0.17)]
    print(FIRE, len(cand), "cells", len(jobs), "runs", flush=True)
    rp_ = os.path.join(OUT, "runs.csv.gz")
    if os.path.exists(rp_) and not os.environ.get("RERUN"): df = pd.read_csv(rp_)
    else:
        with Pool(2) as p: res = [r for rr in p.imap_unordered(job, jobs, chunksize=16) for r in rr]
        df = pd.DataFrame(res); df.to_csv(rp_, index=False)
    S = dict(fire=FIRE, date=DAY, detections=int(len(F)), passes_mdt=[f"{int(p)%24:02d}:{int(round((p%1)*60)):02d}" for p in passes],
             night_detections=int((F.daynight == "N").sum()), max_pass_frp_mw=round(float(F.groupby(F.t.round(3)).frp.sum().max()), 1),
             detection_span_h=round(float(last - first), 2), scar_km2=round(scar_km2, 3), scar_touches_window_edge=edge_hit,
             cwfis_days=[dict(date=str(r.d.date()), ffmc=r.ffmc, isi=r.isi, fwi=r.fwi) for r in cw[cw.d.isin(pd.to_datetime(DATES))].itertuples()], ffmc_start=ff0,
             max_wind_kmh=float(W[(W.t >= 0) & (W.t <= 24 * len(DATES))].ws.max()), min_rh=float(W[(W.t >= 0) & (W.t <= 24 * len(DATES))].rh.min()),
             peak_std_ros_kmh=round(float(W[(W.t >= 0) & (W.t <= 24 * len(DATES))].ros_std_kmh.max()), 2), stop_times_h=VARS, n_runs=len(jobs))
    for v in VARS:
        d = df[(df.variant == v) & df.ok]
        if not len(d): S[v] = None; continue
        wts = np.exp((d.jaccard.values - d.jaccard.max()) / 0.05); wts /= wts.sum()
        std = d[d.K == 1.0]
        S[v] = dict(best_jaccard=float(d.jaccard.max()), weight_by_K={str(k): round(float(wts[d.K == k].sum()), 3) for k in (1.0, 0.5, 0.3, 0.17)},
                    standard_rate_km2_p10_p50_p90=[round(float(x), 2) for x in std.final_km2.quantile([.1, .5, .9])] if len(std) else None,
                    ratio_standard_to_observed=round(float(std.final_km2.median()) / scar_km2, 1) if len(std) and scar_km2 > 0 else None,
                    ignition_weighted_median_h=round(float(np.interp(0.5, np.cumsum(wts[np.argsort(d.t0.values)]), np.sort(d.t0.values))), 2))
    json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=str); print(json.dumps(S, indent=1, default=str))
