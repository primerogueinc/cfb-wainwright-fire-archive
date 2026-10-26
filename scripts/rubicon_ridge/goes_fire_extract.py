"""Task 1b: GOES-18/19 ABI Full Disk fire detection (FDCF) and L1b radiances (RadF band 7 = 3.9 um,
band 13 = 10.3 um) around the CFB Wainwright fire, Oct. 17, 2026 (day 290) 16:00 UTC - Oct. 18 00:59 UTC.

Files are read lazily over anonymous HTTPS (fsspec + h5netcdf), so only the HDF5 chunks covering the
small crop box are transferred; nothing full-disk is written to disk.

Usage: python3 -I goes_fire_extract.py OUT_DIR
Writes (OUT_DIR):
  fdcf_crop_G18.nc / fdcf_crop_G19.nc   Mask, Power, Temp, Area, DQF stacks over the crop box
  radf_c07_crop_G1x.nc / radf_c13_crop_G1x.nc  radiance + brightness temperature stacks
  fdc_fire_pixels.csv     every pixel in the crop box with a fire mask code (10-15, 30-35), per scan
  fdc_point_series.csv    per scan: FDC values at the pixel containing the fire centre and Range 2,
                          plus fire-pixel count / total FRP within the burn box
  rad_point_series.csv    per scan: C07/C13 BT at the fire pixel, burn-box max, background median
  conus_coverage_check.json  whether the CONUS/PACUS FDC sector reaches the fire
"""
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fsspec
import numpy as np
import pandas as pd
import xarray as xr
import goes_common as gc

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
FS = fsspec.filesystem("https", block_size=2 ** 18)
FIRE = (52.7645, -110.9052)
RANGE2 = (52.772, -110.90089)
BOX = dict(lat0=52.45, lat1=53.10, lon0=-111.45, lon1=-110.35)       # ~70 x 75 km crop saved
BURN = dict(lat0=52.72, lat1=52.81, lon0=-110.98, lon1=-110.83)       # fire area for counting
BG = gc.BG_BOX
FIRE_CODES = {10, 11, 12, 13, 14, 15, 30, 31, 32, 33, 34, 35}
HOURS = [(290, h) for h in range(16, 24)] + [(291, 0)]


def keys(sat, prod, chan=None):
    out = []
    for doy, h in HOURS:
        for k, s in gc.list_keys(f"noaa-goes{sat}", f"{prod}/2026/{doy:03d}/{h:02d}/"):
            if chan is None or f"C{chan:02d}_" in k:
                out.append(k)
    return sorted(out)


def open_remote(sat, key):
    f = FS.open(f"https://noaa-goes{sat}.s3.amazonaws.com/{key}", "rb")
    return xr.open_dataset(f, engine="h5netcdf", mask_and_scale=True), f


def pix_index(ds, lat, lon):
    x, y = gc.latlon_to_xy(ds, lat, lon)
    xs, ys = ds["x"].values, ds["y"].values
    return int(np.argmin(np.abs(ys - y))), int(np.argmin(np.abs(xs - x)))


CACHE = {}


def crop_geo(ds, tag):
    """crop slices, lat/lon of cropped pixels; cached per (sat, resolution)"""
    if tag not in CACHE:
        sj, si = gc.crop_index(ds, box=BOX, pad=1)
        sub = ds.isel(y=sj, x=si)
        lat, lon = gc.pixel_latlon(sub)
        CACHE[tag] = (sj, si, lat, lon)
    return CACHE[tag]


def in_box(lat, lon, b):
    return (lat >= b["lat0"]) & (lat <= b["lat1"]) & (lon >= b["lon0"]) & (lon <= b["lon1"])


