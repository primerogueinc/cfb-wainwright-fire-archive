# Part 8: the fire started on Range 11, the AGL range

**Question.** The base's standing orders identify Range 11 as the automatic grenade launcher (AGL) range, and DND's Oct. 22 briefing said the fire was reported on the AGL range. Does a start in Range 11's impact area change the model?

**What changed.** Parts 1-7 started the model from the outline of the fire seen by satellite at 12:17 p.m. (Landsat) and 2:49 p.m. (VIIRS), clipped to the burn scar: 1.94 km². Here the starting fire also includes all burned ground within the C16 launcher's reach (2.2 km) of Range 11 on an easterly firing sector (bearings 40-120°, into Permanent Danger Area 2), as if that ground was burning or had burned before the 3:16 p.m. front: +1.43 km², 2.98 km² in all. Range 11's position is the OpenStreetMap node (52.7678 N, 110.9577 W); its firing direction is not public.

Scripts: `scripts/authentic_stoic_alternative_hypothesis/part8/spread_range11.py` (part 1 model with the larger start) and `gen_grids_r11.py` (part 4 escape grids). Everything else is unchanged.

## Results

| | Parts 1-7 | Range 11 start |
|---|---|---|
| Fire's edge to Range 2 point at the front | 586 m | 586 m |
| Fire's edge to road head at the front | 1,105 m | 1,105 m |
| Fire arrival at Range 2 point, minutes after the front (median, range) | 6.4 (3.1-17.5) | 6.4 (3.1-17.5) |
| Fire arrival at road head (median, range) | 13.2 (5.9-32.8) | 13.2 (5.9-32.8) |
| Escape odds, Range 2 area, jog, leaving at the gust / +3 min / +7 min | 80% / 43% / 10% | 80% / 43% / 10% |
| Same, fast fires (8-12 km/h) | 70% / 15% / 0% | 70% / 15% / 0% |
| Escape odds, road head, jog, at the gust / +3 / +7 | 100% / 83% / 53% | 100% / 83% / 53% |
| Shape fit to the burn scar (Jaccard, median of 30 runs) | 0.46 | 0.48 |
| GOES-18 pixel pattern score (of 5, mean) | 2.87 | 3.00 |

**Range 2 and the road head: no change.** The extra starting fire lies west and southwest, upwind of the northwest wind after 3:16 and farther from Range 2 and the road head than the fire's existing southeastern edge. Every arrival time and escape figure for the two points is identical in all 30 fire scenarios.

**What does change.** Ground south and southwest of the starting fire burns earlier: the strip north of Jamieson Lake by a median 8 minutes (up to 35), the tracks to the south by 1-6 minutes, the west pond area immediately. The modelled burn also matches the mapped scar and the GOES-18 heat pattern slightly better.

**Conclusion.** A Range 11 start is consistent with the satellite data, fits slightly better, and leaves the findings about C Company unchanged. Where the fire started matters for how it began, not for what happened at Range 2 and the road head after 3:16, which depends on where its southeastern edge was when the wind turned.

Contains modified Copernicus Sentinel data [2026]. Fire detections: NASA FIRMS. Range positions: © OpenStreetMap contributors.
