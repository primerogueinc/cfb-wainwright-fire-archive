#!/usr/bin/env python3
"""Pull digital elevation models for the CFB Wainwright burn area.

Sources (each tried independently; failures are logged, not fatal):
  * NRCan MRDEM-30 (Medium Resolution DEM, 30 m, DTM), Open Government Licence - Canada
    https://canelevation-dem.s3.ca-central-1.amazonaws.com/mrdem-30/mrdem-30-dtm.tif
  * NRCan HRDEM (High Resolution DEM, 1-2 m lidar) via the NRCan STAC catalogue, if it covers the area
  * Copernicus GLO-30 DSM (30 m), tile N52 W111, (c) DLR/Airbus, provided under COPERNICUS by the EU and ESA

Each is clipped to the study box and written as a GeoTIFF in its native CRS, plus a copy
resampled to 10 m in NAD83 / Alberta 10-TM (EPSG:3400) for analysis. Outputs: data/dem/.
"""
import json, os, sys, traceback, urllib.request
from pathlib import Path
import numpy as np
import rasterio
from rasterio.warp import transform_bounds, calculate_default_transform, reproject, Resampling
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "dem"; OUT.mkdir(parents=True, exist_ok=True)
BOX = (-111.06, 52.69, -110.78, 52.86)   # lon/lat: burn scar + 5 km
LOG = []
def log(*a):
    m = " ".join(str(x) for x in a); LOG.append(m); print(m, flush=True)

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif,.tiff")

TIGHT = (-110.975, 52.725, -110.845, 52.815)   # scar + ~1.5 km, for lidar
MAXMB = 90

def clip(url, name, note, box=BOX, min_res=None):
    with rasterio.open(url) as src:
        b = transform_bounds("EPSG:4326", src.crs, *box, densify_pts=21)
        win = from_bounds(*b, transform=src.transform).round_offsets().round_lengths()
        f = 1
        if min_res and src.res[0] < min_res:
            f = int(round(min_res / src.res[0]))
        shape = (int(win.height // f), int(win.width // f))
        arr = src.read(1, window=win, out_shape=shape, boundless=True, resampling=Resampling.average,
                       fill_value=src.nodata if src.nodata is not None else -9999)
        tr = src.window_transform(win) * rasterio.Affine.scale(win.width / shape[1], win.height / shape[0])
        prof = dict(driver="GTiff", height=arr.shape[0], width=arr.shape[1], count=1, dtype=arr.dtype,
                    crs=src.crs, transform=tr, nodata=src.nodata, compress="deflate", predictor=2 if arr.dtype.kind == "f" else 1)
        p = Path("/tmp") / f"{name}_native.tif"
        with rasterio.open(p, "w", **prof) as dst: dst.write(arr, 1)
        res = (src.res[0] * f, src.res[1] * f)
    valid = arr[(arr != (src.nodata if src.nodata is not None else -9999)) & np.isfinite(arr)]
    log(f"{name}: {arr.shape} px at {res}, elevation {valid.min():.1f}-{valid.max():.1f} m" if valid.size else f"{name}: no valid data")
    # 10 m EPSG:3400 copy
    dst_crs = "EPSG:3400"
    with rasterio.open(p) as s:
        t, w, h = calculate_default_transform(s.crs, dst_crs, s.width, s.height, *s.bounds, resolution=10)
        out = np.full((h, w), -9999, "float32")
        reproject(rasterio.band(s, 1), out, src_transform=s.transform, src_crs=s.crs, src_nodata=s.nodata,
                  dst_transform=t, dst_crs=dst_crs, dst_nodata=-9999, resampling=Resampling.bilinear)
    with rasterio.open(OUT / f"{name}_3400_10m.tif", "w", driver="GTiff", height=h, width=w, count=1, dtype="float32",
                       crs=dst_crs, transform=t, nodata=-9999, compress="deflate", predictor=3) as d: d.write(out, 1)
    mb = p.stat().st_size / 1e6
    if mb <= MAXMB:
        import shutil; shutil.move(str(p), OUT / p.name)
    else:
        log(f"{name}: native clip {mb:.0f} MB > {MAXMB} MB, kept only the 10 m copy"); p.unlink()
    return dict(name=name, url=url, note=note, native_kept=mb <= MAXMB, native_res=list(res), shape=list(arr.shape),
                min=float(valid.min()) if valid.size else None, max=float(valid.max()) if valid.size else None)

results = []
# 1. MRDEM-30
try:
    results.append(clip("/vsicurl/https://canelevation-dem.s3.ca-central-1.amazonaws.com/mrdem-30/mrdem-30-dtm.tif",
                        "mrdem30_dtm", "NRCan MRDEM-30 bare-earth DTM, 30 m. Open Government Licence - Canada."))
except Exception as e:
    log("MRDEM failed:", repr(e)); traceback.print_exc()
# 2. Copernicus GLO-30
try:
    results.append(clip("/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N52_00_W111_00_DEM/Copernicus_DSM_COG_10_N52_00_W111_00_DEM.tif",
                        "copernicus_glo30_dsm", "Copernicus GLO-30 DSM (surface model), 30 m. (c) DLR e.V. 2010-2014 and (c) Airbus 2014-2018, provided under COPERNICUS by the EU and ESA."))
except Exception as e:
    log("Copernicus failed:", repr(e)); traceback.print_exc()
# 3. HRDEM via STAC (lidar coverage is patchy; take any item intersecting the box)
try:
    import pystac_client
    cat = pystac_client.Client.open("https://datacube.services.geo.ca/stac/api/")
    cols = [c.id for c in cat.get_collections()]
    log("STAC collections with 'hrdem':", [c for c in cols if "hrdem" in c.lower()])
    for col in [c for c in cols if "hrdem" in c.lower()]:
        items = list(cat.search(collections=[col], bbox=BOX, max_items=20).items())
        log(f"{col}: {len(items)} items")
        for it in items[:6]:
            for k, a in it.assets.items():
                if a.href.endswith(".tif") and ("dtm" in k.lower() or "dtm" in a.href.lower()):
                    try:
                        results.append(clip("/vsicurl/" + a.href, f"{col}_{it.id}_{k}".replace("/", "_")[:90],
                                            f"NRCan {col} item {it.id}, asset {k}, averaged to 2 m over the scar + ~1.5 km. Open Government Licence - Canada.",
                                            box=TIGHT, min_res=2.0))
                    except Exception as e:
                        log("HRDEM item failed:", it.id, k, repr(e))
                    break
except Exception as e:
    log("HRDEM/STAC failed:", repr(e)); traceback.print_exc()

json.dump(results, open(OUT / "sources.json", "w"), indent=1)
(OUT / "run.log").write_text("\n".join(LOG) + "\n")
print(json.dumps(results, indent=1))
sys.exit(0 if results else 1)
