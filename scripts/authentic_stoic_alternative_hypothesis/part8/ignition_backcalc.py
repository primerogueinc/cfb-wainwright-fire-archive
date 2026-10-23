"""Part 8b: when and where did the fire start? Back-calculate ignition from the 12:17 p.m. Landsat and 2:49 p.m. VIIRS detections.

Usage: python3 ignition_backcalc.py REPO RES_M CAND_SPACING_M [OUT_SUBDIR]

Model
- Grass fire (CFFDRS Fire Behaviour Prediction, fuel type O-1a, curing 95%), spreading as an ellipse (Huygens, rear focus) over a
  grid. Wind direction and speed change hour by hour from the base station (CZWN climate hourly, converted to MDT, interpolated).
- Fine-fuel moisture from the hourly FFMC equations (Van Wagner 1977), started from CWFIS daily FFMC 87.2 at 1 p.m. MDT Oct. 16.
  Head rate of spread from ISI with the O-1a curve, times a calibration factor k fitted so the model's head advance between
  12:17 and 2:49 p.m. matches what the satellites measured (0.43 km/h, part 6). Length-to-breadth ratio 1.1*WS^0.464.
- Fire can only spread inside the mapped burn scar (+100 m), less water.
- Candidates: every scar cell on a regular grid within 3.5 km of Range 11; ignition times 04:00-12:00 MDT.
- Fit: share of the 59 Landsat 12:17 detections the modelled fire reaches between 11:47 and 12:22 (burning when imaged), and share
  of the 8 VIIRS 14:49 pixels (375 m) with modelled fire arriving between 13:49 and 14:54 inside the pixel. Score = 0.7*Landsat + 0.3*VIIRS.
"""
import sys, os, math, json, heapq
import numpy as np, pandas as pd, geopandas as gpd, rasterio
from rasterio import features
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from shapely.geometry import Point
from pyproj import Geod, Transformer

REPO = sys.argv[1]; RES = float(sys.argv[2]); SP = float(sys.argv[3]); SUB = sys.argv[4] if len(sys.argv) > 4 else "part8b_ignition"
OUT = os.path.join(REPO, "data/authentic-stoic-stress-test", SUB); os.makedirs(OUT, exist_ok=True)
CRS = "EPSG:3400"; G = Geod(ellps="WGS84"); tf = Transformer.from_crs(4326, CRS, always_xy=True).transform
R11 = (-110.9577, 52.7678); r11x, r11y = tf(*R11)

# ---------- weather: hourly, MDT, as hours since 00:00 Oct 17
c = pd.read_csv(os.path.join(REPO, "data/weather_exports/3_climate_hourly_czwn_oct2026.csv"))
c["t"] = (pd.to_datetime(c["time_mdt_local_clock_utc-6"]) - pd.Timestamp("2026-10-17")).dt.total_seconds() / 3600
c = c[(c.t >= -11) & (c.t <= 16)].sort_values("t")
T_, RH_, WS_, WD_ = c.t.values, c["Rel Hum (%)"].values, c["Wind Spd (km/h)"].values, c.wind_dir_deg.values
TEMP_ = c["Temp (°C)"].values

def hffmc(f0, temp, rh, ws, hours=1.0):
    mo = 147.27723 * (101 - f0) / (59.5 + f0)
    ed = 0.942 * rh ** 0.679 + 11 * math.exp((rh - 100) / 10) + 0.18 * (21.1 - temp) * (1 - math.exp(-0.115 * rh))
    ew = 0.618 * rh ** 0.753 + 10 * math.exp((rh - 100) / 10) + 0.18 * (21.1 - temp) * (1 - math.exp(-0.115 * rh))
    if mo > ed:
        a = rh / 100; k0 = 0.424 * (1 - a ** 1.7) + 0.0694 * ws ** 0.5 * (1 - a ** 8); k = k0 * 0.0579 * math.exp(0.0365 * temp)
        m = ed + (mo - ed) * 10 ** (-k * hours)
    elif mo < ew:
        a = (100 - rh) / 100; k0 = 0.424 * (1 - a ** 1.7) + 0.0694 * ws ** 0.5 * (1 - a ** 8); k = k0 * 0.0579 * math.exp(0.0365 * temp)
        m = ew - (ew - mo) * 10 ** (-k * hours)
    else:
        m = mo
    return 59.5 * (250 - m) / (147.27723 + m)

def isi(ffmc, ws):
    fm = 147.27723 * (101 - ffmc) / (59.5 + ffmc)
    sf = 19.115 * math.exp(-0.1386 * fm) * (1 + fm ** 5.31 / 4.93e7)
    fw = math.exp(0.05039 * ws) if ws < 40 else 12 * (1 - math.exp(-0.0818 * (ws - 28)))
    return 0.208 * fw * sf

ff = 87.2; HRS = []
for i in range(len(T_)):
    if T_[i] >= -11 + 1e-6: ff = hffmc(ff, TEMP_[i], RH_[i], WS_[i])
    HRS.append(dict(t=T_[i], ffmc=ff, isi=isi(ff, WS_[i]), ws=WS_[i], wd=WD_[i], rh=RH_[i], temp=TEMP_[i]))
