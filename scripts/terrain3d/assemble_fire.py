"""Label the 3D fire frames (clock, captions, wind) and encode the video.

Run: python3 assemble_fire.py RENDERDIR OUT.mp4 [render_fps] [LAYERDIR SILHOUETTEDIR]
With LAYERDIR and SILHOUETTEDIR, a representative C Company section is drawn
between Range 2 and the roadhead (see troops.py).
"""
import sys, os, json, glob, math, subprocess
from PIL import Image, ImageDraw, ImageFont

Rd, out = sys.argv[1], sys.argv[2]
FPS = int(sys.argv[3]) if len(sys.argv) > 3 else 12
F = '/usr/share/fonts/opentype/inter/'
fb = lambda s: ImageFont.truetype(F + 'Inter-Bold.otf', s)
fm = lambda s: ImageFont.truetype(F + 'Inter-Medium.otf', s)
fr = lambda s: ImageFont.truetype(F + 'Inter-Regular.otf', s)
INK = (14, 16, 20); WHITE = (255, 255, 255); MUTED = (200, 205, 212)
AMBER = (255, 196, 64); BLUE = (110, 170, 255); RED = (255, 90, 60)
hm = lambda h, m: h * 60 + m
T_LS, T_V, T_SHIFT, T_RUN0, T_RUN1 = hm(12, 17), hm(14, 49), hm(15, 16), hm(15, 20), hm(15, 35)

meta = {}
for m in glob.glob(os.path.join(Rd, 'fire_meta_*.json')):
    meta.update(json.load(open(m))['frames'])
frames = sorted(glob.glob(os.path.join(Rd, 'fire_[0-9]*.png')))
N = len(frames)
lab = os.path.join(Rd, 'lab'); os.makedirs(lab, exist_ok=True)
N_FR = int(18 * FPS)  # frames in the full story (scene.py STORY), for the camera path
TROOPS = None
if len(sys.argv) > 5:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from troops import Scene
    TROOPS = Scene(sys.argv[4], sys.argv[5], fps=FPS)


