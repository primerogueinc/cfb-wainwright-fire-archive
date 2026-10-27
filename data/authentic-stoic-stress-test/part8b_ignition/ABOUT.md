# Part 8b: when and where the fire started (working model v2.1)

Scripts: `scripts/authentic_stoic_alternative_hypothesis/part8/ignition_backcalc.py` (search), `ignition_sensitivity.py`, `progression.py`. Graphic: `data/graphics_published/cfb-wainwright-fire-progression-model.jpg` (`scripts/maps/g17_progression.py`).

## Method

- **Spread.** Grass fire, CFFDRS Fire Behaviour Prediction fuel type O-1a (curing 95%), elliptical (Huygens) spread on a 40-80 m grid, confined to the mapped burn scar (+100 m), water excluded.
- **Weather.** Hourly wind, temperature and humidity from the base station (CZWN climate hourly, converted to MDT, interpolated to 5-minute steps). Fine-fuel moisture by the hourly FFMC equations (Van Wagner 1977), started from the CWFIS daily FFMC (87.2) at 1 p.m. MDT Oct. 16 (`weather_hourly_model.csv`).
- **Calibration.** Head rate of spread is scaled so the model's average head advance between 12:17 and 2:49 p.m. equals the 0.43 km/h measured from the satellites in part 6 (factor 1.17).
- **Fit.** For each candidate start, the misfit is the average distance between the modelled fire edge and the 59 Landsat detections at 12:17 p.m. (both directions), plus half the same for the 8 VIIRS pixels at 2:49 p.m.
- **Candidates.** (a) single points: every scar cell within 3.5 km of Range 11 on a 240 m grid, starts every 30 min from 4 p.m. Oct. 16 to noon Oct. 17 (`ignition_grid_80m.csv`); (b) lines, as rounds landing along a line of fire from Range 11 at bearings 56-84° and distances 1.0-2.2 km (`line_ignition_80m.csv`).

## Findings

**Where.** The best-fitting starts cluster at the fire's southwestern tip, **1.9-2.5 km east of Range 11 (bearings 71-94°)**: the end of the C16's roughly 2 km reach, inside Permanent Danger Area 2, on the likely firing sector. The best single fit is 2.15 km out at 81°. A line of starts 1.4-2.2 km out along 80°, as from rounds landing along the line of fire, fits better than any single point (misfit about 150 m against 185-195 m). This is where the scar ends to the southwest, so the model is locating the scar's tip; that the tip sits at the C16's maximum reach on the likely line of fire is what supports a Range 11 start.

**When.** The start time depends on how fast the fire ran in the cool, humid morning (RH 44-53%, wind 13-18 km/h before 11 a.m.), which the afternoon calibration does not pin down. Multiplying the morning spread rate only (`sensitivity_best.csv`):

| Morning spread vs calibrated model | Best start (line of fire) | Window (within 20 m of best fit) |
|---|---|---|
| 0.75× | 2:15 a.m. | 10 p.m. Oct. 16 to 3:30 a.m. |
| 1× (calibrated) | 3:00 a.m. | 1:45 to 4:15 a.m. |
| 1.5× | 6:00 a.m. | 4:45 to 6:45 a.m. |
| 2× | 7:15 a.m. | 6:30 to 8:00 a.m. |
| 3× | 8:45 a.m. | 8:15 to 9:45 a.m. |

Every case puts the start **at least 2.5 hours before Landsat saw the fire at 12:17 p.m., 5.5 hours before the 2:14 p.m. wind warning, and 6.5 hours before DND's "approximately 4:00 p.m."** Sunrise was about 7:50 a.m. MDT: a start after sunrise needs the morning fire to have run at least about twice the calibrated rate, which is plausible (the hourly moisture model gives FFMC 89 at 1 p.m. against the official daily 91.8, so it likely underrates morning spread). Starts before sunrise would mean night firing, or a fire holding over from earlier activity. The model cannot tell these apart.

**Growth (central case, start 7:15 a.m.).** About 0.5 km² by 10 a.m., 1.1 km² at noon, 2.3 km² at 2:49 p.m., 2.7 km² at 3:16 p.m. (`progression.csv`; bracketing cases 2.4-2.9 km² at 3:16).

**Where the edge was at 3:16 p.m.** Modelled distance from the fire's edge to the Range 2 point: **425-466 m** across all four cases; to the road head: **905-934 m**. This is an independent check on part 6, which put Range 2 at 430-480 m by a different method, and it matches Maj.-Gen. Rutland's "the fire was a kilometre away when the wind shifted" if measured from the road head.

**Earlier fire.** A VIIRS detection at 2:51 p.m. on Oct. 14 lies 1.9 km southeast of Range 11 (bearing 139°), also within the C16's reach and outside the Oct. 17 scar.

## Limits

A model fitted to two satellite snapshots, not an observation of the start. Assumes one continuous grass fuel bed confined to the final scar, spreading as an ellipse; spotting, suppression, smouldering and fuel breaks are not modelled. Range 11's position (OpenStreetMap) and firing direction are not official. Morning spread rate is the main uncertainty and is shown as a range.

Fire detections: NASA FIRMS. Weather: Environment and Climate Change Canada. FWI: NRCan CWFIS. Contains modified Copernicus Sentinel data [2026].
