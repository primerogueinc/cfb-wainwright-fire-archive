"""Task 3/4: ECCC MSC Datamart SWOB-ML hourly observations, Oct. 17, 2026 (UTC day) + Oct. 18 00-06 UTC,
for MSC stations and Alberta Agriculture (ACIS, ab_agriculture partner network) stations within
RADIUS_KM of the fire. Raw XML saved; a parsed long-format CSV and a wide key-variable CSV are written.

Usage: python3 -I swob_pull.py OUT_DIR   (OUT_DIR must already hold the two station-list CSVs)
"""
import concurrent.futures as cf
import csv
import datetime as dt
import math
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

import requests

OUT = sys.argv[1]
RADIUS_KM = 110
FIRE = (52.7645, -110.9052)
BASE = "https://dd.weather.gc.ca"
S = requests.Session()


def dist(lat, lon):
    a, b = map(math.radians, FIRE)
    c, d = math.radians(lat), math.radians(lon)
    return 6371 * math.acos(min(1, math.sin(a) * math.sin(c) + math.cos(a) * math.cos(c) * math.cos(d - b)))


def get(url, tries=3):
    for i in range(tries):
        try:
            r = S.get(url, timeout=60)
            return r
        except requests.RequestException as e:
            err = e
            time.sleep(2 + 2 * i)
    raise err


def listing(url):
    r = get(url)
    if r.status_code != 200:
        return []
    return re.findall(r'href="([^"?/][^"]*)"', r.text)


stations = []  # (network, id, dir_url_template, name, lat, lon, dist)
for r in csv.DictReader(open(os.path.join(OUT, "swob-xml_station_list.csv"))):
    try:
        dd = dist(float(r["Latitude"]), float(r["Longitude"]))
    except ValueError:
        continue
    if dd <= 160 and r["IATA_ID"] not in [s[1] for s in stations]:
        stations.append(("msc", r["IATA_ID"], "{day}/WXO-DD/observations/swob-ml/{day}/" + r["IATA_ID"] + "/",
                         r["Name"], float(r["Latitude"]), float(r["Longitude"]), round(dd, 1)))
for r in csv.reader(open(os.path.join(OUT, "swob-xml_partner_station_list.csv"))):
    if r[0].startswith("#") or r[3] != "AB":
        continue
    try:
        dd = dist(float(r[5]), float(r[6]))
    except ValueError:
        continue
    if dd <= RADIUS_KM and "Agriculture" in r[13]:
        stations.append(("ab_agriculture", r[0], "{day}/WXO-DD/observations/swob-ml/partners/ab_agriculture/{day}/" + r[0].lower() + "/",
                         r[2], float(r[5]), float(r[6]), round(dd, 1)))
    if dd <= 160 and "Forestry" in r[13]:
        stations.append(("ab-firewx", r[0], "{day}/WXO-DD/observations/swob-ml/partners/ab-firewx/{day}/" + r[0].lower() + "/",
                         r[2], float(r[5]), float(r[6]), round(dd, 1)))

with open(os.path.join(OUT, "stations_pulled.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["network", "id", "name", "lat", "lon", "dist_km_from_fire"])
    for s in stations:
        w.writerow([s[0], s[1], s[3], s[4], s[5], s[6]])
print(len(stations), "stations", flush=True)


def want(fn, day):
    m = re.match(r"(\d{4}-\d{2}-\d{2})-(\d{4})-", fn)
    if not m or not fn.endswith(".xml"):
        return False
    if day == "20261018":
        return int(m.group(2)) <= 600
    return True


jobs = []
for net, sid, tmpl, *_ in stations:
    for day in ("20261017", "20261018"):
        d = BASE + "/" + tmpl.format(day=day)
        for fn in listing(d):
            if want(fn, day):
                jobs.append((net, sid, d + fn, os.path.join(OUT, "xml", net, sid, fn)))
print(len(jobs), "files", flush=True)


def dl(job):
    net, sid, url, dest = job
    if os.path.exists(dest):
        return job, "cached"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    r = get(url)
    if r.status_code != 200:
        return job, f"HTTP {r.status_code}"
    with open(dest, "wb") as f:
        f.write(r.content)
    return job, "ok"


fails = []


def _safe(j):
    try:
        return dl(j)
    except Exception as e:
        return j, f"ERR {e}"


with cf.ThreadPoolExecutor(6) as ex:
    for job, st in ex.map(_safe, jobs):
        if st not in ("ok", "cached"):
            fails.append((job[2], st))
print("fails", len(fails), flush=True)
with open(os.path.join(OUT, "download_failures.txt"), "w") as f:
    for u, s in fails:
        f.write(f"{u}\t{s}\n")

# ---------- parse ----------
NS = {"om": "http://www.opengis.net/om/1.0", "": "http://dms.ec.gc.ca/schema/point-observation/2.0"}
long_rows = []
for net, sid, *_ in stations:
    d = os.path.join(OUT, "xml", net, sid)
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        try:
            root = ET.parse(os.path.join(d, fn)).getroot()
        except ET.ParseError:
            continue
        obs_time = None
        for el in root.iter():
            if el.tag.endswith("samplingTime"):
                for t in el.iter():
                    if t.tag.endswith("timePosition"):
                        obs_time = t.text
        for el in root.iter():
            if el.tag.endswith("}element") and "name" in el.attrib and el.attrib.get("value") not in (None, "MSNG"):
                q = ""
                for sub in el:
                    if sub.tag.endswith("qualifier") and sub.attrib.get("name") == "qa_summary":
                        q = sub.attrib.get("value", "")
                long_rows.append(dict(network=net, station=sid, file=fn, obs_time_utc=obs_time,
                                      element=el.attrib["name"], value=el.attrib["value"],
                                      uom=el.attrib.get("uom", ""), qa_summary=q))

with open(os.path.join(OUT, "swob_long.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(long_rows[0].keys()))
    w.writeheader()
    w.writerows(long_rows)
print("parsed", len(long_rows), flush=True)
