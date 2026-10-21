#!/usr/bin/env python3
"""Overlay the burn scar and fire detections on Natural Resources Canada
topographic maps, to help locate range features (e.g. the grenade range).

Sources (Open Government Licence – Canada):
  * NRCan Toporama WMS (current CanVec-based topographic map)
  * NRCan CanMatrix 1:50,000 scanned NTS sheets 073D10 and 073D15, which can
    show older named features, buildings and range infrastructure

Outputs go to data/topo/.
"""

from __future__ import annotations

import io
import json
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "topo"
CACHE = OUT / "cache"
VIEW = dict(west=-111.08, south=52.69, east=-110.78, north=52.85)   # burn area + surroundings
SHEETS = ["073d10", "073d15"]
UA = {"User-Agent": "prime-rogue-cfb-wainwright-archive/1.0"}
LOG = []


def log(*a):
    msg = " ".join(str(x) for x in a)
    LOG.append(msg)
    print(msg, flush=True)


def http(url, timeout=300):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def toporama():
    base = "https://maps.geogratis.gc.ca/wms/toporama_en"
    try:
        caps = http(base + "?service=WMS&version=1.3.0&request=GetCapabilities").decode("utf-8", "replace")
    except Exception as exc:
        log("toporama capabilities failed:", exc)
        return None
    layers = re.findall(r"<Layer[^>]*>\s*<Name>([^<]+)</Name>", caps)
    log("toporama layers:", layers[:40])
    layer = next((l for l in layers if "toporama" in l.lower()), layers[0] if layers else None)
    if not layer:
        return None
    w = 2400
    h = int(w * (VIEW["north"] - VIEW["south"]) / ((VIEW["east"] - VIEW["west"]) * np.cos(np.radians(52.77))))
    params = {"service": "WMS", "version": "1.1.1", "request": "GetMap", "layers": layer, "styles": "",
              "srs": "EPSG:4326", "bbox": f"{VIEW['west']},{VIEW['south']},{VIEW['east']},{VIEW['north']}",
              "width": w, "height": h, "format": "image/png", "transparent": "false"}
    data = http(base + "?" + urllib.parse.urlencode(params))
    if not data.startswith(b"\x89PNG"):
        log("toporama GetMap did not return PNG:", data[:300])
        return None
    (OUT / "toporama_view.png").write_bytes(data)
    import matplotlib.image as mpimg
    return mpimg.imread(io.BytesIO(data)), (VIEW["west"], VIEW["east"], VIEW["south"], VIEW["north"]), layer


def canmatrix():
    """Find, download and mosaic the CanMatrix 1:50k GeoTIFFs for our sheets."""
    import rasterio
    from rasterio.merge import merge
    from rasterio.warp import Resampling, calculate_default_transform, reproject

    roots = ["https://ftp.maps.canada.ca/pub/nrcan_rncan/raster/canmatrix2/50k_tif/073/d/",
             "https://ftp.maps.canada.ca/pub/nrcan_rncan/raster/canmatrix/50k_tif/073/d/"]
    found = []
    for root in roots:
        try:
            listing = http(root).decode("utf-8", "replace")
        except Exception as exc:
            log("canmatrix listing failed", root, exc)
            continue
        names = sorted(set(re.findall(r'href="([^"]+)"', listing)))
        log("canmatrix listing", root, [n for n in names if any(s in n.lower() for s in SHEETS)][:20])
        for s in SHEETS:
            cand = [n for n in names if s in n.lower() and n.lower().endswith((".zip", ".tif"))]
            if cand:
                found.append(urllib.parse.urljoin(root, sorted(cand)[-1]))
        if found:
            break
    if not found:
        return None
    CACHE.mkdir(parents=True, exist_ok=True)
    tifs = []
    for url in found:
        p = CACHE / Path(urllib.parse.urlparse(url).path).name
        if not p.exists():
            p.write_bytes(http(url, timeout=900))
        if p.suffix.lower() == ".zip":
            with zipfile.ZipFile(p) as z:
                z.extractall(CACHE / p.stem)
            tifs += [t for t in (CACHE / p.stem).rglob("*.tif")]
        else:
            tifs.append(p)
    log("canmatrix tifs:", [t.name for t in tifs])
    # reproject each to EPSG:4326 over VIEW and composite (first non-empty wins)
    w = 2400
    h = int(w * (VIEW["north"] - VIEW["south"]) / ((VIEW["east"] - VIEW["west"]) * np.cos(np.radians(52.77))))
    dst_t = rasterio.transform.from_bounds(VIEW["west"], VIEW["south"], VIEW["east"], VIEW["north"], w, h)
    out = np.zeros((3, h, w), dtype="uint8")
    filled = np.zeros((h, w), bool)
    for t in tifs:
        sib = sorted(p.name for p in t.parent.iterdir())
        log("files beside", t.name, sib)
        with rasterio.open(t) as src:
            src_crs = src.crs
            if src_crs is None:
                prj = next((p for p in t.parent.glob(t.stem + "*.prj")), None) or next(t.parent.glob("*.prj"), None)
                if prj:
                    from rasterio.crs import CRS
                    src_crs = CRS.from_wkt(prj.read_text())
                    log("crs from", prj.name, src_crs)
            if src_crs is None:
                log("no CRS for", t.name, "- skipping")
                continue
            bands = src.count
            if src.colorinterp and src.count == 1 and src.colormap(1):
                cmap = src.colormap(1)
                idx = src.read(1)
                lut = np.zeros((256, 3), "uint8")
                for k, v in cmap.items():
                    lut[k] = v[:3]
                rgb = np.moveaxis(lut[idx], -1, 0)
            else:
                rgb = src.read([1, 2, 3]) if bands >= 3 else np.repeat(src.read(1)[None], 3, 0)
            tmp = np.zeros((3, h, w), "uint8")
            for b in range(3):
                reproject(rgb[b], tmp[b], src_transform=src.transform, src_crs=src_crs, dst_transform=dst_t,
                          dst_crs="EPSG:4326", resampling=Resampling.bilinear)
            has = tmp.sum(axis=0) > 0
            put = has & ~filled
            out[:, put] = tmp[:, put]
            filled |= has
    if not filled.any():
        log("canmatrix: no georeferenced sheets; no overlay made")
        return None
    img = np.moveaxis(out, 0, -1)
    import matplotlib.pyplot as plt
    plt.imsave(OUT / "canmatrix_view.png", img)
    return img, (VIEW["west"], VIEW["east"], VIEW["south"], VIEW["north"]), ", ".join(t.stem for t in tifs)


