"""Fire arrival-time field for the 3D animation (working model v4 timing).

Observed anchors (all already in the archive):
  12:17  Landsat 8: 59 active-fire pixels (the noon fire line)
  14:49  NOAA-20 VIIRS: 8 fire pixels; with the Landsat pixels they define the
         pre-shift footprint (convex hull, clipped to the burn scar)
  15:16  CZWN: 82 km/h gust, wind turns northwest (306 deg)
  15:10-15:40  GOES-18: fire power peaks at 15:30 (1,215 MW), fades by 16:00
  Oct 24 Sentinel-2 dNBR: final burn scar and severity

Everything between those anchors is MODELLED, following working model v4:
  0. before 3:16 p.m.: v4's best-fit morning fire (case v4b: start 5:00 a.m.,
     1.4-2.2 km east of Range 11, 2x morning spread, L:B x3), read from
     data/authentic-stoic-stress-test/model_v4/arrival_prefront_v4b_*.tif on
     the authentic-stoic-alternative-hypothesis branch (hours after midnight).
  1. cells of the 12:17/2:49 detection outline that v4b has not reached by
     3:16 burn by distance from the noon line, 12:17 -> 2:49 (v4 likewise
     joins this outline to its 3:16 fire before the post-front runs).
  2. after 15:16: cells downwind (306 deg) of the footprint burn in order of
     their distance downwind, the run taking 15:20 -> 15:35 (the published
     "about 3:20 to 3:35 p.m.").
  3. the rest of the scar burns outward from what is already burning at a
     flank rate of 2 km/h, starting no earlier than 15:16.
  4. scar patches not connected to any of that get no time (shown as burned
     only in the final frames, labelled as timing unknown).

Run: python3 fire_field.py LAYERDIR [PREFRONT_TIF]
"""
import sys, os, json, heapq
import numpy as np
from PIL import Image
from shapely.geometry import MultiPoint, Polygon, mapping
from rasterio.features import rasterize
from rasterio.transform import from_origin

Ld = sys.argv[1]
P = json.load(open(os.path.join(Ld, 'points.json')))
G = P['grid']; RES = G['res']; W, H = G['w'], G['h']
dnbr = np.load(os.path.join(Ld, 'dnbr.npy'))
scar5 = np.asarray(Image.open(os.path.join(Ld, 'scar.png'))) > 127
scar = scar5.reshape(H, 2, W, 2).mean(axis=(1, 3)) >= 0.5

hm = lambda h: int(h[:2]) * 60 + int(h[3:5])
T_LS, T_V, T_SHIFT, T_RUN0, T_RUN1 = hm('12:17'), hm('14:49'), hm('15:16'), hm('15:20'), hm('15:35')
FLANK_MPM = 2000 / 60  # 2 km/h in metres per minute

ls = [h for h in P['hotspots'] if h['source'] == 'LANDSAT_NRT' and '12:17' in (h['time_mdt'] or '')]
vi = [h for h in P['hotspots'] if h['source'] == 'VIIRS_NOAA20_NRT' and '14:49' in (h['time_mdt'] or '')]
T = from_origin(0, H * RES, RES, RES)  # grid metres, origin lower-left
hull = MultiPoint([(h['x'], h['y']) for h in ls + vi]).convex_hull
hullm = rasterize([(mapping(hull), 1)], out_shape=(H, W), transform=T, dtype=np.uint8).astype(bool) & scar
print(f'pre-shift footprint {hullm.sum() * RES * RES / 1e6:.2f} km2 (published: 2.00)')

arr = np.full((H, W), np.nan)

# --- 1. pre-shift creep (geodesic distance inside the footprint) ------------
def dijkstra(seeds, allowed, speed_mpm=None, floor=None):
    """seeds: dict (r, c) -> start value. Returns distance (m) or time (min) field."""
    out = np.full((H, W), np.inf)
    pq = []
    for (r, c), v in seeds.items():
        out[r, c] = v; heapq.heappush(pq, (v, r, c))
    steps = [(-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1),
             (-1, -1, 2 ** .5), (-1, 1, 2 ** .5), (1, -1, 2 ** .5), (1, 1, 2 ** .5)]
    while pq:
        v, r, c = heapq.heappop(pq)
        if v > out[r, c]:
            continue
        for dr, dc, k in steps:
            rr, cc = r + dr, c + dc
            if 0 <= rr < H and 0 <= cc < W and allowed[rr, cc]:
                step = k * RES if speed_mpm is None else k * RES / speed_mpm
                nv = v + step
                if floor is not None:
                    nv = max(nv, floor)
                if nv < out[rr, cc]:
                    out[rr, cc] = nv; heapq.heappush(pq, (nv, rr, cc))
    return out

