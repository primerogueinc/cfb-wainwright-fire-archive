#!/usr/bin/env python3
"""Map the CFB Wainwright burn scar from Copernicus Sentinel-2 and overlay
NASA FIRMS and NOAA GOES fire detections.

Method (standard burn-severity mapping):
  * find Sentinel-2 L2A scenes over the base (public archive, no key) and pick
    the clearest scene before the fire (on or before Oct 16) and the clearest
    after it (on or after Oct 18)
  * compute the Normalized Burn Ratio, NBR = (B8A - B12) / (B8A + B12), for
    each, and the change dNBR = NBR_before - NBR_after
  * map the scar as dNBR >= 0.27 (USGS moderate-low severity and above),
    keep only patches touching the satellite fire detections, fill holes,
    and measure area. Lower values (0.10-0.27) are widespread across the
    region between scenes (autumn curing, harvest, haze), so they are only
    counted as a "possible light-burn fringe" within 500 m of the scar.
  * mask clouds, shadows, water and snow with the scene classification layer

Outputs go to data/copernicus/. Contains modified Copernicus Sentinel data [2026].

Usage:
    python3 scripts/sentinel2_burn.py           # skip if the chosen scenes haven't changed
    python3 scripts/sentinel2_burn.py --force
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "copernicus"
STAC = "https://earth-search.aws.element84.com/v1/search"

# Kept inside Sentinel-2 tile 12UWD (which starts at ~111.0°W here) so every scene shares one grid.
AOI = dict(west=-110.99, east=-110.70, south=52.66, north=52.90)
TILE = ("12", "U", "WD")
SEARCH_FROM = "2026-09-01"
FIRE_DATE = date(2026, 10, 17)
DNBR_BURNED = 0.10      # USGS: 0.10-0.27 low severity
DNBR_MODERATE = 0.27    # USGS: >= 0.27 moderate-low severity and above
CLEAR = {2, 4, 5, 7}    # SCL: dark area (fresh burns), vegetation, not-vegetated, unclassified
SEED_BUFFER_M = 1500    # burned patches must lie within this distance of a detection
MDT_OFFSET = -6


def stac_search():
    body = {"collections": ["sentinel-2-l2a"],
            "bbox": [AOI["west"], AOI["south"], AOI["east"], AOI["north"]],
            "datetime": f"{SEARCH_FROM}T00:00:00Z/{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ}",
            "limit": 200, "query": {"eo:cloud_cover": {"lt": 90}}}
    req = urllib.request.Request(STAC, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        feats = json.load(r)["features"]
    return [f for f in feats if (str(f["properties"].get("mgrs:utm_zone")), f["properties"].get("mgrs:latitude_band"),
                                 f["properties"].get("mgrs:grid_square")) == TILE]


def read_aoi(href, res=20):
    """Read an asset over the AOI on a fixed UTM grid (same grid for every scene)."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    with rasterio.open(href) as src:
        b = transform_bounds("EPSG:4326", src.crs, AOI["west"], AOI["south"], AOI["east"], AOI["north"])
        # snap bounds to the analysis grid so all scenes align
        b = (np.floor(b[0] / res) * res, np.floor(b[1] / res) * res,
             np.ceil(b[2] / res) * res, np.ceil(b[3] / res) * res)
        win = from_bounds(*b, transform=src.transform)
        shape = (int(round((b[3] - b[1]) / res)), int(round((b[2] - b[0]) / res)))
        data = src.read(1, window=win, out_shape=shape, boundless=True, fill_value=0,
                        resampling=Resampling.nearest if res >= 20 else Resampling.bilinear)
        transform = rasterio.transform.from_origin(b[0], b[3], res, res)
        return data, transform, src.crs


def scene_record(f):
    p, a = f["properties"], f["assets"]
    scl, transform, crs = read_aoi(a["scl"]["href"])
    valid = scl > 0
    clear = np.isin(scl, list(CLEAR))
    frac = float(clear.sum() / max(valid.sum(), 1))
    coverage = float(valid.mean())
    return {"id": f["id"], "datetime": p["datetime"], "date": p["datetime"][:10], "clear_frac": frac,
            "coverage": coverage, "crs": str(crs), "feature": f}


