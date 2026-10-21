import sys, subprocess, os, math
sys.path.insert(0, "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/vis")
from pr import *
OUT = "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/vis/"
FR = OUT + "frames/"; os.makedirs(FR, exist_ok=True)
for f in os.listdir(FR): os.remove(FR + f)

m = Map(-110.962, -110.858, 52.737, 52.797, 128)
b4 = m.base("2026-10-04"); b19 = m.base("2026-10-19")
TOP, BOT = 150, 96
CW, CH = m.w, m.h + TOP + BOT
scar = scar_main(); hull = preshift_hull(); bnd = band()
L, V, _ = detections()
o = osm(); r2 = o[o["name"] == "Range 2 (Grenade)"].geometry.iloc[0]; r3 = o[o["name"] == "Range 3"].geometry.iloc[0]
g = pd.read_csv(ACH + "scar_grid_upwind_distances.csv")
g = g[g.A_hull_306.notna()]
cells = [(m.P(r.y, r.x), r.A_hull_306) for r in g.itertuples()]
cs = 0.05 * m.pxkm / 2 + 0.6
# SE flank of the hull: hull boundary points whose outward normal faces ~130 deg
hb = list(hull.exterior.coords)

frames = []


def frame(basei, clock, caption, sub, draw=None, hold=1):
    im = Image.new("RGBA", (CW, CH), BG + (255,))
    im.alpha_composite(basei, (0, TOP))
    lay = Image.new("RGBA", (m.w, m.h), (0, 0, 0, 0))
    if draw: draw(lay)
    im.alpha_composite(lay, (0, TOP))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, CW, TOP], fill=BG)
    d.rectangle([0, 0, CW, 5], fill=GOLD)
    d.text((26, 18), clock, font=D(52), fill=GOLD)
    d.text((26, 84), caption, font=K(28), fill=CREAM)
    if sub: d.text((26, 120), sub, font=M(18), fill=MUTED)
    d.rectangle([0, CH - BOT, CW, CH], fill=NAVY)
    d.text((26, CH - BOT + 16), "Sentinel-2 (Copernicus) · NASA FIRMS · NOAA GOES-18 · ECCC CZWN · OpenStreetMap (ODbL)", font=M(16), fill=CREAM)
    d.text((26, CH - BOT + 42), "Spread shown as distance downwind, not exact times. Ranges not verified by DND.", font=M(16), fill=MUTED)
    d.text((CW - 26, CH - 18), "Kevin Duska Jr. (Prime Rogue Inc.)", font=B(16), fill=GOLD, anchor="rb")
    # scale bar
    d.rectangle([CW - 26 - m.pxkm, TOP + m.h - 30, CW - 26, TOP + m.h - 23], fill=CREAM)
    d.text((CW - 26 - m.pxkm, TOP + m.h - 56), "1 km", font=B(17), fill=CREAM)
    for _ in range(hold):
        frames.append(im.convert("RGB"))


def dots(lay, which=("L",)):
    dd = ImageDraw.Draw(lay)
    if "L" in which:
        for r in L.itertuples():
            x, y = m.P(r.latitude, r.longitude); dd.rectangle([x - 4, y - 4, x + 4, y + 4], fill=YEL + (255,))
    if "V" in which:
        for r in V.itertuples():
            x, y = m.P(r.latitude, r.longitude); h = 0.1875 * m.pxkm
            dd.rectangle([x - h, y - h, x + h, y + h], outline=BLUE + (255,), width=3)


def hullf(lay, a=60):
    dd = ImageDraw.Draw(lay); m.poly(dd, hull, fill=(255, 140, 0, a)); m.outline(dd, hull, YEL + (255,), 3, dash=(12, 8))


def wind(lay, frm, col, lab, pos):
    dd = ImageDraw.Draw(lay)
    to = math.radians((frm + 180) % 360)
    x0, y0 = m.P(*pos); L_ = 1.4 * m.pxkm
    arrow(dd, (x0, y0), (x0 + L_ * math.sin(to), y0 - L_ * math.cos(to)), col + (255,), 10, 32)
    label(dd, (x0 - 10, y0 + 22), lab, col, 19)


