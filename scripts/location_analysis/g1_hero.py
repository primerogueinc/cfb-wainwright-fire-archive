import sys, math
sys.path.insert(0, "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/vis")
from pr import *

OUT = "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/vis/"
W, H = 1800, 1380
im, d = canvas(W, H, "CFB WAINWRIGHT  ·  OCT. 17, 2026  ·  SATELLITE AND WEATHER DATA",
               "Where the wind turned the fire",
               "If the fire was \"a kilometre away\" when the wind shifted, as Maj.-Gen. Rutland said, the data points to the area around Range 2.")

m = Map(-110.962, -110.858, 52.737, 52.797, 150)
base = m.base().convert("RGBA")
# darken slightly so overlays read
base = Image.blend(base, Image.new("RGBA", base.size, (0, 0, 0, 255)), 0.18)
ov = Image.new("RGBA", base.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)

scar = scar_main(); hull = preshift_hull(); bnd = band()
o = osm()
r2 = o[o["name"] == "Range 2 (Grenade)"].geometry.iloc[0]
r3 = o[o["name"] == "Range 3"].geometry.iloc[0]
cfb = o[o["name"] == "CFB Wainwright"].geometry.iloc[0]

# downwind band: teal fill
m.poly(od, bnd, fill=TEAL + (42,))
m.outline(od, bnd, INK + (200,), 9)
m.outline(od, bnd, TEAL + (255,), 4)
# pre-shift fire: yellow hatched area
m.poly(od, hull, fill=YEL + (70,))
m.outline(od, hull, YEL + (255,), 3, dash=(14, 9))
# scar outline
m.outline(od, scar, CREAM + (230,), 3)
# ranges
m.poly(od, r3, fill=(255, 255, 255, 50))
m.outline(od, r3, INK + (220,), 8)
m.outline(od, r3, (255, 255, 255, 255), 4)
rx, ry = m.P(r2.centroid.y, r2.centroid.x)
od.ellipse([rx - 13, ry - 13, rx + 13, ry + 13], outline=INK + (230,), width=8)
od.ellipse([rx - 13, ry - 13, rx + 13, ry + 13], outline=(255, 255, 255, 255), width=4)
# base boundary
bd = cfb.boundary if cfb.geom_type == "Polygon" else cfb
m.outline(od, bd.intersection(box(m.W, m.S, m.E, m.N)), GOLD + (230,), 3, dash=(16, 10))
# detections
L, V, Oo = detections()
for _, r in L.iterrows():
    x, y = m.P(r.latitude, r.longitude); od.rectangle([x - 4, y - 4, x + 4, y + 4], fill=YEL + (255,))
base.alpha_composite(ov)
md = ImageDraw.Draw(base)

# wind arrows
def km(dx, dy): return dx * m.pxkm, dy * m.pxkm
cx, cy = m.P(52.7745, -110.925)
# before: SW wind pushing NE (from 235 -> toward 55)
a0 = math.radians(55)
p0 = m.P(52.7585, -110.9595); p1 = (p0[0] + 1.3 * m.pxkm * math.sin(a0), p0[1] - 1.3 * m.pxkm * math.cos(a0))
arrow(md, p0, p1, CREAM, 9, 30)
label(md, (p0[0] - 4, p0[1] + 18), "Southwest wind,\nnoon to 3:16 p.m.", CREAM, 18)
# after: NW wind pushing SE (from 306 -> toward 126)
a1 = math.radians(126)
q0 = m.P(52.7915, -110.889); q1 = (q0[0] + 1.9 * m.pxkm * math.sin(a1), q0[1] - 1.9 * m.pxkm * math.cos(a1))
arrow(md, q0, q1, RED, 11, 34)
label(md, (q0[0] - 250, q0[1] - 4), "Northwest wind\nafter the 3:16 p.m. gust", RED, 18)

