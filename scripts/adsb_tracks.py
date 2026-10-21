#!/usr/bin/env python3
"""Pull every aircraft position recorded near CFB Wainwright on Oct. 17-18, 2026
from the adsb.lol open archive (ODbL 1.0), which publishes each day's readsb
"globe history" as GitHub release assets.

The archive is streamed (never written to disk whole). For any aircraft with at
least one position inside NEAR_BBOX during the window, the script keeps:

  data/adsb/oct17/raw_traces/<release>/<trace file>   original trace, unaltered
  data/adsb/oct17/points.csv                          every position, UTC and MDT
  data/adsb/oct17/aircraft.csv                        one row per aircraft
  data/adsb/oct17/low_slow_near_scar.csv              positions on the ground or
                                                      low and slow within 30 km
  data/adsb/oct17/tracks_map.png, tracks_zoom.png

ADS-B shows only aircraft that broadcast and were heard by a volunteer receiver.
Military helicopters often do not broadcast, and low-level flight far from
receivers is often missed. Absence of a track proves nothing.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import math
import os
import re
import subprocess
import sys
import tarfile
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "adsb" / "oct17"
REPO = "adsblol/globe_history_2026"
DAYS = ("2026.10.17", "2026.10.18")  # UTC days; Oct. 17 MDT afternoon/evening spans both
T0 = datetime(2026, 10, 17, 16, 0, tzinfo=timezone.utc)   # 10 a.m. MDT
T1 = datetime(2026, 10, 18, 14, 0, tzinfo=timezone.utc)   # 8 a.m. MDT Oct. 18
NEAR_BBOX = (52.25, 53.30, -111.95, -109.85)  # lat_s, lat_n, lon_w, lon_e (~60-70 km around the base)
SCAR = (52.775, -110.905)  # approximate centre of the Oct. 17 burn scar
MDT = timezone(timedelta(hours=-6))
LOG: list[str] = []


def log(*a):
    m = " ".join(str(x) for x in a)
    LOG.append(m)
    print(m, flush=True)


def api(url):
    h = {"Accept": "application/vnd.github+json", "User-Agent": "prime-rogue-archive"}
    if os.environ.get("GITHUB_TOKEN"):
        h["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=120) as r:
        return json.loads(r.read())


def releases_for(day):
    rels, page = [], 1
    while page < 20:
        batch = api(f"https://api.github.com/repos/{REPO}/releases?per_page=100&page={page}")
        if not batch:
            break
        rels += batch
        if any(day in r["tag_name"] for r in batch) and not any(day in r["tag_name"] for r in batch[-5:]):
            break
        page += 1
    hits = [r for r in rels if day in r["tag_name"]]
    if not hits:
        log("no release for", day, "- sample tags:", [r["tag_name"] for r in rels[:8]])
    prod = [r for r in hits if "prod" in r["tag_name"]] or hits
    return prod


def km(lat1, lon1, lat2, lon2):
    p = math.pi / 180
    a = 0.5 - math.cos((lat2 - lat1) * p) / 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * (1 - math.cos((lon2 - lon1) * p)) / 2
    return 12742 * math.asin(math.sqrt(a))


def parse_trace(raw: bytes):
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    pts, aircraft = [], {}
    s, n, w, e = NEAR_BBOX
    for day in DAYS:
        for rel in releases_for(day):
            tag = rel["tag_name"]
            assets = sorted((a for a in rel["assets"] if ".tar" in a["name"]), key=lambda a: a["name"])
            if not assets:
                log("no tar assets in", tag)
                continue
            log("release", tag, [a["name"] for a in assets], sum(a["size"] for a in assets) // 2**20, "MiB")
            urls = [a["browser_download_url"] for a in assets]
            proc = subprocess.Popen(["curl", "-sSfL", "--retry", "5", *urls], stdout=subprocess.PIPE)
            kept = scanned = 0
            try:
                with tarfile.open(fileobj=proc.stdout, mode="r|*") as tf:
                    for m in tf:
                        if not m.isfile() or "traces/" not in m.name:
                            continue
                        raw = tf.extractfile(m).read()
                        scanned += 1
                        try:
                            tr = parse_trace(raw)
                        except Exception:
                            continue
                        base = tr.get("timestamp", 0)
                        rows, near = [], False
                        for p in tr.get("trace", []):
                            t = datetime.fromtimestamp(base + p[0], tz=timezone.utc)
                            if not (T0 <= t <= T1):
                                continue
                            lat, lon = p[1], p[2]
                            inside = s <= lat <= n and w <= lon <= e
                            near |= inside
                            det = p[8] if len(p) > 8 and isinstance(p[8], dict) else {}
                            rows.append({
                                "icao": tr.get("icao"), "reg": tr.get("r", ""), "type": tr.get("t", ""),
                                "desc": tr.get("desc", ""), "callsign": (det.get("flight") or "").strip(),
                                "utc": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "mdt": t.astimezone(MDT).strftime("%Y-%m-%d %H:%M:%S"),
                                "lat": lat, "lon": lon, "alt_baro_ft": p[3], "gs_kt": p[4], "track": p[5],
                                "geom_alt_ft": p[10] if len(p) > 10 else "", "source": p[9] if len(p) > 9 else "",
                                "km_from_scar": round(km(lat, lon, *SCAR), 2), "release": tag,
                            })
                        if not near:
                            continue
                        kept += 1
                        d = OUT / "raw_traces" / tag
                        d.mkdir(parents=True, exist_ok=True)
                        (d / Path(m.name).name).write_bytes(raw)
                        pts += rows
                        ic = tr.get("icao")
                        a = aircraft.setdefault(ic, {"icao": ic, "reg": tr.get("r", ""), "type": tr.get("t", ""),
                                                     "desc": tr.get("desc", ""), "callsigns": set(), "min_km": 1e9})
                        a["callsigns"] |= {r["callsign"] for r in rows if r["callsign"]}
                        a["min_km"] = min(a["min_km"], min(r["km_from_scar"] for r in rows))
            finally:
                proc.stdout.close()
                proc.wait()
            log(tag, "trace files scanned:", scanned, "aircraft kept:", kept, "curl exit:", proc.returncode)

    pts.sort(key=lambda r: (r["icao"], r["utc"]))
    cols = ["icao", "reg", "type", "desc", "callsign", "utc", "mdt", "lat", "lon", "alt_baro_ft", "gs_kt", "track",
            "geom_alt_ft", "source", "km_from_scar", "release"]
    with (OUT / "points.csv").open("w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); wr.writeheader(); wr.writerows(pts)
    for a in aircraft.values():
        mine = [r for r in pts if r["icao"] == a["icao"]]
        near = [r for r in mine if r["km_from_scar"] <= 30]
        a.update(callsigns=" ".join(sorted(a["callsigns"])), min_km=round(a["min_km"], 2), points=len(mine),
                 first_mdt=mine[0]["mdt"] if mine else "", last_mdt=mine[-1]["mdt"] if mine else "",
                 first_within_30km_mdt=near[0]["mdt"] if near else "", last_within_30km_mdt=near[-1]["mdt"] if near else "")
    with (OUT / "aircraft.csv").open("w", newline="") as fh:
        f = ["icao", "reg", "type", "desc", "callsigns", "min_km", "points", "first_mdt", "last_mdt",
             "first_within_30km_mdt", "last_within_30km_mdt"]
        wr = csv.DictWriter(fh, fieldnames=f, lineterminator="\n"); wr.writeheader()
        wr.writerows(sorted(aircraft.values(), key=lambda a: a["min_km"]))

    def low_slow(r):
        alt, gs = r["alt_baro_ft"], r["gs_kt"]
        if alt == "ground":
            return True
        try:
            return (gs is not None and float(gs) < 40) or (alt is not None and float(alt) < 3200)
        except (TypeError, ValueError):
            return False
    ls = [r for r in pts if r["km_from_scar"] <= 30 and low_slow(r)]
    with (OUT / "low_slow_near_scar.csv").open("w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); wr.writeheader(); wr.writerows(ls)
    log("aircraft:", len(aircraft), "points:", len(pts), "low/slow within 30 km:", len(ls))

    try:
        plot(pts)
    except Exception as exc:
        log("plot failed:", exc)
    (OUT / "run.log").write_text("\n".join(LOG) + "\n")
    return 0


def plot(pts):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    try:
        import geopandas as gpd
        scar = gpd.read_file(ROOT / "data/infrastructure/scar_patches_revised.geojson").to_crs(4326)
    except Exception:
        scar = None
    by = {}
    for r in pts:
        by.setdefault(r["icao"], []).append(r)
    for name, ext, lab in (("tracks_map", (-111.95, -109.85, 52.25, 53.30), 30), ("tracks_zoom", (-111.05, -110.75, 52.70, 52.85), 6)):
        fig, ax = plt.subplots(figsize=(13, 11), dpi=110)
        if scar is not None:
            scar.plot(ax=ax, color="red", alpha=0.4)
        for ic, rows in by.items():
            near = [r for r in rows if r["km_from_scar"] <= lab]
            if not near:
                continue
            ax.plot([r["lon"] for r in rows], [r["lat"] for r in rows], lw=0.8)
            g = [r for r in rows if r["alt_baro_ft"] == "ground"]
            ax.scatter([r["lon"] for r in g], [r["lat"] for r in g], s=12, c="k", zorder=5)
            r0 = min(near, key=lambda r: r["km_from_scar"])
            ax.text(r0["lon"], r0["lat"], f'{r0["callsign"] or r0["reg"] or ic} {r0["mdt"][11:16]}', fontsize=7)
        ax.plot(SCAR[1], SCAR[0], "r*", ms=12)
        ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
        ax.set_aspect(1 / math.cos(math.radians(52.8)))
        ax.set_title("ADS-B tracks near CFB Wainwright, Oct. 17-18, 2026 (MDT). Black dots: on the ground.\n"
                     "Data: adsb.lol (ODbL). Aircraft that do not broadcast are not shown.", fontsize=10)
        fig.savefig(OUT / f"{name}.png", bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