def nbr(f):
    a = f["assets"]
    b8a, transform, crs = read_aoi(a["nir08"]["href"])
    b12, *_ = read_aoi(a["swir22"]["href"])
    scl, *_ = read_aoi(a["scl"]["href"])
    # L2A processing baseline >= 04.00 adds an offset of -1000 to reflectance DNs.
    off = float(f["properties"].get("earthsearch:boa_offset_applied", False) is False and
                str(f["properties"].get("s2:processing_baseline", "00.00")) >= "04.00") * 1000
    b8a = (b8a.astype("float32") - off) / 10000
    b12 = (b12.astype("float32") - off) / 10000
    with np.errstate(divide="ignore", invalid="ignore"):
        n = (b8a - b12) / (b8a + b12)
    ok = np.isin(scl, list(CLEAR)) & np.isfinite(n)
    return n, ok, transform, crs


def truecolour(f, res=10):
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds
    with rasterio.open(f["assets"]["visual"]["href"]) as src:
        b = transform_bounds("EPSG:4326", src.crs, AOI["west"], AOI["south"], AOI["east"], AOI["north"])
        win = from_bounds(*b, transform=src.transform)
        img = src.read([1, 2, 3], window=win, boundless=True, fill_value=0)
        return np.moveaxis(img, 0, -1), b


