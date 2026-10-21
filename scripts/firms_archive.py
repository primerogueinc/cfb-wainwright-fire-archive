#!/usr/bin/env python3
"""Archive NASA FIRMS active-fire detections over CFB Wainwright, Alberta.

Pulls every FIRMS source (VIIRS S-NPP / NOAA-20 / NOAA-21, MODIS, Landsat)
for a bounding box around the base, keeps every raw API response that
differs from what we already hold (raw files are never overwritten), and
rebuilds a merged, de-duplicated detections table plus a GeoJSON that
GitHub renders as a map.

Standard library only. The FIRMS MAP_KEY is read from the FIRMS_MAP_KEY
environment variable and is never written to disk or printed.

Usage:
    FIRMS_MAP_KEY=... python3 scripts/firms_archive.py
    FIRMS_MAP_KEY=... python3 scripts/firms_archive.py --start 2026-10-01 --end 2026-10-20
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

API = "https://firms.modaps.eosdis.nasa.gov/api"

# west,south,east,north. Generous box around CFB Wainwright / the Wainwright
# training area, the town, and the land the fire crossed into.
BBOX = "-111.6,52.4,-110.2,53.2"

# Default archive window starts well before the Oct 17, 2026 fire so the
# record shows what was (or wasn't) burning on the range beforehand.
DEFAULT_START = date(2026, 10, 1)

SOURCES = [
    "VIIRS_SNPP_NRT",
    "VIIRS_SNPP_SP",
    "VIIRS_NOAA20_NRT",
    "VIIRS_NOAA20_SP",
    "VIIRS_NOAA21_NRT",
    "MODIS_NRT",
    "MODIS_SP",
    "LANDSAT_NRT",
]

MAX_DAYS_PER_CALL = 5  # FIRMS area API limit
MDT = timezone(timedelta(hours=-6))  # Alberta in October (MDT, UTC-6)

ROOT = Path(__file__).resolve().parent.parent
FIRMS_DIR = ROOT / "data" / "firms"
RAW_DIR = FIRMS_DIR / "raw"
MANIFEST_DIR = ROOT / "data" / "manifests"


class FirmsError(RuntimeError):
    pass


def get(url: str, key: str, retries: int = 3) -> str:
    """GET a FIRMS URL. Errors are re-raised with the key scrubbed."""
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "prime-rogue-firms-archive/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError) as exc:  # network / HTTP errors
            last = str(exc).replace(key, "***")
            time.sleep(5 * (attempt + 1))
    raise FirmsError(f"request failed after {retries} attempts: {last}")


def availability(key: str) -> dict[str, tuple[date, date]]:
    text = get(f"{API}/data_availability/csv/{key}/ALL", key)
    if "data_id" not in text:
        raise FirmsError(f"unexpected data_availability response: {text.strip()[:200]}")
    out = {}
    for row in csv.DictReader(io.StringIO(text)):
        try:
            out[row["data_id"]] = (date.fromisoformat(row["min_date"]), date.fromisoformat(row["max_date"]))
        except (KeyError, ValueError):
            continue
    return out


def windows(start: date, end: date):
    d = start
    while d <= end:
        days = min(MAX_DAYS_PER_CALL, (end - d).days + 1)
        yield d, days
        d += timedelta(days=days)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def known_hashes(folder: Path, prefix: str) -> set[str]:
    """Hashes of raw files already held for one query window (e.g. '2026-10-16_5d')."""
    return {sha256(p.read_bytes()) for p in folder.glob(f"{prefix}__*.csv")} if folder.exists() else set()


def fetch_all(key: str, start: date, end: date, fetched_at: str) -> list[Path]:
    avail = availability(key)
    new_files: list[Path] = []
    for source in SOURCES:
        if source not in avail:
            print(f"[skip] {source}: not listed in data_availability")
            continue
        lo, hi = avail[source]
        s, e = max(start, lo), min(end, hi)
        if s > e:
            print(f"[skip] {source}: available {lo}..{hi}, outside {start}..{end}")
            continue
        folder = RAW_DIR / source
        for wstart, days in windows(s, e):
            prefix = f"{wstart.isoformat()}_{days}d"
            seen = known_hashes(folder, prefix)
            url = f"{API}/area/csv/{key}/{source}/{BBOX}/{days}/{wstart.isoformat()}"
            text = get(url, key)
            if not text.lstrip().startswith("latitude"):
                raise FirmsError(f"{source} {wstart}: unexpected response: {text.strip()[:200]}")
            body = text.encode("utf-8")
            rows = max(0, len(text.strip().splitlines()) - 1)
            digest = sha256(body)
            if digest in seen:
                print(f"[same] {source} {wstart} +{days}d ({rows} rows)")
                continue
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / f"{prefix}__fetched_{fetched_at}.csv"
            path.write_bytes(body)
            new_files.append(path)
            print(f"[new ] {source} {wstart} +{days}d ({rows} rows) -> {path.relative_to(ROOT)}")
            time.sleep(1)
    return new_files


def acq_utc(row: dict) -> datetime | None:
    try:
        hhmm = str(row.get("acq_time", "")).strip().zfill(4)
        return datetime.strptime(f"{row['acq_date']} {hhmm}", "%Y-%m-%d %H%M").replace(tzinfo=timezone.utc)
    except (KeyError, ValueError):
        return None


def rebuild_merged() -> int:
    """Merge every raw file into one de-duplicated table + GeoJSON."""
    merged: dict[tuple, dict] = {}
    for path in sorted(RAW_DIR.glob("*/*.csv")):
        source = path.parent.name
        with path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                when = acq_utc(row)
                if when is None:
                    continue
                key = (source, row.get("latitude"), row.get("longitude"), row.get("acq_date"), row.get("acq_time"))
                rec = merged.setdefault(key, {"source": source, "first_seen_file": str(path.relative_to(ROOT))})
                rec.update({k: v for k, v in row.items() if k})
                rec["acq_datetime_utc"] = when.isoformat().replace("+00:00", "Z")
                rec["acq_datetime_mdt"] = when.astimezone(MDT).strftime("%Y-%m-%d %H:%M MDT")

    rows = sorted(merged.values(), key=lambda r: (r["acq_datetime_utc"], r["source"], r.get("latitude", "")))
    lead = ["acq_datetime_utc", "acq_datetime_mdt", "source", "latitude", "longitude", "satellite", "instrument",
            "confidence", "frp", "daynight"]
    others = sorted({k for r in rows for k in r} - set(lead) - {"first_seen_file"})
    fields = lead + others + ["first_seen_file"]

    FIRMS_DIR.mkdir(parents=True, exist_ok=True)
    with (FIRMS_DIR / "detections.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    features = []
    for r in rows:
        try:
            lon, lat = float(r["longitude"]), float(r["latitude"])
        except (KeyError, ValueError):
            continue
        props = {k: r.get(k) for k in fields if k not in ("latitude", "longitude") and r.get(k) not in (None, "")}
        features.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]},
                         "properties": props})
    (FIRMS_DIR / "detections.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, indent=1) + "\n", encoding="utf-8")
    return len(rows)


def write_manifest(files: list[Path], fetched_at: str) -> Path | None:
    if not files:
        return None
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    path = MANIFEST_DIR / f"firms_{fetched_at}.sha256"
    lines = [f"{sha256(p.read_bytes())}  {p.relative_to(ROOT).as_posix()}" for p in sorted(files)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", type=date.fromisoformat, default=DEFAULT_START)
    ap.add_argument("--end", type=date.fromisoformat, default=None, help="default: today (UTC)")
    ap.add_argument("--merge-only", action="store_true", help="rebuild merged outputs from raw files, no download")
    args = ap.parse_args()

    if not args.merge_only:
        key = os.environ.get("FIRMS_MAP_KEY", "").strip()
        if not key:
            print("FIRMS_MAP_KEY is not set (add it as a repository secret).", file=sys.stderr)
            return 2
        end = args.end or datetime.now(timezone.utc).date()
        fetched_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        try:
            new = fetch_all(key, args.start, end, fetched_at)
        except FirmsError as exc:
            print(f"FIRMS error: {exc}", file=sys.stderr)
            return 1
        manifest = write_manifest(new, fetched_at)
        print(f"{len(new)} new raw file(s)" + (f"; manifest {manifest.relative_to(ROOT)}" if manifest else ""))

    total = rebuild_merged()
    print(f"merged detections: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
