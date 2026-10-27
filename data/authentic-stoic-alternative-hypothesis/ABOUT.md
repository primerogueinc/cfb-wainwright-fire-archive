# Alternative hypothesis test: a westerly wind after 3:16 p.m.

*Run Oct. 22, 2026. Prime Rogue Inc. Credit to X user @AuthenticStoic for the challenge.*

## The challenge

On Oct. 22, @AuthenticStoic argued that our Oct. 21 analysis gets the fire's direction wrong. The CZWN peak gusts came from 269° (west) at 3:16 p.m. and 288° at 4:09 p.m. On that reading:

- the fire should have run east, not southeast, until after 4 p.m.;
- the burn should be stretched to the east;
- our fixed 306° wind is therefore suspect.

That's a fair test of an assumption, so we modelled it.

## What the weather records say

From the CZWN swob observations (`data/eccc/swob_observations.csv`):

| Obs (MDT) | 10-min mean dir | 2-min mean dir | Strongest 10-min gust from | Peak gust in hour |
|---|---|---|---|---|
| 3:00 p.m. | 236° | 236° | 236° | 50.8 km/h from 246° (2:48) |
| 4:00 p.m. | **307°** | **306°** | **305°** | 82.0 km/h from 269° (3:16) |
| 5:00 p.m. | 306° | 310° | 318° | 72.2 km/h from 288° (4:09) |

The peak-gust direction is a single instantaneous gust within the hour. The 10-minute mean is a separate field. By the 4 p.m. report, every averaged measure was 305–307°.

CZWN is about 15 km west of the fire. Its timings are approximate for the fire site.

## Method

The model is `scripts/authentic_stoic_alternative_hypothesis/spread.py`.

**Spread model.** Grass-fire spread on a 40 m grid, solved for time-dependent arrival (Dijkstra, 16 neighbours). Spread in each direction follows an elliptical spread rate:
- the fire sits at the ellipse's rear focus;
- length-to-breadth ratio LB = 1.1·U^0.464 = 6.6 at 48 km/h (FBP grass).

**Starting fire.** The same pre-shift fire as the Oct. 21 analysis: the outline of the Landsat 12:17 and VIIRS 14:49 detections, clipped to the scar. It is held fixed until the front arrives.

**Fuel.** Everything is burnable except open water (Sentinel-2 NDWI, Oct. 4). There are no roads, fire guards or suppression in the model.

**Front arrival at the fire.** Two cases: 3:16 (station time) or 3:25 (allowing about 9 minutes for the front to travel ~15 km east).

**Head spread rate.** 4.4, 8 or 12 km/h (`data/location_analysis/fire_models.csv`).

**Wind schedules.** Each is the direction the wind comes from:

