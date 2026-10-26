"""Flames and smoke for the 3D fire animation, composited in 2D.

The Blender render darkens burned ground and gives the front a faint glow, but
at 3-6 km a slow morning fire reads as a dark patch, not a fire. This layer
draws what is burning at each moment from the same modelled arrival times:

  - flames: every 20 m cell whose modelled arrival is within the last few
    minutes (40 min before the wind shift, when the fire crept at ~0.4 km/h;
    4 min in the run), drawn as additive glow that flickers;
  - smoke: puffs rising from those cells and drifting downwind (from the
    southwest before 3:16 p.m., the northwest after), ILLUSTRATIVE: v4's smoke
    model is not used here, and puff speed is in screen time, not the clock.

Projection is shared with troops.Scene, so flames sit on the rendered terrain.
"""
import math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageChops

T_SHIFT = 15 * 60 + 16


class FireFX:
    def __init__(self, scene, arrival_min, step=2, seed=5):
        self.S = scene
        a = np.asarray(arrival_min, np.float64)[::step, ::step]
        rr, cc = np.nonzero(np.isfinite(a))
        RES = scene.RES * step; H = a.shape[0]
        self.cells = np.column_stack([(cc + 0.5) * RES, (H - 1 - rr + 0.5) * RES, a[rr, cc]])
        rng = np.random.default_rng(seed)
        self.phase = rng.uniform(0, 2 * math.pi, len(self.cells))
        self.jit = rng.uniform(-0.5, 0.5, (len(self.cells), 2)) * RES
        self.z = np.array([scene.gz(x, y) for x, y, _ in self.cells])
        self.emit = rng.random(len(self.cells))  # which cells give off smoke puffs

    def _project_many(self, f, X, Y, Z):
        loc, fwd, right, up = self.S.camera(f)
        V = np.column_stack([X, Y, Z]) - loc
        z = V @ fwd
        fpx = 30.0 / 36.0 * self.S.W
        return self.S.W / 2 + fpx * (V @ right) / z, self.S.H / 2 - fpx * (V @ up) / z, z

    def draw(self, im, f, g, t):
        """Composite flames and smoke for camera frame f, global frame g, clock t (min)."""
        W, H = im.size; sx, sy = W / self.S.W, H / self.S.H; Sc = W / 960
        dt = t - self.cells[:, 2]
        win = np.where(self.cells[:, 2] < T_SHIFT, 40.0, 4.0)
        act = (dt >= 0) & (dt <= win)
        if not act.any():
            return im
        idx = np.nonzero(act)[0]
        inten = np.exp(-dt[idx] / (win[idx] * 0.45))
        inten *= 0.75 + 0.25 * np.sin(g * 1.7 + self.phase[idx])  # flicker
        X = self.cells[idx, 0] + self.jit[idx, 0]; Y = self.cells[idx, 1] + self.jit[idx, 1]
        Z = self.z[idx] + 2
        px, py, depth = self._project_many(f, X, Y, Z)
        ok = (depth > 0) & (px > -50) & (px < self.S.W + 50) & (py > -50) & (py < self.S.H + 50)

        # --- smoke (drawn first, under the flames) -------------------------
        wind_to = math.radians((235 if t < T_SHIFT else 306) + 180)
        wx, wy = math.sin(wind_to), math.cos(wind_to)
        smoke = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(smoke)
        AGE = 18  # frames a puff lives
        drift = 28.0 if t < T_SHIFT else 60.0  # metres per frame downwind (screen time)
        rise = 20.0                            # scene units per frame (height is x3)
        em = idx[(self.emit[idx] < (0.10 if t < T_SHIFT else 0.03))]
        for j in em:
            x0, y0, z0 = self.cells[j, 0], self.cells[j, 1], self.z[j]
            for k in range(0, AGE, 3):
                age = (g + int(self.phase[j] * 3)) % 3 + k
                xs = x0 + wx * drift * age; ys = y0 + wy * drift * age; zs = z0 + 10 + rise * age
                qx, qy, qd = self.S.project(f, (xs, ys, zs))
                if qd <= 0:
                    continue
                r = (3 + 0.9 * age) * Sc * 5200 / qd
                a = int(115 * (1 - age / AGE))
                X_, Y_ = qx * sx, qy * sy
                sd.ellipse([X_ - r, Y_ - r, X_ + r, Y_ + r], fill=(205, 200, 195, a))
        smoke = smoke.filter(ImageFilter.GaussianBlur(3 * Sc))
        im = im.convert('RGBA'); im.alpha_composite(smoke)

        # --- flames (additive glow) ----------------------------------------
        glow = Image.new('RGB', (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow)
        core = Image.new('RGB', (W, H), (0, 0, 0)); cd = ImageDraw.Draw(core)
        for x, y, d, v in zip(px[ok] * sx, py[ok] * sy, depth[ok], inten[ok]):
            r = max(1.2, 2.6 * Sc * 5200 / d)
            c = (int(255 * v), int(110 * v), int(20 * v))
            gd.ellipse([x - 2 * r, y - 2 * r, x + 2 * r, y + 2 * r], fill=c)
            cc_ = (int(255 * v), int(215 * v), int(140 * v))
            cd.ellipse([x - r * 0.6, y - r * 1.2, x + r * 0.6, y + r * 0.2], fill=cc_)
        glow = glow.filter(ImageFilter.GaussianBlur(4 * Sc))
        core = core.filter(ImageFilter.GaussianBlur(0.8 * Sc))
        base = im.convert('RGB')
        base = ImageChops.add(base, glow)
        base = ImageChops.add(base, core)
        return base
