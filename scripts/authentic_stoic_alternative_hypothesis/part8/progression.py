"""Part 8b: modelled fire progression from ignition to the 3:16 p.m. front for the bracketing cases, and distance from the
modelled 3:16 edge to Range 2 point A and road head B. Writes arrival GeoTIFFs and progression.csv. Usage: python3 progression.py REPO"""
import sys, os, json
import numpy as np, pandas as pd, rasterio
from scipy import ndimage
REPO = sys.argv[1]
src = open(os.path.join(REPO, "scripts/authentic_stoic_alternative_hypothesis/part8/ignition_backcalc.py")).read().split("# candidates:")[0]
sys.argv = ["x", REPO, "40", "240"]; exec(src)
K0 = K; OUTD = os.path.join(REPO, "data/authentic-stoic-stress-test/part8b_ignition")
line = set()
for dd in np.arange(1.4, 2.2001, RES / 2000):
    lo, la, _ = G.fwd(R11[0], R11[1], 80, dd * 1000); i, j = cell(*tf(lo, la))
    if fuel[i, j]: line.add((i, j))
CASES = [("A_calibrated_line_0300", 1.0, 3.0), ("B_1.5x_line_0600", 1.5, 6.0), ("C_2x_line_0715", 2.0, 7.25), ("D_3x_line_0845", 3.0, 8.75)]
pts = {"A_range2": tf(-110.9063, 52.7728), "B_road_head": tf(-110.89965, 52.77045)}
rows = []
for name, mult, t0 in CASES:
    MORNING_MULT = mult
    A = run(0, 0, t0, starts=list(line), tend=15 + 16 / 60)
    l1, l2, s, v = score(A)
    with rasterio.open(os.path.join(OUTD, f"arrival_{name}.tif"), "w", driver="GTiff", height=H, width=W, count=1, dtype="float32", crs=CRS, transform=T, nodata=np.nan, compress="deflate") as o:
        o.write(np.where(np.isfinite(A), A, np.nan).astype("float32"), 1)
    B = A <= 15 + 16 / 60
    D = ndimage.distance_transform_edt(~B) * RES
    r = dict(case=name, ros_multiplier=mult, ignition=f"{int(t0):02d}:{int(round((t0 % 1) * 60)):02d}", misfit_m=s, landsat_to_fire_m=l1, fire_edge_to_landsat_m=l2, viirs_misfit_m=v,
             area_km2_at_1217=round(float((A <= TL).sum()) * RES * RES / 1e6, 2), area_km2_at_1449=round(float((A <= TV).sum()) * RES * RES / 1e6, 2),
             area_km2_at_1516=round(float(B.sum()) * RES * RES / 1e6, 2))
    for k, (x, y) in pts.items():
        i, j = cell(x, y); r[f"edge_to_{k}_m_at_1516"] = int(round(D[i, j]))
    for hh in range(6, 16):
        r[f"area_km2_{hh:02d}00"] = round(float((A <= hh).sum()) * RES * RES / 1e6, 3)
    rows.append(r)
df = pd.DataFrame(rows); df.to_csv(os.path.join(OUTD, "progression.csv"), index=False); print(df.T.to_string())
