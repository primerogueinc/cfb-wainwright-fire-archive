"""Prime Rogue house style + shared geodata for the Oct. 21 location graphics."""
import math, numpy as np, pandas as pd, geopandas as gpd, rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from shapely.geometry import box, Point
from shapely.ops import unary_union

REPO = "/home/claude/cfb-wainwright-fire-archive/"
ACH = "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/ach/"
F = "/usr/share/fonts/opentype/inter/"
BG = (28, 20, 15); PANEL = (37, 26, 20); GOLD = (212, 175, 104); CREAM = (238, 230, 214)
MUTED = (169, 155, 132); NAVY = (30, 52, 82); RED = (224, 96, 60); BLUE = (79, 141, 214)
YEL = (255, 214, 0); TEAL = (64, 224, 208); INK = (20, 14, 10); GRIDC = (53, 40, 32)


def font(n, s):
    return ImageFont.truetype(F + n, int(s))


B = lambda s: font("Inter-Bold.otf", s)
M = lambda s: font("Inter-Medium.otf", s)
K = lambda s: font("Inter-Black.otf", s)
D = lambda s: font("InterDisplay-Black.otf", s)

_LOGO = Image.open(REPO + "data/graphics_published/oct20_flank_became_the_front/cfb-wainwright-burn-pattern.jpg").crop((1688, 1203, 1772, 1287))


def canvas(w, h, kicker, title, sub=None):
    im = Image.new("RGBA", (w, h), BG + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 12, h], fill=GOLD)
    d.text((54, 44), kicker, font=B(20), fill=GOLD)
    d.text((54, 74), title, font=D(46), fill=CREAM)
    if sub:
        for i, l in enumerate(sub.split("\n")):
            d.text((54, 134 + i * 28), l, font=M(19), fill=MUTED)
    return im, d


def footer(im, lines, fh=112):
    w, h = im.size
    d = ImageDraw.Draw(im)
    d.rectangle([0, h - fh, w, h], fill=NAVY)
    d.rectangle([0, h - fh, w, h - fh + 5], fill=GOLD)
    for i, l in enumerate(lines):
        d.text((54, h - fh + 20 + i * 25), l, font=M(16.5), fill=CREAM)
    d.text((54, h - 22), "PRIME ROGUE", font=K(19), fill=GOLD, anchor="lb")
    im.paste(_LOGO, (w - 84 - 36, h - fh + (fh - 84) // 2 + 2))


def label(d, xy, text, col=CREAM, size=17, pad=7, anchor="la", bg=INK, alpha=None):
    x, y = xy
    lines = text.split("\n")
    f = B(size)
    lw = max(d.textlength(l, font=f) for l in lines)
    lh = size + 6
    hgt = lh * len(lines)
    if anchor == "ra":
        x -= lw
    elif anchor == "ma":
        x -= lw / 2
    d.rounded_rectangle([x - pad, y - pad + 2, x + lw + pad, y + hgt + pad - 2], radius=5, fill=bg)
    for i, l in enumerate(lines):
        d.text((x, y + i * lh), l, font=f, fill=col)
    return (x - pad, y - pad, x + lw + pad, y + hgt + pad)


def arrow(d, p0, p1, col, width=8, head=26):
    d.line([p0, p1], fill=col, width=width)
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    l, r = a + math.radians(150), a - math.radians(150)
    d.polygon([p1, (p1[0] + head * math.cos(l), p1[1] + head * math.sin(l)), (p1[0] + head * math.cos(r), p1[1] + head * math.sin(r))], fill=col)


class Map:
    """Equal-distance map window in lon/lat with a Sentinel-2 false-colour base."""

    def __init__(self, W, E, S, N, pxkm, date="2026-10-19"):
        self.W, self.E, self.S, self.N = W, E, S, N
        lat0 = (S + N) / 2
        self.kx = 111.32 * math.cos(math.radians(lat0)); self.ky = 111.2
        self.w = int(round((E - W) * self.kx * pxkm)); self.h = int(round((N - S) * self.ky * pxkm))
        self.pxkm = pxkm; self.date = date

    def P(self, lat, lon):
        return ((lon - self.W) / (self.E - self.W) * self.w, (self.N - lat) / (self.N - self.S) * self.h)

    def base(self, date=None, bright=1.0):
        date = date or self.date
        import os
        Dd = REPO + f"data/copernicus/manual_exports/{date}/L1C/{date}-00_00_{date}-23_59_Sentinel-2_L1C_%s_(Raw).tiff"
        if not os.path.exists(Dd % "B12"):
            Dd = REPO + f"data/copernicus/manual_exports/{date}/{date}-00_00_{date}-23_59_Sentinel-2_L2A_%s_(Raw).tiff"
        chans = []
        for b in ("B12", "B8A", "B04"):
            with rasterio.open(Dd % b) as r:
                a = r.read(1, window=from_bounds(self.W, self.S, self.E, self.N, r.transform), out_shape=(self.h, self.w), resampling=Resampling.bilinear)
                wide = r.read(1, window=from_bounds(-111.05, 52.68, -110.80, 52.86, r.transform))
            lo, hi = np.nanpercentile(wide, 1), np.nanpercentile(wide, 99.3)
            chans.append(np.clip((a - lo) / (hi - lo), 0, 1))
        rgb = np.dstack(chans) ** 0.85 * bright
        return Image.fromarray((np.clip(rgb, 0, 1) * 255).astype("uint8")).convert("RGBA")

    def poly(self, d, geom, **kw):
        geoms = getattr(geom, "geoms", [geom])
        for g in geoms:
            if g.geom_type == "Polygon":
                d.polygon([self.P(y, x) for x, y in g.exterior.coords], **kw)
            elif g.geom_type == "LineString":
                d.line([self.P(y, x) for x, y in g.coords], fill=kw.get("outline"), width=kw.get("width", 2))

    def outline(self, d, geom, col, width=3, dash=None):
        geoms = getattr(geom, "geoms", [geom])
        for g in geoms:
            rings = [g.exterior] if g.geom_type == "Polygon" else [g]
            for ring in rings:
                pts = [self.P(y, x) for x, y in ring.coords]
                if not dash:
                    d.line(pts, fill=col, width=width, joint="curve")
                else:
                    dashed(d, pts, col, width, dash)


def dashed(d, pts, col, width, dash):
    on, off = dash; acc = 0; draw = True
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        pos = 0
        while pos < L:
            step = min((on if draw else off) - acc, L - pos)
            if draw:
                t0, t1 = pos / L, (pos + step) / L
                d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], fill=col, width=width)
            pos += step; acc += step
            if acc >= (on if draw else off):
                acc = 0; draw = not draw


