#!/usr/bin/env python3
"""Re-fetch reference data used in the first analysis (Oct. 19-20, 2026) whose
original downloads were not kept:

  * ECCC hourly observations, Oct. 2026, for the stations used to time the cold
    front (Edmonton International, Camrose, Vegreville, Coronation) plus CFB
    Wainwright and Lloydminster for comparison
  * NRCan Canadian Geographical Names Database entries near the site
  * NRCan CanVec 1:50K transport, resource-management and man-made features
    clipped to the area around the base
  * Alberta Energy Regulator pipelines clipped to the same area

Outputs go to data/reference/. Large national files are downloaded to a cache
(git-ignored) and only the clipped subsets are kept.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "reference"
CACHE = OUT / "cache"
BBOX = (-111.35, 52.55, -110.45, 52.98)  # west, south, east, north
UA = {"User-Agent": "prime-rogue-cfb-wainwright-archive/1.0"}
LOG: list[str] = []


def log(*a):
    m = " ".join(str(x) for x in a)
    LOG.append(m)
    print(m, flush=True)


def http(url, timeout=600):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def cached(url, name):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / name
    if not p.exists():
        p.write_bytes(http(url, timeout=1800))
    return p


# ------------------------------------------------------------- ECCC hourly
STATIONS = [("EDMONTON INTERNATIONAL", "EDMONTON INTL A"), ("CAMROSE",), ("VEGREVILLE",), ("CORONATION",),
            ("WAINWRIGHT CFB AIRFIELD 21",), ("LLOYDMINSTER",)]


def eccc_hourly():
    inv = http("https://collaboration.cmc.ec.gc.ca/cmc/climate/Get_More_Data_Plus_de_donnees/"
               "Station%20Inventory%20EN.csv").decode("utf-8", "replace")
    lines = inv.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith('"Name"'))
    rows = list(csv.DictReader(lines[start:]))
    d = OUT / "eccc_hourly_oct2026"
    d.mkdir(parents=True, exist_ok=True)
    picked = []
    for names in STATIONS:
        cands = [r for r in rows if r["Province"] == "ALBERTA" and any(r["Name"].upper().startswith(n) for n in names)
                 and r.get("HLY Last Year", "").strip() and int(r["HLY Last Year"]) >= 2026]
        if not cands:
            log("no hourly station for", names)
            continue
        for r in cands:
            sid = r["Station ID"]
            url = ("https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID="
                   f"{sid}&Year=2026&Month=10&Day=1&time=LST&timeframe=1&submit=Download+Data")
            body = http(url)
            fn = f"{re.sub(r'[^A-Za-z0-9]+', '_', r['Name']).strip('_')}_{r['Climate ID']}_hourly_2026-10.csv"
            # the bulk service sometimes returns rows with no values; fall back to MSC GeoMet's OGC API
            sample = [l for l in body.decode("utf-8", "replace").splitlines() if "2026-10-17 14:00" in l]
            if not sample or sample[0].count(",") < 12:
                api = ("https://api.weather.gc.ca/collections/climate-hourly/items?f=json&limit=10000"
                       f"&CLIMATE_IDENTIFIER={r['Climate ID']}&datetime=2026-10-01T00:00:00Z/2026-10-31T23:59:59Z")
                try:
                    j = json.loads(http(api))
                    feats = j.get("features", [])
                    log("bulk CSV empty for", r["Name"], "- GeoMet API rows:", len(feats))
                    if feats:
                        (d / fn.replace(".csv", "_geomet.json")).write_text(json.dumps(j) + "\n")
                        keys = sorted({k for f_ in feats for k in f_["properties"]})
                        with (d / fn.replace(".csv", "_geomet.csv")).open("w", newline="") as fh:
                            wr = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
                            wr.writeheader()
                            wr.writerows(sorted((f_["properties"] for f_ in feats),
                                                key=lambda p: str(p.get("LOCAL_DATE", ""))))
                except Exception as exc:
                    log("GeoMet API failed for", r["Name"], exc)
            (d / fn).write_bytes(body)
            picked.append({"name": r["Name"], "climate_id": r["Climate ID"], "station_id": sid,
                           "lat": r.get("Latitude (Decimal Degrees)"), "lon": r.get("Longitude (Decimal Degrees)"),
                           "file": fn, "bytes": len(body)})
            log("ECCC", r["Name"], sid, len(body), "bytes")
    with (d / "stations.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["name", "climate_id", "station_id", "lat", "lon", "file", "bytes"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(picked)


# ------------------------------------------------------------- CGNDB names
def geonames():
    w, s, e, n = BBOX
    url = f"https://geogratis.gc.ca/services/geoname/en/geonames.json?bbox={w},{s},{e},{n}"
    data = json.loads(http(url))
    items = data.get("items", data if isinstance(data, list) else [])
    (OUT / "cgndb_geonames_near_site.json").write_text(json.dumps(data, indent=1) + "\n")
    with (OUT / "cgndb_geonames_near_site.csv").open("w", newline="") as fh:
        wr = csv.writer(fh, lineterminator="\n")
        wr.writerow(["name", "concise", "generic", "latitude", "longitude", "id"])
        for it in items:
            wr.writerow([it.get("name"), (it.get("concise") or {}).get("code"), (it.get("generic") or {}).get("term"),
                         it.get("latitude"), it.get("longitude"), it.get("id")])
    log("CGNDB names:", len(items))


# ------------------------------------------------------------- clipping helper
def clip_shapefiles(zpath: Path, outname: str, pattern=r"\.shp$"):
    import geopandas as gpd
    from shapely.geometry import box

    ext = CACHE / (zpath.stem + "_x")
    if not ext.exists():
        with zipfile.ZipFile(zpath) as z:
            z.extractall(ext)
    area = gpd.GeoSeries([box(*BBOX)], crs="EPSG:4326")
    layers = {}
    for shp in sorted(ext.rglob("*.shp")):
        if not re.search(pattern, shp.name, re.I):
            continue
        try:
            g = gpd.read_file(shp, bbox=area)
        except Exception as exc:
            log("skip", shp.name, exc)
            continue
        if len(g):
            layers[shp.stem] = g.to_crs("EPSG:4326")
            log(outname, shp.stem, len(g))
    if layers:
        import pandas as pd
        allg = pd.concat([g.assign(layer=k) for k, g in layers.items()], ignore_index=True)
        allg = gpd.GeoDataFrame(allg, geometry="geometry", crs="EPSG:4326")
        for c in allg.columns:
            if allg[c].dtype == object and c != "geometry":
                allg[c] = allg[c].astype(str)
        allg.to_file(OUT / f"{outname}.geojson", driver="GeoJSON")
    return len(layers)


def canvec():
    base = "https://ftp.maps.canada.ca/pub/nrcan_rncan/vector/canvec/shp"
    for theme in ("Transport", "Res_MGT", "ManMade"):
        z = cached(f"{base}/{theme}/canvec_50K_AB_{theme}_shp.zip", f"canvec_{theme}.zip")
        clip_shapefiles(z, f"canvec50k_{theme.lower()}_near_site")


def aer_pipelines():
    z = cached("https://static.aer.ca/prd/data/pipeline/Pipelines_SHP.zip", "aer_pipelines.zip")
    clip_shapefiles(z, "aer_pipelines_near_site", pattern=r"GCS|NAD83|\.shp$")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in (("eccc", eccc_hourly), ("cgndb", geonames), ("canvec", canvec), ("aer", aer_pipelines)):
        if only and name not in only:
            continue
        try:
            fn()
        except Exception as exc:
            log(f"{name} FAILED: {exc}")
    (OUT / "refetch.log").write_text("\n".join(LOG) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
