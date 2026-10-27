"""Working model v4: 2D reconstruction animation of Oct. 17, 2026, 11 a.m. to 4 p.m. (Prime Rogue house style).
Usage: python3 g40_v4_animation.py [P4ROOT]
Pre-front: arrival_prefront_v4b_2x_lb3.0_0500.tif (hours since midnight). Post-front: the same case's best-fitting run
(S4_fixed315, 8 km/h head spread, steady shape; scar fit 0.547, within 0.004 of the best of all 240 runs), from
P4ROOT/p4_v4_v4b_2x_lb3.0_0500/arr_S4_fixed315_8.0_steady.npy (minutes after 3:00 p.m.) and meta.npy (minx, maxy, res, H, W).
Writes data/graphics_published/oct25_model_v4/cfb-wainwright-v4-reconstruction.{mp4,gif}."""
import sys, os, subprocess, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pr import *  # noqa
import numpy as np, rasterio
from pyproj import Transformer
P4 = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/"
MV4 = REPO + "data/authentic-stoic-stress-test/model_v4/"
OUT = REPO + "data/graphics_published/oct25_model_v4/"
FR = "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/v4anim/"; os.makedirs(FR, exist_ok=True)
for f in os.listdir(FR): os.remove(FR + f)

m = Map(-110.958, -110.846, 52.733, 52.797, 124)
b16 = m.base("2026-10-04"); b19 = m.base("2026-10-19")
# map pixel -> EPSG:3400 -> grid indices
jj, ii = np.meshgrid(np.arange(m.w) + 0.5, np.arange(m.h) + 0.5)
lon = m.W + jj / m.w * (m.E - m.W); lat = m.N - ii / m.h * (m.N - m.S)
X, Y = Transformer.from_crs(4326, 3400, always_xy=True).transform(lon, lat)
def sample(a, minx, maxy, res):
    r = ((maxy - Y) // res).astype(int); c = ((X - minx) // res).astype(int)
    ok = (r >= 0) & (r < a.shape[0]) & (c >= 0) & (c < a.shape[1]); o = np.full(X.shape, np.nan, "float32")
    o[ok] = a[r[ok], c[ok]]; return o
with rasterio.open(MV4 + "arrival_prefront_v4b_2x_lb3.0_0500.tif") as r:
    PRE = (sample(r.read(1), r.transform.c, r.transform.f, r.transform.a) - 15) * 60      # minutes after 3 p.m. (negative = earlier)
W4 = P4 + "p4_v4_v4b_2x_lb3.0_0500/"; mt = np.load(W4 + "meta.npy")
POST = sample(np.load(W4 + "arr_S4_fixed315_8.0_steady.npy"), mt[0], mt[1], mt[2])

TOP, BOT, TL = 158, 112, 122
CW, CH = m.w, m.h + TOP + TL + BOT
L, V, _ = detections(); o = osm(); scar = scar_main()
R2 = (52.7728, -110.9063); RH = (52.7705, -110.8996)
T0, T1 = -240, 60          # timeline: 11 a.m. to 4 p.m.
EV = [(-163, "12:17 Landsat", YEL), (-11, "2:49 VIIRS", BLUE), (10, "3:10", MUTED), (16, "3:16 gust", RED), (30, "3:30 GOES peak", RED), (40, "3:40", MUTED), (58, "DND: just before 4", GOLD)]
frames = []
hm = lambda t: f"{(int((t + 180) // 60) - 1) % 12 + 1}:{int(round((t + 180) % 60)):02d} {'a.m.' if t < -180 else 'p.m.'}"

def fire_layer(t, active):
    A = PRE if t < 16 else POST
    rgba = np.zeros((m.h, m.w, 4), "uint8")
    if t >= 16: active = min(active, 5)
    burnt = np.isfinite(A) & ((A <= t - active) | ((A <= 16) if t >= 16 else False)); act = np.isfinite(A) & (A <= t) & ~burnt
    rgba[burnt] = (24, 20, 20, 205); rgba[act] = (255, 122, 24, 235)
    return Image.fromarray(rgba, "RGBA")

def wind(d, frm, col, lab, pos):
    to = math.radians((frm + 180) % 360); x0, y0 = m.P(*pos); L_ = 1.1 * m.pxkm
    arrow(d, (x0, y0), (x0 + L_ * math.sin(to), y0 - L_ * math.cos(to)), col + (255,), 9, 28); label(d, (x0 - 10, y0 + 20), lab, col, 18)

def frame(t, caption, sub, base=None, active=10, dets=(), wnd=None, hits=(), hold=1, last=False):
    im = Image.new("RGBA", (CW, CH), BG + (255,)); im.alpha_composite(base or b16, (0, TOP))
    lay = Image.new("RGBA", (m.w, m.h), (0, 0, 0, 0))
    if last:
        dd = ImageDraw.Draw(lay); m.outline(dd, scar, INK + (255,), 6); m.outline(dd, scar, CREAM + (255,), 3)
        A = np.isfinite(POST) & (POST <= 120); rg = np.zeros((m.h, m.w, 4), "uint8"); rg[A] = (255, 122, 24, 90); lay.alpha_composite(Image.fromarray(rg, "RGBA"))
    else:
        lay.alpha_composite(fire_layer(t, active))
    d = ImageDraw.Draw(lay)
    if "L" in dets:
        for r in L.itertuples():
            x, y = m.P(r.latitude, r.longitude); d.rectangle([x - 3, y - 3, x + 3, y + 3], fill=YEL + (255,))
    if "V" in dets:
        for r in V.itertuples():
            x, y = m.P(r.latitude, r.longitude); h = 0.1875 * m.pxkm; d.rectangle([x - h, y - h, x + h, y + h], outline=BLUE + (255,), width=3)
    for (pt, name, dx, dy) in ((R2, "Range 2", 16, -40), (RH, "Road head", 22, 4)):
        x, y = m.P(*pt); hit = name in hits
        c = RED if hit else (255, 255, 255)
        d.ellipse([x - 10, y - 10, x + 10, y + 10], outline=INK + (255,), width=7); d.ellipse([x - 10, y - 10, x + 10, y + 10], outline=c + (255,), width=4)
        label(d, (x + dx, y + dy), name + (" (reached)" if hit else ""), RED if hit else CREAM, 17)
    if wnd: wind(d, *wnd)
    im.alpha_composite(lay, (0, TOP)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, CW, 5], fill=GOLD)
    d.text((26, 16), "Oct. 19 burn scar" if last else hm(t), font=D(52), fill=GOLD)
    d.text((26, 84), caption, font=K(27), fill=CREAM)
    if sub: d.text((26, 122), sub, font=M(17), fill=MUTED)
    d.text((CW - 26, 26), "WORKING MODEL V4", font=B(16), fill=GOLD, anchor="ra"); d.text((CW - 26, 48), "Reconstruction, not observation", font=M(15), fill=MUTED, anchor="ra")
    # scale bar
    d.rectangle([CW - 26 - m.pxkm, TOP + m.h - 30, CW - 26, TOP + m.h - 23], fill=CREAM); d.text((CW - 26 - m.pxkm, TOP + m.h - 56), "1 km", font=B(17), fill=CREAM)
    # legend
    lx, ly = 22, TOP + m.h - 74
    if last: lx = -9999
    d.rectangle([lx, ly, lx + 300, ly + 56], fill=INK)
    d.rectangle([lx + 10, ly + 10, lx + 28, ly + 24], fill=(255, 122, 24)); d.text((lx + 36, ly + 8), "Modelled fire edge (newly burning)", font=M(15), fill=CREAM)
    d.rectangle([lx + 10, ly + 33, lx + 28, ly + 47], fill=(24, 20, 20), outline=CREAM); d.text((lx + 36, ly + 31), "Modelled burned ground", font=M(15), fill=CREAM)
    # timeline
    ty = TOP + m.h; d.rectangle([0, ty, CW, ty + TL], fill=PANEL)
    x0, x1 = 40, CW - 40; X_ = lambda tt: x0 + (tt - T0) / (T1 - T0) * (x1 - x0); yb = ty + 84
    d.line([x0, yb, x1, yb], fill=MUTED, width=3)
    for hh in range(T0, T1 + 1, 60):
        d.line([X_(hh), yb - 6, X_(hh), yb + 6], fill=MUTED, width=2); d.text((X_(hh), yb + 12), hm(hh).replace(":00", ""), font=M(13), fill=MUTED, anchor="ma")
    if not last: d.rectangle([x0, yb - 3, X_(min(t, T1)), yb + 3], fill=GOLD)
    TIER = {-163: (-32, "ma"), -11: (-32, "ra"), 16: (-32, "ra"), 58: (-54, "ra")}
    for tt, lab, c in EV:
        if tt in TIER:
            dy, an = TIER[tt]; d.line([X_(tt), yb + dy + 16, X_(tt), yb], fill=c, width=2); d.text((X_(tt) + (4 if an == "ra" else 0), yb + dy), lab, font=B(13), fill=c, anchor=an)
        else: d.line([X_(tt), yb - 12, X_(tt), yb], fill=c, width=3)
    if not last: d.ellipse([X_(min(t, T1)) - 8, yb - 8, X_(min(t, T1)) + 8, yb + 8], fill=GOLD, outline=INK, width=2)
    # footer
    fy = ty + TL; d.rectangle([0, fy, CW, CH], fill=NAVY)
    d.text((26, fy + 12), "Model: FBP O-1a grass, hourly ECCC CZWN weather, NASA FIRMS / Landsat / NOAA GOES-18 timings. Best-fitting run of", font=M(14), fill=CREAM)
    d.text((26, fy + 32), "case v4b (one of 240): front at 3:16 p.m., wind from 315°. Base: Sentinel-2 (Copernicus), Oct. 4 and 19.", font=M(14), fill=CREAM)
    d.text((26, fy + 52), "Range 2 and road head locations are Prime Rogue's inference, not confirmed by DND. CC BY-NC 4.0.", font=M(14), fill=MUTED)
    d.text((CW - 26, CH - 14), "Kevin Duska Jr. (Prime Rogue Inc.)", font=B(15), fill=GOLD, anchor="rb")
    for _ in range(hold): frames.append(im.convert("RGB"))

