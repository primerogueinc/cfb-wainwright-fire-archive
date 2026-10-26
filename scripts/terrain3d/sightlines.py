"""Line-of-sight from each POV to the fire as Landsat saw it at 12:17 p.m., Oct 17.

For each POV (eye at 1.7 m) and each of the 59 Landsat 8 fire pixels, sample the
sightline every 5 m and test whether terrain (and, separately, terrain plus
canopy) rises above it. Targets are tested at three heights: ground (0 m),
3 m (typical grass/shrub flame) and 30 m (low smoke).

Two surfaces bracket the truth:
  bare earth  NRCan MRDEM-30 (30 m) - optimistic: ignores all vegetation
  + canopy    adds the Meta/WRI canopy height model (10 m cells) - pessimistic:
              treats mid-October aspen, mostly bare, as a solid wall
The earth's curvature is included (refraction k = 0.13).

Run: python3 sightlines.py LAYERDIR
"""
import sys, os, json
import numpy as np

Ld = sys.argv[1]
P = json.load(open(os.path.join(Ld, 'points.json')))
h = np.load(os.path.join(Ld, 'height.npy')).astype(np.float64)
c = np.load(os.path.join(Ld, 'canopy.npy')).astype(np.float64)
RES = P['grid']['res']
nr, nc = h.shape
R_EFF = 6371000 / (1 - 0.13)


def sample(surf, x, y):
    fc = np.clip(x / RES, 0, nc - 1.001); fr = np.clip(nr - 1 - y / RES, 0, nr - 1.001)
    c0, r0 = fc.astype(int), fr.astype(int); dc, dr = fc - c0, fr - r0
    return (surf[r0, c0] * (1 - dc) * (1 - dr) + surf[r0, c0 + 1] * dc * (1 - dr)
            + surf[r0 + 1, c0] * (1 - dc) * dr + surf[r0 + 1, c0 + 1] * dc * dr)


def visible(surf, ox, oy, tx, ty, eye=1.7, tgt_h=0.0, clear_r=25.0):
    d = np.hypot(tx - ox, ty - oy)
    n = max(int(d / 5), 2)
    t = np.linspace(0, 1, n + 1)[1:-1]
    xs, ys = ox + t * (tx - ox), oy + t * (ty - oy)
    s = sample(surf, xs, ys)
    dist = t * d
    # the observer stands in a small clearing; ignore canopy right at the eye
    if surf is not h:
        near = dist < clear_r
        s[near] = sample(h, xs[near], ys[near])
    z0 = sample(h, np.array([ox]), np.array([oy]))[0] + eye
    z1 = sample(h, np.array([tx]), np.array([ty]))[0] + tgt_h
    line = z0 + t * (z1 - z0)
    drop = dist * (d - dist) / (2 * R_EFF)  # curvature bulge between the two ends
    return bool(np.all(s + drop < line)), float(np.max(s + drop - line))


fire = [dict(hs, i=i) for i, hs in enumerate(P['hotspots']) if hs['source'] == 'LANDSAT_NRT' and '12:17' in (hs['time_mdt'] or '')]
surfaces = {'bare earth': h, '+ canopy': h + c}
out = {'targets': len(fire), 'note': __doc__.strip().split('\n\n')[1], 'pov': {}}
for k, v in P['pov'].items():
    rec = {}
    dists = [np.hypot(f['x'] - v['x'], f['y'] - v['y']) for f in fire]
    rec['dist_m'] = [round(min(dists)), round(max(dists))]
    for sname, surf in surfaces.items():
        for th in (0.0, 3.0, 30.0):
            vis = [visible(surf, v['x'], v['y'], f['x'], f['y'], tgt_h=th)[0] for f in fire]
            rec[f'{sname} | {th:g} m'] = int(sum(vis))
            rec[f'per_pixel | {sname} | {th:g} m'] = vis
    rec['pixel_index'] = [f['i'] for f in fire]
    out['pov'][k] = rec
json.dump(out, open(os.path.join(Ld, 'sightlines.json'), 'w'), indent=1)

print(f"Landsat 8 fire pixels at 12:17 p.m.: {len(fire)}. Visible from 1.7 m eye height:")
cols = [f'{s} | {t:g} m' for s in surfaces for t in (0, 3, 30)]
print(f"{'':10s}{'dist km':>12s}  " + '  '.join(f'{c:>18s}' for c in cols))
for k, r in out['pov'].items():
    print(f"{k:10s}{r['dist_m'][0]/1000:5.1f}-{r['dist_m'][1]/1000:4.1f}  " +
          '  '.join(f'{r[c]:>18d}' for c in cols))
