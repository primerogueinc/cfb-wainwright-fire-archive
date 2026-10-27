# Part 6: Where was the fire when the wind turned?

Parts 1-5 measured from the pre-shift hull (Landsat 12:17 + VIIRS 14:49) and assumed no growth from 14:49 to the front (3:16 or 3:25 p.m.). Script: `scripts/authentic_stoic_alternative_hypothesis/part6/edge_at_316.py`.

## Measured pace before the front
- Head advance from Landsat 12:17 to VIIRS 14:49 along 45-71° (the pre-front spread direction): about 1.0-1.2 km in 152 min, **0.39-0.47 km/h** (±190 m VIIRS half-pixel gives 0.31-0.54). `empirical_head_advance.csv`
- This average spans a calmer period. CZWN mean wind rose from about 15 km/h (1 p.m.) to 30-32 km/h at 2-3 p.m., gusts 46-51 km/h (RH 16-17%). Correction, Oct. 22: an earlier version gave 30-33 km/h and RH 16-22%, mixing in Lloydminster (CYLL) values, so the last half-hour may have run faster than the average.

## Fire power check
- VIIRS 14:49: 8 pixels, 74.6 MW total. GOES-18 FDC 15:10: 1 pixel, 76.5 MW. GOES-18 15:30 (after the front): 3 pixels, 1215 MW.
- Expected FRP (Byram intensity, 0.3 kg/m² grass, 18 MJ/kg, 15% radiative, 1-1.3 km front): 0.45 km/h → 100-130 MW; 1.5 → 340-440; 4 → 900-1170; 8 → 1800-2340. `frp_expected.csv`
- The 15:10 reading matches a slow fire. Caveats: 96-100% cloud flag in the box and no detection at 15:20, so cloud attenuation could hide a faster fire; the FRP model is order-of-magnitude.

## Growth model
Huygens expansion of the hull with an elliptical template (rear focus), 27 or 36 min, head 0.45 / 1.5 / 4 / 8 km/h, LB 3 or 5.4, wind 236/246/256°, clipped to scar + 150 m. Then re-ran the part 1 band (0.6-1.5 km, all 12 winds 270-325°). `edge_growth_scenarios.csv`, `edge_at_front.geojson` (LB 5.4, 246°).

| Head pace | Range 2 (A) distance to edge | Likely ground shifts | Range 2 zone share of core |
|---|---|---|---|
| none (parts 1-5) | 586 m | — | 1.00 |
| 0.45 km/h | 380-480 m | 120-230 m SE | 0.97-1.00 |
| 1.5 km/h | 0-250 m | 300-670 m SE | 0.55-0.98 |
| 4 km/h | burned before the front | 540-1170 m SE | 0-0.82 |

## Conclusion
At the measured pace, the edge came 100-200 m closer to Range 2 and the likely ground moves about 100-230 m south-east (along the post-front path, within part 2's ±400 m). Range 2 stays inside it. The finding breaks if the fire roughly tripled its pace in its last half-hour; the GOES fire power does not show that, but cloud weakens the test.
