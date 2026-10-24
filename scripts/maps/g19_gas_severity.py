import sys; sys.path.insert(0, "vis")
from pr import *
import json
from shapely.geometry import shape
from pyproj import Transformer
R = REPO + "data/"
dn = rasterio.open(R + "copernicus/severity_matched_10m/dnbr_10m_oct04_oct19.tif"); Dv = dn.read(1).astype(float)
tf = Transformer.from_crs(4326, dn.crs, always_xy=True).transform
W_, S_, E_, N_ = -110.9135, 52.7655, -110.8925, 52.7775
x0, y0 = tf(W_, S_); x1, y1 = tf(E_, N_)
i0, j0 = dn.index(x0, y1); i1, j1 = dn.index(x1, y0)
sub = Dv[i0:i1, j0:j1]; SC = 11
cols = np.array([(58, 48, 40), (150, 120, 60), (214, 140, 60), (214, 70, 47), (122, 16, 32)], dtype=np.uint8)
idx = np.digitize(sub, [0.10, 0.20, 0.27, 0.44])
img = Image.fromarray(cols[idx]).resize((sub.shape[1] * SC, sub.shape[0] * SC), Image.NEAREST).convert("RGBA")
ox, oy = dn.transform * (j0, i0)
def PX(lon, lat):
    x, y = tf(lon, lat); return ((x - ox) / 10 * SC, (oy - y) / 10 * SC)
dd = ImageDraw.Draw(img)
for f in json.load(open(R + "reference/aer_pipelines_near_site.geojson"))["features"]:
    p = f["properties"]; g = shape(f["geometry"])
    for gg in getattr(g, "geoms", [g]):
        xy = [PX(*c) for c in gg.coords]
        if p["SEG_STATUS"] == "Operating": dd.line(xy, fill=INK, width=9); dd.line(xy, fill=(255, 214, 0), width=5)
wx, wy = PX(-110.898943, 52.773642)
for r in (50, 100):
    rp = r / 10 * SC; dashed(dd, [(wx + rp * math.cos(a), wy + rp * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 120)], CREAM, 2, (6, 6))
dd.rectangle([wx - 10, wy - 10, wx + 10, wy + 10], outline=YEL, width=4)
def dot(p, col, r=11): dd.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col, outline=INK, width=3)
A = PX(-110.90632, 52.77279); Bp = PX(-110.89965, 52.77045); Ew = PX(-110.90429, 52.77186)
dot(A, CREAM); dot(Bp, CREAM); dot(Ew, (255, 214, 0), r=9)
label(dd, (wx + 20, wy - 70), "WELL 1-11 (registered site)\nunburned; nothing burned\nwithin 100 m", col=YEL, size=17)
label(dd, (A[0] - 30, A[1] - 78), "RANGE 2", size=17, anchor="ma")
label(dd, (Bp[0] + 24, Bp[1] + 14), "ROAD HEAD", size=17)
label(dd, (Ew[0] - 26, Ew[1] + 26), "West end of line 58333-78 (mapped):\nedge of the main burn, not a circle", col=(255, 214, 0), size=16, anchor="ra")
lx, ly = 18, img.size[1] - 210
dd.rounded_rectangle([lx, ly, lx + 430, ly + 192], radius=8, fill=INK)
for k, (c, t) in enumerate([((255, 214, 0), "Gas line, operating (AER)")] + [(tuple(int(v) for v in cols[i]), t) for i, t in enumerate(["Unburned", "Low", "Moderate-low", "Moderate", "High"])]):
    yy = ly + 14 + k * 29
    if k == 0: dd.line([lx + 10, yy + 9, lx + 38, yy + 9], fill=c, width=5)
    else: dd.rectangle([lx + 12, yy + 1, lx + 36, yy + 17], fill=c)
    dd.text((lx + 50, yy), t, font=M(16), fill=CREAM)
L300 = 300 / 10 * SC; sx, sy = img.size[0] - L300 - 40, img.size[1] - 46
dd.rectangle([sx, sy, sx + L300, sy + 10], fill=CREAM); dd.text((sx + L300 / 2, sy - 26), "300 m", font=B(17), fill=CREAM, anchor="ma")
TOP, L = 196, 48
im, d = canvas(img.size[0] + 2 * L, TOP + img.size[1] + 24 + 140, "CFB WAINWRIGHT FIRE · GAS INFRASTRUCTURE TEST · WORKING MODEL V2.1",
               "At the gas lines, the fire burned lighter, not hotter",
               "Burn severity from Sentinel-2 (Oct. 4 vs Oct. 19). A gas fire at a break would leave a circle of higher severity on the line. There is none.\nWithin 30 m of the lines the ground is mostly unburned or lightly burned; the burn's edge follows line 58333-78. The well's registered site did not burn.")
im.paste(img, (L, TOP))
footer(im, ["Burn severity: dNBR from Sentinel-2 L2A (20 m bands, 10 m grid, seasonal offset removed); contains modified Copernicus Sentinel data [2026]. A scorch under ~20-40 m,",
            "or a release lasting seconds to minutes, would not show at this scale. Pipelines and well: Alberta Energy Regulator licence data (mapped, not surveyed).",
            "Graphic: Kevin Duska Jr. (Prime Rogue Inc.), CC BY-NC 4.0. Data and method: github.com/primerogueinc/cfb-wainwright-fire-archive (part 9)"], fh=140)
im.convert("RGB").save("vis/cfb-wainwright-gas-burn-severity.jpg", quality=92); print(im.size)
