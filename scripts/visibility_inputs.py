#!/usr/bin/env python3
"""Inputs for the visibility test (stress test part 5): what could people near Range 2 see?

1. Airport observations (METARs) Oct. 17, 2026, via the Iowa Environmental Mesonet: visibility and
   present-weather codes (blowing dust BLDU, dust DU, smoke FU, haze HZ) as the cold front crossed Alberta.
2. Satellite imagery from NASA GIBS (Worldview): NOAA-20, NOAA-21 and Suomi-NPP VIIRS and Aqua/Terra MODIS
   true colour for Oct. 17, plus GOES-West (GOES-18) visible / GeoColor frames 20:30-22:30 UTC if available.
3. Canopy height: Meta / World Resources Institute 1 m global canopy height (quadkey 021300232),
   with ESA WorldCover 2021 10 m land cover (tree cover class) as a fallback.
Outputs: data/visibility/.
"""
import json, os, sys, traceback, urllib.request, urllib.parse, datetime as dt
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "visibility"; OUT.mkdir(parents=True, exist_ok=True)
LOG = []
UA = {"User-Agent": "prime-rogue-cfb-wainwright-archive/1.0"}
def log(*a):
    m = " ".join(str(x) for x in a); LOG.append(m); print(m, flush=True)
def get(url, path, timeout=120):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r, open(path, "wb") as f:
        f.write(r.read())
    log("ok", path.name, os.path.getsize(path), "bytes <-", url[:160])

# 1. METARs
st = ["CYEG", "CYED", "CYXD", "CYLL", "CYOD", "CYQF", "CYQL", "CYBW", "CYYC", "CYPA", "CYXE", "CYQV", "CYVG", "CYPE", "CYET", "CYQU", "CYZH", "CYCT", "CYOJ"]
q = [("station", s) for s in st] + [("data", "all"), ("year1", "2026"), ("month1", "10"), ("day1", "17"), ("year2", "2026"), ("month2", "10"), ("day2", "18"),
     ("tz", "Etc/UTC"), ("format", "onlycomma"), ("latlon", "yes"), ("elev", "yes"), ("missing", "M"), ("trace", "T"), ("direct", "no"), ("report_type", "3"), ("report_type", "4")]
try:
    get("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?" + urllib.parse.urlencode(q), OUT / "metar_2026-10-17.csv")
except Exception as e:
    log("METAR failed", repr(e))

# 2. GIBS imagery (EPSG:4326 WMS)
BB = (51.8, -113.6, 53.8, -109.4)   # lat/lon box: Edmonton to the base
BBZ = (52.62, -111.20, 52.92, -110.60)  # base close-up
def wms(layer, time, bbox, w, h, name, fmt="image/jpeg"):
    p = dict(SERVICE="WMS", REQUEST="GetMap", VERSION="1.3.0", LAYERS=layer, STYLES="", CRS="EPSG:4326",
             BBOX=",".join(map(str, bbox)), WIDTH=w, HEIGHT=h, FORMAT=fmt, TIME=time)
    url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?" + urllib.parse.urlencode(p)
    try:
        get(url, OUT / name)
    except Exception as e:
        log("GIBS failed", layer, time, repr(e))
for layer in ["VIIRS_NOAA20_CorrectedReflectance_TrueColor", "VIIRS_NOAA21_CorrectedReflectance_TrueColor",
              "VIIRS_SNPP_CorrectedReflectance_TrueColor", "MODIS_Aqua_CorrectedReflectance_TrueColor", "MODIS_Terra_CorrectedReflectance_TrueColor"]:
    wms(layer, "2026-10-17", BB, 1400, 667, f"gibs_{layer}_region.jpg")
    wms(layer, "2026-10-17", BBZ, 1200, 600, f"gibs_{layer}_base.jpg")
# GOES-West frames
for hhmm in ["2030", "2040", "2050", "2100", "2110", "2120", "2130", "2140", "2150", "2200", "2210", "2220", "2230"]:
    t = f"2026-10-17T{hhmm[:2]}:{hhmm[2:]}:00Z"
    for layer in ["GOES-West_ABI_GeoColor", "GOES-West_ABI_Band2_Red_Visible_1km"]:
        wms(layer, t, BB, 1400, 667, f"gibs_{layer}_{hhmm}Z_region.jpg")
        wms(layer, t, BBZ, 1200, 600, f"gibs_{layer}_{hhmm}Z_base.jpg")
# also the capabilities list for GOES-West layers (to know what exists)
try:
    get("https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/1.0.0/WMTSCapabilities.xml", OUT / "_gibs_capabilities.xml", timeout=180)
    cap = (OUT / "_gibs_capabilities.xml").read_text(errors="ignore")
    import re
    ids = sorted(set(re.findall(r"<ows:Identifier>(GOES-West[^<]*)</ows:Identifier>", cap)))
    log("GOES-West layers:", ids)
    (OUT / "_gibs_capabilities.xml").unlink()
except Exception as e:
    log("caps failed", repr(e))

# 3. Canopy height + land cover
import numpy as np, rasterio
from rasterio.warp import transform_bounds, calculate_default_transform, reproject, Resampling
from rasterio.windows import from_bounds
BOX = (-110.97, 52.725, -110.845, 52.815)
def clip(url, name, res):
    with rasterio.open(url) as src:
        b = transform_bounds("EPSG:4326", src.crs, *BOX, densify_pts=21)
        win = from_bounds(*b, transform=src.transform).round_offsets().round_lengths()
        arr = src.read(1, window=win, boundless=True, fill_value=src.nodata if src.nodata is not None else 0)
        tr = src.window_transform(win); crs = src.crs; nod = src.nodata
    p = Path("/tmp") / f"{name}_native.tif"
    with rasterio.open(p, "w", driver="GTiff", height=arr.shape[0], width=arr.shape[1], count=1, dtype=arr.dtype, crs=crs, transform=tr, nodata=nod, compress="deflate") as d: d.write(arr, 1)
    with rasterio.open(p) as s:
        t, w, h = calculate_default_transform(s.crs, "EPSG:3400", s.width, s.height, *s.bounds, resolution=res)
        out = np.zeros((h, w), "float32")
        reproject(rasterio.band(s, 1), out, src_transform=s.transform, src_crs=s.crs, src_nodata=s.nodata, dst_transform=t, dst_crs="EPSG:3400",
                  resampling=Resampling.max if "chm" in name else Resampling.mode)
    with rasterio.open(OUT / f"{name}_3400_{int(res)}m.tif", "w", driver="GTiff", height=h, width=w, count=1, dtype="float32", crs="EPSG:3400", transform=t, nodata=-9999, compress="deflate") as d: d.write(out, 1)
    log(name, "ok", arr.shape, "max", float(np.nanmax(arr)))
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
try:
    clip("/vsicurl/https://dataforgood-fb-data.s3.amazonaws.com/forests/v1/alsgedi_global_v6_float/chm/021300232.tif", "meta_wri_chm", 10.0)
except Exception as e:
    log("Meta CHM failed", repr(e)); traceback.print_exc()
try:
    clip("/vsicurl/https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N51W111_Map.tif", "esa_worldcover2021", 10.0)
except Exception as e:
    log("WorldCover failed", repr(e)); traceback.print_exc()
(OUT / "run.log").write_text("\n".join(LOG) + "\n")
