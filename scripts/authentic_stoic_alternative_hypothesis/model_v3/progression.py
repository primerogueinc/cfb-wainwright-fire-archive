"""Working model v3, step 2: spread from ignition to the 3:16 p.m. wind shift for four bracketing cases from fit_shape.py,
and where the fire's edge was at 3:16. Usage: python3 progression.py REPO
Writes model_v3/arrival_prefront_<case>.tif (hours since midnight Oct. 17) and progression.csv."""
import sys, os, json
import numpy as np, pandas as pd, rasterio
REPO = sys.argv[1]
src = open(os.path.join(REPO, "scripts/authentic_stoic_alternative_hypothesis/part8/ignition_backcalc.py")).read().split("# candidates:")[0]
src = src.replace("lb = 1.1 * max(ws, 1) ** 0.464", "lb = max(1.0, LBM * 1.1 * max(ws, 1) ** 0.464)")
LBM = 1.0
sys.argv = ["x", REPO, "40", "240"]; exec(src)
OUTD = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v3")
line = set()
for dd in np.arange(1.4, 2.2001, RES / 2000):
    lo, la, _ = G.fwd(R11[0], R11[1], 80, dd * 1000); i, j = cell(*tf(lo, la))
    if fuel[i, j]: line.add((i, j))
CASES = [("v3a_1.5x_lb2.0_0330", 1.5, 2.0, 3.5), ("v3b_2x_lb1.5_0630", 2.0, 1.5, 6.5), ("v3c_3x_lb2.5_0700", 3.0, 2.5, 7.0), ("v3d_3x_lb3.0_0530", 3.0, 3.0, 5.5)]
PTS = {"A_range2": (-110.9063, 52.7728), "B_road_head": (-110.8996, 52.7705), "well_1-11_registered": (-110.898943, 52.773642), "line_58333-78_west_end": (-110.90429, 52.77186)}
import geopandas as gpd
from shapely.geometry import shape
gas = gpd.read_file(os.path.join(REPO, "data/reference/aer_pipelines_near_site.geojson")); gas = gas[gas.SEG_STATUS == "Operating"].to_crs(CRS)
gas_m = features.rasterize([(g, 1) for g in gas.geometry], out_shape=(H, W), transform=T, fill=0, dtype="uint8", all_touched=True).astype(bool)
D_gas = ndimage.distance_transform_edt(~gas_m) * RES
rows = []
for name, mult, lbm, t0 in CASES:
    MORNING_MULT, LBM = mult, lbm
    A = run(0, 0, t0, starts=sorted(line), tend=15 + 16 / 60)
    f = fit_ = score(A)
    with rasterio.open(os.path.join(OUTD, f"arrival_prefront_{name}.tif"), "w", driver="GTiff", height=H, width=W, count=1, dtype="float32", crs=CRS, transform=T, nodata=np.nan, compress="deflate") as o:
        o.write(np.where(np.isfinite(A), A, np.nan).astype("float32"), 1)
    B = A <= 15 + 16 / 60; D = ndimage.distance_transform_edt(~B) * RES
    r = dict(case=name, ros_multiplier=mult, lb_multiplier=lbm, ignition=f"{int(t0):02d}:{int(round((t0 % 1) * 60)):02d}",
             area_km2_1217=round(float((A <= TL).sum()) * RES * RES / 1e6, 2), area_km2_1449=round(float((A <= TV).sum()) * RES * RES / 1e6, 2), area_km2_1516=round(float(B.sum()) * RES * RES / 1e6, 2),
             nearest_gas_line_m_at_1217=int(D_gas[A <= TL].min()), nearest_gas_line_m_at_1516=int(D_gas[B].min()))
    for k, (lo, la) in PTS.items():
        i, j = cell(*tf(lo, la)); r[f"edge_to_{k}_m_at_1516"] = int(round(D[i, j]))
    for hh in range(4, 16):
        r[f"area_km2_{hh:02d}00"] = round(float((A <= hh).sum()) * RES * RES / 1e6, 3)
    rows.append(r); print(name, r, flush=True)
pd.DataFrame(rows).to_csv(os.path.join(OUTD, "progression.csv"), index=False)
