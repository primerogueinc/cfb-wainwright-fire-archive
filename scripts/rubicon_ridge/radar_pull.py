"""Task 3a: ECCC MSC Datamart radar imagery archived for Oct. 17, 2026 (dd.weather.gc.ca/20261017/WXO-DD/radar).
Only GIF composites (CAPPI 1.5 km RAIN / 1.0 km SNOW, DPQPE) are kept on the Datamart; no volume scans.
Pulls the 6-minute CAPPI and DPQPE GIFs, 16:00-23:59 UTC, for the radars nearest Wainwright and the
Prairie (PNR) composite.

Usage: python3 -I radar_pull.py OUT_DIR
"""
import concurrent.futures as cf
import os
import re
import sys
import time

import requests

OUT = sys.argv[1]
BASE = "https://dd.weather.gc.ca/20261017/WXO-DD/radar"
RADARS = ["CASCV", "CASRA", "CASSU", "CASSM", "PNR"]
S = requests.Session()


def get(url):
    for i in range(3):
        try:
            return S.get(url, timeout=60)
        except requests.RequestException as e:
            err = e
            time.sleep(3 + 3 * i)
    raise err


jobs = []
for prod in ("CAPPI", "DPQPE"):
    for rad in RADARS:
        d = f"{BASE}/{prod}/GIF/{rad}/"
        r = get(d)
        if r.status_code != 200:
            print("no dir", d, r.status_code)
            continue
        for fn in sorted(set(re.findall(r'href="(\d{12}_[^"]+\.gif)"', r.text))):
            hh = int(fn[8:10])
            if 16 <= hh <= 23 and "A11Y" not in fn:
                jobs.append((d + fn, os.path.join(OUT, prod, rad, fn)))
print(len(jobs), "files", flush=True)


def dl(j):
    url, dest = j
    if os.path.exists(dest):
        return j, "cached"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        r = get(url)
    except Exception as e:
        return j, f"ERR {e}"
    if r.status_code != 200:
        return j, f"HTTP {r.status_code}"
    open(dest, "wb").write(r.content)
    return j, "ok"


bad = []
with cf.ThreadPoolExecutor(6) as ex:
    for j, st in ex.map(dl, jobs):
        if st not in ("ok", "cached"):
            bad.append(f"{j[0]}\t{st}")
open(os.path.join(OUT, "download_failures.txt"), "w").write("\n".join(bad) + "\n")
print("fails", len(bad))
