# Working model v3 (Oct. 24, 2026)

A full re-run of the fire model with Landsat 8's 12:17 p.m. image of the fire built in. Scripts: `scripts/authentic_stoic_alternative_hypothesis/model_v3/` (`fit_shape.py`, `progression.py`, `post_front.py`). This is a working model, not a final finding.

## What's new

1. **Fire shape fitted to Landsat.** Landsat 8 recorded the fire at 12:17 p.m. as a strip about 2 km long and 0.3 km wide ([CFB-Wainwright-Landsat-8-9](https://github.com/primerogueinc/CFB-Wainwright-Landsat-8-9), `analysis/2026-10-17`). The model gained one parameter, a multiplier on the fire's length-to-breadth ratio (1-3), fitted with the start (lines and points from Range 11), start time and morning spread rate to Landsat's burned area at 12:17 and VIIRS at 2:49 p.m. (`fit_shape_all.csv.gz`, `fit_shape_best.csv`).
2. **Spread to the wind shift** for four bracketing cases (`progression.csv`, `arrival_prefront_*.tif`, hours since midnight Oct. 17).
3. **After the wind shift**: the part 1 model (5 wind schedules × 3 head spread rates × 2 shapes = 30 fires) from a new starting fire: the v3 fire at 3:16 p.m. joined with the outline of the 12:17 and 2:49 p.m. satellite detections (the fire cannot have been smaller than what was seen). Then the part 4 escape analysis on the 30 fires (`<case>/`).

## Findings

**Start.** Best fit: a line of starts **1.4-2.2 km east of Range 11 along 80°** (as from rounds landing along the line of fire), unchanged from v2.1/v2.2. Start time depends on the morning spread rate: **3:30 a.m. (1.5×) to 7:00 a.m. (3×)**.

**Shape.** Narrowing the fire improves the fit only slightly (misfit 126 m at the old shape, 113-118 m at 1.5-3× narrower) and the width is weakly constrained. The model's fire at 12:17 covers 0.9-1.1 km², closer to Landsat's loosest outline (0.84 km²) than its central one (0.44 km²); thin cloud probably hides some burned ground from Landsat.

**Cases**

| Case | Morning spread | Shape (LB ×) | Start | Area at 12:17 / 2:49 / 3:16 (km²) | Nearest gas line at 12:17 / 3:16 |
|---|---|---|---|---|---|
| v3a | 1.5× | 2.0 | 3:30 a.m. | 0.97 / 1.42 / 1.62 | 1,000 m / 440 m |
| v3b | 2× | 1.5 | 6:30 a.m. | 1.06 / 1.76 / 2.00 | 913 m / 240 m |
| v3c | 3× | 2.5 | 7:00 a.m. | 0.99 / 1.44 / 1.51 | 920 m / 440 m |
| v3d | 3× | 3.0 | 5:30 a.m. | 1.06 / 1.49 / 1.53 | 894 m / 480 m |

Landsat measured the nearest flames at 12:17 p.m. 0.86 km from a gas line; the model gives 0.89-1.0 km.

**Range 2 and the road head: no change from v2.1.**

| | v2.1 (published) | v3 (cases a, c, d) | v3b (widest fire) |
|---|---|---|---|
| Fire's edge to Range 2 point at 3:16 | 586 m | 591 m | 566 m |
| Fire's edge to road head at 3:16 | 1,105 m | 1,109 m | 1,047 m |
| Fire's edge to well 1-11 (registered site) | — | 967-984 m | 849 m |
| Fire arrival at Range 2 point, minutes after the front (median, range)* | 5.4 (3.1-17.5) | 5.4 (3.1-17.5) | 5.4 (2.8-15.9) |
| Fire arrival at road head* | 10.2 (5.9-32.8) | 10.2 (5.9-32.3 to 32.8) | 10.0 (5.4-29.7) |
| Escape odds, Range 2 area, jog: at the gust / +3 min / +7 min | 80% / 43% / 10% | 80% / 43% / 10% | 80% / 40% / 10% |
| Same, fast fires (8-12 km/h) | 70% / 15% / 0% | 70% / 15% / 0% | 70% / 10% / 0% |
| Escape odds, road head, jog | 100% / 83% / 53% | 100% / 83% / 53% | 100% / 80% / 50% |
| Same, fast fires | 100% / 75% / 30% | 100% / 75% / 30% | 100% / 70% / 25% |

*Measured identically for both versions: arrival in each of the 30 fires at the point (or the nearest burned ground within 150 m), median and range. The 6.4 and 13.2 minutes published in part 8 came from a different set of runs (the scar-limited runs, both front times); on this measure v2.1 also gives 5.4 and 10.2.

**Why so little changes.** In three of four cases, the fire's southeastern edge at 3:16 is set by where satellites saw fire at 2:49 p.m., not by the model: the narrower v3 fire stays northwest of it. Only the widest case (v3b) reaches past it, 25 m closer to Range 2 and 62 m closer to the road head. What happened to C Company depends on where that edge was when the wind turned, and v3 confirms it.

**Check run** (`check_v21_prefront/`): the same post-front model from part 8b's central pre-front fire (wider still, edge 425 m from the Range 2 point) gives Range 2 escape odds of 80% / 40% / 10% (fast fires 70% / 10% / 0%): the published figures hold across every starting fire tested.

## Limits

Landsat's 12:17 outline depends on a burn-ratio threshold under thin cloud. Fire shape is weakly constrained. The post-front model assumes continuous grass, no suppression, and the wind schedules of part 1. Range 11's position and firing direction are not official.

Landsat data courtesy of the U.S. Geological Survey. Fire detections: NASA FIRMS. Weather: ECCC. Contains modified Copernicus Sentinel data [2026].
