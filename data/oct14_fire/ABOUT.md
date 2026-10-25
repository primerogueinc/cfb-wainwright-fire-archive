# The fires before Oct. 17: Sept. 20 and Oct. 14, 2026 (Permanent Danger Area 2)

Scripts: `scripts/oct14_fire/` (`layers.py`, `vectors.py`, `model.py`); graphic: `scripts/maps/g35_oct14_fire.py` → `data/graphics_published/oct25_oct14_fire/`.

## What burned

| Fire | Satellite detections (NASA FIRMS, MDT) | Burn scar | Where (OpenStreetMap, not official) |
|---|---|---|---|
| **Sept. 20** | 31 VIIRS detections from S-NPP, NOAA-20 and NOAA-21: **3:07, 3:26 and 4:11 a.m.** (night passes), then 12:56 to 2:55 p.m., peak 286 MW summed at 2:00 p.m. | About **5.4 km²**, already burned on the Sentinel-2 image of Oct. 4; south-east of the lakes, its south-west edge along a straight north-west to south-east line | Permanent Danger Area 2 |
| **Oct. 14** | One VIIRS detection, NOAA-21, **2:51 p.m.**, 11.7 MW (52.7549, −110.9389); NOAA's Hazard Mapping System kept it. No GOES-18 or GOES-19 detection (fire too small) | **1.06 km²** (0.91-1.13 across thresholds), burned between Sentinel-2 Oct. 4 and Landsat 9 Oct. 16, on the north-west edge of the Sept. 20 scar; the earlier 0.57 km² patch mapped on Oct. 19 is 98% inside it | Permanent Danger Area 2, at "Range 13"; 1.7-2.1 km south-east of Range 11 |

Other detections in the FIRMS box that month: Sept. 16, 1:34 p.m. (north-east of the base, outside the mapped danger areas); Sept. 18, 3:14 and 3:33 p.m. (Permanent Danger Area 2, about 5 km south-east of the Oct. 14 burn); Sept. 21, 1:42 to 3:23 p.m. (Permanent Danger Area 3A F1, about 9.5 km west of the Oct. 17 site). None between Sept. 22 and Oct. 13. The FIRMS history (`data/firms/history_2012-2026/`) shows fire in this part of the range most years; detections are heat, not cause.

Mapping (`layers.py`): NBR from Sentinel-2 B8A/B12 (Oct. 4, L2A surface reflectance) and Landsat 9 B5/B7 (Oct. 16, top-of-atmosphere reflectance; the scene is 99.99% cloud overall but clear over the fire). Each date thresholded on its own (Oct. 4 < −0.05, Oct. 16 < 0.06; sensitivity −0.08/0.05, −0.02/0.07); new burn = burned on Oct. 16, not within 30 m of ground burned on Oct. 4, connected to ground within 500 m of the Oct. 14 detection. `burns.geojson` holds both burns (the Sept. 20 polygon there is clipped to the 7.2 km layer window, 4.0 km²; 5.4 km² on the graphic's larger window).

## The Oct. 14 fire model (`model.py`)

FBP O-1a grass, 95% curing, corrected ISI; FFMC run hourly from the CWFIS daily 80.5 (Oct. 13) through the CZWN hourly weather; Huygens ellipse spread on the 30 m grid; water and the Sept. 20 burn do not burn. Ignition at every 150 m cell in and around the burn (170 cells), 6:00 a.m. to 2:30 p.m. every 30 minutes; rate factor K (1 = standard). A run counts only if the fire is burning inside the 375 m VIIRS pixel at 2:51 p.m. Three variants for when the fire stops: dusk (6:40 p.m.), humidity reaching 60% (9:30 p.m.), or free-burning to 10 a.m. Oct. 15.

**Weather on Oct. 14:** a north-west wind shift at about 1 p.m. (south-west 240° at noon to 340° at 1 p.m.), then 30-43 km/h from the north-west from 3 p.m. to midnight; humidity 36-46% through the afternoon. Standard head-fire spread rose from about 0.3 km/h in the morning to about 3 km/h from 4 p.m.

| Fire stops at | Area at the standard rate (10th-90th percentile of VIIRS-consistent runs) | Best fit (overlap with the burn) | Best-fit rate factor | Best-fit start |
|---|---|---|---|---|
| Dusk | 2.8-6.7 km² (median 3.8) | 0.48 | 0.3-0.5 | 6:00-8:30 a.m. (72% of weight) |
| Humidity 60% | 3.4-8.6 km² (median 5.0) | 0.41 | 0.3-0.5 | 63% by 8:30 a.m. |
| Next morning | 4.8-12.5 km² (median 8.8) | 0.40 | 0.17-0.5 | 52% by 8:30 a.m. |

Observed: 1.06 km². **At the standard rate, a fire burning at 2:51 p.m. should have grown 3 to 12 times larger than it did.** It fits when it spread at roughly a third to a sixth of the standard rate (the Oct. 17 fire ran at about a sixth before its wind shift) and started early in the morning; 6:00 a.m. was the earliest start tested, so earlier starts are possible. Best-fit start points lie 240-520 m south of the OSM "Range 13". Alternatives the model cannot exclude: the fire was put out or contained, or it burned against features too small to map. Overlap with the mapped burn never exceeds 0.48, so the shape fit is moderate.

## Limits

OSM range and danger-area outlines are not official. One VIIRS detection gives one time; NOAA-20 and S-NPP pass times on Oct. 14 are not recorded in FIRMS, so their non-detections cannot be used. The cross-sensor burn map has 30 m pixels; burns under about 1 ha are not mapped. No ground information; cause unknown.

Data: NASA FIRMS; Copernicus Sentinel-2 (contains modified Copernicus Sentinel data [2026]); USGS Landsat 9; ECCC; NRCan CWFIS; OpenStreetMap contributors (ODbL). Analysis: Prime Rogue Inc., CC BY-NC 4.0.
