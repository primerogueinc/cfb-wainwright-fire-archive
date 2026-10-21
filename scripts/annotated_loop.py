#!/usr/bin/env python3
"""Annotated GOES loop of the Oct 17, 2026 CFB Wainwright fire, for publication.

Side-by-side GOES-18 red visible (0.5 km) and Fire Temperature RGB (2 km),
zoomed on the base, with a large local-time clock, plain-language captions,
rings on pixels NOAA's fire algorithm flagged as fire, and the loop slowed
over the critical 2:30-4:20 p.m. window. Uses the same NOAA data and code
path as goes_loops.py.

Usage:
    python3 scripts/annotated_loop.py            # writes data/goes/annotated/
"""

from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import goes_loops as g  # noqa: E402

SAT = 18
START = datetime(2026, 10, 17, 17, 0, tzinfo=timezone.utc)   # 11:00 MDT
END = datetime(2026, 10, 18, 0, 31, tzinfo=timezone.utc)     # 18:30 MDT
ZOOM = dict(west=-112.05, east=-109.75, south=52.42, north=53.18)
OUT = g.ROOT / "data" / "goes" / "annotated"
MDT = g.MDT

FPS = 4
SLOW = (datetime(2026, 10, 17, 20, 30, tzinfo=timezone.utc), datetime(2026, 10, 17, 22, 21, tzinfo=timezone.utc))


def mdt(h, m):
    return datetime(2026, 10, 17, h, m, tzinfo=MDT).astimezone(timezone.utc)


# (from, to, caption) in UTC; first match wins. Plain language, sourced claims only.
CAPTIONS = [
    (mdt(12, 10), mdt(12, 29), "12:17 p.m. — Landsat 8 records 59 fire hotspots at the cluster (NASA FIRMS). "
                               "GOES can't see them through the thin high cloud."),
    (mdt(14, 40), mdt(14, 59), "2:49 p.m. — NASA's VIIRS satellite records more hotspots at the cluster. "
                               "Heat starts rising on GOES as the high cloud thins."),
    (mdt(15, 10), mdt(15, 19), "3:10 p.m. — NOAA's fire algorithm flags its first fire pixel at the cluster (76 MW)."),
    (mdt(15, 20), mdt(15, 29), "3:20 p.m. — Heat stays elevated over the cluster."),
    (mdt(15, 30), mdt(15, 39), "3:30 p.m. — PEAK: NOAA flags 3 fire pixels spread over ~4–5 km, ~1,200 MW total. "
                               "The cold front's cloud line is reaching the base."),
    (mdt(15, 40), mdt(15, 49), "3:40 p.m. — Fire still flagged (336 MW). Front's cloud arriving over the base."),
    (mdt(15, 50), mdt(15, 59), "3:50 p.m. — Thick cloud closes over the base. The satellites lose sight of the fire."),
    (mdt(16, 0), mdt(16, 9), "4:00 p.m. — DND's stated ignition time. The fire had been visible from space "
                             "for at least 50 minutes."),
    (mdt(16, 10), mdt(16, 29), "Winds shift with the front. Cloud hides the fire from GOES from here on."),
    (mdt(11, 0), mdt(12, 9), "Late morning: a sheet of thin high cloud over the base."),
    (mdt(12, 30), mdt(14, 39), "Early afternoon: the fire is burning on the range (per Landsat/VIIRS) under thin high cloud."),
    (mdt(16, 30), mdt(18, 30), "Evening: the front's cloud covers the area."),
]

KEY_HOLD = {mdt(15, 10): 3.0, mdt(15, 30): 4.0, mdt(15, 40): 3.0, mdt(16, 0): 4.0, mdt(12, 20): 2.0,
            mdt(14, 50): 2.0}


def caption_for(t):
    for a, b, text in CAPTIONS:
        if a <= t <= b + timedelta(minutes=0, seconds=59):
            return text
    return ""


