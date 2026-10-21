# NASA FIRMS fire history around the site, 2012–2026

Every FIRMS fire detection in a box around the Oct. 17 site (detections fall within about 52.67–52.88°N, 110.75–111.10°W, roughly 24 × 23 km, covering most of the central training area), pulled from the FIRMS area API in 5-day windows on Oct. 19–20, 2026.

| Path | Contents |
|---|---|
| `raw/SOURCE_YYYY-MM-DD_N.csv` | Unaltered API responses, one per window (`N` = days). A file with only a header row means no detections in that window. |
| `pull.log`, `pull2.log` | Logs of the two pull runs. The first run hit repeated "Invalid MAP_KEY" and "transaction limit" errors; the second retried them. **Every window was eventually retrieved: there are no gaps in any series.** The logs contain no key. |
| `all_detections_merged.csv` | All responses merged and de-duplicated, with distance from the Oct. 17 site (52.7767°N, 110.9210°W). |
| `summary_by_year.csv` | Detections, days with any detection, detections within 2 km of the site, and October detections, by year. |

**Coverage by sensor:** VIIRS Suomi-NPP standard processing Jan. 2012–June 2026; Landsat 8/9 near-real-time June 2022–Oct. 2026; VIIRS S-NPP, NOAA-20 and NOAA-21 near-real-time July–Oct. 2026; GOES near-real-time Oct. 12–18, 2026. MODIS and VIIRS NOAA-20 standard data were not pulled.

**What it shows**
- **Fire on this part of the range is routine:** detections on 5 to 19 days every year since 2012, and within 2 km of the Oct. 17 site in 14 of 15 years.
- **October fires are not unusual:** October detections in 12 of 15 years; October 2022 alone had 320 (seven days).
- The FIRMS GOES series includes a detection at 3:10 p.m. MDT on Oct. 17, 2026 (52.7917°N, 110.9058°W), matching NOAA's fire product in `data/goes/fire_timeline.csv`.

**Do not compare raw detection counts across years.** Landsat (30 m pixels, added mid-2022) produces many more points per fire than VIIRS (375 m), so counts jump after 2022 regardless of fire activity; "days with fire" is the fairer measure. Detections show heat, not cause: many will be prescribed burns or range fires from training.

Data: NASA FIRMS (LANCE), NASA open data. Merged tables and notes: Prime Rogue Inc., CC BY 4.0.
