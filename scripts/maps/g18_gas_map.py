import sys; sys.path.insert(0, "vis")
from pr import *
import json
from shapely.geometry import shape
from pyproj import Geod
G = Geod(ellps="WGS84")
m = Map(-111.000, -110.862, 52.739, 52.800, 168)
TOP, L = 196, 48
Wc, Hc = m.w + 2 * L, TOP + m.h + 24 + 140
im, d = canvas(Wc, Hc, "CFB WAINWRIGHT FIRE · GAS INFRASTRUCTURE TEST · WORKING MODEL V2.1",
               "No gas line or well in the grenade launcher's line of fire",
               "Every licensed pipeline and well around the fire, against Range 11's likely firing sector: none inside it within 2.5 km, even widened to 20°-160°.\nNearest gas lines: 350-560 m behind the firing point. The Range 2 lines are 3.5-4 km away; the fire reached them about 3:25 p.m.")
base = m.base(bright=0.8)
ov = Image.new("RGBA", base.size, (0, 0, 0, 0)); o = ImageDraw.Draw(ov)
R11 = (52.7678, -110.9577)
def wedge(a0, a1, r):
    pts = [m.P(*R11)]
    for az in range(a0, a1 + 1, 2):
        lo, la, _ = G.fwd(R11[1], R11[0], az, r); pts.append(m.P(la, lo))
    return pts
o.polygon(wedge(20, 160, 2500), fill=TEAL + (28,))
o.polygon(wedge(40, 120, 2500), fill=TEAL + (60,))
for f in json.load(open(REPO + "data/copernicus/burn_scar.geojson"))["features"]:
    m.outline(o, shape(f["geometry"]), RED + (230,), width=3)
base = Image.alpha_composite(base, ov); dd = ImageDraw.Draw(base)
pts = []
for az in range(0, 361, 2):
    lo, la, _ = G.fwd(R11[1], R11[0], az, 2200); pts.append(m.P(la, lo))
dashed(dd, pts, TEAL, 3, (16, 9))
dashed(dd, wedge(20, 160, 2500), TEAL, 2, (6, 6))
GASC = (255, 214, 0)
for f in json.load(open(REPO + "data/reference/aer_pipelines_near_site.geojson"))["features"]:
    p = f["properties"]; g = shape(f["geometry"])
    op = p["SEG_STATUS"] == "Operating"
    for gg in getattr(g, "geoms", [g]):
        xy = [m.P(y, x) for x, y in gg.coords]
        if op: dd.line(xy, fill=INK, width=7); dd.line(xy, fill=GASC, width=4)
        else: dashed(dd, xy, MUTED, 2, (7, 6))
W = pd.read_csv(REPO + "data/infrastructure/wells_within_5km_of_scar.csv")
for r in W.itertuples():
    if r.Lic_Status in ("Abandoned", "RecCertified", "Cancelled"): continue
    x, y = m.P(r.lat, r.lon)
    if 0 < x < m.w and 0 < y < m.h: dd.rectangle([x - 6, y - 6, x + 6, y + 6], outline=CREAM, width=3)
