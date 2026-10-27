"""Task 1: inventory GOES-18/19 ABI products for 2026 day 290, 19-23 UTC, and test sector coverage
of the fire point from each file's own projection.

Usage: python3 -I goes_inventory.py OUT_DIR TMP_DIR
"""
import collections
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xarray as xr
import goes_common as gc

OUT, TMP = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)
HOURS = ["19", "20", "21", "22", "23"]
PRODUCTS = ["ABI-L1b-RadF", "ABI-L1b-RadC", "ABI-L1b-RadM",
            "ABI-L2-CMIPF", "ABI-L2-CMIPC", "ABI-L2-CMIPM",
            "ABI-L2-MCMIPF", "ABI-L2-MCMIPC", "ABI-L2-MCMIPM",
            "ABI-L2-FDCF", "ABI-L2-FDCC", "ABI-L2-FDCM",
            "ABI-L2-ACMF", "ABI-L2-ACMC", "ABI-L2-ACMM"]

rows, summary, coverage = [], [], []
for sat in ("18", "19"):
    bucket = f"noaa-goes{sat}"
    for prod in PRODUCTS:
        for hr in HOURS:
            keys = gc.list_keys(bucket, f"{prod}/2026/290/{hr}/")
            for k, s in keys:
                fn = k.split("/")[-1]
                # e.g. OR_ABI-L1b-RadM1-M6C07_G18_... -> sector RadM1, mode/channel M6C07
                parts = fn.split("_")[1].split("-")
                sector = parts[2]
                chan = parts[3]
                rows.append(dict(sat=f"G{sat}", product=prod, sector=sector, mode_chan=chan,
                                 scan_start_utc=gc.scan_start(k).isoformat(), size=s, key=k))
        print(sat, prod, sum(1 for r in rows if r["sat"] == f"G{sat}" and r["product"] == prod), flush=True)

with open(os.path.join(OUT, "goes_inventory_doy290_19-23z.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

cnt = collections.Counter((r["sat"], r["product"], r["sector"], r["mode_chan"]) for r in rows)
with open(os.path.join(OUT, "goes_inventory_summary.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["sat", "product", "sector", "mode_channel", "n_files_19-23z"])
    for k in sorted(cnt):
        w.writerow(list(k) + [cnt[k]])

# Coverage test: use the smallest band file of each sector (C07 for Rad, ACM for others)
results = []
for sat in ("G18", "G19"):
    bucket = f"noaa-goes{sat[1:]}"
    for sector in ("RadC", "RadM1", "RadM2"):
        cand = sorted([r for r in rows if r["sat"] == sat and r["sector"] == sector and r["mode_chan"].endswith("C07")],
                      key=lambda r: r["scan_start_utc"])
        if not cand:
            results.append(dict(sat=sat, sector=sector, files=0))
            continue
        # CONUS/PACUS are fixed: sample 3; mesos can move: sample every 5th file (~5 min)
        step = max(1, len(cand) // 3) if sector == "RadC" else 5
        samples = cand[::step] + [cand[-1]]
        for r in samples:
            dest = os.path.join(TMP, os.path.basename(r["key"]))
            if not os.path.exists(dest):
                gc.download(bucket, r["key"], dest)
            with xr.open_dataset(dest, engine="netcdf4") as ds:
                cov = bool(gc.covers(ds, gc.FIRE_LAT, gc.FIRE_LON))
                ext = ds["geospatial_lat_lon_extent"].attrs
                results.append(dict(sat=sat, sector=sector, scan=r["scan_start_utc"], covers_fire=cov,
                                    centre_lat=float(ext.get("geospatial_lat_center", float("nan"))),
                                    centre_lon=float(ext.get("geospatial_lon_center", float("nan"))),
                                    north=float(ext["geospatial_northbound_latitude"]),
                                    south=float(ext["geospatial_southbound_latitude"]),
                                    west=float(ext["geospatial_westbound_longitude"]),
                                    east=float(ext["geospatial_eastbound_longitude"])))
            os.remove(dest)
            print(results[-1], flush=True)

with open(os.path.join(OUT, "goes_sector_coverage.json"), "w") as f:
    json.dump(results, f, indent=1)
