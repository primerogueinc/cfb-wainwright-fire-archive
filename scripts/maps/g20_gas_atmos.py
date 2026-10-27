import sys, glob; sys.path.insert(0, "vis")
from pr import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.cm as cm
S5 = "/home/claude/cfb-wainwright-sentinel-5p-archives/sentinel-5p/"
WIN = (-114.6, -107.2, 51.2, 54.3)  # W E S N
def panel(path, cmap, vmin, vmax, w):
    r = rasterio.open(path); a = r.read(1, window=from_bounds(WIN[0], WIN[2], WIN[1], WIN[3], r.transform), boundless=True, fill_value=np.nan)
    rgba = (matplotlib.colormaps[cmap](np.clip((a - vmin) / (vmax - vmin), 0, 1)) * 255).astype("uint8")
    rgba[~np.isfinite(a)] = (58, 48, 40, 255)
    im = Image.fromarray(rgba).convert("RGBA")
    h = int(w * (WIN[3] - WIN[2]) * 111.2 / ((WIN[1] - WIN[0]) * 111.32 * math.cos(math.radians(52.75))))
    im = im.resize((w, h), Image.NEAREST); dd = ImageDraw.Draw(im)
    def P(lon, lat): return ((lon - WIN[0]) / (WIN[1] - WIN[0]) * w, (WIN[3] - lat) / (WIN[3] - WIN[2]) * h)
    for n, (lo, la) in {"Edmonton": (-113.49, 53.55), "Lloydminster": (-110.0, 53.28), "Saskatoon": (-106.67, 52.13), "Red Deer": (-113.81, 52.27)}.items():
        x, y = P(lo, la)
        if 0 < x < w - 20: dd.ellipse([x - 4, y - 4, x + 4, y + 4], fill=INK); label(dd, (x + 10, y - 8), n, col=CREAM, size=13, pad=4)
    x, y = P(-110.92, 52.776); dd.ellipse([x - 9, y - 9, x + 9, y + 9], outline=(0, 0, 0), width=5); dd.ellipse([x - 9, y - 9, x + 9, y + 9], outline=TEAL, width=3)
    return im
f = lambda d, p: glob.glob(S5 + f"2026-10-{d}/{p}/*" + ("340_380_(Raw).tiff" if p == "AER_AI" else "(Raw).tiff"))[0]
PW = 500
A = [panel(f(d, "AER_AI"), "YlOrBr", -1, 3, PW) for d in ("16", "17", "18")]
Mth = panel(f("18", "CH4"), "viridis", 1890, 1960, PW)
TOP, L, GAP = 220, 48, 24
ph = A[0].size[1]
Wc = L * 2 + 3 * PW + 2 * GAP; Hc = TOP + 44 + ph + 70 + 44 + ph + 40 + 140
im, d = canvas(Wc, Hc, "CFB WAINWRIGHT FIRE · GAS INFRASTRUCTURE TEST · WORKING MODEL V2.1",
               "The air showed no sign of a gas leak, but it can't settle the question",
               "Sentinel-5P (TROPOMI) over the base. Its Oct. 17 pass came at 2:34 p.m., about 50 minutes before the fire reached the gas lines, and cloud blanked carbon\nmonoxide and methane over the base. Smoke haze was no higher than the day before. On Oct. 18, methane coverage was good: no sign of a large leak at or downwind.")
y0 = TOP + 44
d.text((L, y0 - 34), "UV AEROSOL INDEX (SMOKE AND HAZE)", font=B(19), fill=GOLD)
for k, (pn, t, v) in enumerate(zip(A, ["Oct. 16 · 2:53 p.m. (before)", "Oct. 17 · 2:34 p.m. (fire day)", "Oct. 18 · 2:15 p.m. (after)"], ["0.40", "0.38", "0.24"])):
    x = L + k * (PW + GAP); im.paste(pn, (x, y0))
    d.text((x, y0 + ph + 10), t, font=B(17), fill=CREAM); d.text((x + PW, y0 + ph + 10), f"base: {v}", font=B(17), fill=TEAL, anchor="ra")
y1 = y0 + ph + 70 + 44
d.text((L, y1 - 34), "METHANE, OCT. 18 · 2:15 P.M.", font=B(19), fill=GOLD)
im.paste(Mth, (L, y1)); d.text((L, y1 + ph + 10), "Within 10 km: 1,914 ppb · region: 1,927 ppb", font=B(17), fill=CREAM)
bx = L + PW + GAP; bw = 2 * PW + GAP
d.rounded_rectangle([bx, y1, bx + bw, y1 + ph], radius=10, fill=PANEL)
rows = [("Can show", "A large leak still venting the next day. None seen.", TEAL),
        ("Can't show", "A brief release as the fire crossed the lines, about 3:25 p.m. The pass came\nfirst, cloud covered the base, and methane disperses within hours.", RED),
        ("Can't show", "A gas fire: burning gas makes little smoke or carbon monoxide.", RED),
        ("Verdict", "No sign of gas involvement, but on its own it neither confirms nor excludes it.", GOLD)]
yy = y1 + 22
for k, (h, t, c) in enumerate(rows):
    d.text((bx + 26, yy), h.upper(), font=B(17), fill=c)
    for i, l in enumerate(t.split("\n")): d.text((bx + 170, yy + i * 27), l, font=M(19), fill=CREAM)
    yy += 27 * len(t.split("\n")) + 20
lx = bx + 26; ly = y1 + ph - 36
for k, (cmap, lab, lo, hi) in enumerate([("YlOrBr", "Aerosol index", "-1", "3"), ("viridis", "Methane (ppb)", "1,890", "1,960")]):
    x = lx + k * 440; g = (matplotlib.colormaps[cmap](np.linspace(0, 1, 200))[:, :3] * 255).astype("uint8")
    bar = Image.fromarray(np.repeat(g[None], 14, 0)); im.paste(bar, (x + 140, ly + 4))
    d.text((x, ly), lab, font=M(15), fill=MUTED); d.text((x + 140, ly + 22), lo, font=M(13), fill=MUTED); d.text((x + 340, ly + 22), hi, font=M(13), fill=MUTED, anchor="ra")
d.ellipse([lx + 880 - 400, ly - 30, lx + 898 - 400, ly - 12], outline=TEAL, width=3); d.text((lx + 905 - 400, ly - 32), "CFB Wainwright fire", font=M(15), fill=MUTED)
d.rectangle([lx + 880 - 400 + 220, ly - 30, lx + 898 - 400 + 220, ly - 12], fill=(58, 48, 40)); d.text((lx + 905 - 400 + 220, ly - 32), "No data (cloud)", font=M(15), fill=MUTED)
footer(im, ["Sentinel-5P TROPOMI via Copernicus Browser; contains modified Copernicus Sentinel data [2026]. Pass times from orbital elements (Space-Track). Pixels ~5.5 x 3.5 km.",
            "Detects only large methane sources (roughly several tonnes per hour). Raw exports and manifests: github.com/primerogueinc/CFB-Wainwright-Sentinel-5P-Archives",
            "Graphic: Kevin Duska Jr. (Prime Rogue Inc.), CC BY-NC 4.0. Analysis: github.com/primerogueinc/cfb-wainwright-fire-archive (part 9)"], fh=140)
im.convert("RGB").save("vis/cfb-wainwright-gas-atmosphere.jpg", quality=92); print(im.size)