| Schedule | Wind |
|---|---|
| S0 | Fixed 306° (Oct. 21 analysis) |
| S1 | **The challenge:** 269° → 288° at 4:09 → 306° at 4:20 |
| S2 | 269° → 305° by 3:50 (the station's own transition) |
| S3 | 269° → 305° by 3:30 (fast veer) |
| S4 | Fixed 315° (control; 5 p.m. strongest 10-min gust from 318°) |

That gives 5 schedules × 2 front times × 3 spread rates = 30 runs, each run both unconstrained and limited to the scar (+150 m).

## Results

### 1. Shape: the scar is not stretched east, so the challenge's wind does not fit

Each unconstrained run is stopped when its burned area equals the mapped scar. It is then compared with the scar (`shape_test.csv`, `summary.csv`, `wind_schedule_comparison.png`).

| Schedule | Overlap with scar (Jaccard) | East/south reach (scar = 1.17) |
|---|---|---|
| S4 fixed 315° | **0.54** | **1.11** |
| S0 fixed 306° | 0.47 | 1.25 |
| S3 fast veer | 0.41–0.47 | 1.30–1.80 |
| S2 station veer | 0.32–0.44 | 1.52–2.56 |
| **S1 challenge** | **0.22–0.34** | **2.33–4.34** |

The challenge's wind produces exactly the east-stretched burn its author predicted. The scar does not show one: it reaches about as far south as east.

Fit improves steadily as the wind is made more northwesterly, and the best fit is 315°. In other words, the scar says the fire spent most of its run under a northwest wind. The westerly phase after 3:16 was short.

### 2. Timing: the location and overrun window hold, and the challenge makes Range 2 earlier

Arrival times are from the scar-limited runs (`arrival_times.csv`). Ranges span 12 → 4.4 km/h.

| Point | Front at 3:16 (all schedules) | Front at 3:25 (all schedules) | Challenge (S1) only |
|---|---|---|---|
| Range 2 (OSM centroid) | 3:19–3:33 | 3:28–3:42 | 3:19–3:35 |
| Road dead end (CanVec) | 3:22–3:49 | 3:31–3:58 | 3:22–3:45 |
| Building (CanVec) | 3:24–3:56 | 3:33–4:05 | 3:24–3:53 |
| Range track at 52.765 | 3:24–4:18 | 3:33–4:21 | 3:56–4:21 |

The Range 2 area lies east-southeast of the starting fire. A westerly wind reaches it **sooner**, not later.

Only the southern track points are delayed under the challenge's wind. Across every schedule, the Range 2 area burns between roughly 3:20 and 3:45, which matches the published window of about 3:25–3:45.

The starting fire was already about 590 m from the Range 2 centroid before the front arrived.

### 3. GOES-18: weak evidence, with one correction to our own reading

The pixel north-east of the start ("E", 517 MW at 3:30) contains **no mapped scar at all** (`observed_reference.json`). Its heat is almost certainly spill-over from the intense fire next door, through the sensor's blur and pixel geolocation error. It is not evidence of an eastward run. We had read it that way in conversation on Oct. 22; that reading is withdrawn.

The southern pixel ("S", 420 MW at 3:30) does carry information. Fire reaches it by 3:30 only if:
- the front reached the fire close to 3:16, and
- spread was at least 8 km/h.

That holds in every schedule. GOES therefore constrains timing, not wind direction.

## Verdict

The challenge is right that the wind at the front was westerly and that our fixed 306° simplified the transition.

It is wrong that this sends the fire east until after 4 p.m. The burn scar's shape rules that out. The station's averaged winds were 305–307° by 4 p.m. Its proposed wind would also have brought the fire to the Range 2 area earlier, not later.

**The Oct. 21 location judgment and overrun window stand.** The next update will:
- describe the first minutes after the front as westerly;
- drop the GOES "east" pixel as evidence of direction;
- note that the scar fits a 306–315° run best.

## Limits

- **Simplified model.** Uniform grass with no roads, fire guards, suppression, terrain or fuel differences. Absolute extents are upper bounds; the comparisons are relative.
- **Shape metrics are coarse.** They use the 95th-percentile reach from the starting fire's centroid, and Jaccard overlap.
- **Wind at the fire is inferred** from a station about 15 km west. Speed is held at 48 km/h, and the first gust-driven minutes are not modelled separately.
- **GOES-18 pixels** are about 2 × 4 km here, with kilometre-scale geolocation error.

## Files

| File | Contents |
|---|---|
| `summary.csv` | One row per run: shape fit and GOES pattern score |
| `shape_test.csv` | Shape metrics |
| `goes_test.csv` | Active area per GOES pixel at 3:30 and 3:40 |
| `arrival_times.csv` | Arrival times at the candidate points |
| `observed_reference.json` | Observed scar shape and scar area per GOES pixel |
| `arrival_*_8kmh_front316.tif` | Arrival-time grids (minutes after 3:00 p.m. MDT, EPSG:3400) for the 8 km/h, 3:16-front case |
| `wind_schedule_comparison.png` | Four-panel figure |

Scripts are in `scripts/authentic_stoic_alternative_hypothesis/`. Reproduce with:

```
python3 spread.py <repo> && python3 figure.py <repo>
```
