#!/usr/bin/env python3
"""Plot the Sentinel-2 burn scar against infrastructure on and around CFB Wainwright.

Inputs:
  * data/copernicus/burn_scar.geojson   (from sentinel2_burn.py)
  * data/firms/detections.csv, data/goes/fire_timeline.csv (detections)
  * Alberta Energy Regulator ST37 well list (free shapefile package)
  * OpenStreetMap via the Overpass API: roads, pipelines, power lines,
    military land use, water, buildings, place names

Revises the scar: splits it into patches, identifies the main Oct 17 run
(the patch holding the 12:17 p.m. Landsat line), flags a patch matching the
Oct 14 VIIRS detection, drops specks under 2 ha, and measures the main run.

Outputs go to data/infrastructure/.
"""

from __future__ import annotations

import csv
import io
import json
import math
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "infrastructure"
CACHE = ROOT / "data" / "infrastructure" / "cache"   # git-ignored
BBOX = dict(west=-111.25, south=52.55, east=-110.55, north=52.98)
UTM = "EPSG:32612"
OCT14_VIIRS = (-110.939, 52.755)
MIN_PATCH_KM2 = 0.02
UA = {"User-Agent": "prime-rogue-cfb-wainwright-archive/1.0 (+https://github.com/primerogueinc/cfb-wainwright-fire-archive)"}