# ---------- CONUS sector check ----------
cov = {}
for sat in ("18", "19"):
    ks = keys(sat, "ABI-L2-FDCC")
    if not ks:
        cov[f"G{sat}"] = "no FDCC files"
        continue
    ds, f = open_remote(sat, ks[len(ks) // 2])
    x, y = gc.latlon_to_xy(ds, *FIRE)
    xs, ys = ds["x"].values, ds["y"].values
    cov[f"G{sat}"] = dict(file=ks[len(ks) // 2], fire_x_rad=float(x), fire_y_rad=float(y),
                         sector_x=[float(xs.min()), float(xs.max())], sector_y=[float(ys.min()), float(ys.max())],
                         covers=bool(xs.min() <= x <= xs.max() and ys.min() <= y <= ys.max()),
                         n_files_16_00z=len(ks))
    ds.close(); f.close()
json.dump(cov, open(os.path.join(OUT, "conus_coverage_check.json"), "w"), indent=1)
print(cov, flush=True)

# ---------- FDCF ----------
fire_rows, pt_rows = [], []
for sat in ("18", "19"):
    stack = []
    for k in keys(sat, "ABI-L2-FDCF"):
        try:
            ds, f = open_remote(sat, k)
            sj, si, lat, lon = crop_geo(ds, (sat, "fdc"))
            sub = ds[["Mask", "Power", "Temp", "Area", "DQF"]].isel(y=sj, x=si).load()
            t0 = gc.scan_start(k)
            jf, if_ = pix_index(ds, *FIRE)
            jr, ir = pix_index(ds, *RANGE2)
            ds.close(); f.close()
        except Exception as e:
            print("FAIL", k, e, flush=True)
            continue
        m = sub["Mask"].values
        burn = in_box(lat, lon, BURN)
        isfire = np.isin(m, list(FIRE_CODES))
        for j, i in zip(*np.where(isfire)):
            fire_rows.append(dict(scan_start_utc=t0.isoformat(timespec="seconds"),
                                  scan_start_mdt=(t0 - dt.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
                                  sat=f"G{sat}", pix_lat=round(float(lat[j, i]), 4), pix_lon=round(float(lon[j, i]), 4),
                                  in_burn_box=bool(burn[j, i]), mask=int(m[j, i]),
                                  frp_mw=float(sub["Power"].values[j, i]), temp_k=float(sub["Temp"].values[j, i]),
                                  area_m2=float(sub["Area"].values[j, i]), dqf=int(sub["DQF"].values[j, i]), file=k))
        r = dict(scan_start_utc=t0.isoformat(timespec="seconds"),
                 scan_start_mdt=(t0 - dt.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"), sat=f"G{sat}")
        for tag, (jj, ii) in (("fire", (jf, if_)), ("range2", (jr, ir))):
            lj, li = jj - sj.start, ii - si.start
            r[f"{tag}_pix_lat"] = round(float(lat[lj, li]), 4)
            r[f"{tag}_pix_lon"] = round(float(lon[lj, li]), 4)
            for v in ("Mask", "Power", "Temp", "Area", "DQF"):
                r[f"{tag}_{v}"] = float(sub[v].values[lj, li])
        r["burnbox_fire_pixels"] = int((isfire & burn).sum())
        r["burnbox_frp_mw"] = float(np.nansum(np.where(isfire & burn, sub["Power"].values, 0)))
        r["burnbox_max_temp_k"] = float(np.nanmax(np.where(isfire & burn, sub["Temp"].values, np.nan))) if (isfire & burn).any() else np.nan
        r["burnbox_mask_codes"] = ";".join(str(int(c)) for c in sorted(set(m[burn].ravel().tolist())))
        r["cropbox_fire_pixels"] = int(isfire.sum())
        r["file"] = k
        pt_rows.append(r)
        sub = sub.expand_dims(t=[np.datetime64(t0)])
        stack.append(sub.drop_vars([c for c in sub.coords if c not in ("t",)], errors="ignore"))
        print(sat, "FDCF", t0, r["burnbox_fire_pixels"], r["burnbox_frp_mw"], flush=True)
    if stack:
        sj, si, lat, lon = CACHE[(sat, "fdc")]
        S = xr.concat(stack, "t")
        S = S.assign_coords(lat=(("y", "x"), lat), lon=(("y", "x"), lon))
        S.attrs.update(source=f"noaa-goes{sat} ABI-L2-FDCF, cropped {BOX}", note="t = scan start UTC")
        S.to_netcdf(os.path.join(OUT, f"fdcf_crop_G{sat}.nc"),
                    encoding={v: {"zlib": True} for v in S.data_vars})

pd.DataFrame(fire_rows).to_csv(os.path.join(OUT, "fdc_fire_pixels.csv"), index=False)
pd.DataFrame(pt_rows).sort_values("scan_start_utc").to_csv(os.path.join(OUT, "fdc_point_series.csv"), index=False)

# ---------- RadF band 7 and 13 ----------
rad_rows = {}
for sat in ("18", "19"):
    for ch in (7, 13):
        stack = []
        for k in keys(sat, "ABI-L1b-RadF", ch):
            try:
                ds, f = open_remote(sat, k)
                sj, si, lat, lon = crop_geo(ds, (sat, "2km"))
                sub = ds[["Rad", "DQF"]].isel(y=sj, x=si).load()
                fk1, fk2 = float(ds["planck_fk1"]), float(ds["planck_fk2"])
                bc1, bc2 = float(ds["planck_bc1"]), float(ds["planck_bc2"])
                jf, if_ = pix_index(ds, *FIRE)
                t0 = gc.scan_start(k)
                ds.close(); f.close()
            except Exception as e:
                print("FAIL", k, e, flush=True)
                continue
            R = sub["Rad"].values
            with np.errstate(invalid="ignore", divide="ignore"):
                bt = (fk2 / np.log(fk1 / R + 1) - bc1) / bc2
            sub["BT"] = (("y", "x"), bt.astype("float32"))
            burn, bg = in_box(lat, lon, BURN), in_box(lat, lon, BG)
            key = (t0.isoformat(timespec="seconds"), f"G{sat}")
            row = rad_rows.setdefault(key, dict(scan_start_utc=key[0],
                                                scan_start_mdt=(t0 - dt.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
                                                sat=key[1]))
            lj, li = jf - sj.start, if_ - si.start
            row[f"c{ch:02d}_fire_pix_bt_k"] = round(float(bt[lj, li]), 2)
            row[f"c{ch:02d}_burnbox_max_bt_k"] = round(float(np.nanmax(bt[burn])), 2)
            row[f"c{ch:02d}_burnbox_median_bt_k"] = round(float(np.nanmedian(bt[burn])), 2)
            bgv = bt[bg] if bg.any() else bt
            row[f"c{ch:02d}_bg_median_bt_k"] = round(float(np.nanmedian(bgv)), 2)
            jm = np.nanargmax(np.where(burn, bt, -np.inf))
            row[f"c{ch:02d}_burnbox_max_lat"] = round(float(lat.ravel()[jm]), 4)
            row[f"c{ch:02d}_burnbox_max_lon"] = round(float(lon.ravel()[jm]), 4)
            sub = sub.expand_dims(t=[np.datetime64(t0)])
            stack.append(sub.drop_vars([c for c in sub.coords if c != "t"], errors="ignore"))
            print(sat, ch, t0, row[f"c{ch:02d}_burnbox_max_bt_k"], flush=True)
        if stack:
            sj, si, lat, lon = CACHE[(sat, "2km")]
            S = xr.concat(stack, "t").assign_coords(lat=(("y", "x"), lat), lon=(("y", "x"), lon))
            S.attrs.update(source=f"noaa-goes{sat} ABI-L1b-RadF C{ch:02d}, cropped {BOX}",
                           note="BT from planck_fk1/fk2/bc1/bc2 in each file; t = scan start UTC")
            S.to_netcdf(os.path.join(OUT, f"radf_c{ch:02d}_crop_G{sat}.nc"),
                        encoding={v: {"zlib": True} for v in S.data_vars})

pd.DataFrame(list(rad_rows.values())).sort_values(["scan_start_utc", "sat"]).to_csv(
    os.path.join(OUT, "rad_point_series.csv"), index=False)
print("done")
