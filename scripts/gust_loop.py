#!/usr/bin/env python3
"""Short GOES-18 visible loop, 2:30-4:30 p.m. MDT on Oct 17, 2026, marking the
CFB Wainwright weather station (CZWN), where an 82 km/h gust was recorded at
3:16 p.m., and the fire about 13 km to its east-southeast. For social video.

The satellite shows cloud, not wind. The gust is a station measurement.

Usage:
    python3 scripts/gust_loop.py      # writes data/goes/gust_loop/
"""

from __future__ import annotations

import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import goes_loops as g  # noqa: E402
import annotated_loop as al  # noqa: E402

SAT = 18
START = datetime(2026, 10, 17, 20, 30, tzinfo=timezone.utc)  # 2:30 p.m. MDT
END = datetime(2026, 10, 17, 22, 31, tzinfo=timezone.utc)    # 4:30 p.m. MDT
ZOOM = dict(west=-111.95, east=-110.35, south=52.52, north=53.06)
OUT = g.ROOT / "data" / "goes" / "gust_loop"
MDT = g.MDT
STN = (-111.0956, 52.8294)     # CZWN, from the SWOB files
FIRE = (-110.925, 52.775)      # Landsat 12:17 p.m. cluster
TOWN = (-110.857, 52.839)
LOGO = g.ROOT / "docs" / "prime-rogue-logo.png"

BG, PANEL, GOLD, CREAM, MUTED, BLUE, RED = "#22150E", "#2E1E15", "#D9B56C", "#F3EAD8", "#B9A88F", "#6E9BD6", "#E8735A"


def mdt(h, m):
    return datetime(2026, 10, 17, h, m, tzinfo=MDT).astimezone(timezone.utc)


CAPTIONS = [  # (from, to inclusive, text), MDT scan-start times
    (mdt(14, 30), mdt(14, 59), "The fire is burning on the range under thin high cloud. At the station, "
                               "winds are from the southwest, gusting to about 50 km/h."),
    (mdt(15, 0), mdt(15, 9), "The cold front's cloud line is approaching from the west."),
    (mdt(15, 10), mdt(15, 19), "3:16 p.m. — the weather station records its strongest gust of the day: "
                               "82 km/h from the west."),
    (mdt(15, 20), mdt(15, 29), "The front keeps moving east, toward the fire, about 13 km away."),
    (mdt(15, 30), mdt(15, 39), "3:30 p.m. — NOAA's fire product flags the fire at its strongest, about 1,215 MW."),
    (mdt(15, 40), mdt(15, 49), "Cloud spreads over the base. NOAA still flags the fire."),
    (mdt(15, 50), mdt(16, 9), "The station's 4 p.m. report: temperature down 10 °C in an hour, "
                              "wind now from the northwest."),
    (mdt(16, 10), mdt(16, 30), "Thick cloud hides the fire from the satellite from here on."),
]
HOLD = {mdt(15, 10): 4.0, mdt(15, 30): 3.5, mdt(15, 50): 3.0}


def caption_for(t):
    for a, b, text in CAPTIONS:
        if a <= t <= b.replace(second=59):
            return text
    return ""


def seconds_for(t):
    for k, s in HOLD.items():
        if abs((t - k).total_seconds()) < 120:
            return s
    return 1.6