SW = (235, CREAM, "Southwest wind", (52.743, -110.950)); NW = (315, RED, "Northwest wind", (52.792, -110.875))
for t in range(-240, -163, 15): frame(t, "A slow grass fire on the range", "Modelled from the morning on: in light winds it creeps, well under 1 km/h.", wnd=SW, active=30, hold=2)
frame(-163, "Landsat 8 sees a fire line", "Yellow: 59 fire detections at 12:17 p.m.", dets="L", wnd=SW, active=30, hold=10)
for t in range(-150, -11, 15): frame(t, "Still slow, drifting north-east", "The model keeps the fire small: about 1 km² by early afternoon.", dets="L", wnd=SW, active=30, hold=2)
frame(-11, "NOAA-20 sees it at 2:49 p.m.", "Blue: VIIRS fire pixels. The fire is about 1 km from Range 2.", dets="LV", wnd=SW, active=30, hold=10)
for t in range(-5, 16, 5): frame(t, "Before the front", "GOES-18 records 76 MW at 3:10 p.m., a small fire." if t >= 10 else "Southwest wind, about 30 km/h.", dets="LV", wnd=SW, active=30, hold=2)
frame(16, "3:16 p.m.: an 82 km/h gust. The wind turns northwest", "Its long south-east side becomes the front. Start: the modelled fire plus all ground the satellites saw burning.", wnd=NW, hold=12)
for t in range(17, 46):
    hits = tuple(n for n, a in (("Range 2", 20.7), ("Road head", 24.9)) if t >= a)
    cap = {21: "The modelled fire reaches Range 2", 25: "...and the road head", 30: "GOES-18: 1,215 MW, the day's peak"}.get(t, "The fire runs south-east")
    sub = "In this run: 3:21 p.m. at Range 2, 3:25 p.m. at the road head (240-run medians: 3:21 and 3:26)." if t >= 21 else "Head spread about 8 km/h with a northwest wind."
    frame(t, cap, sub, wnd=NW, hits=hits, hold=6 if t in (21, 25, 30) else 2)
    if t == 25: STILL = len(frames) - 1
