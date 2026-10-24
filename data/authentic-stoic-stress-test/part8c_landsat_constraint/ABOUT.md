# Part 8c: start of the fire, re-fitted to Landsat's 12:17 p.m. burned area (working model v2.2)

Script: `scripts/authentic_stoic_alternative_hypothesis/part8/ignition_landsat.py` (uses the part 8b model unchanged, on a 40 m grid). Input: `burned_1217_classes.tif`, the burned-and-burning area Landsat 8 recorded at 12:17 p.m. MDT, from [CFB-Wainwright-Landsat-8-9](https://github.com/primerogueinc/CFB-Wainwright-Landsat-8-9) (`analysis/2026-10-17/area.py`).

## What changed from v2.1

Part 8b fitted the start to Landsat's 59 fire detections (the flaming edge). The full Landsat bands also show the ground already burned inside that edge: a strip about 2.0-2.3 km long, 0.26-0.37 km wide, axis 55-58°, **0.26-0.84 km² (central 0.44 km²)** at 12:17 p.m. Its back (southwest) end is 1.2-1.5 km east of Range 11 at 78-82°. A start has to lie inside that area, so candidates here are model cells within 120 m of it (219 points, 80 m apart), plus lines of starts along bearings 60-100° from Range 11, each at morning spread rates 1×, 2× and 3× the calibrated model, start times every 30 minutes from 4 p.m. Oct. 16 to noon Oct. 17 (`fit_all.csv`, best per candidate in `fit_best.csv`).

Misfit = mean distance between the modelled and observed 12:17 outlines (central threshold, both directions) + half the 2:49 p.m. VIIRS misfit, as in part 8b. Overlap (intersection over union) is reported for the strict, central and loose outlines.

## Findings

**Where.** Best fit, again: **a line of starts 1.4-2.2 km out from Range 11 along 80°**, as from rounds landing along the line of fire (misfit 126 m; overlap 0.31 central, 0.54 loose). Best single points: **1.6-2.0 km out at 78-85°** (misfit 148-163 m). v2.1's best point was 2.15 km at 81°: the start moves up to ~0.5 km closer to Range 11 and stays inside the C16's reach and the inferred firing sector.

**When** (line at 80°, start within 20 m of best misfit):

| Morning spread vs calibrated | Best start | Window |
|---|---|---|
| 1× | 3:00 a.m. | 1:30-5:30 a.m. |
| 2× | **7:30 a.m.** | 6:30-9:00 a.m. |
| 3× | 9:30 a.m. | 8:30-10:30 a.m. |

Same picture as v2.1 (2× case 7:15 a.m.): the fire started hours before noon.

**Distance to gas.** Nearest operating gas line: **1.44 km** from the closest point of the best-fitting line of starts; 1.9-2.0 km from the best single points. The "about 1.4 km" used in the gas-test article is the minimum and stands.

**What the model gets wrong.** The modelled fire at 12:17 covers 1.0-1.3 km², against 0.44 km² observed (0.84 at the loosest): the model's fire is too wide. Landsat's strip is long and narrow (length to breadth 6-8), which the model's wind-based ellipse (about 3-4 at morning wind speeds) does not reproduce. Possible reasons: a narrower fuel bed or fuel breaks, a line of ignitions, or stronger, steadier wind at ground level than the station measured. This limits how far the timing can be trusted, not where the start is.

## Limits

Thin cloud over the base at 12:17 makes the burned outline threshold-dependent (range given). 40 m model grid; Range 11's position and firing direction are not official; morning spread rate is the main uncertainty.

Landsat data courtesy of the U.S. Geological Survey. Fire detections: NASA FIRMS. Weather: ECCC.
