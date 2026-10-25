"""Working model v4: where the smoke went, before and after the 3:16 p.m. wind shift.
Usage: python3 smoke.py REPO P4_DIR_PREFIX OUT_DIR [MODEL_DIR, default model_v4]

Sources: every 40 m cell of the modelled fire, emitting for 10 minutes from the time the fire reaches it
(pre-front: v4 arrival grids, hours since midnight; post-front: the 30 post-front fires per case, minutes after 3 p.m.;
cells inside the observed 12:17/2:49 outline but outside the v3 fire are given 2:49 p.m.).
Emission: fuel consumed 0.35 kg/m2 (FBP O-1b grass) x 8 g PM2.5/kg (grassland; Akagi et al. 2011, Andreae 2019).
Transport: Gaussian plume, ground-level source with ground reflection (the "low" case of part 5; wind-driven grass fire,
Byram convection number < 1 for most hours, computed below), Briggs rural dispersion: class E before 8 a.m.,
class C 8 a.m.-3:16 p.m. (daytime, sunny, moderate wind), class D after the front (strong wind, overcast).
Smoke emitted at time te reaches a point x m downwind at te + x/u. Wind: CZWN hourly (part 8b table) before the front,
the five post-front wind schedules after it. Wind-direction uncertainty: each run repeated with the wind turned
-20, -10, 0, +10, +20 degrees; we report the median and the worst of the five.
Visibility (dark objects) = 3 / (4.5 m2/g x PM2.5 g/m3) (Koschmieder; part 5), capped at 20 km.
"In smoke" = visibility under 1 km (obvious haze); "dense smoke" = under 100 m.
Smoke modelled, not observed: HMS mapped no plume (cloud), so the model is checked against Landsat at 12:17 (smoke_check.py)."""
import sys, os, glob, json, math
import numpy as np, pandas as pd, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from pyproj import Transformer
REPO, P4, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
MD = sys.argv[4] if len(sys.argv) > 4 else "model_v4"
CASES = sorted(os.path.basename(p)[len(os.path.basename(P4)):] for p in glob.glob(P4 + "*") if os.path.isdir(p))
W_KG, EF, MEE, DUR = 0.35, 8.0, 4.5, 10.0
wx = pd.read_csv(os.path.join(REPO, "data/authentic-stoic-stress-test/part8b_ignition/weather_hourly_model.csv"))
wx = wx[wx.t >= 0].copy(); wx["min"] = wx.t * 60 - 900          # minutes after 15:00
def pre_wind(tm):
    return float(np.interp(tm, wx["min"], wx.wd)), max(float(np.interp(tm, wx["min"], wx.ws)), 5.0)
SCHED = {"S0_fixed306": [(16, 306), (999, 306)], "S1_stoic": [(16, 269), (69, 288), (80, 306), (999, 306)],
         "S2_station_veer": [(16, 269), (50, 305), (60, 306), (999, 306)], "S3_fast_veer": [(16, 269), (30, 305), (40, 306), (999, 306)],
         "S4_fixed315": [(16, 315), (999, 315)]}
def post_wind(s, tm):
    ts, ds = zip(*SCHED[s]); return float(np.interp(tm, ts, ds)), 48.0
def sig(x, tm):
    if tm < -420:   # before 8 a.m.: stable (E)
        return 0.06 * x * (1 + 0.0001 * x) ** -0.5, 0.03 * x * (1 + 0.0003 * x) ** -1
    if tm < 16:     # day, before front: class C
        return 0.11 * x * (1 + 0.0001 * x) ** -0.5, 0.08 * x * (1 + 0.0002 * x) ** -0.5
    return 0.08 * x * (1 + 0.0001 * x) ** -0.5, 0.06 * x * (1 + 0.0015 * x) ** -0.5   # D
tf = Transformer.from_crs(4326, 3400, always_xy=True).transform
PTS = {"Range 2 point": (-110.9063, 52.7728), "Road head": (-110.8996, 52.7705), "C": (-110.9160, 52.7640),
       "D": (-110.8995, 52.7628), "E": (-110.8990, 52.7530)}
zone = pd.read_csv(os.path.join(REPO, "data/authentic-stoic-stress-test/part2/part2_core_frequency.csv"))
zone = zone[zone.n_scenarios_in_core > 0]
zs = zone.sample(60, weights="n_scenarios_in_core", random_state=1, replace=False)
REC = [(k, *tf(*v), 1.0, "point") for k, v in PTS.items()] + [(f"zone{i}", *tf(r.x, r.y), r.n_scenarios_in_core, "zone") for i, r in zs.iterrows()]
RX = np.array([r[1] for r in REC]); RY = np.array([r[2] for r in REC])