def ranges(lay):
    dd = ImageDraw.Draw(lay)
    m.outline(dd, r3, (255, 255, 255, 255), 3)
    rx, ry = m.P(r2.centroid.y, r2.centroid.x)
    dd.ellipse([rx - 11, ry - 11, rx + 11, ry + 11], outline=(255, 255, 255, 255), width=4)
    label(dd, (rx + 18, ry - 30), "Range 2 (Grenade)", CREAM, 17)
    x, y = m.P(52.7839, -110.9034); label(dd, (x + 36, y - 12), "Range 3", CREAM, 17)


def burned(lay, D, front=350):
    px = lay.load(); dd = ImageDraw.Draw(lay)
    for (x, y), dist in cells:
        if dist <= D - front:
            dd.rectangle([x - cs, y - cs, x + cs, y + cs], fill=(60, 18, 10, 170))
        elif dist <= D:
            dd.rectangle([x - cs, y - cs, x + cs, y + cs], fill=(255, 120, 20, 235))


# 1 noon
frame(b4, "12:17 p.m.", "Landsat 8 sees a fire line on the range", "Yellow: 59 fire detections, about 1.9 km long. Base: Sentinel-2, Oct. 4.",
      lambda l: (dots(l), ranges(l)), hold=10)
# 2 2:49
frame(b4, "2:49 p.m.", "The fire has crept north", "Blue: NOAA-20 fire pixels. A southwest wind pushes it north and northeast.",
      lambda l: (hullf(l), dots(l, ("L", "V")), ranges(l), wind(l, 235, CREAM, "Southwest wind", (52.757, -110.958))), hold=10)
# 3 3:16
frame(b4, "3:16 p.m.", "An 82 km/h gust. The wind turns northwest", "The fire's long southeast side becomes its front.",
      lambda l: (hullf(l, 90), ranges(l), wind(l, 306, RED, "Northwest wind", (52.7925, -110.889))), hold=10)
# 4 sweep
steps = list(range(0, 4900, 200))
for i, DD in enumerate(steps):
    km_ = DD / 1000
    frame(b4, "about 3:20 to 3:35 p.m.", "The fire runs southeast", f"{km_:.1f} km downwind of where it was at the shift. NOAA's GOES-18: 1,215 MW at 3:30.",
          lambda l, DD=DD: (hullf(l, 90), burned(l, DD), m.outline(ImageDraw.Draw(l), bnd, INK + (255,), 8), m.outline(ImageDraw.Draw(l), bnd, TEAL + (255,), 4), ranges(l), wind(l, 306, RED, "Northwest wind", (52.7925, -110.889)),
                          label(ImageDraw.Draw(l), (m.P(52.7605, -110.897)[0], m.P(52.7605, -110.897)[1]), "About 1 km\ndownwind", TEAL, 19)),
          hold=2 if not (600 <= DD <= 1500) else 4)
# 5 band
frame(b19, "Oct. 19", "The burn scar, and the area 1 km downwind", "If the fire was \"a kilometre away\" when the wind turned, as Maj.-Gen. Rutland said.",
      lambda l: (m.poly(ImageDraw.Draw(l), bnd, fill=TEAL + (45,)), m.outline(ImageDraw.Draw(l), bnd, INK + (255,), 9), m.outline(ImageDraw.Draw(l), bnd, TEAL + (255,), 4),
                 m.outline(ImageDraw.Draw(l), scar, CREAM + (220,), 2), ranges(l),
                 label(ImageDraw.Draw(l), (m.P(52.7668, -110.917)[0], m.P(52.7668, -110.917)[1]), "Most likely area", TEAL, 20)), hold=24)

for i, f in enumerate(frames):
    f.save(FR + f"f{i:04d}.png")
print(len(frames), frames[0].size)
# GIF at 1000 px wide, 250 ms per frame
gw = 1000; gh = int(CH * gw / CW)
small = [f.resize((gw, gh), Image.LANCZOS).quantize(colors=200, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
small[0].save(OUT + "cfb-wainwright-where-the-wind-turned.gif", save_all=True, append_images=small[1:], duration=250, loop=0, optimize=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "4", "-i", FR + "f%04d.png", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", OUT + "cfb-wainwright-where-the-wind-turned.mp4"], check=True)
frames[-1].save(OUT + "_anim_last.png"); frames[12].save(OUT + "_anim_mid.png"); frames[50].save(OUT + "_anim_sweep.png")