for t in range(47, 61, 2):
    frame(t, "DND: \"just before 4:00\"" if t >= 57 else "Burning out toward the south-east", "By DND's time, the model has the fire past both points for more than half an hour." if t >= 57 else "GOES-18 falls to 336 MW at 3:40 p.m. and no fire by 3:50.", wnd=NW, hits=("Range 2", "Road head"), hold=14 if t == 59 else 2)
frame(60, "Model against the burn scar", "Orange: modelled burned area. Cream line: the scar mapped from Sentinel-2 on Oct. 19.", base=b19, hits=("Range 2", "Road head"), hold=22, last=True)

for i, f in enumerate(frames): f.save(FR + f"f{i:04d}.png")
print(len(frames), frames[0].size)
name = OUT + "cfb-wainwright-v4-reconstruction"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "4", "-i", FR + "f%04d.png", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", name + ".mp4"], check=True)
gw = 900; gh = int(CH * gw / CW)
small = [f.resize((gw, gh), Image.LANCZOS).quantize(colors=200, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
small[0].save(name + ".gif", save_all=True, append_images=small[1:], duration=250, loop=0, optimize=True)
frames[STILL].save(FR.replace("v4anim/", "") + "v4anim_still_0325.png")
for k in (20, 60, 95, len(frames) - 1): frames[min(k, len(frames) - 1)].save(FR + f"_check_{k}.png")
