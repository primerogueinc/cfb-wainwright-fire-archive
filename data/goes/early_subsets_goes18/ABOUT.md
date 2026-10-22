# Early GOES-18 subsets and frames (first analysis, Oct. 18–19, 2026)

Prime Rogue's first GOES-18 analysis of the Oct. 17 fire, made before the full pipeline in `scripts/goes_loops.py`. Kept as produced, so the published early graphics can be traced to their inputs.

| File(s) | What it is |
|---|---|
| `goes18_C{01,02,03,07}_290HHMM.npz` | NumPy subsets of NOAA GOES-18 ABI L2 CMIP full-disk bands 1, 2, 3 and 7, ~60 km around the Oct. 17 detection site (52.7767°N, 110.9210°W), for scans 20:40–22:20 UTC (2:40–4:20 p.m. MDT). `290` is the day of year (Oct. 17); `HHMM` is the scan start in UTC. Arrays: `a` (values), `x`, `y` (fixed-grid metres), `cx`, `cy` (site pixel). |
| `sub.py` | Extracts a subset from NOAA's public S3 archive with HTTP range requests. Usage: `python3 sub.py noaa-goes18 07 290 21 30`. |
| `render.py` | Builds each frame: true colour (bands 1–3, synthetic green) with band-7 pixels more than 10 K above a 9×9 local median outlined in red. |
| `f_HHMM.jpg`, `sheet.jpg`, `cfb-wainwright-goes18-frames-oct17.jpg`, `cfb-wainwright-goes18-loop-oct17.gif` | The published frames, contact sheet and loop. Times in the labels are MDT. |

**Agreement with the later analysis.** This method flags heat at the site at 3:30, 3:40 and 3:50 p.m. NOAA's own fire product (`data/goes/fire_timeline.csv`) flags fire pixels at 3:10, 3:30 and 3:40 p.m. The two use different tests (a local-anomaly threshold here, NOAA's contextual fire algorithm there), so single-scan differences are expected; both show the fire burning hot before 4 p.m.

Data: NOAA GOES-18 (public domain). Code: MIT. Graphics and notes: Prime Rogue Inc., CC BY-NC 4.0.
