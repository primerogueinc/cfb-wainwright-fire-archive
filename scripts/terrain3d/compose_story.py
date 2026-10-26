"""Composite the full-timeline 3D reconstruction from the story renders.

Inputs: LAYERDIR (points, arrival field, scar, severity, story.json), BASEDIR
(base_<key>.png lit terrain + xy_<key>.png map-position pass from scene.py
'base' mode), SPRITEDIR (silhouettes), POSTFRONT_DIR (v4 post-front grids for
the escape scenarios), SWOB csv (CZWN hourly wind).

Per frame: burned ground and the glowing edge are painted from the modelled
arrival time under each pixel; night is graded from the sun's elevation;
flames, smoke, figures, scenario runners, satellite detections and text are
drawn on top.

Escape scenarios follow v4's part 4 method on the best-fitting post-front fire
(wind fixed from 315 deg, 8 km/h, steady): jogging in kit (8 km/h) on a straight
line from the Range 2 point; safe = ground the fire never reaches (outside the
burn + 150 m) or ground that burned at least 5 minutes earlier. Odds across all
30 modelled fires (v4, best route): 80% leaving at the gust, 43% three minutes
later, 10% seven minutes later.

Run: python3 compose_story.py LAYERDIR BASEDIR SPRITEDIR POSTFRONT_DIR SWOB_CSV OUT.mp4
"""
import sys, os, json, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import map_coordinates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from troops import Scene
from fx2d import FireFX

Ld, Bd, Sd, PF, SWOB, OUT = sys.argv[1:7]
FPS = 12
LAB = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'story_lab'); os.makedirs(LAB, exist_ok=True)
F = '/usr/share/fonts/opentype/inter/'
fb = lambda s: ImageFont.truetype(F + 'Inter-Bold.otf', int(s))
fm = lambda s: ImageFont.truetype(F + 'Inter-Medium.otf', int(s))
freg = lambda s: ImageFont.truetype(F + 'Inter-Regular.otf', int(s))
INK = (14, 16, 20); WHITE = (255, 255, 255); MUTED = (200, 205, 212)
AMBER = (255, 196, 64); BLUE = (110, 170, 255); RED = (255, 90, 60); GREEN = (120, 220, 140)
hm = lambda h, m=0: h * 60 + m
T_SHIFT = hm(15, 16)

P = json.load(open(os.path.join(Ld, 'points.json')))
G = P['grid']; RES = G['res']; Wm, Hm = G['w'] * RES, G['h'] * RES
arr = np.load(os.path.join(Ld, 'arrival_min.npy')).astype(np.float64)
unk = np.load(os.path.join(Ld, 'unknown.npy'))
sev = np.load(os.path.join(Ld, 'severity.npy'))
scar5 = (np.asarray(Image.open(os.path.join(Ld, 'scar.png'))) > 127).astype(np.float32)
story = json.load(open(os.path.join(Ld, 'story.json')))['frames']
TR = Scene(Ld, Sd)
FX = FireFX(TR, arr)

# ---------------------------------------------------------------- wind (CZWN hourly)
import pandas as pd
sw = pd.read_csv(SWOB)
sw = sw[sw.time_mdt.str.startswith('2026-10-17') & sw.max_wnd_spd_pst1hr_tm.notna()]
sw = sw[sw.time_mdt < '2026-10-17 16:00']  # the 16:00 report holds the 3:16 gust front; it is used only from 3:16
WT = np.array([int(s[11:13]) * 60 for s in sw.time_mdt]) - 30  # mid-hour of the reporting period
WD = sw.avg_wnd_dir_10m_pst10mts.values.astype(float); WS = sw.avg_wnd_spd_10m_pst10mts.values.astype(float)
WG = sw.max_wnd_spd_10m_pst1hr.values.astype(float)


def wind(t):
    if t >= T_SHIFT:  # the gust front: CZWN 82 km/h at 3:16 p.m., then from the northwest
        return 307.0, 47.6, 82.0
    t = min(t, WT[-1])  # hold the last pre-front report until the gust front
    u = np.interp(t, WT, np.sin(np.radians(WD)) * WS); v = np.interp(t, WT, np.cos(np.radians(WD)) * WS)
    return (math.degrees(math.atan2(u, v)) % 360, float(np.interp(t, WT, WS)), float(np.interp(t, WT, WG)))