def conc(srcx, srcy, srct, A, tm, wind_from, u_kmh):
    """PM2.5 g/m3 at all receptors at time tm (minutes after 15:00)."""
    u = u_kmh / 3.6; head = math.radians((wind_from + 180) % 360)
    ex, ey = math.sin(head), math.cos(head)
    dx = RX[:, None] - srcx[None, :]; dy = RY[:, None] - srcy[None, :]
    xd = dx * ex + dy * ey; yc = -dx * ey + dy * ex
    te = tm - xd / u / 60.0                                   # emission time of smoke now at receptor
    ok = (xd > 20) & (te >= srct[None, :]) & (te < srct[None, :] + DUR)
    if not ok.any(): return np.zeros(len(RX))
    xs = np.where(ok, xd, 100.0); sy, sz = sig(xs, tm)
    q = W_KG * A * EF / (DUR * 60)                            # g/s per cell
    c = np.where(ok, q / (math.pi * u * sy * sz) * np.exp(-yc ** 2 / (2 * sy ** 2)), 0)
    return c.sum(1)

def vis(c): return np.minimum(3 / (MEE * np.maximum(c, 1e-12)), 20000.0)
rows = []
for case in CASES:
    W4 = os.path.join(P4 + case)
    minx, maxy, RES, H, Wd = np.load(os.path.join(W4, "meta.npy")); H, Wd = int(H), int(Wd)
    T = from_origin(minx, maxy, RES, RES); A = RES * RES
    pre = np.full((H, Wd), np.nan, "float32")
    with rasterio.open(os.path.join(REPO, f"data/authentic-stoic-stress-test/{MD}/arrival_prefront_{case}.tif")) as r:
        reproject(r.read(1), pre, src_transform=r.transform, src_crs=r.crs, src_nodata=np.nan, dst_transform=T, dst_crs="EPSG:3400", dst_nodata=np.nan, resampling=Resampling.nearest)
    start = np.load(os.path.join(W4, "start316.npy"))
    pre_min = pre * 60 - 900
    pre_min = np.where(start & ~(pre_min <= 16), np.where(np.isfinite(pre_min) & (pre_min <= 16), pre_min, -11.0), pre_min)  # outline cells -> 2:49
    yy, xx = np.mgrid[0:H, 0:Wd]; X = minx + (xx + .5) * RES; Y = maxy - (yy + .5) * RES
    m = start & np.isfinite(pre_min)
    px, py, pt = X[m], Y[m], pre_min[m]
    # before the front: every 10 min from 3:00 a.m. to 3:16 p.m.
    for tm in np.arange(-720, 17, 10):
        wd, ws = pre_wind(tm)
        for off in (-20, -10, 0, 10, 20):
            c = conc(px, py, pt, A, tm, wd + off, ws)
            for (k, _, _, w, kind), ci in zip(REC, c):
                rows.append(dict(case=case, phase="pre", run="pre", time_min=int(tm), off=off, rec=k, kind=kind, w=w, pm=ci))
    # after the front: 30 fires, every minute 3:16-4:00 p.m.
    for f in sorted(glob.glob(os.path.join(W4, "arr_*.npy"))):
        run = os.path.basename(f)[4:-4]; s = next(k for k in SCHED if run.startswith(k + "_"))
        arr = np.load(f); post = (~start) & np.isfinite(arr)
        sx = np.concatenate([px, X[post]]); sy_ = np.concatenate([py, Y[post]]); st = np.concatenate([pt, arr[post]])
        for tm in np.arange(16, 61, 1):
            wd, ws = post_wind(s, tm)
            for off in (-20, 0, 20):
                c = conc(sx, sy_, st, A, tm, wd + off, ws)
                for (k, _, _, w, kind), ci in zip(REC, c):
                    rows.append(dict(case=case, phase="post", run=run, time_min=int(tm), off=off, rec=k, kind=kind, w=w, pm=ci))
    print("done", case, len(rows), flush=True)
df = pd.DataFrame(rows); df["vis_m"] = vis(df.pm.values)
df.to_parquet(os.path.join(OUT, "smoke_receptors.parquet"), index=False)
# Byram convection number by hour (is the plume wind-driven or towering?)
nc = []
for _, r in wx.iterrows():
    R = r.ros_head_m_min / 60; u = r.ws / 3.6; I = 18000 * W_KG * R
    nc.append(dict(hour=int(r.t), wind_kmh=r.ws, wind_from=r.wd, intensity_kWm=round(I), Nc=round(2 * 9.81 * I * 1000 / (1.2 * 1005 * 290 * max(u - R, .5) ** 3), 2)))
pd.DataFrame(nc).to_csv(os.path.join(OUT, "convection_number_by_hour.csv"), index=False)
print("saved")
