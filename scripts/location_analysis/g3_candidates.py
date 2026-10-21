import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/vis")
from pr import *
OUT = "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/vis/"

W, H = 1800, 2150
im, d = canvas(W, H, "CFB WAINWRIGHT  ·  OCT. 17, 2026  ·  FOUR CANDIDATE AREAS",
               "Three places the data rules out",
               "Each area tested against the satellite detections, the wind and the burn scar, independently of what officials said.")
m = Map(-110.962, -110.858, 52.737, 52.797, 113)
base = m.base()
base = Image.blend(base, Image.new("RGBA", base.size, (0, 0, 0, 255)), 0.30)
scar = scar_main(); hull = preshift_hull(); bnd = band()
o = osm(); r3 = o[o["name"] == "Range 3"].geometry.iloc[0]
north = box(-110.918, 52.777, -110.893, 52.796).intersection(scar)
east = box(-110.880, 52.735, -110.850, 52.770).intersection(scar)

tiles = [
    ("MOST LIKELY", TEAL, bnd, "Around Range 2, about 1 km downwind",
     ["0.6 to 1.5 km downwind of the fire when", "the wind turned northwest. Burned in the", "run that followed, about 3:20 to 3:35 p.m."]),
    ("RULED OUT", RED, north.union(r3), "Range 3 and the north end",
     ["Fire was already here at 2:49 p.m.: a NOAA-20", "hotspot sits inside Range 3. The northwest", "wind then pushed the fire away from it."]),
    ("RULED OUT", RED, hull, "Where the fire already was before 3 p.m.",
     ["Burning at 12:17 or 2:49 p.m., before the", "wind shift. Nothing here was \"a kilometre", "away\" from the fire."]),
    ("RULED OUT", RED, east, "The east lobe past the boundary road",
     ["3 to 4.5 km downwind: at a realistic 7 to 14", "km/h, 15 to 30 minutes of warning. Mostly", "outside the base; still burning Oct. 18."]),
]
TW, TH = m.w, m.h
x0s = [54, 54 + TW + 60]
y0s = [200, 200 + TH + 165]
for i, (badge, col, geom, head, body) in enumerate(tiles):
    X, Y = x0s[i % 2], y0s[i // 2]
    dim = Image.blend(base, Image.new("RGBA", base.size, (0, 0, 0, 255)), 0.62)
    mask = Image.new("L", base.size, 0); m.poly(ImageDraw.Draw(mask), geom, fill=255)
    t = Image.composite(base, dim, mask)
    od = ImageDraw.Draw(t)
    m.outline(od, scar, CREAM + (150,), 2)
    m.outline(od, geom, INK + (255,), 9)
    m.outline(od, geom, col + (255,), 5)
    im.alpha_composite(t, (X, Y))
    d = ImageDraw.Draw(im)
    d.rectangle([X - 1, Y - 1, X + TW, Y + TH], outline=GRIDC, width=1)
    bw = d.textlength(badge, font=K(17)) + 24
    d.rounded_rectangle([X + 14, Y + 14, X + 14 + bw, Y + 46], radius=6, fill=col)
    d.text((X + 26, Y + 19), badge, font=K(17), fill=INK)
    d.text((X, Y + TH + 18), head, font=K(23), fill=CREAM)
    for j, l in enumerate(body):
        d.text((X, Y + TH + 56 + j * 27), l, font=M(18.5), fill=CREAM)
# scale on first tile
d.rectangle([x0s[0] + 20, y0s[0] + TH - 30, x0s[0] + 20 + m.pxkm, y0s[0] + TH - 24], fill=CREAM)
d.text((x0s[0] + 20, y0s[0] + TH - 56), "1 km", font=B(16), fill=CREAM)
print(TW, TH)
footer(im, ["Base: Copernicus Sentinel-2, Oct. 19, 2026 (contains modified Copernicus Sentinel data 2026); cream line = burn scar. Fire: NASA FIRMS (Landsat 8, NOAA-20, Oct. 17-18).",
            "Wind: ECCC CZWN. Ranges: OpenStreetMap contributors (ODbL), not verified by DND. A fifth area, a strip just north of Jamieson Lake, remains possible. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"])
im.convert("RGB").save(OUT + "cfb-wainwright-candidate-areas.jpg", quality=91, optimize=True)
print(im.size)