# ---------- shared data
P3400 = "EPSG:3400"


def scar_main():
    s = gpd.read_file(REPO + "data/infrastructure/scar_patches_revised.geojson").to_crs(4326)
    return max(s.geometry, key=lambda g: g.area)


def detections():
    d = pd.read_csv(REPO + "data/firms/detections.csv")
    d = d[(d.latitude.between(52.7, 52.85)) & (d.longitude.between(-111.0, -110.82))]
    L = d[d.acq_datetime_mdt == "2026-10-17 12:17 MDT"]
    V = d[d.acq_datetime_mdt == "2026-10-17 14:49 MDT"]
    O = d[d.acq_date == "2026-10-18"]
    return L, V, O


def preshift_hull():
    L, V, _ = detections()
    pts = gpd.GeoSeries(gpd.points_from_xy(pd.concat([L.longitude, V.longitude]), pd.concat([L.latitude, V.latitude])), crs=4326).to_crs(P3400)
    h = pts.unary_union.convex_hull
    m = gpd.GeoSeries([scar_main()], crs=4326).to_crs(P3400).iloc[0]
    return gpd.GeoSeries([h.intersection(m)], crs=P3400).to_crs(4326).iloc[0]


def band(col="A_hull_306", lo=600, hi=1500):
    g = pd.read_csv(ACH + "scar_grid_upwind_distances.csv")
    g = g[g[col].between(lo, hi)]
    pts = gpd.GeoSeries(gpd.points_from_xy(g.x, g.y), crs=4326).to_crs(P3400)
    u = unary_union([p.buffer(26, cap_style=3) for p in pts]).buffer(30).buffer(-30)
    m = gpd.GeoSeries([scar_main()], crs=4326).to_crs(P3400).iloc[0]
    return gpd.GeoSeries([u.intersection(m)], crs=P3400).to_crs(4326).iloc[0]


def osm():
    o = gpd.read_file(REPO + "data/infrastructure/osm_infrastructure_ODbL.geojson")
    return o


def km_to_px(m, km):
    return km * m.pxkm