def osm_history(way_id):
    try:
        x = http(f"https://api.openstreetmap.org/api/0.6/way/{way_id}/history").decode("utf-8", "replace")
        vers = re.findall(r'<way [^>]*version="(\d+)"[^>]*timestamp="([^"]+)"[^>]*user="([^"]*)"', x)
        tags = re.findall(r'<tag k="([^"]+)" v="([^"]*)"', x)
        log(f"OSM way {way_id} history: {vers}; tags (all versions): {sorted(set(tags))}")
    except Exception as exc:
        log("osm history failed", way_id, exc)


def overlay(base, title, credit, path, view=None, ranges=False):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from shapely.geometry import shape

    img, ext, _ = base
    fig, ax = plt.subplots(figsize=(14, 10.5), dpi=150)
    ax.imshow(img, extent=ext, interpolation="antialiased")
    ax.set_aspect(1 / np.cos(np.radians(52.77)))
    v = view or dict(west=ext[0], east=ext[1], south=ext[2], north=ext[3])
    ax.set_xlim(v["west"], v["east"]), ax.set_ylim(v["south"], v["north"])
    if ranges:
        import geopandas as gpd
        o = gpd.read_file(ROOT / "data" / "infrastructure" / "osm_infrastructure_ODbL.geojson")
        r = o[(o.kind == "military") & o.military.isin(["range", "checkpoint", "training_area"]) & (o.name.fillna("") != "")]
        for _, row in r.iterrows():
            g = row.geometry
            for poly in getattr(g, "geoms", [g]):
                if poly.geom_type != "Polygon":
                    continue
                xs, ys = poly.exterior.xy
                grenade = "grenade" in row["name"].lower()
                ax.plot(xs, ys, color="#1565c0" if not grenade else "#00c853", lw=2.4 if grenade else 1.4, zorder=5)
            c = g.representative_point()
            if v["west"] < c.x < v["east"] and v["south"] < c.y < v["north"]:
                grenade = "grenade" in row["name"].lower()
                ax.annotate(row["name"], (c.x, c.y), xytext=(6, 6) if grenade else (0, 0), textcoords="offset points",
                            fontsize=10 if grenade else 8, weight="bold" if grenade else "normal",
                            color="#1b5e20" if grenade else "#0d47a1", ha="left" if grenade else "center", zorder=8,
                            bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.85, lw=0))
    patches_p = ROOT / "data" / "infrastructure" / "scar_patches_revised.geojson"
    src = patches_p if patches_p.exists() else ROOT / "data" / "copernicus" / "burn_scar.geojson"
    fc = json.loads(src.read_text())
    for f in fc["features"]:
        kind = f["properties"].get("patch", "main Oct 17 run")
        g = shape(f["geometry"])
        for poly in getattr(g, "geoms", [g]):
            xs, ys = poly.exterior.xy
            if kind == "main Oct 17 run":
                ax.fill(xs, ys, color="#ff3d00", alpha=0.18, zorder=3)
                ax.plot(xs, ys, color="#d50000", lw=2, zorder=4)
            elif kind == "possible Oct 14 burn":
                ax.plot(xs, ys, color="#8e24aa", lw=2, ls="--", zorder=4)
    import csv
    for r in csv.DictReader((ROOT / "data" / "firms" / "detections.csv").open()):
        d, src_ = r["acq_datetime_utc"][:10], r["source"]
        lon, lat = float(r["longitude"]), float(r["latitude"])
        if d == "2026-10-17" and src_ == "LANDSAT_NRT":
            ax.plot(lon, lat, "o", ms=4, mfc="#00e5ff", mec="black", mew=0.4, zorder=6)
        elif d == "2026-10-17":
            ax.plot(lon, lat, "s", ms=6, mfc="#ffd54f", mec="black", mew=0.5, zorder=6)
        elif d == "2026-10-18":
            ax.plot(lon, lat, "s", ms=6, mfc="white", mec="black", mew=0.8, zorder=6)
        elif d == "2026-10-14":
            ax.plot(lon, lat, "D", ms=6, mfc="#ce93d8", mec="black", mew=0.6, zorder=6)
    # 1 km grid ticks in lat/lon for reading coordinates off the map
    step_x, step_y = (0.05, 0.025) if not view else (0.01, 0.005)
    ax.set_xticks(np.round(np.arange(np.ceil(v["west"] / step_x) * step_x, v["east"], step_x), 3))
    ax.set_yticks(np.round(np.arange(np.ceil(v["south"] / step_y) * step_y, v["north"], step_y), 3))
    ax.tick_params(labelsize=8)
    ax.grid(color="black", alpha=0.25, lw=0.5)
    handles = [Patch(fc="#ff3d00", alpha=0.3, ec="#d50000", lw=2, label="Oct 17 burn (Sentinel-2, dNBR ≥ 0.27)"),
               Line2D([], [], color="#8e24aa", ls="--", lw=2, label="Separate burn matching Oct 14 detection"),
               Line2D([], [], marker="o", ls="", mfc="#00e5ff", mec="black", ms=5, label="Landsat hotspots 12:17 p.m. Oct 17"),
               Line2D([], [], marker="s", ls="", mfc="#ffd54f", mec="black", ms=6, label="VIIRS hotspots Oct 17"),
               Line2D([], [], marker="s", ls="", mfc="white", mec="black", ms=6, label="VIIRS hotspots Oct 18"),
               Line2D([], [], marker="D", ls="", mfc="#ce93d8", mec="black", ms=6, label="VIIRS hotspot Oct 14")]
    if ranges:
        handles += [Line2D([], [], color="#00c853", lw=2.4, label="'Range 2 (Grenade)' as mapped in OpenStreetMap"),
                    Line2D([], [], color="#1565c0", lw=1.4, label="Other ranges as mapped in OpenStreetMap")]
    ax.legend(handles=handles, loc="lower left", fontsize=8.5, framealpha=0.92)
    ax.set_title(title, loc="left", fontsize=12)
    fig.text(0.01, 0.006, credit, fontsize=7.5, color="#444")
    fig.tight_layout(rect=(0, 0.015, 1, 1))
    fig.savefig(path)
    plt.close(fig)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    common = ("Burn: contains modified Copernicus Sentinel data [2026]. Fire: NASA FIRMS. "
              "Prime Rogue Inc.")
    t = None
    try:
        t = toporama()
    except Exception as exc:
        log("toporama failed:", exc)
    if t:
        overlay(t, "Burn scar and fire detections on NRCan Toporama (current topographic map)",
                f"Base map: Natural Resources Canada, Toporama ({t[2]}), Open Government Licence – Canada. " + common,
                OUT / "topo_toporama_overlay.png")
    c = None
    try:
        c = canmatrix()
    except Exception as exc:
        log("canmatrix failed:", exc)
    if c:
        overlay(c, "Burn scar and fire detections on NRCan 1:50,000 NTS map sheets (CanMatrix scans)",
                f"Base map: Natural Resources Canada, CanMatrix NTS 1:50,000 ({c[2]}), Open Government Licence – "
                "Canada. Sheet editions may be decades old. " + common, OUT / "topo_nts50k_overlay.png")
    if t:
        osm_history(1240048250)
        overlay(t, "Ranges as mapped in OpenStreetMap, with the burn scar and fire detections (Toporama base)",
                f"Base map: NRCan Toporama, OGL – Canada. Ranges: © OpenStreetMap contributors (ODbL), volunteer-mapped, "
                "not verified by DND. " + common, OUT / "topo_ranges_zoom.png",
                view=dict(west=-110.965, east=-110.86, south=52.738, north=52.797), ranges=True)
    (OUT / "run.log").write_text("\n".join(LOG) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