def dot(p, col, r=11): dd.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col, outline=INK, width=3)
P = {k: m.P(*v) for k, v in {"R11": R11, "R2": (52.77279, -110.90632), "RH": (52.77045, -110.89965), "ST": (52.77079, -110.92626)}.items()}
dashed(dd, [P["R11"], P["R2"]], CREAM, 2, (10, 7))
dot(P["R11"], TEAL); dot(P["R2"], CREAM); dot(P["RH"], CREAM)
x, y = P["ST"]; dd.line([x - 13, y - 13, x + 13, y + 13], fill=(255, 120, 80), width=6); dd.line([x - 13, y + 13, x + 13, y - 13], fill=(255, 120, 80), width=6)
wx, wy = m.P(52.773642, -110.898943); dd.rectangle([wx - 9, wy - 9, wx + 9, wy + 9], outline=YEL, width=4)
label(dd, (P["R11"][0], P["R11"][1] + 30), "RANGE 11\nAGL range", col=TEAL, size=18, anchor="ma")
label(dd, m.P(52.7800, -110.9445), "Likely firing sector\n(inferred): no gas line,\nno well within 2.5 km", col=TEAL, size=16)
label(dd, (x - 24, y + 22), "MODELLED START\n(best fit, working model)\n~1.4 km to nearest gas line", col=(255, 150, 110), size=15, anchor="ra")
label(dd, (P["R2"][0] - 40, P["R2"][1] - 84), "RANGE 2", size=16)
label(dd, (P["RH"][0] + 22, P["RH"][1] + 18), "ROAD HEAD\nfire reaches lines ~3:25 p.m.", size=16)
label(dd, (wx + 18, wy - 46), "Well 1-11 (registered site)", col=YEL, size=15)
gx, gy = m.P(*G.fwd(R11[1], R11[0], 335, 2200)[1::-1])
label(dd, (gx - 10, gy - 40), "C16 max. range ~2.2 km", col=TEAL, size=15, anchor="ma")
mx = ((P["R11"][0] + P["R2"][0]) / 2, (P["R11"][1] + P["R2"][1]) / 2)
label(dd, ((P["ST"][0] + P["R2"][0]) / 2 - 40, (P["ST"][1] + P["R2"][1]) / 2 - 52), "Range 2: 3.5 km from Range 11", col=INK, bg=CREAM, size=18, anchor="ma")
lx, ly = 18, m.h - 180
dd.rounded_rectangle([lx, ly, lx + 500, ly + 164], radius=8, fill=INK + (255,))
items = [("gas", GASC, "Gas line, operating (AER licence data)"), ("dash", MUTED, "Other line (abandoned, discontinued)"), ("sq", CREAM, "Licensed well, not abandoned (AER)"),
         ("fill", TEAL, "Firing sector 40-120° (dark), 20-160° (light)"), ("line", RED, "Burn scar (Sentinel-2, Oct. 19)")]
for i, (k, c, t) in enumerate(items):
    yy = ly + 16 + i * 29
    if k == "gas": dd.line([lx + 10, yy + 9, lx + 38, yy + 9], fill=c, width=5)
    elif k == "dash": dashed(dd, [(lx + 8, yy + 9), (lx + 38, yy + 9)], c, 3, (7, 5))
    elif k == "sq": dd.rectangle([lx + 17, yy + 3, lx + 29, yy + 15], outline=c, width=3)
    elif k == "fill": dd.rectangle([lx + 10, yy + 1, lx + 38, yy + 17], fill=(64, 140, 130))
    else: dd.line([lx + 10, yy + 9, lx + 38, yy + 9], fill=c, width=4)
    dd.text((lx + 50, yy), t, font=M(16), fill=CREAM)
sx, sy = m.w - 400, m.h - 50
dd.rectangle([sx, sy, sx + m.pxkm, sy + 10], fill=CREAM); dd.rectangle([sx + m.pxkm, sy, sx + 2 * m.pxkm, sy + 10], fill=INK)
for i, t in enumerate(["0", "1", "2 km"]): dd.text((sx + i * m.pxkm, sy - 26), t, font=B(17), fill=CREAM, anchor="ma")
arrow(dd, (m.w - 60, 130), (m.w - 60, 60), CREAM, width=6, head=20); dd.text((m.w - 60, 140), "N", font=B(22), fill=CREAM, anchor="ma")
im.paste(base, (L, TOP))
footer(im, ["Pipelines and wells: Alberta Energy Regulator licence data (mapped, not surveyed). Range positions: OpenStreetMap contributors. Firing sector inferred; firing direction not public.",
            "C16 range: Inveris C16 AGLS spec. Modelled start: Prime Rogue working model v2.1. Imagery: contains modified Copernicus Sentinel data [2026].",
            "Graphic: Kevin Duska Jr. (Prime Rogue Inc.), CC BY-NC 4.0. Data and method: github.com/primerogueinc/cfb-wainwright-fire-archive (part 9)"], fh=140)
im.convert("RGB").save("vis/cfb-wainwright-gas-sector-map.jpg", quality=92); print(im.size)
