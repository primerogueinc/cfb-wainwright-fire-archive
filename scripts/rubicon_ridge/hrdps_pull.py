"""Task 3c: ECCC HRDPS continental 2.5 km forecasts archived on the MSC Datamart for Oct. 17, 2026.
Runs 06Z (f011-f018), 12Z (f000-f012) and 18Z (f000-f006); near-surface fields only. Each full-domain
GRIB2 file is downloaded to a scratch dir, cropped, point-extracted, then deleted.

Usage: python3 -I hrdps_pull.py OUT_DIR SCRATCH_DIR
Writes OUT_DIR/hrdps_points.csv and OUT_DIR/hrdps_crop_<run>.nc
"""
import concurrent.futures as cf
import datetime as dt
import math
import os
import sys
import time

import eccodes
import numpy as np
import pandas as pd
import requests
import xarray as xr

OUT, TMP = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)
BASE = "https://dd.weather.gc.ca/20261017/WXO-DD/model_hrdps/continental/2.5km"
FIELDS = ["WIND_AGL-10m", "WDIR_AGL-10m", "GUST_AGL-10m", "GUST-Max_AGL-10m", "TMP_AGL-2m",
          "RH_AGL-2m", "DPT_AGL-2m", "PRES_Sfc", "WIND_AGL-80m", "WDIR_AGL-80m"]
RUNS = {"06": range(11, 19), "12": range(0, 13), "18": range(0, 7)}
POINTS = {
    "fire_centre": (52.7645, -110.9052), "range2": (52.772, -110.90089),
    "CZWN_cfb_wainwright": (52.8294, -111.0956), "CYLL_lloydminster": (53.3106, -110.074),
    "HUGH_hughenden": (52.5782, -110.7837), "EDGE_edgerton": (52.7778, -110.4328),
    "GILT_gilt_edge_n": (53.071, -110.621), "BELL_bellshill": (52.5824, -111.4654),
    "ALBE_albert_hall": (53.1134, -111.1812), "RIBS_ribstone_s": (52.587, -110.3429),
    "wainwright_town": (52.839, -110.857),
}
CROP = dict(lat0=52.3, lat1=53.4, lon0=-111.8, lon1=-110.0)
S = requests.Session()


def get(url, dest):
    for i in range(4):
        try:
            r = S.get(url, timeout=180)
            if r.status_code != 200:
                return f"HTTP {r.status_code}"
            open(dest, "wb").write(r.content)
            return "ok"
        except requests.RequestException as e:
            err = str(e)
            time.sleep(3 + 3 * i)
    return "ERR " + err


GEO = {}


def read(path):
    with open(path, "rb") as fh:
        h = eccodes.codes_grib_new_from_file(fh)
        ni, nj = eccodes.codes_get(h, "Ni"), eccodes.codes_get(h, "Nj")
        vals = eccodes.codes_get_values(h).reshape(nj, ni)
        if "lat" not in GEO:
            lat = eccodes.codes_get_array(h, "latitudes").reshape(nj, ni)
            lon = eccodes.codes_get_array(h, "longitudes").reshape(nj, ni)
            lon = np.where(lon > 180, lon - 360, lon)
            GEO["lat"], GEO["lon"] = lat, lon
            m = (lat >= CROP["lat0"]) & (lat <= CROP["lat1"]) & (lon >= CROP["lon0"]) & (lon <= CROP["lon1"])
            jj, ii = np.where(m)
            GEO["crop"] = (slice(jj.min(), jj.max() + 1), slice(ii.min(), ii.max() + 1))
            GEO["pts"] = {}
            for k, (pla, plo) in POINTS.items():
                d = (lat - pla) ** 2 + ((lon - plo) * math.cos(math.radians(pla))) ** 2
                j, i = np.unravel_index(np.argmin(d), d.shape)
                GEO["pts"][k] = (j, i, float(np.sqrt(d[j, i]) * 111.2))
        meta = dict(units=eccodes.codes_get(h, "units"), shortName=eccodes.codes_get(h, "shortName"),
                    stepRange=eccodes.codes_get(h, "stepRange"))
        eccodes.codes_release(h)
    return vals, meta


rows, notes = [], []
for run, steps in RUNS.items():
    t_run = dt.datetime(2026, 10, 17, int(run))
    crops = {}
    for st in steps:
        valid = t_run + dt.timedelta(hours=st)
        jobs = []
        for fld in FIELDS:
            fn = f"20261017T{run}Z_MSC_HRDPS_{fld}_RLatLon0.0225_PT{st:03d}H.grib2"
            jobs.append((fld, f"{BASE}/{run}/{st:03d}/{fn}", os.path.join(TMP, fn)))
        with cf.ThreadPoolExecutor(5) as ex:
            res = list(ex.map(lambda j: (j, get(j[1], j[2])), jobs))
        row = dict(run=f"{run}Z", lead_h=st, valid_utc=valid.strftime("%Y-%m-%d %H:%M"),
                   valid_mdt=(valid - dt.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"))
        for (fld, url, path), status in res:
            if status != "ok":
                notes.append(f"{url}\t{status}")
                continue
            vals, meta = read(path)
            os.remove(path)
            cj, ci = GEO["crop"]
            crops.setdefault(fld, []).append((np.datetime64(valid), vals[cj, ci].astype("float32"), meta))
            for k, (j, i, dkm) in GEO["pts"].items():
                rows.append(dict(row, point=k, grid_dist_km=round(dkm, 2), field=fld,
                                 value=float(vals[j, i]), units=meta["units"], stepRange=meta["stepRange"]))
        print(run, st, flush=True)
    if crops:
        cj, ci = GEO["crop"]
        dvars = {}
        for fld, lst in crops.items():
            times = [x[0] for x in lst]
            dvars[fld.replace("-", "_")] = xr.DataArray(np.stack([x[1] for x in lst]), dims=("time", "y", "x"),
                                                        coords=dict(time=times), attrs=dict(units=lst[0][2]["units"]))
        ds = xr.Dataset(dvars, coords=dict(lat=(("y", "x"), GEO["lat"][cj, ci]), lon=(("y", "x"), GEO["lon"][cj, ci])))
        ds.attrs.update(source=f"ECCC MSC Datamart HRDPS continental 2.5 km, run 2026-10-17 {run}Z", crop=str(CROP))
        ds.to_netcdf(os.path.join(OUT, f"hrdps_crop_{run}Z.nc"), encoding={v: {"zlib": True} for v in ds.data_vars})

df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, "hrdps_points_long.csv"), index=False)
wide = df.pivot_table(index=["run", "lead_h", "valid_utc", "valid_mdt", "point"], columns="field", values="value").reset_index()
wide.to_csv(os.path.join(OUT, "hrdps_points_wide.csv"), index=False, float_format="%.3f")
open(os.path.join(OUT, "download_failures.txt"), "w").write("\n".join(notes) + "\n")
print("done", len(df), "fails", len(notes))
