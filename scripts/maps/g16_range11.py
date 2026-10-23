import sys; sys.path.insert(0, "vis")
from pr import *
import json
from shapely.geometry import shape
from pyproj import Geod
G = Geod(ellps="WGS84")
m = Map(-111.000, -110.862, 52.739, 52.800, 168)
TOP, L = 196, 48
Wc, Hc = m.w + 2 * L, TOP + m.h + 24 + 140
im, d = canvas(Wc, Hc, "CFB WAINWRIGHT FIRE · OCT. 17, 2026",
               "The AGL range, where the fire started, and where it caught C Company",
               "Range 11 is the automatic grenade launcher range, per the base's standing orders. Rings show the C16 launcher's reach (about 2 km).\nAt 12:17 p.m. the fire burned east of it, inside Permanent Danger Area 2. After the 3:16 p.m. wind shift it ran southeast onto Range 2 and the road head.")
base = m.base(bright=0.95)
ov = Image.new("RGBA", base.size, (0, 0, 0, 0)); o = ImageDraw.Draw(ov)
osmf = json.load(open(REPO + "data/infrastructure/osm_infrastructure_ODbL.geojson"))["features"]
pda2 = [shape(f["geometry"]) for f in osmf if f["properties"].get("name") == "Permanent Danger Area 2"][0]
m.outline(o, pda2, YEL + (230,), width=3, dash=(16, 10))
for f in json.load(open(REPO + "data/copernicus/burn_scar.geojson"))["features"]:
    m.outline(o, shape(f["geometry"]), RED + (255,), width=3)
R11 = (52.7678, -110.9577)
def ring(km, col, width, dash):
    pts = []
    for az in range(0, 361, 2):
        lo, la, _ = G.fwd(R11[1], R11[0], az, km * 1000); pts.append(m.P(la, lo))
    dashed(o, pts, col, width, dash)
ring(1.0, TEAL + (200,), 2, (8, 8)); ring(2.0, TEAL + (255,), 4, (18, 9))
base = Image.alpha_composite(base, ov); dd = ImageDraw.Draw(base)
det = pd.read_csv(REPO + "data/firms/detections.csv"); det = det[(det.acq_date == "2026-10-17") & (abs(det.latitude - 52.77) < 0.08) & (abs(det.longitude + 110.92) < 0.12)]
for _, r in det[det.source.str.contains("VIIRS")].iterrows():
    x, y = m.P(r.latitude, r.longitude); dd.ellipse([x - 13, y - 13, x + 13, y + 13], outline=(255, 159, 28), width=3)
for _, r in det[det.source.str.contains("LANDSAT")].iterrows():
    x, y = m.P(r.latitude, r.longitude); dd.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 40, 0))
pts = {"R11": R11, "R2": (52.7728, -110.9063), "RH": (52.77045, -110.89965)}
P = {k: m.P(*v) for k, v in pts.items()}
for (a, b) in [("R11", "R2")]:
    dashed(dd, [P[a], P[b]], CREAM, 2, (10, 7))
def dot(p, col, r=11):
    dd.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col, outline=INK, width=3)
