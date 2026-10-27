"""Ranges at their official grid references in the 2024 Wainwright Range Standing Orders (MGRS zone 12U), against the
Oct. 17, 2026 burn and working model v4. Usage: python3 scripts/reference/rso_map.py [P4ROOT]
P4ROOT: folder holding the v4 post-front arrival grids (p4_v4_<case>/arr_<run>.npy, meta.npy), as made by model_v4/post_front.py.
Outputs: data/reference/range_standing_orders_2024/{rso_points.csv, rso_v4_arrival.csv, fig_rso_ranges.png}."""
import os, sys, numpy as np, pandas as pd, geopandas as gpd, rasterio, mgrs
from rasterio.warp import reproject, Resampling
from shapely.geometry import Point
from pyproj import Transformer
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; import matplotlib.patheffects as pe
from matplotlib.colors import LightSource, LinearSegmentedColormap
from matplotlib.patches import Patch, Circle
from matplotlib.lines import Line2D
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "data/reference/range_standing_orders_2024"); os.makedirs(OUT, exist_ok=True)
P4 = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/"
UTM = 32612; M = mgrs.MGRS()
RSO = [("Range 2", "Grenade Range", "WD 06686 46913", "Ch. 1 para 51b"), ("Range 3", "Jungle Lane", "WD 06434 48187", "para 51c"),
       ("Range 10", "Anti-Tank Weapons Range", "WD 02626 48365", "para 51h"), ("Range 11", "Grenade Launcher Range (AGLS and M203)", "WD 02612 46459", "para 51i"),
       ("Range 13", "Anti-Tank Weapons Range", "WD 02598 45534", "para 51j"), ("Range 14", "Demolition Range", "WD 03975 43748", "para 51k"),
       ("Range 15", "Field Firing Range", "WD 06783 46728", "para 51l"), ("Range 19", "Field Firing Range", "WD 03645 43989", "para 51n"),
       ("Range 20", "Sub Cal Range", "WD 03563 49209", "para 51o"), ("Range 22", "HHAA Static", "WD 01533 46517", "para 51q"),
       ("Range 15 barrier", "Yellow and Fireguard (sentry, flag, swing barrier)", "WD 0677 4673", "Annex H"),
       ("Range 15 barrier", "Yellow and Fireguard, south end (flag, chain barrier)", "WD 0801 4106", "Annex H"),
       ("Range 15 barrier", "Entrance Range 14 (flag, swing barrier)", "WD 0397 4374", "Annex H")]
