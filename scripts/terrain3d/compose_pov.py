"""Eye-level reconstruction: what someone standing at the Range 2 point and at the road
head could have seen on Oct. 17, 2026, from late morning until the fire reached them.

Two fixed cameras (scene.py 'povbase'): true scale, eye height 1.7 m, heading 300 deg
(west-northwest to north-northwest), 15 mm lens, terrain NRCan MRDEM-30 plus Meta/WRI
canopy. Stacked: Range 2 point on top, road head below, same clock.

Fire: working model v4, case v4b morning fire and its best-fitting post-front fire
(wind 315 deg, 8 km/h), via fire_field_v4.py (arrival_min.npy). Visibility in smoke at
each point follows v4's smoke model for that fire: before the front, haze at the Range 2
point from about 3:10 (about 2.7 km), the road head clear; after it, visibility under
1 km at 3:18 at both points, under 100 m at 3:20 (Range 2) and 3:23 (road head); fire at
3:20.7 and 3:24.9. Between those values visibility is interpolated (log scale).
Flame heights (2 m before the wind shift, 3-7 m after) and the smoke column are
illustrative. No people are shown. Each panel cuts to black just before the modelled
fire reaches its point.

Run: python3 compose_pov.py LAYERDIR POVBASEDIR OUT.mp4
"""
import sys, os, json, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import map_coordinates

Ld, Bd, OUT = sys.argv[1:4]
FPS = 12
LAB = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'pov_lab'); os.makedirs(LAB, exist_ok=True)
F = '/usr/share/fonts/opentype/inter/'
fb = lambda s: ImageFont.truetype(F + 'Inter-Bold.otf', int(s))
fm = lambda s: ImageFont.truetype(F + 'Inter-Medium.otf', int(s))
freg = lambda s: ImageFont.truetype(F + 'Inter-Regular.otf', int(s))
INK = (14, 16, 20); WHITE = (255, 255, 255); MUTED = (200, 205, 212)
AMBER = (255, 196, 64); BLUE = (110, 170, 255); RED = (255, 90, 60)
hm = lambda h, m=0: h * 60 + m
T_SHIFT = hm(15, 16)

P = json.load(open(os.path.join(Ld, 'points.json')))
G = P['grid']; RES = G['res']; Wm, Hm = G['w'] * RES, G['h'] * RES
H0 = np.load(os.path.join(Ld, 'height.npy')).astype(np.float64)
CAN = np.load(os.path.join(Ld, 'canopy.npy')).astype(np.float64)
Z0 = float(np.percentile(H0, 1))
arr = np.load(os.path.join(Ld, 'arrival_min.npy')).astype(np.float64)
sev = np.load(os.path.join(Ld, 'severity.npy'))


def gz(x, y):
    c = np.clip(np.asarray(x) / RES, 0, H0.shape[1] - 1.001); r = np.clip(H0.shape[0] - 1 - np.asarray(y) / RES, 0, H0.shape[0] - 1.001)
    return map_coordinates(H0, [r, c], order=1) - Z0


def lin(v):
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


# ---------------------------------------------------------------- visibility (v4 smoke model, best-fit fire)
VIS = {'range2': [(0, 20000), (hm(15, 5), 20000), (hm(15, 10), 2700), (hm(15, 16), 2700), (hm(15, 18), 1000),
                  (hm(15, 20), 100), (hm(15, 20.7), 30)],
       'roadhead': [(0, 20000), (hm(15, 16), 20000), (hm(15, 18), 1000), (hm(15, 23), 100), (hm(15, 24.9), 30)]}
ARRIVE = {'range2': hm(15, 20.7), 'roadhead': hm(15, 24.9)}
NAME = {'range2': 'the Range 2 point', 'roadhead': 'the road head'}
EDGE316 = {'range2': '590 m', 'roadhead': '1.1 km'}


def visibility(slug, t):
    ts, vs = zip(*VIS[slug]); return float(np.exp(np.interp(t, ts, np.log(vs))))