dot(P["R11"], TEAL); dot(P["R2"], CREAM); dot(P["RH"], CREAM)
def km(a, b): return G.inv(pts[a][1], pts[a][0], pts[b][1], pts[b][0])[2] / 1000
mx = ((P["R11"][0] + P["R2"][0]) / 2, (P["R11"][1] + P["R2"][1]) / 2)
label(dd, (mx[0], mx[1] + 14), f"{km('R11','R2'):.1f} km", col=INK, bg=CREAM, size=18, anchor="ma")
label(dd, (P["R11"][0] - 30, P["R11"][1] + 30), "RANGE 11\nAGL range (standing orders)", col=TEAL, size=18, anchor="ra")
label(dd, (P["R2"][0] + 26, P["R2"][1] - 70), "RANGE 2\nhand grenade", size=17)
label(dd, (P["RH"][0] + 26, P["RH"][1] + 16), "ROAD HEAD\nend of range road", size=17)
x2, y2 = m.P(*G.fwd(R11[1], R11[0], 20, 2000)[1::-1])
label(dd, (x2 + 8, y2 - 34), "2 km: C16 reach", col=TEAL, size=16)
x1_, y1_ = m.P(*G.fwd(R11[1], R11[0], 350, 1000)[1::-1])
label(dd, (x1_ - 60, y1_ - 34), "1 km", col=TEAL, size=15)
nx, ny = m.P(52.7842, -110.9120)
label(dd, (nx, ny), "FIRE AT 12:17 P.M.\nLandsat detections", col=(255, 120, 80), size=16)
# wind
arrow(dd, m.P(52.7520, -110.9965), m.P(52.7600, -110.9795), (154, 209, 255), width=9, head=28)
label(dd, m.P(52.7578, -110.9770), "Before 3:16 p.m.:\nsouthwest, ~30 km/h", col=(154, 209, 255), size=16)
arrow(dd, m.P(52.7975, -110.990), m.P(52.7895, -110.973), (255, 138, 138), width=9, head=28)
label(dd, m.P(52.7988, -110.997), "From 3:16 p.m.: northwest, gusts 82 km/h", col=(255, 138, 138), size=16)
# legend
lx, ly = 18, m.h - 150
dd.rounded_rectangle([lx, ly, lx + 470, ly + 134], radius=8, fill=INK + (255,))
items = [("dot", (255, 40, 0), "Fire detected, 12:17 p.m. (Landsat, 30 m)"), ("ring", (255, 159, 28), "Fire detected, 2:49 p.m. (VIIRS, 375 m)"),
         ("line", RED, "Burn scar (Sentinel-2, Oct. 19)"), ("dash", YEL, "Permanent Danger Area 2 (as publicly mapped)")]
for i, (k, c, t) in enumerate(items):
    yy = ly + 18 + i * 29
    if k == "dot": dd.ellipse([lx + 18, yy + 4, lx + 28, yy + 14], fill=c)
    elif k == "ring": dd.ellipse([lx + 13, yy - 1, lx + 33, yy + 19], outline=c, width=3)
    elif k == "line": dd.line([lx + 10, yy + 9, lx + 36, yy + 9], fill=c, width=4)
    else: dashed(dd, [(lx + 8, yy + 9), (lx + 38, yy + 9)], c, 3, (8, 5))
    dd.text((lx + 50, yy), t, font=M(16), fill=CREAM)
# scale + north
sx, sy = m.w - 400, m.h - 50
dd.rectangle([sx, sy, sx + m.pxkm, sy + 10], fill=CREAM); dd.rectangle([sx + m.pxkm, sy, sx + 2 * m.pxkm, sy + 10], fill=INK)
for i, t in enumerate(["0", "1", "2 km"]): dd.text((sx + i * m.pxkm, sy - 26), t, font=B(17), fill=CREAM, anchor="ma")
arrow(dd, (m.w - 60, 130), (m.w - 60, 60), CREAM, width=6, head=20); dd.text((m.w - 60, 140), "N", font=B(22), fill=CREAM, anchor="ma")
im.paste(base, (L, TOP))
footer(im, ["Range positions: OpenStreetMap contributors (volunteer-mapped, not official). C16 reach ~2 km (Inveris C16 AGLS spec, after H&K GMG). Firing direction not public.",
            "Fire detections: NASA FIRMS. Imagery: contains modified Copernicus Sentinel data [2026]. C Company's location is a Prime Rogue estimate; DND has not confirmed it.",
            "Graphic: Kevin Duska Jr. (Prime Rogue Inc.), CC BY-NC 4.0. Data: github.com/primerogueinc/cfb-wainwright-fire-archive"], fh=140)
im.convert("RGB").save("vis/cfb-wainwright-range11-agl-map.jpg", quality=92); print(im.size)
