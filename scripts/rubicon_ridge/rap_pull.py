"""Task 2: NOAA RAP hourly analyses (f00), 13 km grid 130 (awp130pgrb), from the public
noaa-rap-pds bucket (anonymous HTTPS). Byte-range downloads of only the near-surface messages
listed in each .idx file, then point extraction at the fire, Range 2, CZWN and nearby stations.

Usage: python3 -I rap_pull.py OUT_DIR
Writes:
  OUT_DIR/grib/rap.YYYYMMDD.tHHz.awp130pgrbf00.sfc.grib2  (selected messages only, full grid)
           for 15-01 UTC cycles on Oct 17-18 (the fire window plus margin)
  OUT_DIR/rap_points_f00.csv  hourly point series (bilinear and nearest), earth-relative winds
  OUT_DIR/rap_crop_f00.nc     cropped fields around the fire for every cycle
"""
import datetime as dt
import io
import math
import os
import sys

import numpy as np
import requests
import eccodes
import xarray as xr

OUT = sys.argv[1]
os.makedirs(os.path.join(OUT, "grib"), exist_ok=True)
BASE = "https://noaa-rap-pds.s3.amazonaws.com"
S = requests.Session()
eccodes.codes_grib_multi_support_on()  # UGRD/VGRD are packed as sub-messages of one GRIB message

WANT = [("GUST", "surface"), ("PRES", "surface"), ("TMP", "2 m above ground"),
        ("DPT", "2 m above ground"), ("RH", "2 m above ground"),
        ("UGRD", "10 m above ground"), ("VGRD", "10 m above ground"),
        ("UGRD", "80 m above ground"), ("VGRD", "80 m above ground"),
        ("HPBL", "surface"), ("PRATE", "surface"), ("REFC", "entire atmosphere")]

POINTS = {
    "fire_centre": (52.7645, -110.9052),
    "range2": (52.772, -110.90089),
    "CZWN_cfb_wainwright": (52.8294, -111.0956),
    "CYLL_lloydminster": (53.3092, -110.0725),
    "wainwright_town": (52.8390, -110.8570),
    "provost": (52.3537, -110.2690),
    "vermilion": (53.3560, -110.8240),
    "coronation": (52.0740, -111.4490),
    "kindersley": (51.5170, -109.1830),
}
CROP = dict(lat0=51.8, lat1=53.8, lon0=-112.6, lon1=-109.2)
KEEP_GRIB = lambda t: dt.datetime(2026, 10, 17, 15) <= t <= dt.datetime(2026, 10, 18, 1)


def idx_ranges(url):
    lines = S.get(url + ".idx", timeout=60).text.strip().splitlines()
    recs = []
    for ln in lines:
        p = ln.split(":")
        recs.append((p[0], int(p[1]), p[3], p[4]))
    # group sub-messages (211.1, 211.2) by offset
    offs = sorted(set(r[1] for r in recs))
    nxt = {o: (offs[i + 1] - 1 if i + 1 < len(offs) else None) for i, o in enumerate(offs)}
    out = {}
    for num, off, var, lev in recs:
        if (var, lev) in WANT:
            out[off] = nxt[off]
    return sorted(out.items())


def fetch(url):
    chunks = []
    for a, b in idx_ranges(url):
        rng = f"bytes={a}-{b}" if b is not None else f"bytes={a}-"
        r = S.get(url, headers={"Range": rng}, timeout=120)
        r.raise_for_status()
        chunks.append(r.content)
    return b"".join(chunks)


def decode(blob):
    fields, meta = {}, None
    f = io.BytesIO(blob)
    tmp = os.path.join(OUT, ".tmp.grib2")
    with open(tmp, "wb") as fh:
        fh.write(blob)
    with open(tmp, "rb") as fh:
        while True:
            h = eccodes.codes_grib_new_from_file(fh)
            if h is None:
                break
            name = eccodes.codes_get(h, "shortName")
            if name == "unknown":  # e.g. HPBL (0/3/18) has no ecCodes shortName
                name = "d{}c{}n{}".format(*(eccodes.codes_get(h, k) for k in ("discipline", "parameterCategory", "parameterNumber")))
            lev = eccodes.codes_get(h, "level")
            tol = eccodes.codes_get(h, "typeOfLevel")
            ni, nj = eccodes.codes_get(h, "Nx"), eccodes.codes_get(h, "Ny")
            vals = eccodes.codes_get_values(h).reshape(nj, ni)
            if meta is None:
                lats = eccodes.codes_get_array(h, "latitudes").reshape(nj, ni)
                lons = eccodes.codes_get_array(h, "longitudes").reshape(nj, ni)
                lons = np.where(lons > 180, lons - 360, lons)
                meta = dict(lat=lats, lon=lons,
                            LoV=eccodes.codes_get(h, "LoVInDegrees"),
                            Latin1=eccodes.codes_get(h, "Latin1InDegrees"),
                            Latin2=eccodes.codes_get(h, "Latin2InDegrees"))
            rel = eccodes.codes_get(h, "uvRelativeToGrid") if name in ("10u", "10v", "u", "v", "100u") else None
            fields[f"{name}_{tol}_{lev}"] = (vals, rel)
            eccodes.codes_release(h)
    os.remove(tmp)
    return fields, meta