# ---------------------------------------------------------------- sun (night grading)
def sun_elev(t_min, lat=52.77, lon=-110.92, doy=290):
    utc = t_min / 60 + 6
    g = 2 * math.pi / 365 * (doy - 1 + (utc - 12) / 24)
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g) - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    ha = math.radians((utc * 60 + eqt + 4 * lon) / 4 - 180); la = math.radians(lat)
    return 90 - math.degrees(math.acos(math.sin(la) * math.sin(decl) + math.cos(la) * math.cos(decl) * math.cos(ha)))


# ---------------------------------------------------------------- escape scenarios
def scenario_runs():
    minx, maxy, R40, h40, w40 = np.load(os.path.join(PF, 'meta.npy')); h40, w40 = int(h40), int(w40)
    a = np.load(os.path.join(PF, 'arr_S4_fixed315_8.0_steady.npy')).astype(float); a[~np.isfinite(a)] = np.nan
    from pyproj import Transformer
    tr = Transformer.from_crs('EPSG:4326', G['crs'], always_xy=True)
    gx, gy = tr.transform(-110.9063, 52.7728)  # the Range 2 point used by v4
    DS = np.arange(0, 3001, 20); v = 8000 / 60
    first = lambda m: int(m.argmax()) if m.any() else 10 ** 9

    def route(dg, dep):
        X = gx + DS * math.sin(math.radians(dg)); Y = gy + DS * math.cos(math.radians(dg))
        c = ((X - minx) // R40).astype(int); r = ((maxy - Y) // R40).astype(int)
        fa = a[np.clip(r, 0, h40 - 1), np.clip(c, 0, w40 - 1)]; t = dep + DS / v
        safe = np.isnan(fa) | ((fa <= t - 5) & (np.arange(len(DS)) > 0))
        return t, first(safe), first((fa <= t + 3) & ~safe), first((fa <= t) & ~safe)

    # v4's best route from the Range 2 point at the gust (3-minute margin), shortest distance to safety
    best = None
    for dg in range(0, 360, 5):
        t, i_s, i_3, _ = route(dg, 16)
        if i_s < i_3 and i_s < 10 ** 9 and (best is None or DS[i_s] < best[1]):
            best = (dg, int(DS[i_s]))
    dg = best[0] if best else 70
    out = []
    for dep, col, odds in ((16, GREEN, '80%'), (19, AMBER, '43%'), (23, RED, '10%')):
        t, i_s, i_3, i_0 = route(dg, dep)  # everyone takes the route that works at 3:16
        if i_s < i_3:
            end, fate = i_s, 'clear'          # clear with v4's 3-minute margin
        elif i_s < i_0:
            end, fate = i_s, 'close'          # reaches clear ground, with the fire under 3 min behind
        else:
            end, fate = i_0, 'overtaken'      # the fire reaches the route first
        out.append(dict(dep=hm(15, dep), dir=dg, dist=float(DS[end]), t_end=hm(15, 0) + t[end], fate=fate,
                        col=col, odds=odds, x0=gx - G['x0'], y0=gy - G['y0']))
    return out


RUNS = scenario_runs()
for r in RUNS:
    print(f"scenario leave {int(r['dep']//60)}:{int(r['dep']%60):02d} -> {r['fate']} after {r['dist']:.0f} m "
          f"at {int(r['t_end']//60)}:{r['t_end']%60:04.1f} (bearing {r['dir']})")

# ---------------------------------------------------------------- helpers
def lin(v):
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


CACHE = {}


def load_key(key):
    if key not in CACHE:
        if len(CACHE) > 6:
            CACHE.pop(next(iter(CACHE)))
        base = np.asarray(Image.open(os.path.join(Bd, f'base_{key}.png')).convert('RGB')).astype(np.float32) / 255
        xy = cv2.imread(os.path.join(Bd, f'xy_{key}.png'), cv2.IMREAD_UNCHANGED).astype(np.float64) / 65535
        x = lin(xy[..., 2]) * Wm; y = lin(xy[..., 1]) * Hm; ground = xy[..., 3] > 0.5
        col = x / RES - 0.5; row = (G['h'] - 1) - (y / RES - 0.5)
        A = map_coordinates(np.where(np.isfinite(arr), arr, 1e5), [row, col], order=1, mode='nearest')
        A[A > 5e4] = np.nan
        SV = map_coordinates(sev, [row, col], order=1, mode='nearest')
        UK = map_coordinates(unk.astype(np.float32), [row, col], order=1, mode='nearest')
        SC = map_coordinates(scar5, [y_ := (2 * G['h'] - 1) - (y / (RES / 2) - 0.5), x / (RES / 2) - 0.5], order=1, mode='nearest')
        CACHE[key] = dict(base=base, A=np.where(ground, A, np.nan), SV=SV, UK=UK * ground, SC=SC * ground, ground=ground)
    return CACHE[key]


def paint_fire(d, t, final_fade):
    base = d['base'].copy(); A = d['A']
    dt = t - A
    burning = np.nan_to_num(dt, nan=-1) >= 0
    tau = np.where(A < T_SHIFT, 15.0, 0.8)
    glow = np.where(burning, np.exp(-np.clip(np.nan_to_num(dt), 0, None) / tau), 0.0) ** 2
    inscar = d['SC'] > 0.5
    char = np.where(burning & inscar, np.clip(np.nan_to_num(dt) / 2.0, 0, 1), 0.0) * (0.6 + 0.4 * d['SV'])
    charcoal = np.array([0.055, 0.045, 0.04], np.float32)
    img = base * (1 - char[..., None]) + charcoal * char[..., None]
    if final_fade > 0:
        u = (d['UK'] * 0.8 * final_fade)[..., None]
        img = img * (1 - u) + np.array([0.33, 0.30, 0.27], np.float32) * u
    return img, glow * inscar


def night(img, glow, t):
    e = sun_elev(t)
    dark = float(np.clip((2.0 - e) / 8.0, 0, 1))  # full night below -6 deg, daylight above +2
    if dark > 0:
        tint = np.array([0.55, 0.65, 1.0], np.float32)
        img = img * (1 - 0.86 * dark) * (tint * dark + (1 - dark))
    g = glow[..., None] * np.array([1.0, 0.36, 0.06], np.float32)
    gl = cv2.GaussianBlur(g, (0, 0), 1.2) * 1.0 + cv2.GaussianBlur(g, (0, 0), 7) * (0.45 + 1.4 * dark)
    return np.clip(img + gl, 0, 1)


def clock(t):
    h, m = int(t // 60), int(t % 60)
    return f'{h - 12 if h > 12 else h}:{m:02d} ' + ('p.m.' if h >= 12 else 'a.m.')


def caption(fr, t):
    if fr['final']:
        return ('Oct. 24', 'The burn scar, as Sentinel-2 saw it a week later',
                'Grey: burned, timing unknown (not connected to the main fire; includes heat VIIRS saw on Oct. 14).', WHITE)
    if fr['card'] == 'forecast':
        return (clock(t), 'Environment Canada\'s 4:30 a.m. forecast: west winds gusting to 80 km/h this afternoon',
                'Overnight the wind is light, from the south-southwest (CZWN station).', WHITE)
    if t < hm(7, 50):
        return (clock(t), 'Modelled: the fire starts in Range 11\'s impact area',
                'Working model v4 best fit, about 5 a.m. (v4 4:00-6:30; v3 3:30-7). Night firing or a holdover from '
                'earlier firing? The model can\'t tell.', AMBER)
    if t < hm(12, 17):
        return (clock(t), 'Sunrise 7:50. Grenadiers fire on Range 11; the fire burns on in the impact area',
                'Grass fire spreading northeast with a southwest wind (modelled). Firing positions and targets illustrative.', AMBER)
    if t < hm(12, 18):
        return (clock(t), 'Landsat 8 photographs the fire', 'Yellow: its 59 fire pixels. A strip about 2 km long has burned.', AMBER)
    if fr['card'] == 'warning':
        return (clock(t), 'Environment Canada warns of gusts up to 100 km/h',
                'The fire is still burning on the range, about 1 km from C Company\'s likely position.', RED)
    if t < hm(14, 49):
        return (clock(t), 'The fire creeps north; the wind rises', 'Spread between satellite passes is modelled (working model v4).', AMBER)
    if t < T_SHIFT:
        return (clock(t), 'NOAA-20 sees the fire (blue)', 'The wind is gusting to 50-55 km/h from the southwest.', BLUE)
    if fr['card'] == 'gust':
        return (clock(t), 'An 82 km/h gust. The wind turns northwest',
                'The fire\'s long southeast side becomes its front. The edge is about 590 m from the Range 2 point.', RED)
    if t < hm(15, 40):
        return (clock(t), 'Three scenarios: leaving the Range 2 area at 3:16, 3:19 or 3:23',
                'Jogging in kit on the best route, against v4\'s best-fitting fire. Scenarios, not what happened.', RED)
    return (clock(t), 'The fire runs on southeast', 'About 4.8 km in roughly 15-20 minutes (modelled).', RED)


def arrow(d, cx, cy, bearing_screen, length, col, width):
    a = math.radians(bearing_screen); dx, dy = math.sin(a), -math.cos(a)
    x0, y0 = cx - dx * length / 2, cy - dy * length / 2; x1, y1 = cx + dx * length / 2, cy + dy * length / 2
    d.line([x0, y0, x1, y1], fill=col, width=width); hx, hy = -dy, dx
    d.polygon([(x1 + dx * 10, y1 + dy * 10), (x1 - dx * 8 + hx * 9, y1 - dy * 8 + hy * 9),
               (x1 - dx * 8 - hx * 9, y1 - dy * 8 - hy * 9)], fill=col)


def label_at(d, x, y, text, sub, S, anchor='la', col=WHITE):
    d.text((x, y), text, font=fb(14 * S), fill=col, stroke_width=3, stroke_fill=INK, anchor=anchor)
    if sub:
        d.text((x, y + 17 * S), sub, font=freg(11 * S), fill=MUTED, stroke_width=3, stroke_fill=INK, anchor=anchor)


def runner_state(r, t):
    if t < r['dep']:
        return None
    dist = min((t - r['dep']) * 8000 / 60, r['dist'])
    done = t >= r['t_end']
    b = math.radians(r['dir'])
    return r['x0'] + dist * math.sin(b), r['y0'] + dist * math.cos(b), dist, done


# ---------------------------------------------------------------- main loop
N = len(story)
ONLY = os.environ.get('ONLY')  # e.g. "40,120,300" to compose a few frames for checking
sel = set(int(v) for v in ONLY.split(',')) if ONLY else None
for fr in story:
    if sel is not None and fr['i'] not in sel:
        continue
    i, t = fr['i'], fr['t']
    TR.override = (fr['loc'], fr['look'])
    d = load_key(fr['key'])
    final_fade = 1.0 if fr['final'] else 0.0
    img, glow = paint_fire(d, t, final_fade)
    img = night(img, glow, t)
    im = Image.fromarray((img * 255).astype(np.uint8))
    W, H = im.size; S = W / 960
    e = sun_elev(t); dark = float(np.clip((2.0 - e) / 8.0, 0, 1))
    if not fr['final']:
        im = FX.draw(im, i, i, t)  # flames and smoke
    # grenadiers: in daylight on the firing line, firing through the morning
    if not fr['final'] and t >= hm(7, 50):
        TR.draw(im, i, i, min(t, T_SHIFT - 1), group=TR.r11, alpha=1.0)
        if t < hm(12, 0):
            TR.draw_agl(im, i, i % 48, 48)
    # C Company: moving until 3:16; dimmed while the scenarios play
    if not fr['final'] and t >= hm(7, 50):
        a_c = 1.0 if t < T_SHIFT else 0.35
        TR.draw(im, i, i, t, alpha=a_c * (1 - 0.6 * dark))
    dr = ImageDraw.Draw(im)
    # satellite detections
    for hs in P['hotspots']:
        if '2026-10-17' not in (hs['time_mdt'] or ''):
            continue
        if hs['source'] == 'LANDSAT_NRT' and hm(12, 17) <= t < T_SHIFT:
            col, rr = AMBER, 2.5
        elif hs['source'] == 'VIIRS_NOAA20_NRT' and hm(14, 49) <= t < T_SHIFT:
            col, rr = BLUE, 5
        else:
            continue
        x, y, z = TR.project(i, (hs['x'], hs['y'], TR.gz(hs['x'], hs['y'])))
        if z > 0:
            x *= W / TR.W; y *= H / TR.H; q = rr * S
            dr.rectangle([x - q, y - q, x + q, y + q], outline=col, width=max(2, int(2 * S)))
    # scenario runners
    if T_SHIFT <= t < hm(15, 40) and not fr['final']:
        for r in RUNS:
            st = runner_state(r, t)
            if st is None:
                continue
            x, y, dist, done = st
            pts = []
            for s_ in np.linspace(0, dist, 20):
                b = math.radians(r['dir']); px_, py_ = r['x0'] + s_ * math.sin(b), r['y0'] + s_ * math.cos(b)
                q = TR.project(i, (px_, py_, TR.gz(px_, py_))); pts.append((q[0] * W / TR.W, q[1] * H / TR.H))
            if len(pts) > 1:
                dr.line(pts, fill=INK, width=int(5 * S)); dr.line(pts, fill=r['col'], width=int(3 * S))
            sx, sy, sz = TR.project(i, (x, y, TR.gz(x, y)))
            sx *= W / TR.W; sy *= H / TR.H
            key = ('standing_observer' if done else 'walking_equipment') + '_' + ('right' if pts[-1][0] >= pts[0][0] else 'left')
            sp = TR.sprites[key]; k = 22 * S * (5200 / sz) * 0.75 / sp.height
            spr = sp.resize((max(1, int(sp.width * k)), max(1, int(sp.height * k))), Image.LANCZOS)
            alpha = 1.0 if not (done and r['fate'] == 'overtaken') else max(0.3, 1 - (t - r['t_end']) / 1.5)
            a_ = spr.split()[3].point(lambda v: int(v * alpha)); halo = a_.filter(ImageFilter.MaxFilter(3))
            dark_ = Image.new('RGBA', spr.size, (10, 10, 12, 0)); dark_.putalpha(halo)
            body = spr.copy(); body.putalpha(a_)
            pos = (int(sx - spr.width / 2), int(sy - spr.height)); im.paste(dark_, pos, dark_); im.paste(body, pos, body)
            dr = ImageDraw.Draw(im)
            tag = f"leave {clock(r['dep'])[:4]}"
            if done:
                tag += {'clear': f" · clear {clock(r['t_end'])[:4]}",
                        'close': f" · clear {clock(r['t_end'])[:4]}, fire under 3 min behind",
                        'overtaken': (" · fire reached Range 2 at 3:21, before they left" if r['dist'] == 0
                                      else f" · overtaken {clock(r['t_end'])[:4]}")}[r['fate']]
            label_at(dr, sx + 10 * S, sy - 30 * S, tag, None, S, col=r['col'])
        # legend
        bx, by = 18 * S, 108 * S
        box = Image.new('RGBA', (int(330 * S), int(92 * S)), (*INK, 205)); im.paste(box, (int(bx), int(by)), box)
        dr = ImageDraw.Draw(im)
        dr.text((bx + 10 * S, by + 8 * S), 'Got clear, across all 30 modelled fires (v4)', font=fb(12 * S), fill=WHITE)
        for j, r in enumerate(RUNS):
            dr.rectangle([bx + 10 * S, by + (30 + 19 * j) * S, bx + 24 * S, by + (42 + 19 * j) * S], fill=r['col'])
            dr.text((bx + 32 * S, by + (28 + 19 * j) * S), f"leave {clock(r['dep'])}: {r['odds']}", font=fm(12 * S), fill=WHITE)
    # place labels
    lab_pts = {k: P['pov'][k] for k in ('Range 13',)}
    lab_pts['Range 11'] = P['extra']['Range 11']
    if t >= T_SHIFT - 1:
        lab_pts.update({k: P['pov'][k] for k in ('Range 2', 'Roadhead')})
    for k, v in lab_pts.items():
        x, y, z = TR.project(i, (v['x'], v['y'], TR.gz(v['x'], v['y'])))
        x *= W / TR.W; y *= H / TR.H
        if z > 0 and 0 < x < W and 100 * S < y < H - 50 * S:
            dr.ellipse([x - 4 * S, y - 4 * S, x + 4 * S, y + 4 * S], fill=WHITE, outline=INK, width=2)
            anc, off = (('rb', (-8, -6)) if k == 'Range 2' else ('lt', (8, 3)))
            dr.text((x + off[0] * S, y + off[1] * S), k, font=fb(15 * S), fill=WHITE, stroke_width=3, stroke_fill=INK, anchor=anc)
    # header
    hdr = Image.new('RGBA', (W, int(92 * S)), (*INK, 210)); im.paste(hdr, (0, 0), hdr); dr = ImageDraw.Draw(im)
    big, cap, sub, col = caption(fr, t)
    dr.text((18 * S, 12 * S), big, font=fb(34 * S), fill=col)
    cx = 18 * S + dr.textlength(big, font=fb(34 * S)) + 18 * S
    dr.text((cx, 16 * S), cap, font=fb(17 * S), fill=WHITE)
    dr.text((cx, 44 * S), sub, font=freg(12 * S), fill=MUTED)
    # wind compass (screen-relative)
    if not fr['final']:
        loc, look = np.array(fr['loc']), np.array(fr['look'])
        heading = math.degrees(math.atan2(look[0] - loc[0], look[1] - loc[1])) % 360
        wd, ws, wg = wind(t)
        bx, by = W - 70 * S, 150 * S
        dr.ellipse([bx - 46 * S, by - 46 * S, bx + 46 * S, by + 46 * S], fill=INK, outline=MUTED, width=2)
        arrow(dr, bx, by, (wd + 180 - heading) % 360, 60 * S, RED if wg >= 70 else (AMBER if wg >= 40 else WHITE), int(5 * S))
        nx, ny = bx + 34 * S * math.sin(math.radians(-heading)), by - 34 * S * math.cos(math.radians(-heading))
        dr.text((nx, ny), 'N', font=fb(13 * S), fill=MUTED, anchor='mm')
        dr.text((bx, by + 60 * S), f'Wind {ws:.0f} km/h', font=fm(13 * S), fill=WHITE, anchor='mm', stroke_width=2, stroke_fill=INK)
        dr.text((bx, by + 76 * S), f'gusts {wg:.0f}', font=fm(13 * S), fill=WHITE, anchor='mm', stroke_width=2, stroke_fill=INK)
    # footer
    ft = Image.new('RGBA', (W, int(40 * S)), (*INK, 210)); im.paste(ft, (0, H - int(40 * S)), ft); dr = ImageDraw.Draw(im)
    dr.text((18 * S, H - 33 * S), 'Clock not to scale · height x3 · fire: working model v4 (modelled) · observed: Landsat 8 12:17, VIIRS 2:49, '
            'CZWN wind, ECCC forecast/warning, Sentinel-2 scar Oct 24', font=freg(11 * S), fill=MUTED)
    dr.text((18 * S, H - 17 * S), 'Figures representative, not to scale · smoke illustrative · ranges from OpenStreetMap, not verified by DND · '
            'Prime Rogue Inc.', font=freg(11 * S), fill=MUTED)
    im.convert('RGB').save(os.path.join(LAB, f'{i:04d}.png'))
    if i % 40 == 0:
        print('frame', i, clock(t), flush=True)

if sel is not None:
    sys.exit(0)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(LAB, '%04d.png'),
                '-vf', 'minterpolate=fps=24:mi_mode=blend', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], check=True)
print('wrote', OUT, N, 'frames')
