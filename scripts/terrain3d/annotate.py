"""Viewshed maps and labelled POV frames for the CFB Wainwright terrain scene.

  viewshed_<pov>.png   map of the ground a 3 m flame would be visible on, from
                       the POV at 1.7 m eye height (bare earth vs + canopy)
  pov_<pov>_lab.jpg    the true-scale render with the 12:17 fire pixels marked
                       (filled = a 3 m flame there is in line of sight on bare
                       earth; open = hidden by terrain), header and source notes
  pov_sheet.jpg        all four labelled POVs with their viewshed maps

Run: python3 annotate.py LAYERDIR RENDERDIR
"""
import sys, os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

Ld, Rd = sys.argv[1], sys.argv[2]
P = json.load(open(os.path.join(Ld, 'points.json')))
S = json.load(open(os.path.join(Ld, 'sightlines.json')))
M = json.load(open(os.path.join(Rd, 'pov_meta.json')))
h = np.load(os.path.join(Ld, 'height.npy')).astype(np.float32)
c = np.load(os.path.join(Ld, 'canopy.npy')).astype(np.float32)
RES = P['grid']['res']
F = '/usr/share/fonts/opentype/inter/'
font = lambda w, s: ImageFont.truetype(F + {'b': 'Inter-Bold.otf', 'r': 'Inter-Regular.otf',
                                            'm': 'Inter-Medium.otf'}[w], s)