def rotate(u, v, lon, meta):
    lat1, lat2 = math.radians(meta["Latin1"]), math.radians(meta["Latin2"])
    if abs(lat1 - lat2) < 1e-6:
        n = math.sin(lat1)
    else:
        n = math.log(math.cos(lat1) / math.cos(lat2)) / math.log(
            math.tan(math.pi / 4 + lat2 / 2) / math.tan(math.pi / 4 + lat1 / 2))
    lov = meta["LoV"] if meta["LoV"] <= 180 else meta["LoV"] - 360
    a = np.radians(n * (lon - lov))
    return np.cos(a) * u + np.sin(a) * v, -np.sin(a) * u + np.cos(a) * v


def interp_points(meta):
    """Return per point: nearest (j,i) and bilinear weights from the 4 surrounding cells via
    local inverse-distance on the 2x2 cell (adequate on a 13 km quasi-uniform grid)."""
    lat, lon = meta["lat"], meta["lon"]
    res = {}
    for k, (pla, plo) in POINTS.items():
        d = (lat - pla) ** 2 + ((lon - plo) * math.cos(math.radians(pla))) ** 2
        j, i = np.unravel_index(np.argmin(d), d.shape)
        js, is_ = slice(max(j - 1, 0), j + 2), slice(max(i - 1, 0), i + 2)
        dd = np.sqrt(d[js, is_]) * 111.2
        w = 1.0 / np.maximum(dd, 0.1) ** 2
        res[k] = dict(j=j, i=i, js=js, is_=is_, w=w / w.sum(), dist_km=float(np.sqrt(d[j, i]) * 111.2),
                      glat=float(lat[j, i]), glon=float(lon[j, i]))
    return res


rows, crops = [], []
t = dt.datetime(2026, 10, 16, 12)
end = dt.datetime(2026, 10, 18, 12)
pts = None
while t <= end:
    url = f"{BASE}/rap.{t:%Y%m%d}/rap.t{t:%H}z.awp130pgrbf00.grib2"
    try:
        blob = fetch(url)
    except Exception as e:
        print("FAIL", t, e, flush=True)
        t += dt.timedelta(hours=1)
        continue
    if KEEP_GRIB(t):
        with open(os.path.join(OUT, "grib", f"rap.{t:%Y%m%d}.t{t:%H}z.awp130pgrbf00.sfc.grib2"), "wb") as fh:
            fh.write(blob)
    F, meta = decode(blob)
    if pts is None:
        pts = interp_points(meta)
        lat, lon = meta["lat"], meta["lon"]
        m = (lat >= CROP["lat0"]) & (lat <= CROP["lat1"]) & (lon >= CROP["lon0"]) & (lon <= CROP["lon1"])
        jj, ii = np.where(m)
        cj, ci = slice(jj.min(), jj.max() + 1), slice(ii.min(), ii.max() + 1)
    # earth-relative winds
    for lvl, uk, vk in (("10m", "10u_heightAboveGround_10", "10v_heightAboveGround_10"),
                        ("80m", "u_heightAboveGround_80", "v_heightAboveGround_80")):
        if uk in F and vk in F:
            u, v = F[uk][0], F[vk][0]
            if F[uk][1] == 1:
                u, v = rotate(u, v, meta["lon"], meta)
            F[f"U{lvl}_earth"] = (u, 0)
            F[f"V{lvl}_earth"] = (v, 0)
    names = sorted(F)
    for k, p in pts.items():
        row = dict(valid_utc=t.strftime("%Y-%m-%d %H:%M"),
                   valid_mdt=(t - dt.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"),
                   point=k, grid_lat=round(p["glat"], 4), grid_lon=round(p["glon"], 4),
                   nearest_km=round(p["dist_km"], 2))
        for n in names:
            a = F[n][0]
            row[n + "_nearest"] = float(a[p["j"], p["i"]])
            row[n + "_idw"] = float((a[p["js"], p["is_"]] * p["w"]).sum())
        for lvl in ("10m", "80m"):
            for kind in ("nearest", "idw"):
                u, v = row.get(f"U{lvl}_earth_{kind}"), row.get(f"V{lvl}_earth_{kind}")
                if u is not None:
                    row[f"wspd{lvl}_kmh_{kind}"] = round(math.hypot(u, v) * 3.6, 2)
                    row[f"wdir{lvl}_deg_{kind}"] = round((math.degrees(math.atan2(-u, -v)) + 360) % 360, 1)
        rows.append(row)
    ds = xr.Dataset({n.replace(" ", "_"): (("y", "x"), F[n][0][cj, ci].astype("float32")) for n in names},
                    coords=dict(lat=(("y", "x"), meta["lat"][cj, ci]), lon=(("y", "x"), meta["lon"][cj, ci])))
    ds = ds.expand_dims(time=[np.datetime64(t)])
    crops.append(ds)
    print("ok", t, len(blob), flush=True)
    t += dt.timedelta(hours=1)

import pandas as pd
df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, "rap_points_f00.csv"), index=False, float_format="%.4f")
xr.concat(crops, "time").to_netcdf(os.path.join(OUT, "rap_crop_f00.nc"),
                                   encoding={v: {"zlib": True, "complevel": 4} for v in crops[0].data_vars})
print("done", len(df))