H_ = pd.DataFrame(HRS)
CF = 0.176 + 0.02 * (95 - 58.8)
def rsi(I): return 190 * (1 - math.exp(-0.0310 * I)) ** 1.4 * CF  # m/min, O-1a
def wx(t):
    ws = float(np.interp(t, H_.t, H_.ws)); I = float(np.interp(t, H_.t, H_.isi))
    a = np.radians(H_.wd.values); u, v = np.interp(t, H_.t, np.sin(a)), np.interp(t, H_.t, np.cos(a))
    wd = math.degrees(math.atan2(u, v)) % 360
    return ws, I, wd

# ---------- calibration: k so mean modelled head ROS 12:17-14:49 equals 0.43 km/h (7.17 m/min)
MORNING_MULT = 1.0  # spread-rate multiplier before 12:17 only (sensitivity); afternoon stays calibrated to the measured pace
ts = np.arange(12 + 17 / 60, 14 + 49 / 60, 1 / 60)
raw = np.mean([rsi(wx(t)[1]) for t in ts]); K = 7.17 / raw

# ---------- grid
scar_all = gpd.read_file(os.path.join(REPO, "data/infrastructure/scar_patches_revised.geojson")).to_crs(CRS)
scar = max(scar_all.geometry, key=lambda g: g.area)
minx, miny, maxx, maxy = scar.bounds; pad = 2500
minx, miny, maxx, maxy = min(minx, r11x) - pad, miny - pad, maxx + pad, maxy + pad
W = int(math.ceil((maxx - minx) / RES)); H = int(math.ceil((maxy - miny) / RES)); T = from_origin(minx, maxy, RES, RES)
rast = lambda g: features.rasterize([(g, 1)], out_shape=(H, W), transform=T, fill=0, dtype="uint8").astype(bool)
S2 = os.path.join(REPO, "data/copernicus/manual_exports/2026-10-04/2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L2A_%s_(Raw).tiff")
def band(b):
    with rasterio.open(S2 % b) as r:
        dst = np.zeros((H, W), "float32")
        reproject(r.read(1).astype("float32"), dst, src_transform=r.transform, src_crs=r.crs, dst_transform=T, dst_crs=CRS, resampling=Resampling.average)
    return dst