ORANGE = (255, 120, 30); WHITE = (255, 255, 255); INK = (20, 22, 26)
COMPASS = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
compass = lambda b: COMPASS[int((b + 11.25) // 22.5) % 16]


def viewshed(ox, oy, surf, step=2, eye=1.7, tgt=3.0, clear=25.0):
    """Visible cells (target `tgt` m above bare earth) on a grid coarsened by `step`."""
    R_EFF = 6371000 / (1 - 0.13)
    hs, ss = h[::step, ::step], surf[::step, ::step]
    nr, nc = hs.shape
    cell = RES * step
    gy, gx = np.mgrid[0:nr, 0:nc]
    X = (gx + 0.5) * cell; Y = (nr - 1 - gy + 0.5) * cell
    oc, orr = int(ox / cell), int(nr - 1 - oy / cell)
    z0 = hs[orr, oc] + eye
    vis = np.zeros((nr, nc), bool)
    flatX, flatY = X.ravel(), Y.ravel()
    zt = hs.ravel() + tgt
    D = np.hypot(flatX - ox, flatY - oy)
    N = 160
    t = (np.arange(1, N) / N)[None, :]
    out = np.zeros(D.size, bool)
    for s0 in range(0, D.size, 20000):
        sl = slice(s0, s0 + 20000)
        xs = ox + t * (flatX[sl, None] - ox); ys = oy + t * (flatY[sl, None] - oy)
        cc = np.clip((xs / cell).astype(int), 0, nc - 1)
        rr = np.clip((nr - 1 - ys / cell).astype(int), 0, nr - 1)
        dist = t * D[sl, None]
        surf_s = np.where(dist < clear, hs[rr, cc], ss[rr, cc])
        line = z0 + t * (zt[sl, None] - z0)
        drop = dist * (D[sl, None] - dist) / (2 * R_EFF)
        out[sl] = np.all(surf_s + drop < line, axis=1)
    return out.reshape(nr, nc)


tc = Image.open(os.path.join(Ld, 'pre_tc.png')).convert('RGB')
fire = [hs for hs in P['hotspots'] if hs['source'] == 'LANDSAT_NRT' and '12:17' in (hs['time_mdt'] or '')]
step = 2
maps, labs = {}, {}
for k, v in P['pov'].items():
    slug = k.lower().replace(' ', '')
    vb = viewshed(v['x'], v['y'], h, step)
    vc = viewshed(v['x'], v['y'], h + c, step)
    # --- map: grey out what is hidden; tint what's visible only on bare earth
    base = tc.resize((vb.shape[1] * 2, vb.shape[0] * 2), Image.LANCZOS)
    arr = np.asarray(base).astype(np.float32) / 255
    vbb = np.kron(vb, np.ones((2, 2), bool)); vcc = np.kron(vc, np.ones((2, 2), bool))
    grey = arr.mean(axis=2, keepdims=True) * 0.45
    out = np.where(vcc[..., None], arr, np.where(vbb[..., None], arr * 0.55 + np.array([0.0, 0.25, 0.45]) * 0.45, grey))
    im = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    px = lambda x, y: (x / (RES * step) * 2, (vb.shape[0] - y / (RES * step)) * 2)
    for ring in P['scar_outline']:
        d.line([px(x, y) for x, y in ring], fill=(230, 60, 50), width=2)
    for f in fire:
        X, Y = px(f['x'], f['y']); d.ellipse([X - 3, Y - 3, X + 3, Y + 3], fill=ORANGE)
    X, Y = px(v['x'], v['y'])
    nf = P['noon_fire']; FX, FY = px(nf['x'], nf['y'])
    d.line([X, Y, FX, FY], fill=WHITE, width=1)
    d.regular_polygon((X, Y, 11), 5, fill=WHITE, outline=INK)
    d.text((X + 14, Y - 10), k, font=font('b', 20), fill=WHITE, stroke_width=3, stroke_fill=INK)
    # crop to a square around POV and fire line
    xs = [X, FX] + [px(f['x'], f['y'])[0] for f in fire]; ys = [Y, FY] + [px(f['x'], f['y'])[1] for f in fire]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    half = max(max(xs) - min(xs), max(ys) - min(ys)) / 2 + 120
    im = im.crop((int(cx - half), int(cy - half), int(cx + half), int(cy + half))).resize((900, 900), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    sb = 1000 / (RES * step) * 2 * 900 / (2 * half)  # 1 km in pixels
    d.rectangle([20, 845, 20 + sb, 853], fill=WHITE, outline=INK)
    d.text((20, 815), '1 km', font=font('m', 20), fill=WHITE, stroke_width=3, stroke_fill=INK)
    d.text((880, 20), 'N ↑', font=font('b', 24), fill=WHITE, stroke_width=3, stroke_fill=INK, anchor='ra')
    # legend: what a 3 m flame at each spot would look like from the POV
    lg = Image.new('RGBA', (560, 132), (12, 14, 18, 215)); im.paste(lg, (320, 752), lg)
    d = ImageDraw.Draw(im)
    d.text((336, 762), f'Where a 3 m flame would be in sight from {k}', font=font('b', 18), fill=WHITE)
    for j, (sw, txt) in enumerate([((150, 120, 80), 'natural colour: in sight, even with trees'),
                                   ((70, 120, 170), 'blue: in sight only if trees are ignored'),
                                   ((40, 40, 40), 'dark: hidden by terrain')]):
        d.rectangle([336, 794 + j * 28, 356, 810 + j * 28], fill=sw, outline=(200, 200, 200))
        d.text((366, 791 + j * 28), txt, font=font('r', 17), fill=WHITE)
    d.ellipse([20, 770, 30, 780], fill=ORANGE)
    d.text((36, 764), 'fire pixel, 12:17 p.m.', font=font('r', 17), fill=WHITE, stroke_width=3, stroke_fill=INK)
    im.save(os.path.join(Rd, f'viewshed_{slug}.png'))
    maps[k] = im
    s = S['pov'][k]
    print(f"{k}: 3 m target visible over {vb.mean()*100:.0f}% of scene (bare earth), {vc.mean()*100:.0f}% (+ canopy)")

    # --- labelled POV
    pov = Image.open(os.path.join(Rd, f'pov_{slug}.png')).convert('RGB')
    W, H = pov.size
    d = ImageDraw.Draw(pov)
    m = M['frames'][k]
    vis3 = dict(zip(s['pixel_index'], s['per_pixel | bare earth | 3 m']))
    shown = 0
    for hs in m['hotspots_screen']:
        if hs['depth'] <= 0 or not (0 <= hs['x'] <= W):
            continue
        shown += 1
        x = hs['x']; yb = hs['y_base']
        y = yb - 26
        if vis3.get(hs['i']):
            d.polygon([(x - 7, y - 14), (x + 7, y - 14), (x, y)], fill=ORANGE, outline=INK)
        else:
            d.polygon([(x - 7, y - 14), (x + 7, y - 14), (x, y)], outline=ORANGE, width=2)
    bearing, dist = m['bearing_to_noon_fire'], m['dist_to_noon_fire_m']
    # header band
    band = Image.new('RGBA', (W, 150), (12, 14, 18, 210)); pov.paste(band, (0, 0), band)
    d = ImageDraw.Draw(pov)
    d.text((48, 28), f'From {k}, looking {compass(bearing)} ({bearing:.0f}°) toward the fire line Landsat recorded at 12:17 p.m.',
           font=font('b', 34), fill=WHITE)
    d.text((48, 82), f"Eye height 1.7 m · fire pixels {s['dist_m'][0]/1000:.1f}–{s['dist_m'][1]/1000:.1f} km away · "
           f"a 3 m flame is in line of sight at {s['bare earth | 3 m']} of 59 pixels on bare earth, "
           f"{s['+ canopy | 3 m']} with tree cover · 30 m smoke at {s['bare earth | 30 m']} of 59",
           font=font('r', 25), fill=(220, 224, 230))
    # legend + sources
    fb = Image.new('RGBA', (W, 96), (12, 14, 18, 200)); pov.paste(fb, (0, H - 96), fb)
    d = ImageDraw.Draw(pov)
    d.polygon([(48, H - 70), (62, H - 70), (55, H - 56)], fill=ORANGE, outline=INK)
    d.text((72, H - 76), 'in line of sight', font=font('m', 22), fill=WHITE)
    d.polygon([(258, H - 70), (272, H - 70), (265, H - 56)], outline=ORANGE, width=2)
    d.text((282, H - 76), f'hidden by terrain   ({shown} of 59 pixels fall inside this frame)', font=font('m', 22), fill=WHITE)
    d.text((48, H - 40), 'True scale. Terrain: NRCan MRDEM-30 (30 m, small rises not resolved). Trees: Meta/WRI canopy height. '
           'Imagery: Copernicus Sentinel-2, Oct 4. Smoke not modelled. Prime Rogue Inc., working model v4',
           font=font('r', 18), fill=(190, 195, 205))
    pov.save(os.path.join(Rd, f'pov_{slug}_lab.jpg'), quality=92)
    labs[k] = pov

# contact sheet: POV left, viewshed right, one row per point
rows = []
for k in P['pov']:
    p = labs[k].resize((1600, 900), Image.LANCZOS); mp = maps[k].resize((900, 900), Image.LANCZOS)
    r = Image.new('RGB', (2500, 900), INK); r.paste(p, (0, 0)); r.paste(mp, (1600, 0)); rows.append(r)
sheet = Image.new('RGB', (2500, 900 * len(rows) + 20 * (len(rows) - 1)), INK)
for i, r in enumerate(rows):
    sheet.paste(r, (0, i * 920))
sheet.save(os.path.join(Rd, 'pov_sheet.jpg'), quality=88)