# labels
x, y = m.P(52.7815, -110.951)
label(md, (x - 40, y - 70), "Fire before the shift\n(12:17 and 2:49 p.m.\nsatellite detections)", YEL, 18)
x, y = m.P(52.7839, -110.9034)
md.line([(x + 30, y), (x + 70, y)], fill=CREAM, width=2)
label(md, (x + 76, y - 12), "Range 3\nbeside the fire at 2:49", CREAM, 17)
md.line([(rx + 13, ry), (rx + 58, ry - 8)], fill=CREAM, width=2)
label(md, (rx + 64, ry - 22), "Range 2 (Grenade)", CREAM, 17)
x, y = m.P(52.7445, -110.944)
label(md, (x, y), "Older scar,\nbefore Oct. 4", MUTED, 16)
x, y = m.P(52.7625, -110.902)
label(md, (x + 40, y + 6), "About 1 km downwind of\nthe fire when the wind\nshifted: most likely area", TEAL, 19)
x, y = m.P(52.7472, -110.872)
label(md, (x - 60, y + 50), "Burn scar, Oct. 19", CREAM, 17)
x, y = m.P(52.792, -110.8755)
label(md, (x + 10, y + 0), "Base\nboundary", GOLD, 16)
# scale bar + north
sx, sy = 30, m.h - 40
md.rectangle([sx, sy, sx + m.pxkm, sy + 8], fill=CREAM); md.text((sx, sy - 30), "1 km", font=B(19), fill=CREAM)
md.polygon([(m.w - 40, 22), (m.w - 52, 56), (m.w - 28, 56)], fill=CREAM); md.text((m.w - 40, 62), "N", font=B(19), fill=CREAM, anchor="mt")

MX, MY = 54, 196
im.alpha_composite(base, (MX, MY))
d = ImageDraw.Draw(im)
d.rectangle([MX - 1, MY - 1, MX + m.w, MY + m.h], outline=GOLD, width=1)

# right panel
X = MX + m.w + 56
d.text((X, MY + 6), "What the record shows", font=K(26), fill=GOLD)
items = [
    ("12:17 p.m.", "Landsat 8 sees a 1.9 km fire line\non the range."),
    ("2:49 p.m.", "The fire has crept about 1 km north,\npushed by a southwest wind. A road\nholds its east side."),
    ("3:16 p.m.", "An 82 km/h gust. The wind swings to\nthe northwest and the fire's long\nsoutheast side becomes its front."),
    ("3:30 p.m.", "NOAA's GOES-18 measures 16 times\nthe fire power of 20 minutes earlier."),
    ("1 km downwind", "is the area around Range 2, along\nthe north-south range road. Range 3\nwas already beside the fire at 2:49."),
]
y = MY + 58
for h, b in items:
    d.text((X, y), h, font=K(21), fill=CREAM)
    for i, l in enumerate(b.split("\n")):
        d.text((X, y + 32 + i * 27), l, font=M(18.5), fill=CREAM)
    y += 32 + 27 * len(b.split("\n")) + 26
d.line([X, y, W - 60, y], fill=GRIDC, width=2); y += 22
d.text((X, y), "Ruled out by the data", font=K(21), fill=CREAM); y += 34
for l in ["Range 3 and the north end: fire was", "already there before the shift.", "The west of the burn: burning at 12:17.", "The east lobe past the road: 3 to 4.5 km", "downwind, 15 to 30 minutes of warning."]:
    d.text((X, y), l, font=M(18.5), fill=CREAM); y += 27
y += 18; d.line([X, y, W - 60, y], fill=GRIDC, width=2); y += 22
for i, l in enumerate(["What it can't show: where C Company", "actually was. DND has not said. This is", "an estimate from public data, not a finding."]):
    d.text((X, y + i * 27), l, font=M(18.5), fill=MUTED)

footer(im, ["Base: Copernicus Sentinel-2, Oct. 19, 2026, bands 12, 8A, 4 (contains modified Copernicus Sentinel data 2026). Fire: NASA FIRMS (Landsat 8, NOAA-20 VIIRS); NOAA GOES-18.",
            "Wind: ECCC, CFB Wainwright station (CZWN). Ranges and base boundary: OpenStreetMap contributors (ODbL), not verified by DND. Times MDT. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"])
im.convert("RGB").save(OUT + "cfb-wainwright-where-the-wind-turned.jpg", quality=91, optimize=True)
print(im.size, m.w, m.h)
