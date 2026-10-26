"""Figures for the 3D fire animation, composited in 2D over the Blender frames.

Two groups, both REPRESENTATIVE (DND has not said how many soldiers were where):
  - C Company: about 30 figures (a platoon-sized slice of a ~100-150-strong
    company) in a band from Range 2 to the roadhead, the area named in Prime
    Rogue's location analysis.
  - Range 11 (the AGL range per the standing orders, as reported): twelve
    grenadiers prone on a firing line facing east, with range staff behind.

Movement is illustrative, not reconstructed: soldiers stand, kneel and walk
between nearby spots at walking pace; range staff pace behind the firing line;
the grenadiers stay down. Nothing public says what anyone did once the wind
turned, so all movement stops at 3:16 p.m. and the figures hold where they
are: the animation does not show their reaction to the fire.

At the camera's distance (3-6 km) a person is a fraction of a pixel, so figures
are drawn at a fixed screen size (labelled "not to scale"). The camera here
re-creates scene.py's camera (same path, 30 mm lens on a 36 mm sensor, look-at
with world up) so figures sit on the rendered terrain.
"""
import os, json, math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

EXAG = 3.0
T_SHIFT = 15 * 60 + 16


class Scene:
    def __init__(self, layers, sil_dir, res=(960, 540), fps=12, seconds=18.0):
        self.P = json.load(open(os.path.join(layers, 'points.json')))
        self.h = np.load(os.path.join(layers, 'height.npy')).astype(np.float64)
        self.arr = np.load(os.path.join(layers, 'arrival_min.npy'))
        self.Z0 = float(np.percentile(self.h, 1))
        self.RES = self.P['grid']['res']
        self.W, self.H = res
        self.NF = int(seconds * fps)
        c = self.P['scar_centroid']
        self.tgt0 = np.array([c['x'], c['y'], self.gz(c['x'], c['y'])])
        self.sprites = {}
        for f in os.listdir(sil_dir):
            if f.endswith('.png'):
                im = Image.open(os.path.join(sil_dir, f)).convert('RGBA')
                self.sprites[f[:-4]] = im.crop(im.getbbox())
        self.override = None   # (loc, look) from Blender's prologue metadata, when set
        self.g_shift = None    # global frame at which the clock reaches 3:16
        self.troops = self.place_cco()
        self.r11 = self.place_r11()
        for grp in (self.troops, self.r11):
            for t in grp:
                self.schedule(t)

    # ------------------------------------------------------------ geometry
    def gz(self, x, y):
        h = self.h; RES = self.RES
        fc = np.clip(x / RES, 0, h.shape[1] - 2); fr = np.clip(h.shape[0] - 1 - y / RES, 0, h.shape[0] - 2)
        c, r = int(fc), int(fr); dc, dr = fc - c, fr - r
        b = h[r:r + 2, c:c + 2]
        v = b[0, 0] * (1 - dc) * (1 - dr) + b[0, 1] * dc * (1 - dr) + b[1, 0] * (1 - dc) * dr + b[1, 1] * dc * dr
        return (v - self.Z0) * EXAG

    def grid_xy(self, lon, lat):
        from pyproj import Transformer
        g = self.P['grid']
        x, y = Transformer.from_crs('EPSG:4326', g['crs'], always_xy=True).transform(lon, lat)
        return x - g['x0'], y - g['y0']

    def camera(self, f):
        if self.override is not None:
            loc, look = (np.array(v, float) for v in self.override)
        else:
            u = f / max(self.NF - 1, 1)
            ang = math.radians(212 + 14 * u)
            R, Hc = 5600 - 600 * u, 2700 - 300 * u
            loc = self.tgt0 + np.array([R * math.sin(ang), R * math.cos(ang), Hc])
            look = self.tgt0 + np.array([0, 0, -450])
        fwd = look - loc; fwd /= np.linalg.norm(fwd)
        right = np.cross(fwd, [0, 0, 1]); right /= np.linalg.norm(right)
        return loc, fwd, right, np.cross(right, fwd)

    def project(self, f, p):
        loc, fwd, right, up = self.camera(f)
        v = np.asarray(p, float) - loc
        z = v @ fwd
        fpx = 30.0 / 36.0 * self.W  # sensor fit: width
        return (self.W / 2 + fpx * (v @ right) / z, self.H / 2 - fpx * (v @ up) / z, z)

    def check(self, meta_frames):
        errs = []
        for f, m in meta_frames.items():
            for k, (sx, sy, _) in m['screen'].items():
                if k in self.P['pov']:
                    v = self.P['pov'][k]
                    px, py, _ = self.project(int(f), (v['x'], v['y'], self.gz(v['x'], v['y'])))
                    errs.append(math.hypot(px - sx, py - sy))
        return max(errs) if errs else None

    # ------------------------------------------------------------ placement
    def place_cco(self, n=30, seed=17, spread=120.0, min_gap=28.0):
        a, b = self.P['pov']['Range 2'], self.P['pov']['Roadhead']
        rng = np.random.default_rng(seed)
        dx, dy = b['x'] - a['x'], b['y'] - a['y']; L = math.hypot(dx, dy)
        ux, uy, nx, ny = dx / L, dy / L, -dy / L, dx / L
        self.cco_axis = (a['x'], a['y'], ux, uy, nx, ny, L, spread)
        pts = []
        while len(pts) < n:  # rejection sampling keeps figures from piling up
            t = rng.uniform(-0.05, 1.05); off = rng.uniform(-spread, spread)
            x, y = a['x'] + t * dx + off * nx, a['y'] + t * dy + off * ny
            if all(math.hypot(x - px, y - py) >= min_gap for px, py in pts):
                pts.append((x, y))
        out = []
        for i, (x, y) in enumerate(pts):
            r = int(np.clip(self.h.shape[0] - 1 - y / self.RES, 0, self.h.shape[0] - 1))
            c = int(np.clip(x / self.RES, 0, self.h.shape[1] - 1))
            out.append({'role': 'cco', 'x': x, 'y': y, 'seed': 1000 + i,
                        'arrival_min': float(self.arr[r, c]) if np.isfinite(self.arr[r, c]) else None})
        return out

    def place_r11(self, lat=52.76781, lon=-110.95771):
        """Range 11 centroid (OpenStreetMap way/1240048252)."""
        cx, cy = self.grid_xy(lon, lat)
        self.r11_xy = (cx, cy)
        out = []
        for i in range(12):  # firing line, 25 m between firing points
            out.append({'role': 'gunner', 'x': cx + (6 if i % 2 else 0), 'y': cy - 137 + 25 * i, 'seed': 2000 + i})
        staff = ['standing_range_safety', 'standing_instructor', 'standing_radio', 'standing_binoculars',
                 'standing_range_safety', 'standing_clipboard']
        for i, pose in enumerate(staff):
            out.append({'role': 'staff', 'pose0': pose, 'x': cx - 45 - 25 * (i % 2), 'y': cy - 110 + 45 * i,
                        'seed': 3000 + i})
        return out

    # ------------------------------------------------------------ movement
    def schedule(self, t, horizon=1500):
        """Deterministic plan in global frames: dwell at a spot, walk to another, repeat.
        Walking speed is in screen time (3-6 m per frame at 12 fps), not the clock,
        which runs at minutes per frame early on."""
        rng = np.random.default_rng(t['seed'])
        x, y = t['x'], t['y']
        if t['role'] == 'gunner':
            t['segs'] = [(0, horizon, x, y, x, y, 'prone_launcher')]
            return
        segs = []  # (g0, g1, x0, y0, x1, y1, idle_pose or None while walking)
        g = -int(rng.integers(0, 40))  # stagger, so not everyone moves at once
        while g < horizon:
            if t['role'] == 'cco':
                idle = str(rng.choice(['standing_observer', 'kneeling_observer', 'crouched_observer'],
                                      p=[0.6, 0.25, 0.15]))
                dwell = int(rng.integers(14, 60))
            else:
                idle = t['pose0']; dwell = int(rng.integers(14, 45))
            segs.append((g, g + dwell, x, y, x, y, idle)); g += dwell
            if t['role'] == 'cco':
                if rng.random() < 0.4:
                    continue  # stays put, changes stance
                ax, ay, ux, uy, nx, ny, L, spread = self.cco_axis
                for _ in range(30):
                    tx = x + rng.uniform(-90, 90); ty = y + rng.uniform(-90, 90)
                    s = (tx - ax) * ux + (ty - ay) * uy; o = (tx - ax) * nx + (ty - ay) * ny
                    if -0.08 * L <= s <= 1.08 * L and abs(o) <= spread:
                        break
                speed = rng.uniform(4.0, 6.0)
            else:  # staff pace up and down behind the firing line
                cx, cy = self.r11_xy
                tx = t['x'] + rng.uniform(-15, 15); ty = cy + rng.uniform(-150, 150)
                speed = rng.uniform(3.0, 4.5)
            n = max(2, int(math.hypot(tx - x, ty - y) / speed))
            segs.append((g, g + n, x, y, tx, ty, None)); g += n
            x, y = tx, ty
        t['segs'] = segs

    def state(self, t, g):
        for g0, g1, x0, y0, x1, y1, idle in t['segs']:
            if g0 <= g < g1:
                q = (g - g0) / max(g1 - g0, 1)
                return x0 + (x1 - x0) * q, y0 + (y1 - y0) * q, idle is None, idle, (x1 - x0, y1 - y0)
        s = t['segs'][-1]
        return s[4], s[5], False, s[6] or 'standing_observer', (0, 0)

    # ------------------------------------------------------------ drawing
    def draw(self, im, f, g, sim_t, alpha=1.0, height_px=None, group=None):
        """Composite one group onto `im`. f = camera frame, g = global frame (for
        movement), sim_t = clock in minutes. Movement stops at the wind shift."""
        if sim_t >= T_SHIFT and self.g_shift is None:
            self.g_shift = g
        ge = self.g_shift if (self.g_shift is not None and sim_t >= T_SHIFT) else g
        S = im.width / 960
        hpx = height_px or 15 * S
        items = []
        for t in (group if group is not None else self.troops):
            x, y, walking, idle, (vx, vy) = self.state(t, ge)
            z = self.gz(x, y)
            px, py, depth = self.project(f, (x, y, z))
            if walking:  # face the way they're walking, on screen
                qx, _, _ = self.project(f, (x + vx, y + vy, z)); right = qx >= px
                pose = 'walking_equipment' if t['seed'] % 3 else 'walking_unarmed'
                if sim_t >= T_SHIFT:  # frozen mid-stride reads as running; stand them instead
                    pose = 'standing_observer'
            elif t['role'] in ('gunner', 'staff'):  # face the range (east)
                qx, _, _ = self.project(f, (x + 100, y, z)); right = qx >= px
                pose = idle
            else:
                right = (t['seed'] + ge // 45) % 2 == 0
                pose = idle
            items.append((depth, px * im.width / self.W, py * im.height / self.H,
                          f"{pose}_{'right' if right else 'left'}", t))
        for depth, x, y, key, t in sorted(items, key=lambda i: -i[0]):
            sp = self.sprites[key]
            near = 5200 / depth  # nearer figures a little larger
            if key.startswith('prone'):
                k = hpx * 1.25 * near / sp.width
            else:
                k = hpx * near * (0.72 if key.startswith(('kneeling', 'crouched')) else 1.0) / sp.height
            s = sp.resize((max(1, int(sp.width * k)), max(1, int(sp.height * k))), Image.LANCZOS)
            a = s.split()[3]  # dark outline so white figures read on char and grass
            halo = a.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
            dark = Image.new('RGBA', s.size, (10, 10, 12, 0)); dark.putalpha(halo.point(lambda v: int(v * 0.9 * alpha)))
            body = s.copy(); body.putalpha(a.point(lambda v: int(v * alpha)))
            pos = (int(x - s.width / 2), int(y - s.height))
            im.paste(dark, pos, dark); im.paste(body, pos, body)
        return [(d, x, y, t) for d, x, y, _, t in items]

    # ------------------------------------------------------------ AGL rounds
    def agl_targets(self, n=36, seed=3):
        """Illustrative impact points 1.9-2.5 km east-northeast of Range 11 (the
        working model's best-fitting start zone, at the C16's ~2 km reach)."""
        rng = np.random.default_rng(seed)
        cx, cy = self.r11_xy
        out = []
        for _ in range(n):
            b = math.radians(rng.uniform(62, 84)); r = rng.uniform(1900, 2500)
            x, y = cx + r * math.sin(b), cy + r * math.cos(b)
            out.append((x, y, self.gz(x, y)))
        return out

    def draw_agl(self, im, f, k, nk):
        """Rounds in flight from the firing line to the impact zone, prologue frame k of nk."""
        d = ImageDraw.Draw(im, 'RGBA')
        S = im.width / 960; sx, sy = im.width / self.W, im.height / self.H
        guns = [t for t in self.r11 if t['role'] == 'gunner']
        FLIGHT = 9  # frames per round in flight (illustrative, not to time)
        for j, (tx, ty, tz) in enumerate(self.agl_targets()):
            g = guns[j % len(guns)]; gz = self.gz(g['x'], g['y'])
            start = (j * 0.83) % max(nk - FLIGHT, 1)
            ph = (k - start) / FLIGHT
            pts = []
            for q in np.linspace(0, 1, 24):  # parabola, apex 150 m x3 exaggeration
                x = g['x'] + (tx - g['x']) * q; y = g['y'] + (ty - g['y']) * q
                z = gz + 3 + (tz - gz) * q + 4 * 450 * q * (1 - q)
                px, py, _ = self.project(f, (x, y, z)); pts.append((px * sx, py * sy))
            if 0 <= ph <= 1:
                d.line(pts[:max(2, int(ph * 23) + 1)], fill=(255, 235, 180, 110), width=max(1, int(1 * S)))
                i = int(ph * 23); x, y = pts[i]
                d.ellipse([x - 2 * S, y - 2 * S, x + 2 * S, y + 2 * S], fill=(255, 245, 210, 255))
            elif 1 < ph <= 1.6:  # burst at impact
                x, y = pts[-1]; r = (4 + 10 * (ph - 1)) * S; a = int(255 * (1.6 - ph) / 0.6)
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 170, 60, a))
                d.ellipse([x - r / 2, y - r / 2, x + r / 2, y + r / 2], fill=(255, 245, 220, a))

    def erase_pins(self, im, f, names=('Range 2', 'Roadhead')):
        """Paint out the rendered white marker pins next to the figures."""
        a = np.asarray(im).astype(np.float32).copy()
        Wd, Hd = im.size
        for k in names:
            v = self.P['pov'][k]; z = self.gz(v['x'], v['y'])
            x0, y0, _ = self.project(f, (v['x'], v['y'], z))
            x1, y1, _ = self.project(f, (v['x'], v['y'], z + 240))
            x0 *= Wd / self.W; x1 *= Wd / self.W; y0 *= Hd / self.H; y1 *= Hd / self.H
            hw = max(2, int(round(2 * Wd / 960)))
            for yy in range(int(min(y0, y1)) - 6, int(max(y0, y1)) + 3):
                if not 0 <= yy < Hd:
                    continue
                t = 0 if y1 == y0 else (yy - y0) / (y1 - y0)
                xc = int(round(x0 + t * (x1 - x0)))
                l, r = xc - hw - 2, xc + hw + 2
                if l < 0 or r >= Wd:
                    continue
                for xx in range(xc - hw, xc + hw + 1):
                    w = (xx - l) / (r - l)
                    a[yy, xx] = a[yy, l] * (1 - w) + a[yy, r] * w
        return Image.fromarray(a.clip(0, 255).astype(np.uint8))
