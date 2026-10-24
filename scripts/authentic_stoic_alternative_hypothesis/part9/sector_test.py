import os
"""Is any licensed gas line or well inside Range 11's firing sector, within the C16's reach?
Range 11 position and inferred sector (east into Permanent Danger Area 2) as in part 8. Writes sector_test.json."""
import json, numpy as np, pandas as pd
from shapely.geometry import shape, Polygon, Point
from shapely.ops import nearest_points
from pyproj import Geod
G = Geod(ellps="WGS84"); R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../data/"); R11 = (-110.9577, 52.7678)
F = json.load(open(R + "reference/aer_pipelines_near_site.geojson"))["features"]
W = pd.read_csv(R + "infrastructure/wells_within_5km_of_scar.csv")
out = {"range11": R11, "reach_m": 2500, "c16_max_range_m_approx": 2200, "sectors": []}
for a0, a1, lab in [(40, 120, "likely sector"), (20, 160, "generous"), (0, 180, "all bearings east")]:
    S = Polygon([R11] + [G.fwd(*R11, a, 2500)[:2] for a in np.arange(a0, a1 + .1, 2)] + [R11])
    out["sectors"].append({"bearings": [a0, a1], "label": lab,
        "operating_gas_lines": [f["properties"]["LIC_LI_NO"] for f in F if shape(f["geometry"]).intersects(S) and f["properties"]["SEG_STATUS"] == "Operating"],
        "any_lines": [f["properties"]["LIC_LI_NO"] for f in F if shape(f["geometry"]).intersects(S)],
        "wells": [str(r.Well_Lic) for r in W.itertuples() if S.contains(Point(r.lon, r.lat))]})
near = []
for f in F:
    q = nearest_points(Point(R11), shape(f["geometry"]))[1]; az, _, d = G.inv(*R11, q.x, q.y)
    near.append({"line": f["properties"]["LIC_LI_NO"], "status": f["properties"]["SEG_STATUS"], "m": round(d), "bearing": round(az % 360)})
out["nearest_lines_to_range11"] = sorted(near, key=lambda x: x["m"])[:5]
for k, p in {"range2_point_A": (-110.90632, 52.77279), "road_head_B": (-110.89965, 52.77045), "line_58333-78_west_end": (-110.90429, 52.77186), "well_1-11_registered": (-110.898943, 52.773642)}.items():
    az, _, d = G.inv(*R11, *p); out.setdefault("range11_to", {})[k] = {"m": round(d), "bearing": round(az % 360)}
json.dump(out, open("sector_test.json", "w"), indent=1); print(json.dumps(out, indent=1))
