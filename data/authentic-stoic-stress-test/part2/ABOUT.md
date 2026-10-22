# The Authentic Stoic Stress Test, part 2: what does "about a kilometre" mean?

*Run Oct. 22, 2026. Prime Rogue Inc. The series is named for X user @AuthenticStoic, whose challenge started it.*

## Question

Part 1 showed that the wind direction (270–325°) does not move the most likely location of C Company. It held two inputs fixed:
- **the distance:** 0.6–1.5 km, our reading of Maj.-Gen. Rutland's "about a kilometre";
- **the reference:** what that distance is measured from, namely the outline of the satellite fire detections at 12:17 and 2:49 p.m.

Part 2 varies both.

## Method

The script is `scripts/authentic_stoic_alternative_hypothesis/part2_distance.py`, run on the 50 m scar grid from `data/location_analysis/`.

**References,** shown in yellow on the figure:

| Reference | What it is | Area |
|---|---|---|
| `edge_all` | Outline of the 12:17 Landsat and 2:49 VIIRS detections, clipped to the scar (part 1) | 1.94 km² |
| `edge_viirs` | Outline of the latest pass only (VIIRS 2:49), buffered 190 m (half a VIIRS pixel) | 2.96 km² |
| `edge_landsat` | The 12:17 Landsat line only, buffered 15 m | 0.47 km² |
| `main_body` | The part 1 outline shrunk by 300 m, i.e. measured from the fire's body rather than its fringe | 0.45 km² |

**Distance bands for "about a kilometre":** 0.5–1.0, 0.6–1.5 (part 1), 0.75–1.25, 1.0–2.0 and 0.4–2.0 km.

**Procedure.** For each of the 20 combinations, and each of the 12 winds, we found the burned ground in the band. The "core" is the ground in the band under all 12 winds.

## Results

Full results are in `part2_results.csv`; the figure is `part2_grid.png`.

**Core area and share in the Range 2 zone (H1), by reference and distance band:**

| Reference | 0.5–1.0 km | 0.6–1.5 km | 0.75–1.25 km | 1.0–2.0 km | 0.4–2.0 km |
|---|---|---|---|---|---|
| Fire's edge, both passes | 0.40 km², 96% | **0.43 km², 99%** | 0.19 km², 100% | 0.16 km², 86% | 0.80 km², 90% |
| Edge at 2:49 (VIIRS) | 0.32 km², 100% | 0.39 km², 99% | 0.17 km², 100% | 0.27 km², **56%** (44% H6) | 0.78 km², 85% |
| Edge at 12:17 (Landsat) | 0.14 km², **45%** (55% H4b) | 0.26 km², **59%** (41% H4b) | 0.02 km², 100% | 0.08 km², 100% | 0.62 km², **54%** (46% H4b) |
| Fire's main body | 0.26 km², 84% | 0.24 km², 98% | 0.12 km², 100% | 0.04 km², 100% | 0.41 km², 79% |

### 1. The Range 2 zone holds for most readings

In 16 of 20 combinations, at least 79% of the core is the Range 2 zone (H1). The exceptions are the two alternatives the ACH already named:

- **H4b, the strip north of Jamieson Lake.** It gains when the kilometre is measured from the older 12:17 Landsat line, up to 55%.
- **H6, the south-central run.** It gains when "about a kilometre" is read as 1–2 km from the 2:49 edge (44%).

No new area appears in any combination.

### 2. The exact patch does not hold

Within the Range 2 zone, the core shifts by up to about 690 m depending on the reading. Its overlap with the part 1 core falls as low as 0–20%. No cell is in the core for more than 13 of the 20 combinations. The 0.17 km² that is in the core for at least 8 of 20 is all in the Range 2 zone.

So part 1's 0.43 km² is the answer under part 1's assumptions, not a fixed location.

### 3. Which named point fits depends on the distance

| Point | Distance from the fire's edge | Fits when "about a kilometre" means… |
|---|---|---|
| Range 2 centroid | about 590 m | Bands that start at 0.6 km or below |
| Road's end | about 1.1 km | Bands of 0.75 km and up |

Range 2 is in the band for all 12 winds in 9 of the 20 combinations. The road's end is in it for all 12 in 8 of 20.

## Verdict

The **Range 2 zone** (about 1.9 km² along the north–south range road) survives every reasonable reading of "about a kilometre" except one: measuring from the fire's noon position. The **exact spot** within it does not survive, and part 1's 0.43 km² should not be presented as the location.

The ranking of the assessment is unchanged:
- **Range 2 zone (H1):** likely.
- **Strip north of Jamieson Lake (H4b):** credible alternative.
- **South-central run (H6):** unlikely.

Confidence is unchanged at low to moderate.

## Limits

- **Same scar grid and scar map as part 1.** The burn-severity threshold is tested in part 7.
- **References are outlines of active-fire pixels, not mapped fire perimeters.** Growth of the edge up to 3:16 p.m. is part 3.
- **Distance is measured straight downwind** of the reference for each wind. Terrain is not included (part 4).