# --- 0. v4 best-fit morning fire --------------------------------------------
if len(sys.argv) > 2:
    import rasterio
    from rasterio.warp import reproject, Resampling
    pre = np.full((H, W), np.nan, np.float32)
    TG = from_origin(G['x0'], G['y0'] + H * RES, RES, RES)
    with rasterio.open(sys.argv[2]) as src:
        reproject(rasterio.band(src, 1), pre, dst_transform=TG, dst_crs=G['crs'],
                  dst_nodata=np.nan, resampling=Resampling.bilinear)
    # v4 works on a 40 m grid; bilinear resampling to 10 m smooths its stair steps
    pre_min = pre * 60
    v4 = np.isfinite(pre_min) & (pre_min <= T_SHIFT)
    arr[v4] = pre_min[v4]
    print(f'v4b morning fire: {v4.sum()*RES*RES/1e6:.2f} km2 by 3:16 (v4: 1.23), first cell {np.nanmin(pre_min)/60:.2f} h')
    hullm_pre = hullm & ~v4
else:
    hullm_pre = hullm

rc = lambda x, y: (int(np.clip(H - 1 - y / RES, 0, H - 1)), int(np.clip(x / RES, 0, W - 1)))
allowed_pre = hullm.copy()
seeds = {}
for h in ls:
    r, c = rc(h['x'], h['y']); allowed_pre[r, c] = True; seeds[(r, c)] = 0.0
d_pre = dijkstra(seeds, allowed_pre)
fin = np.isfinite(d_pre)
dmax = d_pre[fin].max()
creep = np.where(fin, T_LS + d_pre / dmax * (T_V - T_LS), np.nan)
fill = fin & hullm_pre & ~np.isfinite(arr)
arr[fill] = creep[fill]
fin = np.isfinite(arr)  # the fire's footprint at the shift: v4b plus the detection outline
print(f'pre-shift: farthest cell {dmax/1000:.2f} km from the noon line -> creep {dmax/(T_V-T_LS)*60/1000:.2f} km/h')

# --- 2. the run: distance downwind (upwind ray to the footprint) -------------
foot = fin.copy()
az = np.radians(306)  # wind FROM 306: march upwind toward 306
ux, uy = np.sin(az), np.cos(az)
rr, cc = np.nonzero(scar & ~fin)
X = (cc + 0.5) * RES; Y = (H - 1 - rr + 0.5) * RES
d_up = np.full(rr.size, np.nan)
alive = np.ones(rr.size, bool)
for k in range(1, 700):  # up to 7 km
    s = k * RES
    r2 = np.clip((H - 1 - (Y + s * uy) / RES).astype(int), 0, H - 1)
    c2 = np.clip(((X + s * ux) / RES).astype(int), 0, W - 1)
    hit = alive & foot[r2, c2]
    d_up[hit] = s; alive &= ~hit
ok = ~np.isnan(d_up)
dmax_run = np.nanmax(d_up)
arr[rr[ok], cc[ok]] = T_RUN0 + d_up[ok] / dmax_run * (T_RUN1 - T_RUN0)
print(f'run: {ok.sum()*RES*RES/1e6:.2f} km2 downwind of the footprint, farthest {dmax_run/1000:.2f} km '
      f'-> {dmax_run/1000/((T_RUN1-T_RUN0)/60):.0f} km/h average')

# --- 3. the rest: outward from burning cells at flank rate --------------------
have = np.isfinite(arr)
# flanks only start moving after the shift: the pre-shift footprint seeds at 3:16,
# the run cells at their own (later) times
seeds = {(r, c): max(arr[r, c], T_SHIFT) for r, c in zip(*np.nonzero(have))}
t_flank = dijkstra(seeds, scar | have, speed_mpm=FLANK_MPM, floor=None)
rest = scar & ~have & np.isfinite(t_flank)
arr[rest] = np.maximum(t_flank[rest], T_SHIFT)
unk = scar & ~np.isfinite(arr)
print(f'flank: {rest.sum()*RES*RES/1e6:.2f} km2; timing unknown (unconnected patches): {unk.sum()*RES*RES/1e6:.2f} km2')

sev = np.clip(dnbr / 0.6, 0.35, 1.0).astype(np.float32)
np.save(os.path.join(Ld, 'arrival_min.npy'), arr.astype(np.float32))
np.save(os.path.join(Ld, 'unknown.npy'), unk)
np.save(os.path.join(Ld, 'severity.npy'), sev)
json.dump({'T_LS': T_LS, 'T_V': T_V, 'T_SHIFT': T_SHIFT, 'T_RUN0': T_RUN0, 'T_RUN1': T_RUN1,
           'hull': [list(c) for c in hull.exterior.coords],
           'arr_max': float(np.nanmax(arr))}, open(os.path.join(Ld, 'fire_meta.json'), 'w'))
q = np.nanpercentile(arr[scar], [50, 90, 99])
print('scar burned by (median / 90% / 99%):', ' / '.join(f'{int(v//60)}:{int(v%60):02d}' for v in q))
