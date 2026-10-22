#!/usr/bin/env python3
"""Render GOES-18/19 ABI loops of the Oct 17, 2026 CFB Wainwright fire.

Reads only the needed window of each NOAA GOES full-disk file directly from
NOAA's public archive on AWS (no download of whole files, no key needed) and
produces, per satellite:

  * a 0.5 km red-visible (band 2) loop — the sharpest view of the smoke plume
  * a true-colour loop (1 km)
  * a Fire Temperature RGB loop (2 km) — hot fire glows red/yellow
  * a Dust RGB loop (2 km) — dust shows magenta/pink, separating it from smoke
  * a fire-intensity timeline (3.9 µm brightness temperature and NOAA's
    Fire Detection and Characterization fire power over the base)

Wainwright lies just north of both CONUS sectors and no 1-minute mesoscale
sector was over Alberta, so full-disk (every 10 minutes) is the best GOES
cadence available for this event.

Usage:
    python3 scripts/goes_loops.py                       # Oct 17, 17:00 to Oct 18, 01:00 UTC
    python3 scripts/goes_loops.py --sats 18 --start 2026-10-17T21:00 --end 2026-10-17T23:00
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import fsspec
import h5netcdf
import numpy as np
from pyproj import Proj

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "goes"

# Region shown in the loops (lon/lat). Wide enough to follow the plume downwind.
ROI = dict(west=-113.6, east=-108.2, south=51.7, north=53.9)
# Box used for the fire-intensity timeline (the base and the burn area).
FIRE_BOX = dict(west=-111.15, east=-110.65, south=52.65, north=52.95)

MARKERS = {
    "Oct 17 fire cluster (Landsat 12:17 MDT)": (-110.925, 52.775),
    "Wainwright": (-110.857, 52.839),
    "Lloydminster": (-110.005, 53.278),
    "Vermilion": (-110.853, 53.354),
}
MDT = timezone(timedelta(hours=-6))
EVENTS_UTC = {  # reference lines on the timeline (UTC)
    "VIIRS hotspot Oct 14, 2:51 p.m.": datetime(2026, 10, 14, 20, 51, tzinfo=timezone.utc),
    "Landsat 8 hotspots 12:17": datetime(2026, 10, 17, 18, 17, tzinfo=timezone.utc),
    "VIIRS hotspots 14:49": datetime(2026, 10, 17, 20, 49, tzinfo=timezone.utc),
    "DND ignition time 16:00": datetime(2026, 10, 17, 22, 0, tzinfo=timezone.utc),
    "MD says fire held ~10:45 p.m.": datetime(2026, 10, 18, 4, 45, tzinfo=timezone.utc),
}
SERIES_COLOUR = {18: "#2a78d6", 19: "#eb6834"}  # validated categorical slots 1-2
SERIES_MARKER = {18: "o", 19: "s"}


# ---------------------------------------------------------------- archive

def list_keys(sat: int, product: str, t0: datetime, t1: datetime) -> list[str]:
    """All object keys for a product between t0 and t1 (by scan start)."""
    keys = []
    hour = t0.replace(minute=0, second=0, microsecond=0)
    while hour <= t1:
        prefix = f"{product}/{hour:%Y}/{hour.timetuple().tm_yday:03d}/{hour:%H}/"
        token = None
        while True:
            url = f"https://noaa-goes{sat}.s3.amazonaws.com/?list-type=2&prefix={prefix}"
            if token:
                url += "&continuation-token=" + urllib.request.quote(token, safe="")
            with urllib.request.urlopen(url, timeout=60) as r:
                root = ET.fromstring(r.read())
            ns = {"s": root.tag.split("}")[0].strip("{")}
            keys += [c.find("s:Key", ns).text for c in root.findall("s:Contents", ns)]
            nxt = root.find("s:NextContinuationToken", ns)
            if nxt is None:
                break
            token = nxt.text
        hour += timedelta(hours=1)
    out = []
    for k in keys:
        st = scan_start(k)
        if st and t0 <= st <= t1:
            out.append(k)
    return sorted(out)


def scan_start(key: str) -> datetime | None:
    m = re.search(r"_s(\d{4})(\d{3})(\d{2})(\d{2})(\d{2})", key)
    if not m:
        return None
    y, doy, H, M, S = map(int, m.groups())
    return datetime(y, 1, 1, H, M, S, tzinfo=timezone.utc) + timedelta(days=doy - 1)


_FS = None


def fs():
    global _FS
    if _FS is None:
        _FS = fsspec.filesystem("https", client_kwargs={"trust_env": True})
    return _FS


def read_window(sat: int, key: str, var: str, box: dict, pad: int = 2):
    """Read var within a lon/lat box from a GOES file. Returns (array, x, y, proj)."""
    url = f"https://noaa-goes{sat}.s3.amazonaws.com/{key}"
    with fs().open(url, block_size=2**20, cache_type="bytes") as f, h5netcdf.File(f, "r") as h:
        gp = h["goes_imager_projection"].attrs
        H = float(np.squeeze(gp["perspective_point_height"]))
        p = Proj(proj="geos", h=H, lon_0=float(np.squeeze(gp["longitude_of_projection_origin"])),
                 sweep="x", a=float(np.squeeze(gp["semi_major_axis"])), b=float(np.squeeze(gp["semi_minor_axis"])))

        def coord(name):
            v = h[name]
            return v[:] * float(np.squeeze(v.attrs["scale_factor"])) + float(np.squeeze(v.attrs["add_offset"]))

        x, y = coord("x"), coord("y")
        lons = [box["west"], box["east"], box["west"], box["east"]]
        lats = [box["south"], box["south"], box["north"], box["north"]]
        px, py = p(lons, lats)
        px, py = np.array(px) / H, np.array(py) / H
        dx, dy = x[1] - x[0], y[1] - y[0]  # dy < 0 (north at top)
        i0 = max(0, int(np.floor((px.min() - x[0]) / dx)) - pad)
        i1 = min(len(x), int(np.ceil((px.max() - x[0]) / dx)) + pad)
        j0 = max(0, int(np.floor((py.max() - y[0]) / dy)) - pad)
        j1 = min(len(y), int(np.ceil((py.min() - y[0]) / dy)) + pad)
        v = h[var]
        raw = v[j0:j1, i0:i1]
        fill = v.attrs.get("_FillValue")
        data = raw.astype("float32")
        if "scale_factor" in v.attrs:
            data = data * float(np.squeeze(v.attrs["scale_factor"])) + float(np.squeeze(v.attrs.get("add_offset", 0)))
        if fill is not None:
            data[raw == np.squeeze(fill)] = np.nan
        return data, x[i0:i1], y[j0:j1], p, H


# ---------------------------------------------------------------- imagery

def norm(a, lo, hi, gamma=1.0):
    out = np.clip((a - lo) / (hi - lo), 0, 1)
    return np.power(out, 1.0 / gamma)


def resize_to(a, shape):
    """Nearest/box resample a 2-D array to shape (integer factors)."""
    fy, fx = a.shape[0] / shape[0], a.shape[1] / shape[1]
    if fy >= 1 and fx >= 1 and float(fy).is_integer() and float(fx).is_integer():
        fy, fx = int(fy), int(fx)
        a = a[: shape[0] * fy, : shape[1] * fx]
        return np.nanmean(a.reshape(shape[0], fy, shape[1], fx), axis=(1, 3))
    yi = (np.arange(shape[0]) * a.shape[0] / shape[0]).astype(int)
    xi = (np.arange(shape[1]) * a.shape[1] / shape[1]).astype(int)
    return a[np.ix_(yi, xi)]


_GRID_CACHE: dict = {}


def to_latlon(img, geo, km):
    """Nearest-neighbour reproject a fixed-grid crop onto a north-up lat/lon grid
    (equal ground spacing, ~km per pixel) so shapes and distances look right."""
    x, y, p, H = geo
    ck = (km, len(x), len(y), float(x[0]), float(y[0]))
    if ck not in _GRID_CACHE:
        dlat = km / 111.2
        dlon = dlat / np.cos(np.radians((ROI["south"] + ROI["north"]) / 2))
        lats = np.arange(ROI["north"], ROI["south"], -dlat)
        lons = np.arange(ROI["west"], ROI["east"], dlon)
        LON, LAT = np.meshgrid(lons, lats)
        gx, gy = p(LON, LAT)
        ix = np.rint((np.asarray(gx) / H - x[0]) / (x[1] - x[0])).astype(int)
        iy = np.rint((np.asarray(gy) / H - y[0]) / (y[1] - y[0])).astype(int)
        ok = (ix >= 0) & (ix < len(x)) & (iy >= 0) & (iy < len(y))
        _GRID_CACHE[ck] = (np.clip(ix, 0, len(x) - 1), np.clip(iy, 0, len(y) - 1), ok, lons, lats)
    ix, iy, ok, lons, lats = _GRID_CACHE[ck]
    out = img[iy, ix].astype("float32")
    out[~ok] = 0
    return out, (lons, lats)


def band_key(keys_by_band: dict, band: str, t: datetime):
    for k in keys_by_band.get(band, []):
        if abs((scan_start(k) - t).total_seconds()) < 120:
            return k
    return None


def build_frame(sat, t, keys_by_band, fdc_key, acm_key=None, timeline_only=False):
    """Return dict of products (and stats) for one full-disk scan time."""
    def key(b):
        return band_key(keys_by_band, b, t)

    # --- fire-box statistics (cheap: small windows) ---
    k07, k13 = key("C07"), key("C13")
    if not (k07 and k13):
        return None
    fb, *_ = read_window(sat, k07, "CMI", FIRE_BOX, pad=0)
    c13, *_ = read_window(sat, k13, "CMI", FIRE_BOX, pad=0)
    stats = {"time": t.isoformat(), "sat": sat,
             "c07_max_k": float(np.nanmax(fb)) if np.isfinite(fb).any() else float("nan"),
             "c13_median_c": float(np.nanmedian(c13)) - 273.15,
             "fdc_fire_pixels": 0, "fdc_power_mw": 0.0, "cloud_pct": float("nan"),
             "fdc_key": fdc_key or "", "acm_key": acm_key or ""}
    if fdc_key:
        mask, *_ = read_window(sat, fdc_key, "Mask", FIRE_BOX, pad=0)
        power, *_ = read_window(sat, fdc_key, "Power", FIRE_BOX, pad=0)
        fires = np.isin(mask, [10, 11, 12, 13, 14, 15, 30, 31, 32, 33, 34, 35])
        stats["fdc_fire_pixels"] = int(fires.sum())
        stats["fdc_power_mw"] = float(np.nansum(np.where(fires, power, 0)))
    if acm_key:
        bcm, *_ = read_window(sat, acm_key, "BCM", FIRE_BOX, pad=0)
        if np.isfinite(bcm).any():
            stats["cloud_pct"] = float(np.nanmean(bcm) * 100)
    if timeline_only:
        stats["source_keys"] = ";".join([k07, k13])
        return {"stats": stats}

    # --- imagery ---
    got, geo = {}, {}

    def load(b):
        k = key(b)
        if k is None:
            raise KeyError(f"missing band {b}")
        arr, x, y, p, H = read_window(sat, k, "CMI", ROI)
        got[b], geo[b], got[b + "_key"] = arr, (x, y, p, H), k

    for b in ("C02", "C07", "C11", "C13", "C15"):
        load(b)
    day = float(np.nanmedian(got["C02"])) > 0.03
    if day:
        for b in ("C01", "C03", "C05", "C06"):
            load(b)
    shape2 = got["C13"].shape  # 2 km grid
    out = {"stats": stats}
    zeros2 = np.zeros(shape2, "float32")
    # Fire Temperature RGB (CIRA): R 3.9um 0-60C g0.4; G 2.2um 0-1; B 1.6um 0-0.75. At night G=B=0.
    fire = np.dstack([norm(got["C07"] - 273.15, 0, 60, 0.4),
                      norm(resize_to(got["C06"], shape2), 0, 1) if day else zeros2,
                      norm(resize_to(got["C05"], shape2), 0, 0.75) if day else zeros2])
    # Dust RGB (EUMETSAT/CIRA): R C15-C13 -6.7..2.6; G C13-C11 -0.5..20 g2.5; B C13 261.2..288.7K.
    dust = np.dstack([norm(got["C15"] - got["C13"], -6.7, 2.6),
                      norm(got["C13"] - got["C11"], -0.5, 20, 2.5),
                      norm(got["C13"], 261.2, 288.7)])
    out["firetemp"] = to_latlon(fire, geo["C13"], 2.0)
    out["dust"] = to_latlon(dust, geo["C13"], 2.0)
    if day:
        shape1 = got["C01"].shape  # 1 km grid
        R = resize_to(got["C02"], shape1)
        B, NIR = got["C01"], got["C03"]
        G = 0.45 * R + 0.1 * NIR + 0.45 * B  # synthetic green (CIMSS)
        tc = np.dstack([norm(R, 0, 1, 2.2), norm(G, 0, 1, 2.2), norm(B, 0, 1, 2.2)])
        out["truecolour"] = to_latlon(tc, geo["C01"], 1.0)
        out["red_visible"] = to_latlon(norm(got["C02"], 0, 1, 2.2), geo["C02"], 0.5)
    stats["source_keys"] = ";".join(sorted(v for k, v in got.items() if k.endswith("_key")))
    return out


TITLES = {
    "red_visible": "Red visible, 0.5 km (band 2)",
    "truecolour": "True colour, 1 km",
    "firetemp": "Fire Temperature RGB, 2 km",
    "dust": "Dust RGB, 2 km (dust = magenta/pink)",
}


def render(img, geo, sat, t, product, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    lons, lats = geo
    h, w = img.shape[:2]
    scale = 900 / max(w, h)
    fig = plt.figure(figsize=(w * scale / 100, h * scale / 100 + 0.55), dpi=100)
    ax = fig.add_axes([0, 0.55 / (h * scale / 100 + 0.55), 1, 1 - 0.55 / (h * scale / 100 + 0.55)])
    ax.imshow(np.nan_to_num(img), interpolation="antialiased", aspect="auto",
              cmap="gray" if img.ndim == 2 else None, vmin=0, vmax=1)
    ax.set_xlim(-0.5, w - 0.5)
    ax.set_ylim(h - 0.5, -0.5)
    ax.axis("off")
    for name, (lon, lat) in MARKERS.items():
        cx = (lon - lons[0]) / (lons[1] - lons[0])
        cy = (lat - lats[0]) / (lats[1] - lats[0])
        star = name.startswith("Oct 17")
        ax.plot(cx, cy, marker="+" if star else ".", ms=14 if star else 6, mew=2,
                color="#00e5ff" if star else "white")
        ax.annotate("fire cluster" if star else name, (cx, cy), xytext=(6, -10 if star else 4),
                    textcoords="offset points", fontsize=9, color="white",
                    bbox=dict(boxstyle="round,pad=0.15", fc="black", alpha=0.45, lw=0))
    loc = t.astimezone(MDT)
    fig.text(0.01, 0.012, f"GOES-{sat}  {TITLES[product]}\n"
                          f"Full-disk scan start {t:%Y-%m-%d %H:%M} UTC = {loc:%-I:%M %p} MDT",
             fontsize=9, color="black", va="bottom")
    fig.text(0.99, 0.012, "NOAA GOES-%d ABI\nPrime Rogue Inc. · CC BY-NC 4.0" % sat,
             fontsize=8, color="#555", ha="right", va="bottom")
    fig.savefig(path)
    plt.close(fig)


def write_video(frames: list[Path], mp4: Path, gif: Path):
    import imageio.v2 as imageio
    imgs = [imageio.imread(f) for f in frames]
    h = min(i.shape[0] for i in imgs) // 2 * 2
    w = min(i.shape[1] for i in imgs) // 2 * 2
    imgs = [i[:h, :w, :3] for i in imgs]
    imageio.mimsave(mp4, imgs, fps=4, codec="libx264", quality=8, macro_block_size=2)
    from PIL import Image
    small = [Image.fromarray(i[::2, ::2]) for i in imgs]
    small[0].save(gif, save_all=True, append_images=small[1:], duration=250, loop=0, optimize=True)


def timeline_chart(rows: list[dict], path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    t_lo, t_hi = min(r["time"] for r in rows), max(r["time"] for r in rows)
    events = {k: v for k, v in EVENTS_UTC.items() if t_lo <= v <= t_hi}
    hours = (t_hi - t_lo).total_seconds() / 3600
    fig, axes = plt.subplots(3, 1, figsize=(10 if hours <= 12 else 14, 8.6), sharex=True, dpi=110)
    panels = [("cloud_pct", "Cloud cover over the base, NOAA cloud mask (%)", lambda v: v),
              ("c07_max_k", "Hottest 3.9 µm pixel over the base (°C)", lambda v: v - 273.15),
              ("fdc_power_mw", "NOAA fire power over the base (MW)", lambda v: v)]
    for ax, (field, label, f) in zip(axes, panels):
        for sat in sorted({r["sat"] for r in rows}):
            rs = [r for r in rows if r["sat"] == sat]
            ax.plot([r["time"].astimezone(MDT) for r in rs], [f(r[field]) for r in rs],
                    color=SERIES_COLOUR[sat], marker=SERIES_MARKER[sat], ms=4, lw=2, label=f"GOES-{sat}")
        for name, t in events.items():
            ax.axvline(t.astimezone(MDT), color="#888", lw=1, ls="--")
        ax.set_title(label, loc="left", fontsize=11, color="#222")
        ax.grid(axis="y", color="#e5e5e5", lw=0.8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color("#bbb")
        ax.spines["bottom"].set_color("#bbb")
        ax.tick_params(colors="#555")
    for name, t in events.items():
        axes[0].annotate(name, (t.astimezone(MDT), 1.0), xycoords=("data", "axes fraction"), rotation=90,
                         ha="right", va="top", fontsize=8, color="#555", xytext=(-2, -2), textcoords="offset points")
    axes[0].legend(frameon=False, loc="upper left")
    if hours <= 12:
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%-I %p", tz=MDT))
        axes[-1].set_xlabel(f"{t_lo.astimezone(MDT):%b %-d, %Y} (MDT)", color="#555")
    else:
        axes[-1].xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18], tz=MDT))
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b %-d\n%-I %p", tz=MDT))
        axes[-1].set_xlabel("MDT", color="#555")
    fig.text(0.01, 0.005, "Source: NOAA GOES-18/19 ABI full disk (10-min). Box 52.65–52.95°N, 110.65–111.15°W. "
                          "Prime Rogue Inc. · CC BY-NC 4.0", fontsize=7.5, color="#666")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(path)
    plt.close(fig)


# ---------------------------------------------------------------- main

FRAME_RE = re.compile(r"^g(\d\d)_([a-z_]+)_(\d{8}T\d{4})Z$")


def render_range(sats, t0, t1, frames_dir: Path, workers: int, timeline_only: bool):
    """Render frames + stats for a time range into frames_dir."""
    frames_dir.mkdir(parents=True, exist_ok=True)
    stats_path = frames_dir / f"stats_{t0:%Y%m%dT%H%M}.jsonl"
    with stats_path.open("w") as sf:
        for sat in sats:
            print(f"GOES-{sat}: listing {t0:%Y-%m-%d %H:%M} to {t1:%Y-%m-%d %H:%M} UTC", flush=True)
            cmip = list_keys(sat, "ABI-L2-CMIPF", t0, t1)
            keys_by_band = {}
            for k in cmip:
                m = re.search(r"M\dC(\d\d)_", k)
                if m:
                    keys_by_band.setdefault("C" + m.group(1), []).append(k)
            fdc = list_keys(sat, "ABI-L2-FDCF", t0, t1)
            acm = list_keys(sat, "ABI-L2-ACMF", t0, t1)
            times = sorted({scan_start(k) for k in keys_by_band.get("C13", [])})
            print(f"GOES-{sat}: {len(times)} full-disk scans", flush=True)

            def near(keys, t):
                return next((k for k in keys if abs((scan_start(k) - t).total_seconds()) < 120), None)

            def job(t):
                try:
                    return t, build_frame(sat, t, keys_by_band, near(fdc, t), near(acm, t), timeline_only)
                except Exception as exc:  # keep going; the gap shows in the timeline
                    print(f"  G{sat} {t:%m-%d %H:%M} failed: {exc}", flush=True)
                    return t, None

            with ThreadPoolExecutor(workers) as ex:
                for t, fr in ex.map(job, times):
                    if fr is None:
                        continue
                    for prod in TITLES:
                        if prod in fr:
                            img, geo = fr[prod]
                            render(img, geo, sat, t, prod, frames_dir / f"g{sat}_{prod}_{t:%Y%m%dT%H%M}Z.png")
                    sf.write(json.dumps(fr["stats"]) + "\n")
                    sf.flush()
                    print(f"  G{sat} {t:%m-%d %H:%M} UTC done", flush=True)


def assemble(frames_dirs: list[Path], out_dir: Path, stills: set[str]):
    """Build loops, stills, timeline CSV/PNG from rendered frames + stats."""
    frames: dict[tuple[int, str], list[Path]] = {}
    rows = []
    for d in frames_dirs:
        for pth in d.rglob("*.png"):
            m = FRAME_RE.match(pth.stem)
            if m:
                frames.setdefault((int(m.group(1)), m.group(2)), []).append(pth)
        for sp in d.rglob("stats_*.jsonl"):
            for line in sp.read_text().splitlines():
                if line.strip():
                    r = json.loads(line)
                    r["time"] = datetime.fromisoformat(r["time"])
                    rows.append(r)
    out_dir.mkdir(parents=True, exist_ok=True)
    for (sat, prod), paths in sorted(frames.items()):
        paths.sort(key=lambda p: p.stem.split("_")[-1])
        sat_dir = out_dir / f"goes{sat}"
        (sat_dir / "stills").mkdir(parents=True, exist_ok=True)
        print(f"loop GOES-{sat} {prod}: {len(paths)} frames", flush=True)
        write_video(paths, sat_dir / f"{prod}_loop.mp4", sat_dir / f"{prod}_loop.gif")
        for pth in paths:
            stamp = pth.stem.split("_")[-1]  # YYYYmmddTHHMMZ
            if stamp[:-1] in stills or f"{stamp[9:11]}:{stamp[11:13]}" in stills:
                (sat_dir / "stills" / f"{prod}_{stamp}.png").write_bytes(pth.read_bytes())
    # de-duplicate (overlapping chunks) and sort
    uniq = {}
    for r in rows:
        uniq[(r["time"], r["sat"])] = r
    rows = sorted(uniq.values(), key=lambda r: (r["time"], r["sat"]))
    with (out_dir / "fire_timeline.csv").open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["scan_start_utc", "scan_start_mdt", "satellite", "cloud_pct", "c13_median_c", "c07_max_c",
                    "fdc_fire_pixels", "fdc_power_mw", "fdc_file", "cloud_mask_file", "band_files"])
        for r in rows:
            w.writerow([r["time"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                        r["time"].astimezone(MDT).strftime("%Y-%m-%d %H:%M MDT"), f"GOES-{r['sat']}",
                        "" if r["cloud_pct"] != r["cloud_pct"] else f"{r['cloud_pct']:.0f}",
                        f"{r['c13_median_c']:.1f}", f"{r['c07_max_k'] - 273.15:.1f}", r["fdc_fire_pixels"],
                        f"{r['fdc_power_mw']:.1f}", r.get("fdc_key", ""), r.get("acm_key", ""),
                        r.get("source_keys", "")])
    if rows:
        timeline_chart(rows, out_dir / "fire_timeline.png")
    print(f"assembled {len(rows)} scans into {out_dir}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sats", default="18,19")
    ap.add_argument("--start", default="2026-10-17T17:00")
    ap.add_argument("--end", default="2026-10-18T01:00")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--label", default="", help="output subfolder under data/goes/ (default: data/goes/)")
    ap.add_argument("--timeline-only", action="store_true", help="fire-box statistics only, no imagery")
    ap.add_argument("--frames-dir", type=Path, default=None, help="where to write frames (render step)")
    ap.add_argument("--no-assemble", action="store_true", help="render frames only (for parallel chunks)")
    ap.add_argument("--assemble-from", nargs="*", type=Path, help="assemble loops from these frame dirs only")
    ap.add_argument("--stills", default="18:20,20:50,21:10,21:30,21:40,21:50,22:00,22:10,22:20,22:40,23:30",
                    help="UTC HH:MM (any day) or YYYYmmddTHHMM frames to keep as standalone PNGs")
    args = ap.parse_args()
    out_dir = OUT / args.label if args.label else OUT
    stills = set(args.stills.split(","))

    if args.assemble_from:
        assemble(args.assemble_from, out_dir, stills)
        return 0
    t0 = datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc)
    t1 = datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc)
    frames_dir = args.frames_dir or (OUT / "work" / (args.label or "default"))
    render_range([int(s) for s in args.sats.split(",")], t0, t1, frames_dir, args.workers, args.timeline_only)
    if not args.no_assemble:
        assemble([frames_dir], out_dir, stills)
    return 0


if __name__ == "__main__":
    sys.exit(main())