def clock(t):
    h, m = int(t // 60), int(t % 60)
    return f'{h - 12 if h > 12 else h}:{m:02d} p.m.'


def phase(t, fade):
    if fade > 0.05:
        return ('Oct. 24', 'The burn scar, as Sentinel-2 saw it a week later',
                'Grey: burned, but the timing is unknown (patches not connected to the main fire; '
                'includes the spot where VIIRS detected heat on Oct. 14).', WHITE)
    if t <= T_LS + 1:
        return (clock(t), 'Landsat 8 records a fire line on the range',
                'Yellow: 59 fire pixels (30 m each), about 1.9 km long.', AMBER)
    if t < T_V:
        return (clock(t), 'The fire creeps north',
                'Between satellite passes the spread is modelled, not observed: timed by distance from the noon line.', AMBER)
    if t < T_SHIFT:
        return (clock(t), 'NOAA-20 sees the fire (blue). The wind is from the southwest',
                'The fire has grown about 1 km north since noon.', BLUE)
    if t < T_RUN0:
        return (clock(t), 'An 82 km/h gust. The wind turns northwest',
                'The fire\'s long southeast side becomes its front. (Wainwright CZWN station, 3:16 p.m.)', RED)
    return (clock(t), 'The fire runs southeast',
            'About 4.8 km in roughly 15 minutes (modelled: shown as distance downwind). '
            'GOES-18 measured 1,215 MW at 3:30.', RED)


def arrow(d, cx, cy, bearing_screen, length, col, width=6):
    a = math.radians(bearing_screen)
    dx, dy = math.sin(a), -math.cos(a)
    x0, y0 = cx - dx * length / 2, cy - dy * length / 2
    x1, y1 = cx + dx * length / 2, cy + dy * length / 2
    d.line([x0, y0, x1, y1], fill=col, width=width)
    hx, hy = -dy, dx
    d.polygon([(x1 + dx * 10, y1 + dy * 10), (x1 - dx * 8 + hx * 9, y1 - dy * 8 + hy * 9),
               (x1 - dx * 8 - hx * 9, y1 - dy * 8 - hy * 9)], fill=col)


def group_label(im, items, title, sub, S, above=False, left=False):
    xs = [x for _, x, _, _ in items]; ys = [y for _, _, y, _ in items]
    if max(xs) < 0 or min(xs) > im.width or max(ys) < 100 * S or min(ys) > im.height - 50 * S:
        return
    dd = ImageDraw.Draw(im)
    lx = min(xs) - 10 * S
    ly = (min(ys) - 52 * S) if above else (max(ys) + 8 * S)
    anc = 'la'
    if left:  # to the left of the group, clear of the rounds going up and away
        lx, ly, anc = min(xs) - 14 * S, sum(ys) / len(ys) - 34 * S, 'ra'
    dd.text((lx, ly), title, font=fb(int(14 * S)), fill=WHITE, stroke_width=3, stroke_fill=INK, anchor=anc)
    dd.text((lx, ly + 17 * S), sub, font=fr(int(11 * S)), fill=MUTED, stroke_width=3, stroke_fill=INK, anchor=anc)


def compose(im, n, t, fade, screen, prologue=None, g=0):
    """prologue = (k, nk) for the morning frames, else None."""
    W, H = im.size
    S = W / 960
    if TROOPS is not None:
        im = TROOPS.erase_pins(im, n)
        if prologue and prologue[0] < prologue[1] + 8:
            TROOPS.draw_agl(im, n, *prologue)
        if fade < 0.999:
            r11 = TROOPS.draw(im, n, g, t, alpha=1 - fade, group=TROOPS.r11)
            items = TROOPS.draw(im, n, g, t, alpha=1 - fade)
            if fade < 0.05:
                # anchor labels to where each group starts, so they don't jitter with the movement
                home = lambda grp: [(0, *(lambda q: (q[0] * W / TROOPS.W, q[1] * H / TROOPS.H))(
                    TROOPS.project(n, (t['x'], t['y'], TROOPS.gz(t['x'], t['y'])))), t) for t in grp]
                items, r11 = home(TROOPS.troops), home(TROOPS.r11)
                group_label(im, items, 'C Company (representative)',
                            'positions estimated · movement illustrative · not to scale', S)
                group_label(im, r11, 'Grenadiers, Range 11 (AGL range)',
                            'representative · movement illustrative · not to scale', S, left=True)
    d = ImageDraw.Draw(im)
    if TROOPS is not None and not prologue and T_V <= t < T_SHIFT:
        # the rendered VIIRS markers bloom to white; ring them in blue to match the caption
        for hs in TROOPS.P['hotspots']:
            if hs['source'] == 'VIIRS_NOAA20_NRT' and '2026-10-17' in (hs['time_mdt'] or ''):
                x, y, _ = TROOPS.project(n, (hs['x'], hs['y'], TROOPS.gz(hs['x'], hs['y']) + 20))
                x *= W / TROOPS.W; y *= H / TROOPS.H; r = 6 * S
                d.ellipse([x - r, y - r, x + r, y + r], outline=BLUE, width=max(2, int(2 * S)))
    for k, (x, y, z) in screen.items():
        if k.startswith('Fire line') or y < 100 * S or y > H - 50 * S or (TROOPS is not None and k in ('Range 2', 'Roadhead')):
            continue
        d.ellipse([x - 4 * S, y - 4 * S, x + 4 * S, y + 4 * S], fill=WHITE, outline=INK, width=2)
        anc, off = ('rb', (-8, -6)) if k == 'Range 2' else ('lt', (8, 3))
        d.text((x + off[0] * S, y + off[1] * S), k, font=fb(int(16 * S)), fill=WHITE, stroke_width=3, stroke_fill=INK, anchor=anc)
    # header
    hdr = Image.new('RGBA', (W, int(92 * S)), (*INK, 205)); im.paste(hdr, (0, 0), hdr)
    d = ImageDraw.Draw(im)
    if prologue:
        big, cap, sub, col = ('Morning', 'Grenadiers fire automatic grenade launchers on Range 11',
                              'DND says the fire started on the AGL range (Oct. 22 briefing). Firing positions, '
                              'targets and times shown are illustrative.', AMBER)
    else:
        big, cap, sub, col = phase(t, fade)
    d.text((18 * S, 12 * S), big, font=fb(int(34 * S)), fill=col)
    cx = 18 * S + d.textlength(big, font=fb(int(34 * S))) + 18 * S
    d.text((cx, 16 * S), cap, font=fb(int(19 * S)), fill=WHITE)
    d.text((cx, 44 * S), sub, font=fr(int(12.5 * S)), fill=MUTED)
    # wind + north, screen-relative (camera heading moves 32 -> 46 degrees)
    u = n / max(N_FR - 1, 1)
    heading = (212 + 14 * u + 180) % 360
    if fade < 0.05 and not prologue:
        wind_from = 235 if t < T_SHIFT else 235 + (306 - 235) * min(1, (t - T_SHIFT) / 2)
        bx, by = W - 70 * S, 150 * S
        d.ellipse([bx - 46 * S, by - 46 * S, bx + 46 * S, by + 46 * S], fill=(*INK,), outline=MUTED, width=2)
        arrow(d, bx, by, (wind_from + 180 - heading) % 360, 60 * S, RED if t >= T_SHIFT else WHITE, int(5 * S))
        nx, ny = bx + 34 * S * math.sin(math.radians(-heading)), by - 34 * S * math.cos(math.radians(-heading))
        d.text((nx, ny), 'N', font=fb(int(13 * S)), fill=MUTED, anchor='mm')
        d.text((bx, by + 60 * S), 'Wind from ' + ('NW' if wind_from > 290 else 'SW'), font=fm(int(13 * S)),
               fill=WHITE, anchor='mm', stroke_width=2, stroke_fill=INK)
    # footer
    ft = Image.new('RGBA', (W, int(40 * S)), (*INK, 205)); im.paste(ft, (0, H - int(40 * S)), ft)
    d = ImageDraw.Draw(im)
    d.text((18 * S, H - 33 * S), 'Clock not to scale · height x3 · observed: Landsat 8 12:17, VIIRS 2:49, CZWN wind 3:16, GOES-18 3:10-3:40, '
           'Sentinel-2 scar Oct 24 · spread between them modelled',
           font=fr(int(11 * S)), fill=MUTED)
    d.text((18 * S, H - 17 * S), 'Terrain NRCan MRDEM-30 · imagery Copernicus Sentinel-2 · ranges from OpenStreetMap, not verified by DND · '
           'Prime Rogue Inc., working model v4', font=fr(int(11 * S)), fill=MUTED)
    return im


i = 0
# morning prologue: camera eases from Range 11 to the fire camera while grenadiers fire
pmeta = {}
for mf in glob.glob(os.path.join(Rd, 'pro_meta_*.json')):
    pmeta.update(json.load(open(mf)))
pros = sorted(glob.glob(os.path.join(Rd, 'pro_[0-9]*.png')))
if TROOPS is not None and pros:
    NK = max(int(k) for k in pmeta) + 1
    for pf in pros:
        k = int(os.path.basename(pf)[4:8]); pm = pmeta[str(k)]
        TROOPS.override = (pm['loc'], pm['look'])
        compose(Image.open(pf).convert('RGB'), 0, 600, 0, pm['screen'],
                prologue=(k, int(NK * 0.8)), g=i).save(os.path.join(lab, f'{i:04d}.png')); i += 1
    TROOPS.override = None
for f in frames:
    n = int(os.path.basename(f)[5:9])
    m = meta[str(n)]
    compose(Image.open(f).convert('RGB'), n, m['t'], m.get('final_fade', 0), m['screen'], g=i).save(os.path.join(lab, f'{i:04d}.png'))
    i += 1

# 12 fps renders -> 24 fps with motion-compensated in-betweens
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(lab, '%04d.png'),
                '-vf', 'minterpolate=fps=24:mi_mode=blend', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], check=True)
print('wrote', out, i, 'frames')
