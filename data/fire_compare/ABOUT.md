# Every satellite-detected fire, Aug. 27-Oct. 17, 2026, compared with Oct. 17

Scripts: `scripts/fire_compare/` (`model_fire.py`, `compare.py`, `yoy.py`), `scripts/fetch_history.sh`, `scripts/fetch_nbac.py`; graphics `scripts/maps/g36_fires_overview.py`, `g37_yoy.py`, `g38_long_term.py` → `data/graphics_published/oct25_oct14_fire/`. Table: `comparison.csv`; ranges: `ranges_vs_fires.csv`.

## The fires

| | Fire | Where (OpenStreetMap, not official) | Satellite detections (MDT) | Burn | Fire danger (CWFIS FWI) |
|---|---|---|---|---|---|
| A | Aug. 27-28; again Sept. 21 | PDA 3A F1, AFV Battle Run | 12, all at night: Aug. 27 2:16-3:20 a.m., Aug. 28 2:16-3:58 a.m.; Sept. 21 1:42-3:23 p.m. (7) | Scar mixed with 2020, 2022 and 2023 burns; no reliable size | 24, 20 (Very High); Sept. 21: 23 |
| B | Sept. 16 | Outside the mapped danger areas | 1 (1:34 p.m., 1.1 MW) | Too small to map | 4 (Low) |
| C | Sept. 18-20 | PDA 2, reaching Range 14 | 35 on 10 passes over 48 h: Sept. 18 3:14-3:33 p.m.; Sept. 20 3:07-4:11 a.m. (5, night) and 12:56-2:55 p.m. | 5.7 km² | 11, 19, 22 |
| D | Oct. 14 | PDA 2, Range 13 | 1 (2:51 p.m.) | 1.06 km² | 16 (High) |
| E | Oct. 17 | PDA 2, Range 2 | Landsat 12:17, VIIRS 2:49 p.m., GOES 3:10-3:40 | 10.8 km² | 30.8 (Extreme) |

No satellite detection on Sept. 19, so C may be one fire that burned about two days or two fires. Earlier 2026 detections in the box: Feb. 3, Apr. 20-22 (Apr. 22 at 3:34 a.m.), May 1, July 6.

## Against a free-burning fire

Same model for each (`model_fire.py`): FBP O-1a grass, 95% curing, corrected ISI, station weather (ECCC 301S001 hourly; FFMC from CWFIS), ignition swept within 600 m of the first detection over 12 h, runs kept only if burning in every detection pass's pixel. Grids are 7.8 km square, so large standard-rate areas are lower bounds.

| | At the standard rate | Observed | Rate factor that fits the detections |
|---|---|---|---|
| A | Fills the 61 km² grid | (mixed scar) | 0.17 only |
| C | At least 59 km² over two days | 5.7 km² | 0.3 only |
| D | At least 4 km² by dusk (13 km² by next morning) | 1.06 km² | 0.3 best (0.17-0.5) |
| E (v4) | about 2.5 km/h before the front | 0.43 km/h | 0.17 before 3:16 p.m. |

**Reading.** Every fire in the danger areas this fall behaved like Oct. 17 before its wind shift: far slower and smaller than the standard grass-fire calculation. That supports the explanation that this ground burns slower than the standard model (fine fuel, grazing, cratering, moisture at grass height) and it means range staff would have seen fires stay tame several times in the weeks before. It does not show whether any was suppressed: satellites cannot see firefighting. Fires A and C were burning at night (2-4 a.m.).

## 2025 and 2026 (`fire_days_2025_2026.csv`, graphic `cfb-wainwright-fires-2025-2026.jpg`)

Every day with a NASA satellite fire detection in the central training area, April-October 2025 and 2026 (2025: VIIRS S-NPP and Landsat; 2026 adds NOAA-20 and NOAA-21, so 2026 catches more small fires).

- **Spring:** detections Apr. 24-May 1, 2025 and Apr. 20-May 1, 2026. DND announced spring fuel-reduction ("prescribed") burns for Apr. 10-May 5, 2026 ([Lakeland Connect](https://lakelandconnect.net/2026/04/09/fuel-reduction-burns-underway-at-cfb-wainwright-through-early-may/), [Border Pulse](https://borderpulse.ca/dnd-warns-of-increased-smoke-near-cfb-wainwright/)) and for Apr. 2-May 2, 2024 ([Town of Wainwright](https://wainwright.ca/news/posts/garrison-wainwright-planning-prescribed-burns-in-range-training-area-april-2-may-2-2024/), [Global News](https://globalnews.ca/news/10448300/cfb-wainwright-prescribed-burn/)); "range control staff and firefighters" monitored the 2024 burn "around the clock". We found no 2025 notice in a short search.
- **September 2025:** an 11-day episode in PDA 3A F1/F2, Sept. 5-15, detected at night (about 3-5 a.m.) on six of those days; Sept. 25 in PDA 2. NBAC 2025 maps 5,089 ha in one DND polygon whose detections run Apr. 25-Sept. 11.
- **Fall 2026:** fires A-E above. We found no public notice of fall burns in either year.

The longer record (2012-2024) is outside this story; [backlink to the companion piece goes here].

## Public record

No news coverage or DND statement about the August or September fires was found (searches Oct. 25). Global News quoted a resident: "it is always on fire."

## Limits

Detections show heat, not cause. Satellites pass a few times a day; small or brief fires are missed. September scars come from one post-fire image (Oct. 4) and may include older burns. OSM ranges and danger areas are not official. No information on firefighting.

Data: NASA FIRMS; ECCC; NRCan CWFIS and NBAC; Copernicus Sentinel-2; USGS Landsat 9; OpenStreetMap contributors (ODbL). Analysis: Prime Rogue Inc., CC BY-NC 4.0.
