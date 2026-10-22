# NOAA Hazard Mapping System (HMS), Oct. 13–18, 2026

NOAA's Hazard Mapping System is a daily, analyst-reviewed product: fire points (from GOES, VIIRS and MODIS) and hand-drawn smoke plume outlines over North America.

| Path | Contents |
|---|---|
| `original/` | Files as downloaded from NOAA OSPO: daily fire point text files (`hms_fire2026MMDD.txt`) and smoke polygon shapefiles (`hms_smoke2026MMDD.zip`; `sm/` holds extracted copies for Oct. 14, 17 and 18). Unchanged. |
| `hms_fire_points_within_40km.csv` | Every HMS fire point within 40 km of the Oct. 17 detection site (52.7767°N, 110.9210°W), with UTC and MDT times and distance. |
| `hms_smoke_vs_site.json` | For each day: number of smoke polygons, whether any covers the site, and distance to the nearest one. |

**What it shows**
- **Fire points:** HMS kept one VIIRS point on Oct. 14 (2:49 p.m. MDT, ~2.8 km from the site), eight NOAA-20 VIIRS points on Oct. 17 (2:49 p.m. MDT), and two VIIRS points ~5 km southeast on Oct. 18 (2:10 and 2:30 p.m. MDT). These match `data/firms/detections.csv`. HMS lists no GOES points at the site on Oct. 17, although NOAA's automated GOES fire product flagged fire pixels at 3:10, 3:30 and 3:40 p.m. (`data/goes/fire_timeline.csv`); HMS analysts select which points to keep.
- **Smoke:** no HMS smoke outline covered or came near the site on any day from Oct. 13 to 18. The nearest on Oct. 17 was a light-density plume about 140 km south (2:00–5:30 p.m. MDT), unrelated to the base. The absence matters: NOAA analysts did not map a smoke plume from this fire, likely because cloud from the cold front hid it (see the GOES cloud data).

HMS times are UTC (HHMM); MDT = UTC − 6 h. Data: NOAA (public domain). Summaries: Prime Rogue Inc., CC BY-NC 4.0.