gg, nn = band("B03"), band("B08"); water = (gg - nn) / np.maximum(gg + nn, 1e-6) > 0.05
fuel = rast(scar.buffer(100)) & ~water
cell = lambda x, y: (int((maxy - y) // RES), int((x - minx) // RES))
cxy = lambda i, j: (minx + (j + 0.5) * RES, maxy - (i + 0.5) * RES)

d = pd.read_csv(os.path.join(REPO, "data/firms/detections.csv"))
d = d[(d.latitude.between(52.7, 52.85)) & (d.longitude.between(-111.0, -110.82))]
L = d[d.acq_datetime_mdt == "2026-10-17 12:17 MDT"]; V = d[d.acq_datetime_mdt == "2026-10-17 14:49 MDT"]
Lc = [cell(*tf(lo, la)) for la, lo in zip(L.latitude, L.longitude)]
Vxy = [tf(lo, la) for la, lo in zip(V.latitude, V.longitude)]
yy, xx = np.mgrid[0:H, 0:W]; GX = minx + (xx + 0.5) * RES; GY = maxy - (yy + 0.5) * RES
Vmask = [(np.abs(GX - x) <= 187.5) & (np.abs(GY - y) <= 187.5) for x, y in Vxy]
TL, TV = 12 + 17 / 60, 14 + 49 / 60

NB = [(di, dj) for di in range(-2, 3) for dj in range(-2, 3) if (di, dj) != (0, 0) and math.gcd(abs(di), abs(dj)) == 1]
NBg = [(di, dj, RES * math.hypot(di, dj), math.degrees(math.atan2(dj, -di)) % 360) for di, dj in NB]  # bearing: north=0, east=90

def run(i0, j0, t0, tend=15 + 16 / 60, starts=None):
    A = np.full((H, W), np.inf)
    starts = starts if starts is not None else [(i0, j0)]
    pq = []
    for a, b in starts: A[a, b] = t0; pq.append((t0, a, b))
    heapq.heapify(pq)
    cache = {}
    while pq:
        t, i, j = heapq.heappop(pq)
        if t > A[i, j] or t > tend: continue
        key = round(t * 12)  # 5-minute weather steps
        if key not in cache:
            ws, I, wd = wx(key / 12); R = K * rsi(I) * (MORNING_MULT if key / 12 < TL else 1.0); lb = 1.1 * max(ws, 1) ** 0.464; e = math.sqrt(max(0, 1 - 1 / lb ** 2))
            head = (wd + 180) % 360
            cache[key] = [(di, dj, dist / (R * (1 - e) / (1 - e * math.cos(math.radians(brg - head)))) / 60) for di, dj, dist, brg in NBg]
        for di, dj, dt in cache[key]:
            a, b = i + di, j + dj
            if 0 <= a < H and 0 <= b < W and fuel[a, b]:
                tn = t + dt
                if tn < A[a, b]: A[a, b] = tn; heapq.heappush(pq, (tn, a, b))
    return A

from scipy import ndimage
Lmask = np.zeros((H, W), bool)
for i, j in Lc:
    if 0 <= i < H and 0 <= j < W: Lmask[i, j] = True
Vany = np.any(Vmask, axis=0)
D_to_L = ndimage.distance_transform_edt(~Lmask) * RES
D_to_V = ndimage.distance_transform_edt(~Vany) * RES

def chamfer(B, det_cells_mask, D_to_det, det_pts):
    if not B.any(): return 9999.0, 9999.0
    D_to_B = ndimage.distance_transform_edt(~B) * RES
    d1 = np.mean([D_to_B[m].min() for m in det_pts])              # each detection to the modelled fire
    per = B & ~ndimage.binary_erosion(B)
    d2 = float(D_to_det[per].mean())                                # modelled perimeter to the detections
    return float(d1), d2

Lpts = [(lambda m: (m.__setitem__((i, j), True), m)[1])(np.zeros((H, W), bool)) for i, j in Lc if 0 <= i < H and 0 <= j < W]

def score(A):
    l1, l2 = chamfer(A <= TL, Lmask, D_to_L, Lpts)
    v1, v2 = chamfer(A <= TV, Vany, D_to_V, Vmask)
    v1 = max(0.0, v1)
    s = (l1 + l2) / 2 + 0.5 * (v1 + v2) / 2
    return round(l1), round(l2), round(s), round(v1 + v2)

# candidates: scar cells on a grid within 3.5 km of Range 11
step = max(1, int(round(SP / RES)))
cand = [(i, j) for i in range(0, H, step) for j in range(0, W, step) if fuel[i, j] and math.hypot(GX[i, j] - r11x, GY[i, j] - r11y) <= 3500]
times = np.arange(-8, 12.01, 0.5)
rows = []
for n, (i, j) in enumerate(cand):
    lo, la = Transformer.from_crs(CRS, 4326, always_xy=True).transform(*cxy(i, j))
    az, _, dist = G.inv(R11[0], R11[1], lo, la)
    for t0 in times:
        sL, sV, s, reached = score(run(i, j, t0))  # sL: Landsat->fire (m), sV: fire perimeter->Landsat (m), s: total misfit (m)
        rows.append(dict(i=i, j=j, lon=round(lo, 5), lat=round(la, 5), km_from_r11=round(dist / 1000, 2), bearing_from_r11=round(az % 360),
                         in_c16_sector=bool(dist <= 2200 and 40 <= az % 360 <= 120), ignition_mdt=f"{int(t0 % 24):02d}:{int(round((t0 % 1) * 60)):02d}" + (" Oct 16" if t0 < 0 else ""),
                         t0=t0, landsat_to_fire_m=sL, fire_edge_to_landsat_m=sV, misfit_m=s, viirs_misfit_m=reached))
    if n % 10 == 0: print(n, len(cand), flush=True)
df = pd.DataFrame(rows); df.to_csv(os.path.join(OUT, f"ignition_grid_{int(RES)}m.csv"), index=False)
# ---------- line ignition: rounds landing along a gun-target line from Range 11 (bearing b, from d1 to d2 km)
lrows = []
for b in range(56, 85, 4):
    for d1, d2 in [(1.0, 2.2), (1.4, 2.2), (1.8, 2.2), (1.0, 1.6)]:
        st = set()
        for dd in np.arange(d1, d2 + 1e-6, RES / 2000):
            lo, la, _ = G.fwd(R11[0], R11[1], b, dd * 1000); i, j = cell(*tf(lo, la))
            if 0 <= i < H and 0 <= j < W and fuel[i, j]: st.add((i, j))
        if not st: continue
        for t0 in times:
            sL, sV, sc, reached = score(run(0, 0, t0, starts=list(st)))
            lrows.append(dict(bearing=b, d1_km=d1, d2_km=d2, start_cells=len(st), ignition_mdt=f"{int(t0 % 24):02d}:{int(round((t0 % 1) * 60)):02d}" + (" Oct 16" if t0 < 0 else ""),
                              t0=t0, landsat_to_fire_m=sL, fire_edge_to_landsat_m=sV, misfit_m=sc, viirs_misfit_m=reached))
ldf = pd.DataFrame(lrows); ldf.to_csv(os.path.join(OUT, f"line_ignition_{int(RES)}m.csv"), index=False)
print(ldf.sort_values("misfit_m").head(12).to_string())
H_.assign(ros_head_m_min=[K * rsi(x) for x in H_.isi]).round(2).to_csv(os.path.join(OUT, "weather_hourly_model.csv"), index=False)
json.dump(dict(K=round(K, 4), CF=round(CF, 3), res_m=RES, cand=len(cand), times=list(map(float, times))), open(os.path.join(OUT, f"run_{int(RES)}m.json"), "w"), indent=1)
print(df.sort_values("misfit_m").head(15).to_string())