def http(url, data=None, timeout=300):
    req = urllib.request.Request(url, data=data, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ------------------------------------------------------------------ AER wells

def aer_wells():
    import geopandas as gpd

    CACHE.mkdir(parents=True, exist_ok=True)
    page = http("https://www.aer.ca/data-and-performance-reports/statistical-reports/st37").decode("utf-8", "replace")
    links = sorted(set(re.findall(r'href="([^"]+\.zip)"', page, flags=re.I)))
    links = [urllib.parse.urljoin("https://www.aer.ca/", l) for l in links]
    shp_links = [l for l in links if re.search(r"(shp|sh_|shape|gcs)", l, re.I)] or links
    print("ST37 links:", shp_links, flush=True)
    if not shp_links:
        raise RuntimeError("no ST37 zip link found on the AER page")
    url = next((l for l in shp_links if re.search(r"gcs", l, re.I)), shp_links[0])
    zpath = CACHE / Path(urllib.parse.urlparse(url).path).name
    if not zpath.exists():
        zpath.write_bytes(http(url, timeout=900))
    with zipfile.ZipFile(zpath) as z:
        z.extractall(CACHE / "st37")
    shps = [p for p in (CACHE / "st37").rglob("*.shp")]
    surf = [p for p in shps if re.search(r"surf", p.name, re.I)] or shps
    # prefer the geographic (GCS_NAD83) version
    surf.sort(key=lambda p: (not re.search(r"gcs|nad83", str(p), re.I), len(str(p))))
    print("surface-hole shapefile:", surf[0], flush=True)
    g = gpd.read_file(surf[0], bbox=(BBOX["west"], BBOX["south"], BBOX["east"], BBOX["north"]))
    if g.crs is None:
        g = g.set_crs("EPSG:4269")
    g = g.to_crs("EPSG:4326")
    g = g[g.geometry.x.between(BBOX["west"], BBOX["east"]) & g.geometry.y.between(BBOX["south"], BBOX["north"])]
    return g, url


def well_category(row) -> str:
    text = " ".join(str(v) for v in row.values if isinstance(v, str)).upper()
    if "ABD" in text or "ABANDON" in text or "RECCERT" in text or "RECLAIM" in text:
        return "abandoned/reclaimed"
    if "SUSP" in text:
        return "suspended"
    if "GAS" in text and ("FLOW" in text or "PUMP" in text or "PROD" in text):
        return "producing gas"
    if ("CR-OIL" in text or "CRUDE" in text or " OIL" in text) and ("PUMP" in text or "FLOW" in text or "PROD" in text):
        return "producing oil"
    return "other/unknown"


# ------------------------------------------------------------------ OSM

def osm():
    s, w, n, e = BBOX["south"], BBOX["west"], BBOX["north"], BBOX["east"]
    q = f"""[out:json][timeout:180];
    (
      way["highway"]({s},{w},{n},{e});
      way["man_made"="pipeline"]({s},{w},{n},{e});
      way["power"="line"]({s},{w},{n},{e});
      way["landuse"="military"]({s},{w},{n},{e});
      relation["landuse"="military"]({s},{w},{n},{e});
      way["military"]({s},{w},{n},{e});
      relation["military"]({s},{w},{n},{e});
      way["natural"="water"]({s},{w},{n},{e});
      relation["natural"="water"]({s},{w},{n},{e});
      way["building"]({s},{w},{n},{e});
      node["place"]({s},{w},{n},{e});
    );
    out geom tags;"""
    for ep in ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"):
        try:
            return json.loads(http(ep, data=urllib.parse.urlencode({"data": q}).encode(), timeout=300)), ep
        except Exception as exc:
            print("overpass failed", ep, exc, flush=True)
    raise RuntimeError("Overpass unavailable")


def osm_to_gdf(data):
    import geopandas as gpd
    from shapely.geometry import LineString, Point, Polygon
    from shapely.ops import polygonize, unary_union

    rows = []
    for el in data["elements"]:
        tags = el.get("tags", {})
        if el["type"] == "node":
            geom = Point(el["lon"], el["lat"])
        elif el["type"] == "way" and "geometry" in el:
            pts = [(p["lon"], p["lat"]) for p in el["geometry"]]
            closed = len(pts) > 3 and pts[0] == pts[-1]
            area_like = closed and any(k in tags for k in ("building", "landuse", "natural", "military"))
            geom = Polygon(pts) if area_like else LineString(pts)
        elif el["type"] == "relation":
            lines = [LineString([(p["lon"], p["lat"]) for p in m["geometry"]])
                     for m in el.get("members", []) if m.get("geometry") and m.get("role") in ("outer", "")]
            polys = list(polygonize(unary_union(lines))) if lines else []
            if not polys:
                continue
            geom = unary_union(polys)
        else:
            continue
        kind = ("building" if "building" in tags else "road" if "highway" in tags else
                "pipeline" if tags.get("man_made") == "pipeline" else "power line" if tags.get("power") == "line" else
                "military" if tags.get("landuse") == "military" or "military" in tags else
                "water" if tags.get("natural") == "water" else "place" if "place" in tags else "other")
        rows.append({"osm_id": f"{el['type']}/{el['id']}", "kind": kind, "name": tags.get("name", ""),
                     "highway": tags.get("highway", ""), "military": tags.get("military", ""),
                     "substance": tags.get("substance", ""), "place": tags.get("place", ""), "geometry": geom})
    return gpd.GeoDataFrame(rows, crs="EPSG:4326")


# ------------------------------------------------------------------ detections

def detections():
    pts = []
    for r in csv.DictReader((ROOT / "data" / "firms" / "detections.csv").open()):
        pts.append({"lon": float(r["longitude"]), "lat": float(r["latitude"]), "source": r["source"],
                    "date": r["acq_datetime_utc"][:10], "time_mdt": r["acq_datetime_mdt"]})
    return pts


# ------------------------------------------------------------------ main

def main() -> int:
    import geopandas as gpd
    from shapely.geometry import Point, shape
    from shapely.ops import unary_union

    OUT.mkdir(parents=True, exist_ok=True)
    scar_fc = json.loads((ROOT / "data" / "copernicus" / "burn_scar.geojson").read_text())
    scar_props = scar_fc["features"][0]["properties"]
    scar_all = shape(scar_fc["features"][0]["geometry"])
    parts = list(getattr(scar_all, "geoms", [scar_all]))
    patches = gpd.GeoDataFrame({"geometry": parts}, crs="EPSG:4326").to_crs(UTM)
    patches["area_km2"] = patches.area / 1e6
    patches = patches[patches.area_km2 >= MIN_PATCH_KM2].reset_index(drop=True)

    dets = detections()
    det_g = gpd.GeoDataFrame(dets, geometry=[Point(d["lon"], d["lat"]) for d in dets], crs="EPSG:4326").to_crs(UTM)
    landsat17 = det_g[(det_g.source == "LANDSAT_NRT") & (det_g.date == "2026-10-17")]
    oct14 = gpd.GeoSeries([Point(*OCT14_VIIRS)], crs="EPSG:4326").to_crs(UTM).iloc[0]

    def label(row):
        if landsat17.within(row.geometry.buffer(100)).any():
            return "main Oct 17 run"
        if row.geometry.distance(oct14) < 750 and row.geometry.distance(unary_union(landsat17.geometry)) > 500:
            return "possible Oct 14 burn"
        return "other patch"
    patches["patch"] = patches.apply(label, axis=1)
    main_g = unary_union(patches[patches.patch == "main Oct 17 run"].geometry)

    # main-run shape: principal axis via PCA of its boundary area samples
    xs, ys = [], []
    minx, miny, maxx, maxy = main_g.bounds
    for x in np.arange(minx, maxx, 40):
        for y in np.arange(miny, maxy, 40):
            if main_g.contains(Point(x, y)):
                xs.append(x), ys.append(y)
    xy = np.column_stack([xs, ys])
    c = xy - xy.mean(axis=0)
    evals, evecs = np.linalg.eigh(np.cov(c.T))
    major = evecs[:, np.argmax(evals)]
    minor = evecs[:, np.argmin(evals)]
    proj_major, proj_minor = c @ major, c @ minor
    length_km = float(proj_major.max() - proj_major.min()) / 1000
    width_km = float(np.percentile(proj_minor, 97.5) - np.percentile(proj_minor, 2.5)) / 1000
    bearing = (math.degrees(math.atan2(major[0], major[1])) + 360) % 180  # 0-180, from north
    bearing = bearing if bearing >= 90 else bearing + 180  # report as NW->SE style (90-270)

    # ---------- infrastructure
    wells, aer_url = aer_wells()
    wells["category"] = wells.apply(well_category, axis=1)
    wells_u = wells.to_crs(UTM)
    wells_u["dist_to_main_scar_m"] = wells_u.geometry.distance(main_g).round(0)
    wells_u["inside_any_patch"] = wells_u.geometry.within(unary_union(patches.geometry))
    near = wells_u[wells_u.dist_to_main_scar_m <= 5000].sort_values("dist_to_main_scar_m")
    keep_cols = [c for c in wells_u.columns if c != "geometry"]
    ll = near.to_crs("EPSG:4326")
    near_out = near[keep_cols].copy()
    near_out["lon"], near_out["lat"] = ll.geometry.x.round(6), ll.geometry.y.round(6)
    near_out.to_csv(OUT / "wells_within_5km_of_scar.csv", index=False)

    data, ep = osm()
    o = osm_to_gdf(data).to_crs(UTM)
    roads = o[o.kind == "road"]
    pipes = o[o.kind == "pipeline"]
    power = o[o.kind == "power line"]
    mil = o[o.kind == "military"]
    water = o[o.kind == "water"]
    bldg = o[o.kind == "building"]
    places = o[o.kind == "place"]

    crossed = roads[roads.intersects(main_g)]
    road_names = sorted({(r["name"] or r["highway"]) for _, r in crossed.iterrows()})
    pipe_in = pipes[pipes.intersects(main_g.buffer(500))]
    power_in = power[power.intersects(main_g.buffer(500))]
    town = places[places.name.str.contains("Wainwright", case=False, na=False) & (places.place == "town")]
    nearest_bldg = float(bldg.distance(main_g).min()) if len(bldg) else float("nan")
    mil_union = unary_union(mil.geometry) if len(mil) else None
    pct_in_mil = float(main_g.intersection(mil_union).area / main_g.area * 100) if mil_union else float("nan")

    def wcount(cat, d):
        return int(((wells_u.category == cat) & (wells_u.dist_to_main_scar_m <= d)).sum())

    stats = {
        "scar_source": {"pre_scene": scar_props.get("pre_scene"), "post_scene": scar_props.get("post_scene"),
                        "threshold": "dNBR >= 0.27"},
        "patches": [{"patch": r.patch, "area_km2": round(r.area_km2, 2)} for _, r in
                    patches.sort_values("area_km2", ascending=False).iterrows()],
        "main_run": {"area_km2": round(main_g.area / 1e6, 2), "length_km": round(length_km, 1),
                     "width_km_95pct": round(width_km, 1), "axis_bearing_deg": round(bearing)},
        "possible_oct14_burn_km2": round(float(patches[patches.patch == "possible Oct 14 burn"].area_km2.sum()), 2),
        "wells": {
            "source": aer_url,
            "inside_any_scar_patch": int(wells_u.inside_any_patch.sum()),
            "inside_main_run": int(wells_u.geometry.within(main_g).sum()),
            "nearest_to_main_run": [
                {k: (str(v) if not isinstance(v, (int, float)) else v) for k, v in r.items()
                 if k in ("category", "dist_to_main_scar_m") or re.search(r"uwi|licen|name|status|fluid|mode", k, re.I)}
                for r in near.head(8)[keep_cols].to_dict("records")],
            "producing_gas_within_1km": wcount("producing gas", 1000),
            "producing_gas_within_2km": wcount("producing gas", 2000),
            "any_well_within_500m": int((wells_u.dist_to_main_scar_m <= 500).sum()),
            "categories_within_5km": wells_u[wells_u.dist_to_main_scar_m <= 5000].category.value_counts().to_dict(),
        },
        "osm": {"source": ep, "roads_crossed_by_main_run": road_names,
                "osm_pipelines_within_500m": int(len(pipe_in)),
                "power_lines_within_500m": int(len(power_in)),
                "nearest_building_to_main_run_m": round(nearest_bldg),
                "main_run_pct_inside_osm_military_landuse": round(pct_in_mil, 1),
                "town_centre_to_main_run_km": round(float(town.distance(main_g).min()) / 1000, 1) if len(town) else None},
        "notes": "Well status categories are derived from ST37 text fields; check individual wells before publishing. "
                 "OSM coverage of pipelines is incomplete; AER's full pipeline layer is a paid product. "
                 "Base boundary from OSM military land use, not a DND survey.",
    }
    (OUT / "scar_vs_infrastructure.json").write_text(json.dumps(stats, indent=2, default=str) + "\n")
    print(json.dumps(stats, indent=2, default=str), flush=True)

    # revised scar patches + infra GeoJSON (OSM-derived parts are ODbL)
    p_out = patches.to_crs("EPSG:4326")
    p_out["area_km2"] = p_out["area_km2"].round(3)
    p_out.to_file(OUT / "scar_patches_revised.geojson", driver="GeoJSON")
    o.to_crs("EPSG:4326")[o.kind.isin(["road", "pipeline", "power line", "military", "water"])].to_file(
        OUT / "osm_infrastructure_ODbL.geojson", driver="GeoJSON")

    # ---------- map
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    fig, ax = plt.subplots(figsize=(12, 10.5), dpi=130)
    view = main_g.buffer(5500).bounds
    ax.set_xlim(view[0], view[2]), ax.set_ylim(view[1], view[3])
    ax.set_facecolor("#f4f2ec")
    if mil_union is not None:
        gpd.GeoSeries([mil_union], crs=UTM).plot(ax=ax, color="#e6e0cf", edgecolor="#8d8063", lw=1, ls="--", zorder=1)
    water.plot(ax=ax, color="#a9cfe8", edgecolor="#7fb2d6", lw=0.5, zorder=2)
    for hw, lw, col in [("track", 0.5, "#b8ad94"), ("unclassified", 0.8, "#8c8c8c"), ("residential", 0.6, "#9a9a9a"),
                        ("tertiary", 1.1, "#777"), ("secondary", 1.5, "#666"), ("primary", 2, "#555"),
                        ("trunk", 2.2, "#444")]:
        sub = roads[roads.highway == hw]
        if len(sub):
            sub.plot(ax=ax, color=col, lw=lw, zorder=3)
    other_roads = roads[~roads.highway.isin(["track", "unclassified", "residential", "tertiary", "secondary",
                                             "primary", "trunk"])]
    other_roads.plot(ax=ax, color="#9a9a9a", lw=0.5, zorder=3)
    bldg.plot(ax=ax, color="#6d6d6d", lw=0, zorder=3)
    power.plot(ax=ax, color="#7b1fa2", lw=1, ls=(0, (4, 2)), zorder=4)
    pipes.plot(ax=ax, color="#ef6c00", lw=1.4, ls=(0, (6, 2, 1, 2)), zorder=4)
    patches[patches.patch == "main Oct 17 run"].plot(ax=ax, color="#d84315", alpha=0.55, edgecolor="#b71c1c",
                                                    lw=1.6, zorder=5)
    patches[patches.patch == "possible Oct 14 burn"].plot(ax=ax, color="none", edgecolor="#6a1b9a", lw=1.6,
                                                         hatch="///", zorder=5)
    patches[patches.patch == "other patch"].plot(ax=ax, color="#ff8a65", alpha=0.5, lw=0, zorder=5)
    style = {"producing gas": ("^", "#2e7d32", 46), "producing oil": ("^", "#1b1b1b", 46),
             "suspended": ("v", "#f9a825", 40), "abandoned/reclaimed": ("x", "#757575", 18),
             "other/unknown": (".", "#424242", 14)}
    for cat, (m, col, s) in style.items():
        sub = wells_u[wells_u.category == cat]
        if len(sub):
            sub.plot(ax=ax, marker=m, color=col, markersize=s, zorder=6, linewidth=1 if m == "x" else 0)
    l17 = det_g[(det_g.date == "2026-10-17")]
    l17[l17.source == "LANDSAT_NRT"].plot(ax=ax, color="#00acc1", markersize=10, zorder=7, edgecolor="black",
                                          linewidth=0.3)
    l17[l17.source != "LANDSAT_NRT"].plot(ax=ax, color="#ffd54f", marker="s", markersize=22, zorder=7,
                                          edgecolor="black", linewidth=0.5)
    det_g[det_g.date == "2026-10-18"].plot(ax=ax, color="white", marker="s", markersize=26, zorder=7,
                                           edgecolor="black", linewidth=0.8)
    gpd.GeoSeries([oct14], crs=UTM).plot(ax=ax, color="#ce93d8", marker="D", markersize=30, zorder=7,
                                         edgecolor="black", linewidth=0.6)
    for _, r in places.iterrows():
        x, y = r.geometry.x, r.geometry.y
        if view[0] < x < view[2] and view[1] < y < view[3] and r["name"]:
            ax.annotate(r["name"], (x, y), fontsize=9 if r.place == "town" else 7.5, color="#222",
                        ha="center", bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.7, lw=0))
    # nearest producing gas well callout
    pg = wells_u[wells_u.category == "producing gas"].sort_values("dist_to_main_scar_m")
    if len(pg):
        w0 = pg.iloc[0]
        p_on = main_g.exterior.interpolate(main_g.exterior.project(w0.geometry)) if hasattr(main_g, "exterior") else None
        if p_on is not None:
            ax.plot([w0.geometry.x, p_on.x], [w0.geometry.y, p_on.y], color="#2e7d32", lw=1, ls=":", zorder=6)
        ax.annotate(f"Nearest producing gas well\n{w0.dist_to_main_scar_m / 1000:.2f} km from scar",
                    (w0.geometry.x, w0.geometry.y), xytext=(14, 10), textcoords="offset points", fontsize=8.5,
                    color="#1b5e20", bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.85, lw=0), zorder=8)
    # scale bar
    x0, y0 = view[0] + 800, view[1] + 800
    ax.plot([x0, x0 + 2000], [y0, y0], "k-", lw=4, solid_capstyle="butt", zorder=9)
    ax.text(x0 + 1000, y0 + 250, "2 km", ha="center", fontsize=9, zorder=9)
    ax.annotate("N", xy=(view[2] - 700, view[3] - 600), xytext=(view[2] - 700, view[3] - 1600),
                arrowprops=dict(arrowstyle="-|>", color="black"), ha="center", fontsize=11, weight="bold")
    ax.set_xticks([]), ax.set_yticks([])
    m = stats["main_run"]
    handles = [
        Patch(fc="#d84315", alpha=0.55, ec="#b71c1c", label=f"Oct 17 burn (Sentinel-2): {m['area_km2']} km², "
                                                            f"{m['length_km']} × {m['width_km_95pct']} km"),
        Patch(fc="none", ec="#6a1b9a", hatch="///", label="Separate burn matching Oct 14 VIIRS detection"),
        Line2D([], [], marker="o", ls="", mfc="#00acc1", mec="black", ms=5, label="Landsat hotspots 12:17 p.m. Oct 17"),
        Line2D([], [], marker="s", ls="", mfc="#ffd54f", mec="black", ms=6, label="VIIRS hotspots Oct 17"),
        Line2D([], [], marker="s", ls="", mfc="white", mec="black", ms=6, label="VIIRS hotspots Oct 18"),
        Line2D([], [], marker="D", ls="", mfc="#ce93d8", mec="black", ms=6, label="VIIRS hotspot Oct 14"),
        Line2D([], [], marker="^", ls="", mfc="#2e7d32", mec="#2e7d32", ms=7, label="Producing gas well (AER)"),
        Line2D([], [], marker="^", ls="", mfc="#1b1b1b", ms=7, label="Producing oil well (AER)"),
        Line2D([], [], marker="v", ls="", mfc="#f9a825", ms=7, label="Suspended well (AER)"),
        Line2D([], [], marker="x", ls="", color="#757575", ms=6, label="Abandoned/reclaimed well (AER)"),
        Line2D([], [], color="#ef6c00", lw=1.6, ls=(0, (6, 2, 1, 2)), label="Pipeline (OpenStreetMap, incomplete)"),
        Line2D([], [], color="#7b1fa2", lw=1.2, ls=(0, (4, 2)), label="Power line (OSM)"),
        Patch(fc="#e6e0cf", ec="#8d8063", ls="--", label="Military land (OSM)"),
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=8, framealpha=0.92)
    ax.set_title("CFB Wainwright fire: burn scar and nearby infrastructure", loc="left", fontsize=13)
    fig.text(0.01, 0.008, "Burn: contains modified Copernicus Sentinel data [2026] (dNBR ≥ 0.27, Oct 4 → Oct 19). "
                          "Fire: NASA FIRMS. Wells: Alberta Energy Regulator ST37. Roads, pipelines, water, land use: "
                          "© OpenStreetMap contributors (ODbL). Prime Rogue Inc.", fontsize=7, color="#555")
    fig.tight_layout(rect=(0, 0.015, 1, 1))
    fig.savefig(OUT / "scar_infrastructure_map.png")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