def detections():
    """FIRMS detections Oct 17-18 from the archive, plus NOAA GOES fire pixels."""
    pts = []
    path = ROOT / "data" / "firms" / "detections.csv"
    if path.exists():
        for r in csv.DictReader(path.open()):
            if r["acq_datetime_utc"][:10] in ("2026-10-17", "2026-10-18"):
                pts.append({"lon": float(r["longitude"]), "lat": float(r["latitude"]), "kind": "firms",
                            "source": r["source"], "time_utc": r["acq_datetime_utc"],
                            "time_mdt": r["acq_datetime_mdt"]})
    tl = ROOT / "data" / "goes" / "fire_timeline.csv"
    if tl.exists():
        sys.path.insert(0, str(ROOT / "scripts"))
        import goes_loops as g
        for r in csv.DictReader(tl.open()):
            if int(r["fdc_fire_pixels"] or 0) == 0 or not r["fdc_file"]:
                continue
            sat = int(r["satellite"][-2:])
            mask, x, y, p, H = g.read_window(sat, r["fdc_file"], "Mask", g.FIRE_BOX, pad=0)
            power, *_ = g.read_window(sat, r["fdc_file"], "Power", g.FIRE_BOX, pad=0)
            for j, i in zip(*np.where(np.isin(mask, [10, 11, 12, 13, 14, 15, 30, 31, 32, 33, 34, 35]))):
                lon, lat = p(x[i] * H, y[j] * H, inverse=True)
                pts.append({"lon": float(lon), "lat": float(lat), "kind": "goes", "source": r["satellite"],
                            "time_utc": r["scan_start_utc"], "time_mdt": r["scan_start_mdt"],
                            "power_mw": round(float(power[j, i]), 1)})
    return pts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    feats = stac_search()
    print(f"{len(feats)} Sentinel-2 scenes found", flush=True)
    recs = []
    errors = []
    for f in feats:
        try:
            recs.append(scene_record(f))
        except Exception as exc:
            errors.append(f"{f['id']}: {exc}")
            print(f"  skip {f['id']}: {exc}", flush=True)
    diag = [f"{len(feats)} STAC features; {len(recs)} readable"] + [f"error: {e}" for e in errors[:3]]
    if feats:
        p0 = feats[0]["properties"]
        diag.append("sample props: " + ", ".join(f"{k}={p0[k]}" for k in sorted(p0)
                                                  if k.startswith(("mgrs", "proj", "s2:mgrs", "eo:"))))
    by_date = {}
    for r in recs:  # one scene per date: the one covering most of the AOI, then clearest
        k = r["date"]
        if k not in by_date or (r["coverage"], r["clear_frac"]) > (by_date[k]["coverage"], by_date[k]["clear_frac"]):
            by_date[k] = r
    diag += [f"{r['date']} cover {r['coverage']:.0%} clear {r['clear_frac']:.0%}" for r in sorted(by_date.values(), key=lambda r: r["date"])]
    recs = [r for r in by_date.values() if r["coverage"] > 0.9]
    diag.append(f"{len(recs)} dates with >90% AOI coverage")
    print("\n".join(diag), flush=True)
    for r in sorted(recs, key=lambda r: r["datetime"]):
        print(f"  {r['datetime'][:16]}  {r['id']:40}  clear {r['clear_frac']:.0%}", flush=True)
    pre = [r for r in recs if date.fromisoformat(r["date"]) < FIRE_DATE and r["clear_frac"] >= 0.9]
    post = [r for r in recs if date.fromisoformat(r["date"]) > FIRE_DATE and r["clear_frac"] >= 0.6]
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "scenes.csv").open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["datetime_utc", "scene_id", "aoi_clear_pct", "aoi_coverage_pct"])
        for r in sorted(recs, key=lambda r: r["datetime"]):
            w.writerow([r["datetime"], r["id"], f"{r['clear_frac'] * 100:.0f}", f"{r['coverage'] * 100:.0f}"])
    if not pre or not post:
        msg = "no clear post-fire scene yet" if pre else "no clear pre-fire scene"
        print(msg)
        (OUT / "status.txt").write_text(f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%MZ}: {msg}\n" + "\n".join(diag) + "\n")
        return 0
    pre_r = max(pre, key=lambda r: r["datetime"])            # latest clear before the fire
    post_r = max(post, key=lambda r: (r["clear_frac"] >= 0.9, -abs((date.fromisoformat(r["date"]) - FIRE_DATE).days),
                                      r["clear_frac"]))       # clearest, soonest after
    summary_path = OUT / "summary.json"
    if summary_path.exists() and not args.force:
        old = json.loads(summary_path.read_text())
        if old.get("pre_scene") == pre_r["id"] and old.get("post_scene") == post_r["id"]:
            print("scenes unchanged; nothing to do")
            return 0
    print(f"pre  {pre_r['id']}\npost {post_r['id']}", flush=True)

    n_pre, ok_pre, transform, crs = nbr(pre_r["feature"])
    n_post, ok_post, *_ = nbr(post_r["feature"])
    ok = ok_pre & ok_post
    dnbr = np.where(ok, n_pre - n_post, np.nan).astype("float32")

    from pyproj import Transformer
    from rasterio import features
    from scipy import ndimage
    from shapely.geometry import mapping, shape
    from shapely.ops import transform as shp_transform, unary_union

    to_utm = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    to_ll = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    pts = detections()
    burned = np.nan_to_num(dnbr) >= DNBR_MODERATE
    burned = ndimage.binary_opening(burned, iterations=2)
    burned = ndimage.binary_closing(burned, iterations=2)
    labels, n = ndimage.label(burned)
    seed = np.zeros_like(burned)
    inv = ~transform
    rad = int(SEED_BUFFER_M / 20)
    for pnt in pts:
        x, y = to_utm.transform(pnt["lon"], pnt["lat"])
        c, r = inv * (x, y)
        r, c = int(r), int(c)
        seed[max(0, r - rad):r + rad + 1, max(0, c - rad):c + rad + 1] = True
    keep = np.unique(labels[seed & burned])
    keep = keep[keep > 0]
    scar = ndimage.binary_fill_holes(np.isin(labels, keep))
    px_km2 = 20 * 20 / 1e6
    area = float(scar.sum() * px_km2)
    near = ndimage.binary_dilation(scar, iterations=25) & ~scar  # 500 m ring
    fringe = float((near & (np.nan_to_num(dnbr) >= DNBR_BURNED)).sum() * px_km2)
    valid_frac = float(ok.mean())

    polys = [shape(geom) for geom, v in features.shapes(scar.astype("uint8"), mask=scar, transform=transform)
             if v == 1]
    scar_utm = unary_union(polys).simplify(20) if polys else None
    scar_ll = shp_transform(lambda x, y, z=None: to_ll.transform(x, y), scar_utm) if scar_utm else None

    # ---------- GeoJSON outputs
    def pt_feature(p):
        colour = {"LANDSAT_NRT": "#00bcd4", "goes": "#ff3d00"}.get(p["source"] if p["kind"] == "firms" else "goes",
                                                                   "#ffb300")
        props = {k: v for k, v in p.items() if k not in ("lon", "lat")}
        props.update({"marker-color": colour, "marker-size": "small"})
        return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [p["lon"], p["lat"]]},
                "properties": props}

    scar_feat = {"type": "Feature", "geometry": mapping(scar_ll) if scar_ll else None,
                 "properties": {"name": "Burn scar (Sentinel-2 dNBR >= 0.27)", "area_km2": round(area, 2),
                                "pre_scene": pre_r["id"], "post_scene": post_r["id"],
                                "stroke": "#d32f2f", "stroke-width": 2, "fill": "#ff7043", "fill-opacity": 0.35}}
    (OUT / "burn_scar.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [scar_feat]}) + "\n")
    (OUT / "fire_progression.geojson").write_text(json.dumps(
        {"type": "FeatureCollection", "features": [scar_feat] + [pt_feature(p) for p in pts]}) + "\n")

    # ---------- dNBR GeoTIFF
    import rasterio
    with rasterio.open(OUT / "dnbr.tif", "w", driver="GTiff", height=dnbr.shape[0], width=dnbr.shape[1], count=1,
                       dtype="float32", crs=crs, transform=transform, nodata=np.nan, compress="deflate") as dst:
        dst.write(dnbr, 1)

    # ---------- maps
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.lines import Line2D

    ext_utm = (transform.c, transform.c + transform.a * dnbr.shape[1],
               transform.f + transform.e * dnbr.shape[0], transform.f)
    cmap = LinearSegmentedColormap.from_list("dnbr", ["#2a78d6", "#e6e6e6", "#eb6834", "#7a1f05"])
    cmap.set_bad("#bdbdbd")

    def overlay(ax):
        groups = [
            (lambda p: p["kind"] == "firms" and p["source"] == "LANDSAT_NRT", "o", "#00bcd4", 10,
             "Landsat hotspots, 12:17 p.m. Oct 17"),
            (lambda p: p["kind"] == "firms" and p["source"] != "LANDSAT_NRT" and p["time_utc"] < "2026-10-18",
             "^", "#ffd54f", 40, "VIIRS hotspots, 2:49 p.m. Oct 17"),
            (lambda p: p["kind"] == "firms" and p["time_utc"] >= "2026-10-18", "s", "#ffffff", 40,
             "VIIRS hotspots, Oct 18"),
            (lambda p: p["kind"] == "goes", "o", "none", 260, "NOAA GOES fire pixels, 3:10–3:40 p.m. (±2 km)"),
        ]
        handles = []
        for sel, m, c, s, label in groups:
            sub = [p for p in pts if sel(p)]
            if not sub:
                continue
            xy = [to_utm.transform(p["lon"], p["lat"]) for p in sub]
            if c == "none":
                ax.scatter([a for a, _ in xy], [b for _, b in xy], s=s, facecolors="none", edgecolors="#ff1744",
                           linewidths=2, zorder=6)
                handles.append(Line2D([], [], marker="o", ls="", mfc="none", mec="#ff1744", mew=2, ms=11, label=label))
            else:
                ax.scatter([a for a, _ in xy], [b for _, b in xy], s=s, marker=m, c=c, edgecolors="black",
                           linewidths=0.6, zorder=6)
                handles.append(Line2D([], [], marker=m, ls="", mfc=c, mec="black", ms=7, label=label))
        if scar_utm is not None:
            for geom in getattr(scar_utm, "geoms", [scar_utm]):
                xs, ys = geom.exterior.xy
                ax.plot(xs, ys, color="#d50000", lw=1.6, zorder=5)
            handles.append(Line2D([], [], color="#d50000", lw=2, label=f"Burn scar outline ({area:.1f} km²)"))
        for name, lon, lat in [("Wainwright", -110.857, 52.839)]:
            x, y = to_utm.transform(lon, lat)
            ax.plot(x, y, "k.", ms=8)
            ax.annotate(name, (x, y), xytext=(5, 4), textcoords="offset points", fontsize=10,
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8, lw=0))
        ax.set_xticks([]), ax.set_yticks([])
        # 5 km scale bar
        x0 = ext_utm[0] + 0.05 * (ext_utm[1] - ext_utm[0])
        y0 = ext_utm[2] + 0.05 * (ext_utm[3] - ext_utm[2])
        ax.plot([x0, x0 + 5000], [y0, y0], "k-", lw=4, solid_capstyle="butt")
        ax.text(x0 + 2500, y0 + 400, "5 km", ha="center", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.8, lw=0))
        return handles

    def when(r):
        return r["datetime"][:10]

    fig, ax = plt.subplots(figsize=(11, 8.6), dpi=120)
    im = ax.imshow(dnbr, extent=ext_utm, cmap=cmap, vmin=-0.3, vmax=0.8, interpolation="nearest")
    handles = overlay(ax)
    ax.legend(handles=handles, loc="upper right", fontsize=9, framealpha=0.9)
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.01)
    cb.set_label("dNBR (burn severity change; scar = ≥ 0.27)")
    ax.set_title(f"CFB Wainwright burn scar\nSentinel-2 change {when(pre_r)} → {when(post_r)} with fire detections",
                 loc="left", fontsize=12)
    fig.text(0.01, 0.01, "Contains modified Copernicus Sentinel data [2026]; NASA FIRMS; NOAA GOES-18. "
                         "Grey = cloud/shadow/water masked. Prime Rogue Inc. · CC BY-NC 4.0", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(OUT / "burn_scar_map.png")
    plt.close(fig)

    tc_pre, b = truecolour(pre_r["feature"])
    tc_post, _ = truecolour(post_r["feature"])
    ext_tc = (b[0], b[2], b[1], b[3])
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.6), dpi=120)
    for ax, img, r, label in [(axes[0], tc_pre, pre_r, "Before"), (axes[1], tc_post, post_r, "After")]:
        ax.imshow(img, extent=ext_tc)
        ax.set_xlim(ext_utm[0], ext_utm[1]), ax.set_ylim(ext_utm[2], ext_utm[3])
        h = overlay(ax)
        ax.set_title(f"{label}: Sentinel-2, {when(r)}", loc="left", fontsize=12)
    axes[1].legend(handles=h, loc="upper right", fontsize=8.5, framealpha=0.9)
    fig.text(0.01, 0.01, "Contains modified Copernicus Sentinel data [2026]; NASA FIRMS; NOAA GOES-18. "
                         "Prime Rogue Inc. · CC BY-NC 4.0", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / "before_after.png")
    plt.close(fig)

    summary = {"generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "pre_scene": pre_r["id"], "pre_datetime": pre_r["datetime"],
               "post_scene": post_r["id"], "post_datetime": post_r["datetime"],
               "post_aoi_clear_pct": round(post_r["clear_frac"] * 100),
               "valid_pixel_pct_both_scenes": round(valid_frac * 100),
               "burn_scar_km2_dnbr_0.27": round(area, 2),
               "possible_light_burn_fringe_km2_within_500m": round(fringe, 2),
               "burn_patches": int(len(keep)), "detections_used": len(pts),
               "method": "dNBR from Sentinel-2 L2A B8A/B12 at 20 m; SCL classes 2,4,5,7; scar = dNBR >= 0.27 patches "
                         f"within {SEED_BUFFER_M} m of a detection, holes filled"}
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "status.txt").unlink(missing_ok=True)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