P = pd.DataFrame([dict(name=n, description=d, grid_ref=g, source=s, **dict(zip(("lat", "lon"), [round(v, 5) for v in M.toLatLon("12U" + g.replace(" ", ""))]))) for n, d, g, s in RSO])
g = gpd.GeoDataFrame(P, geometry=gpd.points_from_xy(P.lon, P.lat), crs=4326).to_crs(UTM)
s26 = gpd.read_file(os.path.join(REPO, "data/infrastructure/scar_patches_revised.geojson")).to_crs(UTM).union_all()
F = pd.read_csv(os.path.join(REPO, "data/firms/detections.csv")); F = F[F.acq_datetime_mdt == "2026-10-17 12:17 MDT"]
p26 = gpd.GeoSeries(gpd.points_from_xy(F.longitude, F.latitude), crs=4326).to_crs(UTM)
INF = {"Range 2 point (OSM, earlier inference)": (52.7728, -110.9063), "Road head (earlier inference)": (52.7705, -110.8996)}
infg = {k: gpd.GeoSeries([Point(lo, la)], crs=4326).to_crs(UTM).iloc[0] for k, (la, lo) in INF.items()}
P["in_2026_burn"] = [bool(s26.contains(p)) for p in g.geometry]; P["to_2026_burn_edge_m"] = [round(s26.boundary.distance(p)) for p in g.geometry]
P["to_noon_fire_line_km"] = [round(p.distance(p26.union_all()) / 1000, 2) for p in g.geometry]
P["to_range2_point_osm_m"] = [round(p.distance(infg["Range 2 point (OSM, earlier inference)"])) for p in g.geometry]
P["to_road_head_m"] = [round(p.distance(infg["Road head (earlier inference)"])) for p in g.geometry]
P.to_csv(os.path.join(OUT, "rso_points.csv"), index=False)
# ---- v4 arrival (front at the fire 3:16 p.m.) at the official Range 2 and Range 15 grid references, and the earlier points
fit = pd.read_csv(os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4/fit_post/fit_post_all.csv")); mx = fit.jaccard.max()
tf = Transformer.from_crs(4326, 3400, always_xy=True)
Q = {"Range 2 (RSO grid)": (52.77200, -110.90089), "Range 15 (RSO grid)": (52.77034, -110.89946), "Range 2 point (OSM, earlier)": (52.7728, -110.9063), "Road head (earlier)": (52.7705, -110.8996)}
vals = {k: [] for k in Q}; W = []
for r in fit.itertuples():
    d = os.path.join(P4, f"p4_v4_{r.case}"); m = np.load(os.path.join(d, "meta.npy")); a = np.load(os.path.join(d, f"arr_{r.run}.npy")); W.append(np.exp((r.jaccard - mx) / 0.05))
    for k, (la, lo) in Q.items():
        x, y = tf.transform(lo, la); vals[k].append(a[int((m[1] - y) // m[2]), int((x - m[0]) // m[2])])
W = np.array(W); rows = []
def wq(v, w, q):
    o = np.argsort(v); c = np.cumsum(w[o]) / w[o].sum(); return v[o][min(np.searchsorted(c, q), len(v) - 1)]
hm = lambda mnt: f"3:{int(round(mnt)):02d} p.m." if mnt < 60 else f"{mnt:.0f} min after 3"
for k, v in vals.items():
    v = np.array(v, float); ok = np.isfinite(v)
    rows.append(dict(point=k, runs_reaching=f"{ok.sum()}/{len(v)}", weighted_median=hm(wq(v[ok], W[ok], 0.5)), weighted_p10=hm(wq(v[ok], W[ok], 0.1)), weighted_p90=hm(wq(v[ok], W[ok], 0.9)),
                     unweighted_median=hm(np.median(v[ok])), share_first_reached_345_400_weighted_pct=round(100 * W[ok & (v >= 45) & (v < 60)].sum() / W.sum(), 1)))
A = pd.DataFrame(rows); A.to_csv(os.path.join(OUT, "rso_v4_arrival.csv"), index=False)
# ---- map
x0, y0, x1, y1 = s26.bounds; x0 -= 4200; y0 -= 2600; x1 += 1500; y1 += 900
RES = 15.0; Wd, Hh = int((x1 - x0) / RES), int((y1 - y0) / RES); TT = rasterio.Affine(RES, 0, x0, 0, -RES, y1)
z = np.full((Hh, Wd), np.nan, "float32")
with rasterio.open(os.path.join(REPO, "data/dem/mrdem30_dtm_native.tif")) as r: reproject(rasterio.band(r, 1), z, dst_transform=TT, dst_crs=UTM, dst_nodata=np.nan, resampling=Resampling.bilinear)
zf = np.where(np.isfinite(z), z, np.nanmedian(z))
cm = LinearSegmentedColormap.from_list("t", ["#d5e3cc", "#ebe8c9", "#ecdcb9", "#dcc4a2"])
shade = LightSource(315, 40).shade(zf, cmap=cm, blend_mode="soft", vert_exag=8, dx=RES, dy=RES, vmin=np.nanpercentile(z, 1), vmax=np.nanpercentile(z, 99.5))
osm = gpd.read_file(os.path.join(REPO, "data/infrastructure/osm_infrastructure_ODbL.geojson")).to_crs(UTM)
pda = osm[osm.military.fillna("") == "danger_area"]; roads = osm[osm.kind == "road"]
st = lambda c, s=8.5: dict(color=c, fontsize=s, weight="bold", path_effects=[pe.withStroke(linewidth=2.6, foreground="white")])
fig, ax = plt.subplots(figsize=(11, 9.5)); EXT = (x0, x1, y0, y1)
ax.imshow(shade, extent=EXT); ax.contour(np.flipud(zf), levels=np.arange(560, 760, 10), extent=EXT, origin="lower", colors="#8a6a45", linewidths=0.3, alpha=0.5)
C26 = "#d1495b"
gpd.GeoSeries([s26]).plot(ax=ax, color=C26, alpha=0.3, lw=0); gpd.GeoSeries([s26]).boundary.plot(ax=ax, color=C26, lw=1.1)
roads.plot(ax=ax, color="#555", lw=0.6, alpha=0.8); pda.boundary.plot(ax=ax, color="#d97b00", lw=1.3, ls=":")
r11 = g[g.name == "Range 11"].geometry.iloc[0]
ax.add_patch(Circle((r11.x, r11.y), 2200, fill=False, ec="#444", lw=1, ls=(0, (6, 4))))
ax.text(r11.x - 2150, r11.y + 2350, "2.2 km from the Range 11 grid reference\n(about the maximum range of a 40 mm AGL)", **st("#444", 7.5))
ax.scatter(p26.x, p26.y, s=8, marker="s", color="#8b1e2d", zorder=4)
for _, r in g.iterrows():
    bar = r["name"] == "Range 15 barrier"
    ax.plot(r.geometry.x, r.geometry.y, "^" if bar else "D", ms=8, mfc="#f2c14e" if bar else "white", mec="#111" if bar else "#5b2a7a", mew=1.6, zorder=6)
    if bar and "Yellow and Fireguard (" in r["description"]: continue
    lab = ("R15 barrier: " + r["description"].split(" (")[0]) if bar else r["name"]
    dx, dy = {"Range 2": (-900, 120), "Range 15": (110, -170), "Range 14": (100, -180)}.get(r["name"], (90, 60))
    ax.text(r.geometry.x + dx, r.geometry.y + dy, lab, zorder=7, **st("#111" if bar else "#5b2a7a", 8))
for k, q in infg.items(): ax.plot(q.x, q.y, "o", ms=6, mfc="none", mec="k", mew=1.2, zorder=6)
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
ax.plot([x1 - 1600, x1 - 600], [y0 + 500] * 2, color="k", lw=3); ax.text(x1 - 1100, y0 + 620, "1 km", ha="center", **st("k", 9))
leg = [Line2D([], [], marker="D", ls="", mfc="white", mec="#5b2a7a", mew=1.6, ms=8, label="Range at its grid reference (2024 RSO, ch. 1 para 51)"),
       Line2D([], [], marker="^", ls="", mfc="#f2c14e", mec="#111", mew=1.6, ms=8, label="Range 15 sentry/flag/barrier points (RSO Annex H)"),
       Line2D([], [], marker="o", ls="", mfc="none", mec="k", ms=6, label="Earlier inferred points: Range 2 (OSM) and road head"),
       Line2D([], [], marker="s", ls="", color="#8b1e2d", ms=4, label="Oct. 17, 2026, 12:17 p.m. Landsat fire pixels"),
       Patch(color=C26, alpha=0.45, label="Oct. 17, 2026 burn (Sentinel-2)"),
       Line2D([], [], color="#d97b00", lw=1.3, ls=":", label="Permanent danger areas (OSM)"), Line2D([], [], color="#555", lw=0.8, label="Tracks (OSM)")]
ax.legend(handles=leg, loc="lower left", fontsize=7.5, framealpha=0.92)
ax.set_title("PDA 2, CFB Wainwright: ranges at their official grid references (2024 Range Standing Orders) and the Oct. 17, 2026 burn", fontsize=10, loc="left")
fig.text(0.01, 0.012, "Grid references: 3 CDSB Edmonton Det Wainwright Range and Training Area Standing Orders, 2024 edition, converted from MGRS zone 12U. A grid reference marks one point of a range (likely its firing point or entrance), not its whole area.\n"
         "Burn: Prime Rogue fire archive (Sentinel-2, Oct. 19). Terrain: NRCan MRDEM-30. Detections: NASA FIRMS. Danger areas and tracks: OpenStreetMap (ODbL), not official.", fontsize=6.8)
fig.tight_layout(rect=(0, 0.035, 1, 1)); fig.savefig(os.path.join(OUT, "fig_rso_ranges.png"), dpi=150)
print(P[["name", "description", "lat", "lon", "in_2026_burn", "to_2026_burn_edge_m", "to_noon_fire_line_km", "to_road_head_m"]].to_string(index=False)); print(A.to_string(index=False))