def compose(t, vis, pts, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm
    for f in fm.findSystemFonts():
        if "Inter" in f:
            fm.fontManager.addfont(f)
    plt.rcParams["font.family"] = "Inter"

    fig = plt.figure(figsize=(12.8, 7.2), dpi=150, facecolor=BG)
    loc = t.astimezone(MDT)
    fig.text(0.03, 0.95, loc.strftime("%-I:%M p.m."), fontsize=40, weight="bold", color=CREAM, va="top")
    fig.text(0.03, 0.835, "Oct. 17, 2026 · MDT · GOES-18 visible", fontsize=12, color=MUTED, va="top")
    gust_now = t >= mdt(15, 10)
    fig.text(0.97, 0.95, "82 km/h" if gust_now else "", fontsize=34, weight="bold", color=GOLD, ha="right", va="top")
    fig.text(0.97, 0.835, "peak gust at the base weather station, 3:16 p.m." if gust_now else "",
             fontsize=12, color=CREAM, ha="right", va="top")
    if LOGO.exists():
        from PIL import Image
        la = fig.add_axes([0.445, 0.82, 0.11, 0.16])
        la.imshow(Image.open(LOGO).convert("RGBA"))
        la.axis("off")

    ax = fig.add_axes([0.03, 0.2, 0.94, 0.585])
    ax.set_facecolor(PANEL)
    if vis is not None:
        arr, (lons, lats) = vis
        ax.imshow(np.nan_to_num(arr), cmap="gray", vmin=0, vmax=1, aspect="auto",
                  extent=(lons[0], lons[-1], lats[-1], lats[0]), interpolation="antialiased")
    ax.set_xlim(ZOOM["west"], ZOOM["east"])
    ax.set_ylim(ZOOM["south"], ZOOM["north"])
    ax.set_aspect(1 / np.cos(np.radians(52.8)), adjustable="box", anchor="C")
    ax.set_xticks([]), ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#4A3528")
    box = dict(boxstyle="round,pad=0.25", fc=BG, alpha=0.8, lw=0)
    ax.plot(*STN, marker="^", ms=15, color=BLUE, mec=CREAM, mew=1.8, zorder=6)
    ax.annotate("Weather station (CZWN)", STN, xytext=(-14, 12), textcoords="offset points", ha="right",
                fontsize=12, color=CREAM, weight="bold", bbox=box, zorder=7)
    ax.plot(*FIRE, marker="x", ms=11, mew=2.4, color=RED, zorder=6)
    ax.annotate("Fire", FIRE, xytext=(12, -18), textcoords="offset points", fontsize=12, color=RED,
                weight="bold", bbox=box, zorder=7)
    ax.plot(*TOWN, marker="o", ms=5, color=CREAM, zorder=6)
    ax.annotate("Wainwright", TOWN, xytext=(7, 6), textcoords="offset points", fontsize=11, color=CREAM,
                bbox=box, zorder=7)
    ax.plot([STN[0], FIRE[0]], [STN[1], FIRE[1]], color=CREAM, lw=1, ls=(0, (4, 3)), zorder=5)
    if mdt(15, 10) <= t <= mdt(15, 29, ):
        ax.annotate("", xy=(STN[0] + 0.12, STN[1]), xytext=(STN[0] - 0.12, STN[1]), zorder=6,
                    arrowprops=dict(arrowstyle="-|>,head_width=0.5,head_length=0.9", color=GOLD, lw=4))
    if pts:
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=380, facecolors="none", edgecolors=RED,
                   linewidths=2, zorder=5)
        ax.text(0.99, 0.03, f"NOAA fire pixels: {len(pts)} · {sum(p[2] for p in pts):,.0f} MW",
                transform=ax.transAxes, ha="right", fontsize=12, color=RED, weight="bold", bbox=box)
    cap = caption_for(t)
    if cap:
        fig.text(0.03, 0.155, textwrap.fill(cap, 100), fontsize=15, color=CREAM, va="top",
                 bbox=dict(boxstyle="round,pad=0.5", fc=PANEL, ec="#4A3528"))
    fig.text(0.03, 0.035, "The satellite shows cloud, not wind. The 82 km/h was measured at the station, "
                          "about 13 km from the fire.", fontsize=10.5, color=GOLD)
    fig.text(0.03, 0.012, "Data: NOAA GOES-18 ABI band 2 (10-min scans, time = scan start), NOAA fire product; "
                          "ECCC SWOB observations (OGL – Canada). Red rings = NOAA fire pixels, accurate to a few km.",
             fontsize=8, color=MUTED)
    fig.text(0.97, 0.012, "Graphic: Prime Rogue Inc. · CC BY-NC 4.0", fontsize=8.5, color=MUTED, ha="right")
    fig.savefig(path, facecolor=BG)
    plt.close(fig)


def main() -> int:
    g.ROI = ZOOM
    al.ZOOM = ZOOM
    cmip = g.list_keys(SAT, "ABI-L2-CMIPF", START, END)
    c02 = [k for k in cmip if "M6C02_" in k or "C02_" in k]
    fdc = g.list_keys(SAT, "ABI-L2-FDCF", START, END)
    times = sorted({g.scan_start(k) for k in c02})
    work = OUT / "work"
    work.mkdir(parents=True, exist_ok=True)

    def near(keys, t):
        return next((k for k in keys if abs((g.scan_start(k) - t).total_seconds()) < 120), None)

    def job(t):
        try:
            k = near(c02, t)
            arr, x, y, p, H = g.read_window(SAT, k, "CMI", ZOOM)
            vis = g.to_latlon(g.norm(arr, 0, 1, 2.2), (x, y, p, H), 0.5)
            path = work / f"{t:%Y%m%dT%H%M}Z.png"
            compose(t, vis, al.fire_points(near(fdc, t)), path)
            print(f"{t.astimezone(MDT):%H:%M} MDT done", flush=True)
            return t, path
        except Exception as exc:
            print(f"{t:%H:%M} failed: {exc}", flush=True)
            return t, None

    with ThreadPoolExecutor(8) as ex:
        done = [r for r in ex.map(job, times) if r[1]]

    import imageio.v2 as imageio
    fps = 10
    frames = []
    for t, path in done:
        img = imageio.imread(path)[:, :, :3]
        frames += [img] * max(1, round(seconds_for(t) * fps))
    frames += [frames[-1]] * (3 * fps)
    imageio.mimsave(OUT / "cfb-wainwright-gust-loop.mp4", frames, fps=fps, codec="libx264", quality=8,
                    macro_block_size=2, ffmpeg_params=["-movflags", "+faststart"])
    print(f"{len(done)} frames -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