# ---------------------------------------------------------------- panels (static cameras)
class Panel:
    def __init__(self, slug):
        self.slug = slug
        cam = json.load(open(os.path.join(Bd, f'povcam_{slug}.json')))
        self.loc = np.array(cam['loc']); self.W, self.H = cam['res']
        hd = math.radians(cam['heading'])
        look = self.loc + np.array([math.sin(hd), math.cos(hd), 0]) * 1000 + np.array([0, 0, 35])
        f = look - self.loc; self.fwd = f / np.linalg.norm(f)
        r = np.cross(self.fwd, [0, 0, 1]); self.right = r / np.linalg.norm(r); self.up = np.cross(self.right, self.fwd)
        self.fpx = cam['lens'] / 36.0 * self.W
        self.base = np.asarray(Image.open(os.path.join(Bd, f'povbase_{slug}.png')).convert('RGB')).astype(np.float32) / 255
        xyz = cv2.imread(os.path.join(Bd, f'povxyz_{slug}.png'), cv2.IMREAD_UNCHANGED).astype(np.float64) / 65535
        self.ground = xyz[..., 3] > 0.5
        x = lin(xyz[..., 2]) * Wm; y = lin(xyz[..., 1]) * Hm; z = lin(xyz[..., 0]) * 200
        self.Ds = np.where(self.ground, np.sqrt((x - self.loc[0]) ** 2 + (y - self.loc[1]) ** 2 + (z - self.loc[2]) ** 2), 1e9)
        col = x / RES - 0.5; row = (G['h'] - 1) - (y / RES - 0.5)
        A = map_coordinates(np.where(np.isfinite(arr), arr, 1e5), [row, col], order=1, mode='nearest')
        self.A = np.where(self.ground & (A < 5e4), A, np.nan)
        self.SV = map_coordinates(sev, [row, col], order=1, mode='nearest')
        # flame cells: 10 m cells within 4 km, in front of the camera
        rr, cc = np.nonzero(np.isfinite(arr))
        X = (cc + 0.5) * RES; Y = (G['h'] - 1 - rr + 0.5) * RES
        d = np.hypot(X - self.loc[0], Y - self.loc[1]); keep = (d < 4000) & (d > 5)
        X, Y, T = X[keep], Y[keep], arr[rr[keep], cc[keep]]
        Z = gz(X, Y)
        u, v, dep = self.project(np.column_stack([X, Y, Z]))
        vis = (dep > 1) & (u > -20) & (u < self.W + 20)
        self.cells = dict(X=X[vis], Y=Y[vis], Z=Z[vis], T=T[vis], u=u[vis], v=v[vis], d=dep[vis])
        rng = np.random.default_rng(11 + len(slug)); n = len(self.cells['X'])
        self.cells['ph'] = rng.uniform(0, 2 * math.pi, n); self.cells['emit'] = rng.random(n)

    def project(self, pts):
        V = np.atleast_2d(pts) - self.loc
        z = V @ self.fwd
        return self.W / 2 + self.fpx * (V @ self.right) / z, self.H / 2 - self.fpx * (V @ self.up) / z, z

    def bearing_x(self, b):
        p = self.loc + np.array([math.sin(math.radians(b)), math.cos(math.radians(b)), 0]) * 1000
        u, v, z = self.project(p); return float(u[0]) if z[0] > 0 else None

    def frame(self, t, g):
        img = self.base.copy(); A = self.A
        dt = t - A; burning = np.nan_to_num(dt, nan=-1) >= 0
        tau = np.where(A < T_SHIFT, 12.0, 0.6)
        glow = np.where(burning, np.exp(-np.clip(np.nan_to_num(dt), 0, None) / tau), 0) ** 2
        char = np.where(burning, np.clip(np.nan_to_num(dt) / 1.5, 0, 1), 0) * (0.6 + 0.4 * self.SV)
        img = img * (1 - char[..., None]) + np.array([0.05, 0.04, 0.035], np.float32) * char[..., None]
        img = img + glow[..., None] * np.array([0.9, 0.3, 0.05], np.float32) * 0.8
        # --- smoke fog from v4's visibility at this point
        vis = visibility(self.slug, t)
        dens = float(np.clip((1500 - vis) / 1400, 0, 1))
        fogc = np.array([0.72, 0.70, 0.67]) * (1 - dens) + np.array([0.30, 0.27, 0.24]) * dens
        fground = 1 - np.exp(-3 * np.minimum(self.Ds, 3 * vis) / vis)
        fsky = float(np.clip((6000 - vis) / 5000, 0, 1)) * 0.95
        f = np.where(self.ground, fground, fsky)[..., None].astype(np.float32)
        img = img * (1 - f) + fogc.astype(np.float32) * f
        # --- flames (3D columns, hidden behind terrain and canopy), and the smoke column
        c = self.cells
        win = np.where(c['T'] < T_SHIFT, 6.0, 0.45)
        dtc = t - c['T']; act = (dtc >= 0) & (dtc <= win)
        fl = np.zeros_like(img)
        idx = np.nonzero(act)[0]
        for j in idx:
            d = c['d'][j]; pre = c['T'][j] < T_SHIFT
            h = (2.0 if pre else 3.0 + 4.0 * (1 - dtc[j] / win[j])) * (0.75 + 0.25 * math.sin(g * 1.9 + c['ph'][j]))
            u0, vb = c['u'][j], c['v'][j]
            ut, vt, _ = self.project(np.array([c['X'][j], c['Y'][j], c['Z'][j] + h]))
            vt = float(vt[0]); hpx = vb - vt
            wpx = max(1.0, 10.0 * self.fpx / d)
            x0, x1 = int(max(0, u0 - wpx / 2)), int(min(self.W - 1, u0 + wpx / 2))
            y0, y1 = int(max(0, vt)), int(min(self.H - 1, vb))
            if x1 < x0 or y1 < y0:
                continue
            u0 = u0 + (c['ph'][j] / math.pi - 1) * wpx * 0.6   # break up the 10 m grid
            x0, x1 = int(max(0, u0 - wpx / 2)), int(min(self.W - 1, u0 + wpx / 2))
            if x1 < x0:
                continue
            blk = self.Ds[y0:y1 + 1, x0:x1 + 1]
            ok = blk >= d - 12  # in front of whatever surface is behind it
            if not ok.any():
                continue
            ys = np.arange(y0, y1 + 1)[:, None]; xs = np.arange(x0, x1 + 1)[None, :]
            q = np.clip((vb - ys) / max(hpx, 1), 0, 1)   # 0 at base, 1 at tip
            # tongue shape: narrows toward the tip, with a little sway
            sway = math.sin(g * 1.3 + c['ph'][j] * 3) * 0.15 * wpx * q
            half = (wpx / 2) * (1 - q) ** 0.8 + 0.5
            shape = (np.abs(xs - (u0 + sway)) <= half).astype(np.float32)
            col = (np.stack([1.0 - 0.1 * q, 0.55 - 0.35 * q, 0.15 - 0.12 * q], -1) * (1 - 0.5 * q)[..., None])
            att = math.exp(-3 * d / vis) ** 0.5
            fl[y0:y1 + 1, x0:x1 + 1] = np.maximum(fl[y0:y1 + 1, x0:x1 + 1], col * (ok * shape)[..., None] * att)
        if idx.size:
            fl = fl + cv2.GaussianBlur(fl, (0, 0), 6) * 0.9
        img = img + fl
        im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
        # smoke column from the fire (illustrative): puffs rise and drift downwind, drawn at
        # quarter resolution and blurred so they read as a plume, fading into the smoke haze
        q4 = 4
        acc = np.zeros((self.H // q4, self.W // q4), np.float32)
        wind_to = math.radians((235 if t < T_SHIFT else 315) + 180); wx, wy = math.sin(wind_to), math.cos(wind_to)
        em = idx[c['emit'][idx] < 0.15] if t < T_SHIFT else idx[:0]  # after the shift, smoke is the haze (v4 visibility)
        for j in em[:500]:
            for k in range(0, 30):
                age = k + (g % 2) * 0.5
                x = c['X'][j] + wx * 30 * age; y = c['Y'][j] + wy * 30 * age; z = c['Z'][j] + 8 + 22 * age
                u, v, dz = self.project(np.array([x, y, z]))
                if dz[0] <= 30:
                    continue
                u, v, dz = float(u[0]), float(v[0]), float(dz[0])
                ui, vi = int(u), int(v)
                if 0 <= ui < self.W and 0 <= vi < self.H and self.Ds[vi, ui] < dz - 20:
                    continue  # behind terrain
                r = min(max(1.5, (6 + 2.5 * age) * self.fpx / dz), 140) / q4
                cv2.circle(acc, (int(u / q4), int(v / q4)), max(1, int(r)), float(0.22 * (1 - age / 30)), -1, lineType=cv2.LINE_AA)
        acc = cv2.GaussianBlur(np.minimum(acc, 1.0), (0, 0), 5)
        acc = cv2.resize(acc, (self.W, self.H), interpolation=cv2.INTER_LINEAR)
        acc = np.clip(acc * 2.2, 0, 0.85) * (1 - fsky)  # hidden once the haze itself is thick
        arr_im = np.asarray(im.convert('RGB')).astype(np.float32) / 255
        smokec = np.array([0.62, 0.59, 0.56], np.float32)
        arr_im = arr_im * (1 - acc[..., None]) + smokec * acc[..., None]
        im = Image.fromarray((np.clip(arr_im, 0, 1) * 255).astype(np.uint8))
        return im, vis


PANELS = [Panel('range2'), Panel('roadhead')]
for p in PANELS:
    print(p.slug, 'flame cells in view', len(p.cells['X']), 'ground px', int(p.ground.sum()))

# ---------------------------------------------------------------- timeline
SEGS = [(2.5, hm(11, 30), hm(12, 17), None), (2.5, hm(12, 17), hm(12, 17), 'landsat'),
        (3.0, hm(12, 17), hm(14, 14), None), (3.0, hm(14, 14), hm(14, 14), 'warning'),
        (2.5, hm(14, 14), hm(15, 10), None), (3.0, hm(15, 10), hm(15, 16), 'haze'),
        (3.5, hm(15, 16), hm(15, 16), 'gust'), (16.0, hm(15, 16), hm(15, 21), 'run'),
        (10.0, hm(15, 21), hm(15, 26), 'run'), (6.0, hm(15, 26), hm(15, 26), 'end')]
FR = []
for dur, t0, t1, card in SEGS:
    n = int(round(dur * FPS))
    for k in range(n):
        FR.append((t0 + (t1 - t0) * k / n, card))


def clock(t):
    h, m = int(t // 60), int(t % 60); s = int((t * 60) % 60)
    base = f'{h - 12 if h > 12 else h}:{m:02d}'
    return base + (f':{s:02d}' if hm(15, 16) < t < hm(15, 26) else '') + (' p.m.' if h >= 12 else ' a.m.')


def caption(t, card):
    if card == 'landsat':
        return ('Landsat 8 photographs the fire, about 1 km to the west-northwest',
                'In line of sight for a 3 m flame: 7 of its 59 fire pixels from Range 2, none from the road head. '
                'Smoke above 30 m: 35 of 59 from both.', AMBER)
    if card == 'warning':
        return ('Environment Canada warns of gusts up to 100 km/h', 'The wind is from the southwest, carrying the smoke away to the northeast.', RED)
    if card == 'haze':
        return ('Smoke begins to drift over Range 2', 'v4 smoke model: haze at the Range 2 point from about 3:10 (visibility about 2.7 km); '
                'the road head still clear.', AMBER)
    if card == 'gust':
        return ('An 82 km/h gust. The wind turns northwest', 'The fire\'s edge is about 590 m from the Range 2 point and 1.1 km from the road head.', RED)
    if card == 'run':
        return ('The fire runs southeast, toward both points',
                'v4 smoke model: visibility under 1 km by 3:18; under 100 m by 3:20 at Range 2 and 3:23 at the road head.', RED)
    if t < hm(12, 17):
        return ('The fire has been burning since about 5 a.m. (modelled), about 1 km to the west-northwest',
                'From here most of the flames are hidden by the rise; the smoke column is in plain view.', AMBER)
    return ('The fire creeps north; the wind rises', 'Spread between satellite passes is modelled (working model v4).', AMBER)


W, PH = 1920, 540
ONLY = os.environ.get('ONLY'); sel = set(int(v) for v in ONLY.split(',')) if ONLY else None
for i, (t, card) in enumerate(FR):
    if sel is not None and i not in sel:
        continue
    canvas = Image.new('RGB', (W, 2 * PH), INK)
    if card != 'end':
        for k, p in enumerate(PANELS):
            im, vis = p.frame(t, i)
            ARR = ARRIVE[p.slug]
            fade = float(np.clip((t - (ARR - 0.45)) / 0.3, 0, 1))
            if fade > 0:
                im = Image.blend(im, Image.new('RGB', im.size, (0, 0, 0)), fade)
            d = ImageDraw.Draw(im)
            # bearings along the bottom
            for b, lab in ((270, 'W'), (292.5, 'WNW'), (315, 'NW'), (337.5, 'NNW')):
                x = p.bearing_x(b)
                if x is not None and 0 < x < W:
                    d.line([x, PH - 30, x, PH - 22], fill=MUTED, width=2)
                    d.text((x, PH - 18), lab, font=fm(14), fill=MUTED, anchor='mt', stroke_width=2, stroke_fill=INK)
            top = 96 if k == 0 else 12
            d.text((20, top), f'From {NAME[p.slug]}', font=fb(22), fill=WHITE, stroke_width=3, stroke_fill=INK)
            d.text((20, top + 28), f'eye height 1.7 m · visibility {"over 20 km" if vis >= 19000 else f"about {vis:,.0f} m"}',
                   font=fm(15), fill=MUTED, stroke_width=3, stroke_fill=INK)
            if fade > 0.6:
                d.text((W / 2, PH / 2 - 14), f'Modelled: the fire reached {NAME[p.slug]} at about {clock(ARR)[:-8] if False else ("3:21" if p.slug == "range2" else "3:25")} p.m.',
                       font=fb(26), fill=WHITE, anchor='mm')
                d.text((W / 2, PH / 2 + 22), 'Working model v4, best-fitting fire. A model, not an observation.', font=freg(17), fill=MUTED, anchor='mm')
            canvas.paste(im, (0, k * PH))
        d = ImageDraw.Draw(canvas)
        d.line([0, PH, W, PH], fill=INK, width=4)
        hdr = Image.new('RGBA', (W, 84), (*INK, 215)); canvas.paste(hdr, (0, 0), hdr); d = ImageDraw.Draw(canvas)
        cap, sub, col = caption(t, card)
        d.text((22, 14), clock(t), font=fb(40), fill=col)
        cx = 22 + d.textlength(clock(t), font=fb(40)) + 24
        d.text((cx, 16), cap, font=fb(22), fill=WHITE); d.text((cx, 50), sub, font=freg(16), fill=MUTED)
        ft = Image.new('RGBA', (W, 30), (*INK, 215)); canvas.paste(ft, (0, 2 * PH - 30), ft); d = ImageDraw.Draw(canvas)
        d.text((22, 2 * PH - 23), 'True scale · terrain NRCan MRDEM-30 (30 m) + Meta/WRI canopy · fire and smoke visibility: working model v4, best-fitting fire (modelled) · '
               'flame height and smoke column illustrative · clock not to scale · Prime Rogue Inc.', font=freg(14), fill=MUTED)
    else:
        d = ImageDraw.Draw(canvas)
        lines = [('What could be seen from Range 2 and the road head', fb(34), WHITE),
                 ('', fb(10), WHITE),
                 ('Through the morning and early afternoon, most of the flames were hidden by the ground. The smoke column was in view.', freg(22), MUTED),
                 ('At 3:16 p.m. the gust turned the fire toward both points: its edge was about 590 m from Range 2 and 1.1 km from the road head.', freg(22), MUTED),
                 ('On the model, smoke cut visibility below 1 km at both points by 3:18, two minutes after the gust, and below 100 m', freg(22), MUTED),
                 ('about a minute (Range 2) or two minutes (road head) before the fire arrived, at about 3:21 and 3:25 p.m.', freg(22), MUTED),
                 ('', fb(10), WHITE),
                 ('Modelled, not observed. DND has not said where C Company was. Working model v4 · data and code: github.com/primerogueinc/cfb-wainwright-fire-archive', freg(17), MUTED)]
        y = 300
        for txt, fnt, col in lines:
            d.text((W / 2, y), txt, font=fnt, fill=col, anchor='mt'); y += 44 if txt else 18
    canvas.save(os.path.join(LAB, f'{i:04d}.png'))
    if i % 60 == 0:
        print('frame', i, clock(t), flush=True)

if sel is not None:
    sys.exit(0)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(LAB, '%04d.png'),
                '-vf', 'minterpolate=fps=24:mi_mode=blend', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], check=True)
print('wrote', OUT, len(FR), 'frames')