def seconds_for(t):
    for k, sec in KEY_HOLD.items():
        if abs((t - k).total_seconds()) < 120:
            return sec
    if SLOW[0] <= t <= SLOW[1]:
        return 1.25
    return 0.25


def fire_points(fdc_key):
    """Lat/lon + power of NOAA FDC fire pixels within the zoom box."""
    if not fdc_key:
        return []
    mask, x, y, p, H = g.read_window(SAT, fdc_key, "Mask", ZOOM, pad=0)
    power, *_ = g.read_window(SAT, fdc_key, "Power", ZOOM, pad=0)
    pts = []
    for j, i in zip(*np.where(np.isin(mask, [10, 11, 12, 13, 14, 15, 30, 31, 32, 33, 34, 35]))):
        lon, lat = p(x[i] * H, y[j] * H, inverse=True)
        pts.append((lon, lat, float(power[j, i])))
    return pts


def compose(t, vis, fire, pts, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    W, H = 12.8, 7.2
    fig = plt.figure(figsize=(W, H), dpi=100, facecolor="#0e0e0e")
    loc = t.astimezone(MDT)
    # Big clock
    fig.text(0.02, 0.955, loc.strftime("%-I:%M %p").replace("AM", "a.m.").replace("PM", "p.m."),
             fontsize=44, weight="bold", color="white", va="top")
    fig.text(0.02, 0.83, "Friday, Oct. 17, 2026 · Mountain Daylight Time", fontsize=13, color="#bdbdbd", va="top")
    fig.text(0.98, 0.955, "CFB Wainwright fire\nseen from GOES-18", fontsize=15, color="white", ha="right",
             va="top", linespacing=1.3)
    # Detection badge
    if pts:
        total = sum(pw for *_, pw in pts)
        fig.text(0.98, 0.83, f"● NOAA FIRE DETECTED · {len(pts)} pixel{'s' if len(pts) > 1 else ''} · {total:,.0f} MW",
                 fontsize=13, weight="bold", color="#ff5a3c", ha="right", va="top")
    panels = [(vis, "Visible light (like a photo) · 0.5 km", "gray"),
              (fire, "Heat view · fire glows red · 2 km", None)]
    for n, (img, title, cmap) in enumerate(panels):
        ax = fig.add_axes([0.02 + n * 0.49, 0.2, 0.47, 0.58])
        if img is None:
            ax.set_facecolor("#1b1b1b")
            ax.text(0.5, 0.5, "No daylight image", color="#888", ha="center", va="center", transform=ax.transAxes)
            ax.set_xticks([]), ax.set_yticks([])
            ax.set_title(title, color="#dddddd", fontsize=12, loc="left")
            continue
        arr, (lons, lats) = img
        ax.imshow(np.nan_to_num(arr), cmap=cmap, vmin=0, vmax=1, aspect="auto", interpolation="antialiased",
                  extent=(lons[0], lons[-1], lats[-1], lats[0]))
        ax.set_xlim(ZOOM["west"], ZOOM["east"])
        ax.set_ylim(ZOOM["south"], ZOOM["north"])
        ax.set_aspect(1 / np.cos(np.radians(52.8)))
        ax.set_xticks([]), ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("#444")
        ax.set_title(title, color="#dddddd", fontsize=12, loc="left")
        for name, (lon, lat) in g.MARKERS.items():
            if not (ZOOM["west"] < lon < ZOOM["east"] and ZOOM["south"] < lat < ZOOM["north"]):
                continue
            star = name.startswith("Oct 17")
            if star:
                ax.plot(lon, lat, marker="x", ms=7, mew=1.6, color="#00e5ff")
                ax.annotate("Fire cluster\n(Landsat, 12:17 p.m.)", (lon, lat), xytext=(-40, -38),
                            textcoords="offset points", fontsize=10, color="#00e5ff", ha="right",
                            arrowprops=dict(arrowstyle="-", color="#00e5ff", lw=1),
                            bbox=dict(boxstyle="round,pad=0.2", fc="black", alpha=0.6, lw=0))
            else:
                ax.plot(lon, lat, marker=".", ms=7, color="white")
                ax.annotate(name, (lon, lat), xytext=(6, 5), textcoords="offset points", fontsize=10,
                            color="white", bbox=dict(boxstyle="round,pad=0.2", fc="black", alpha=0.55, lw=0))
        if pts:
            ax.scatter([p_[0] for p_ in pts], [p_[1] for p_ in pts], s=420, facecolors="none",
                       edgecolors="#ff5a3c", linewidths=2.2, zorder=5)
    # Caption
    cap = caption_for(t)
    if cap:
        import textwrap
        fig.text(0.02, 0.145, textwrap.fill(cap, 112), fontsize=14.5, color="white", va="top",
                 bbox=dict(boxstyle="round,pad=0.5", fc="#262626", ec="#3a3a3a"))
    fig.text(0.02, 0.012, "Data: NOAA GOES-18 ABI full-disk scans every 10 min (time = scan start); NOAA Fire Detection "
                          "product; NASA FIRMS. Red rings = NOAA fire pixels (located to within a few km).",
             fontsize=8.5, color="#9a9a9a")
    fig.text(0.98, 0.012, "Prime Rogue Inc. · CC BY 4.0", fontsize=9, color="#bdbdbd", ha="right")
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    g.ROI = ZOOM  # crop products to the zoom box
    cmip = g.list_keys(SAT, "ABI-L2-CMIPF", START, END)
    keys_by_band = {}
    for k in cmip:
        m = g.re.search(r"M\dC(\d\d)_", k)
        if m:
            keys_by_band.setdefault("C" + m.group(1), []).append(k)
    fdc = g.list_keys(SAT, "ABI-L2-FDCF", START, END)
    times = sorted({g.scan_start(k) for k in keys_by_band.get("C13", [])})
    work = OUT / "work"
    work.mkdir(parents=True, exist_ok=True)

    def near(keys, t):
        return next((k for k in keys if abs((g.scan_start(k) - t).total_seconds()) < 120), None)

    def job(t):
        try:
            fk = near(fdc, t)
            fr = g.build_frame(SAT, t, keys_by_band, fk, None)
            path = work / f"{t:%Y%m%dT%H%M}Z.png"
            compose(t, fr.get("red_visible"), fr.get("firetemp"), fire_points(fk), path)
            print(f"{t.astimezone(MDT):%H:%M} MDT done", flush=True)
            return t, path
        except Exception as exc:
            print(f"{t:%H:%M} failed: {exc}", flush=True)
            return t, None

    with ThreadPoolExecutor(12) as ex:
        done = [r for r in ex.map(job, times) if r[1]]

    import imageio.v2 as imageio
    frames, gif_frames, gif_dur = [], [], []
    for t, path in done:
        img = imageio.imread(path)[:, :, :3]
        reps = max(1, round(seconds_for(t) * FPS))
        frames += [img] * reps
        gif_frames.append(img[::2, ::2])
        gif_dur.append(seconds_for(t))
    gif_dur[-1] = 3.0
    frames += [frames[-1]] * (3 * FPS)
    imageio.mimsave(OUT / "oct17_goes18_annotated.mp4", frames, fps=FPS, codec="libx264", quality=8,
                    macro_block_size=2)
    from PIL import Image
    pil = [Image.fromarray(f) for f in gif_frames]
    pil[0].save(OUT / "oct17_goes18_annotated.gif", save_all=True, append_images=pil[1:],
                duration=[int(d * 1000) for d in gif_dur], loop=0, optimize=True)
    for key in (mdt(15, 10), mdt(15, 30), mdt(15, 40), mdt(16, 0)):
        for t, path in done:
            if abs((t - key).total_seconds()) < 120:
                (OUT / f"still_{t.astimezone(MDT):%H%M}MDT.png").write_bytes(path.read_bytes())
    print(f"{len(done)} frames -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
