# Working model v4 (Oct. 25, 2026)

A full re-run of the fire model with a bug fix, new imagery (Sentinel-2 and Landsat 8, Oct. 24), a smoke model, a fit of the post-front fire to the final burn scar, and the facts DND confirmed at its Oct. 22 briefing (transcript: `data/reference/dnd_briefing_2026-10-22_transcript.txt`). Scripts: `scripts/authentic_stoic_alternative_hypothesis/model_v4/`. This is a working model, not a final finding.

## Version history

| | v2.1 (Oct. 22) | v3 (Oct. 24) | v4 (Oct. 25) |
|---|---|---|---|
| New evidence | VIIRS, GOES, Sentinel-2 scar | Landsat 8, 12:17 p.m. (fire shape) | Sentinel-2 and Landsat 8, Oct. 24; DND Oct. 22 briefing; Alexander et al. (2013) |
| Start (east of Range 11, 80° line) | 1.4-2.2 km | 1.4-2.2 km | 1.4-2.2 km |
| Start time | 3:30-7 a.m. | 3:30-7 a.m. | 4:00-6:30 a.m. (good fits 3:30-7:00) |
| Fire's edge to Range 2 point at 3:16 p.m. | 586 m | 566-591 m | 566-591 m |
| Arrival at Range 2 point / road head after the front reaches the fire (median) | 5.4 / 10.2 min* | 5.4 / 10.2 min | 5.2-5.4 / 10.0-10.2 min (weighted: 5.1-5.4 / 9.6-10.2) |
| Escape odds from the Range 2 area at the gust / +3 / +7 min (jog) | 80 / 43 / 10% | 80 / 40-43 / 10% | 80 / 40-43 / 10% unweighted; 74-75 / 42-47 / 8% weighted by fit to the scar |
| Post-front fire checked against the final scar | no | no | yes |
| Smoke | post-front, visibility only | same | before and after the front, at every point |

\* v2.1 as published said 6.4 / 13.2 min; measured consistently across all modelled fires it is 5.4 / 10.2 (correction issued with v3).

## What's new

### 1. Bug fix: the morning fire-danger index (affects parts 8b, 8c and v3)

`part8/ignition_backcalc.py` computed the Initial Spread Index (ISI) as 0.208 × f(W) × 19.115 × …, but 19.115 is already 0.208 × 91.9, so every hourly ISI was about 4.8 times too low. The other two ISI functions in the archive (`first_analysis/fwi.py`, `location_analysis/firemodels.py`) are correct, so the post-front spread rates (4.4-12 km/h) were not affected. v4 re-runs the morning fit with the fix (`fit_shape.py`, 16,240 fires; `fit_shape_all.csv.gz`).

- **Effect on the fire model: small.** Because the model's spread rate is calibrated to the measured 0.43 km/h between 12:17 and 2:49 p.m., the fix changes only the relative pace across the day (morning about 20% faster relative to the afternoon). Best fit unchanged in place, slightly better (misfit 107 m vs 113 m), start window narrowed.
- **Effect on the interpretation: large.** With the correct index, the standard Canadian grass-fire calculation (FBP O-1a, 95% curing) says the fire should have spread about **6 times faster** (2.5 km/h against 0.43 km/h; 5-7.5 times allowing for satellite pixel size) than the satellites measured between 12:17 and 2:49 p.m. (calibration factor 0.17 instead of 1.17). This assumes 95% curing and the station's weather. The bug had hidden it.

### 2. Four bracketing cases (`cases.json`, `progression.csv`, `arrival_prefront_*.tif`)

| Case | Morning spread | Shape (LB ×) | Start | Area at 12:17 / 2:49 / 3:16 (km²) | Nearest gas line at 12:17 / 3:16 | Edge to Range 2 point at 3:16 |
|---|---|---|---|---|---|---|
| v4a | 2× | 3.0 | 4:00 a.m. | 0.94 / 1.32 / 1.40 | 963 / 640 m | 805 m (591 m with observed outline) |
| v4b (best fit) | 2× | 3.0 | 5:00 a.m. | 0.83 / 1.15 / 1.23 | 1,000 / 680 m | 800 m (591 m) |
| v4c (widest) | 1.5× | 1.5 | 6:00 a.m. | 1.01 / 1.74 / 1.99 | 930 / 280 m | 566 m |
| v4d | 3× | 3.0 | 6:30 a.m. | 1.02 / 1.46 / 1.48 | 880 / 520 m | 712 m (591 m) |

The post-front runs start from each case's fire at 3:16 joined with the outline of the 12:17 and 2:49 p.m. detections, so the edge distance there is 566-591 m in every case.

### 3. Post-front fire fitted to the final scar (`fit_post/fit_post_all.csv`, `weighted_summary.*`)

In v3 the 30 post-front fires could only burn inside the mapped scar, so they could not be wrong about where the fire stopped. In v4 each fire may burn anything except open water and is stopped when its area equals the scar's; its overlap (Jaccard) with the scar weights it (weight = exp((J − best)/0.05)).

- **Fixed north-west winds fit the scar best:** overlap 0.51-0.55 for a fixed 315° wind, against 0.23-0.34 for the slow veer of the "authentic stoic" reading. No fire overlaps the scar better than 55%. With the weighting chosen (scale 0.05, a judgement call that sets how lopsided the shares look), fixed 315° carries 63% of the weight, 306° 23%, fast veer 10%, station veer 3%, slow veer under 1%. Spread rate is not distinguished (36 / 33 / 31% for 4.4 / 8 / 12 km/h).
- **Arrival and escape odds barely move** (table above).
- **No fire reproduces the unburned pocket at the road head** (all 120 burn it, and agreement with the observed edge near the two points is identical, 0.71, for every fire): something local stopped the fire there (the track, fuel, or people).

### 4. Edge check (`edge_check.py`, three images; `edge/edge_check.json`, `edge/edge_quadrants.json`)

Burned/unburned classified independently on Sentinel-2 Oct. 19 and Oct. 24 (dNBR, 20 m) and Landsat 8 Oct. 24 (NBR, 30 m); a fourth classifier (Sentinel-2 red-band darkening, 10 m) failed on hazy Oct. 19 and is not used.

- **Range 2 point:** inside the burn. 82-84% of the ground within 150 m burned (100% to the south-west and north-west, 64-76% to the north-east and south-east); only its own pad reads unburned.
- **Road head:** exactly on the scar's edge in all three images. 0% burned to the north-east, 100% to the south-west; an unburned or lightly burned pocket of 33-35 ha lies north-east of it.
- The earlier "Range 2 about 70 m from unburned ground" is replaced by this.

### 5. Smoke (`smoke.py`, `smoke_summary.py`, `smoke/`)

Gaussian plume from every modelled burning cell (0.35 kg/m² fuel, 8 g PM2.5/kg), ground-level release (Byram convection number < 1 for most hours), Briggs dispersion (class E before 8 a.m., C to the front, D after), hourly CZWN wind before the front and the five wind schedules after, wind direction varied ±20°. Visibility = 3 / (4.5 m²/g × PM2.5).

- **Before 3:16 p.m. the smoke went north-east, past them.** At the station's wind direction, visibility at the Range 2 point was clear until about 3:10 p.m., then about 2.7 km. With the wind 10-20° more westerly than measured, haze (roughly 2-10 km visibility) on and off from about 12:50 (+20°) or 2:00 p.m. (+10°). At most 6% of the likely ground was in smoke (visibility < 1 km) at any moment.
- **After 3:16 smoke and fire arrived almost together** (weighted medians):

| | Haze (< 1 km) | Dense smoke (< 100 m) | Fire |
|---|---|---|---|
| Range 2 point | 3:18 | 3:20 | 3:21 |
| Road head | 3:19 | 3:23 | 3:26 |
| Track 900 m south of road head | 3:20 | 3:26 | 3:30 |
| Track 2 km south of road head | 3:22 | 3:28 | 3:37 |

- **Modelled, not observed.** NOAA's Hazard Mapping System drew no plume (cloud); a Landsat 12:17 p.m. check (red light vs shortwave infrared, ground removed with the Oct. 24 scene) is inconclusive through the cloud (`smoke/smoke_check_landsat_1217.json`). Ground-hugging smoke is the worst case for visibility.

### 6. How fast should it have burned? (`danger/`, `moisture_wind.csv`, `h0_speed_check.json`)

Suppression classes from Alexander, Heathcott & Schwanke (2013), *Fire behaviour case study of two early winter grass fires in southern Alberta, 27 November 2011* (Partners in Protection / FireSmart Canada; reference note `data/reference/alexander_heathcott_schwanke_2013.md`): head fire < 1 km/h easy; 1-4.9 km/h challenging; ≥ 5 km/h beyond control. The report also uses the model's length-to-breadth relation for grass (L:B = 1.1 × WS^0.464, Table A1.1; originally from the FBP System and McArthur/Cheney), and shows the FBP system predicting a real Alberta grass fire closely (Lethbridge, 8.7 km/h predicted, 8.3 observed, in 64-69 km/h winds).

| | Routine hourly calculation (correct ISI) | Satellites / model |
|---|---|---|
| Morning (6 a.m.-1 p.m.) | about 1 km/h (easy/challenging) | — |
| 12:17-2:49 p.m. (mean) | 2.5 km/h (challenging) | 0.43 km/h (easy) |
| 2-3 p.m. | 3.5-4.4 km/h (challenging, near beyond control) | — |
| 4 p.m. (after the front) | 7 km/h (beyond control) | 4.4-12 km/h (challenging to beyond control) |

- **The slowness is real (H0 not supported).** Re-measured head advance 12:17-2:49: 0.33-0.52 km/h allowing for VIIRS pixel size (the head may have reached Peterson Pond / Range 3, so this is a lower bound). Independently, VIIRS fire radiative power at 2:49 (75 MW) implies the fire was burning 0.2-0.4 km² an hour; a fire at the standard rate would burn about 2.7 km² an hour. GOES-18 fire power went from 76 MW at 3:10 to 1,215 MW at 3:30 (about 16 times; GOES is indicative only: it reads 0 MW at 3:20 and 336 MW at 3:40). The fire-power figures assume a radiative fraction of 0.10-0.20 and 0.35 kg/m² of fuel consumed.
- **Wind alone explains about 3 times (2.8) of the post-front acceleration; the rest (about 4-10 times across the modelled 4.4-12 km/h, about 6.6 at 8 km/h) is the fire reaching its potential once the front arrived.**

### 7. What held the fire back? Hypotheses tested

| | Hypothesis | Test | Result |
|---|---|---|---|
| H0 | No real gap (measurement error) | Re-measure; fire energy | Not supported: the fire was genuinely slow |
| H1 | Active suppression before 3:16 | DND Oct. 22; straight edges in the scar (`fireguards.py`) | DND says direct suppression was not possible inside permanent danger area 2 ("restricted the firefighters ability to conduct direct suppressive operations... monitored"); indirect work at its boundary is not addressed. Eight straight edges (2.7 km, 8% of the 35.5 km perimeter); none lines up with a mapped road or track by our test (70% within 60 m), and none shows a bare strip before or after the fire. The clearest is the scar's east edge, running north-south for about 1 km, partly along a mapped road (64% within 60 m of the southern half), which comes closest to a guard signature |
| H2 | Patchy ground (craters, bare ground, old burns) | Pre-fire Sentinel-2 along the morning vs afternoon paths (`fuel_paths.json`) | Not supported at 10 m: morning path continuous grass, 0% bare, 0% old burn, 0% patchy 100 m blocks (unburned surroundings: 5% bare, 8% old burn, 20% patchy). Sub-10 m features (craters, short-grazed grass) not ruled out |
| H3 | Grass not fully cured | Same | Not supported: morning path slightly *less* green (NDVI 0.42) than the afternoon path (0.44) |
| H4 | Damper fuel / lighter wind at grass height | Sensitivity (`moisture_wind.csv`) | Partial: closing the gap needs, e.g., fuel 6 FFMC points damper with wind at 60% of the 10 m value, or 10-11 points damper at full wind; a stretch at 16-23% humidity |
| H6 | Confined by permanent danger area 2 (boundary roads/guards) | DND Oct. 23 ("initially remained within permanent danger area 2") | Consistent but untested: boundary not public |

**Reading:** we found no evidence that the fire was being held; DND says it was watched. The likeliest mix is lighter wind at grass height, somewhat damper fuel, and features too small for 10 m imagery (short or grazed grass, craters). Grazing in the training area is a question for DND.

### 8. DND's statements against the evidence

| DND, Oct. 18 and 22 | Our evidence | |
|---|---|---|
| Fire "initiated during routine military training activities" on the automatic grenade launcher range | Start 1.4-2.2 km east of Range 11, 4-6:30 a.m. | Consistent |
| "No indication that natural gas infrastructure was involved nor impacted"; no explosion "of any kind" | Part 9: fire about 0.9 km from the nearest gas line at 12:17, no line or well in the firing sector, no methane signal on Oct. 18 (Oct. 17 masked by cloud); a brief release as the fire crossed the lines around 3:25 p.m. cannot be excluded | Consistent |
| Fire "initially remained within permanent danger area 2", "monitored throughout the day by both range control and the base fire hall" | Slow, unsuppressed fire, no containment lines | Consistent |
| "A subsequent change in wind direction and velocity significantly increased the fire's intensity and rate of speed" | Front at CZWN 3:16 p.m., 82 km/h gust; GOES fire power ×16 by 3:30 | Consistent |
| It "crossed the base fireguard and burned beyond the training base" | Scar's straight east edge along the boundary road, with a lobe beyond it | Consistent |
| Fire about a kilometre away when the wind shifted (Oct. 18) **and** overtook the pairs range "just before 4:00" (Oct. 22; DND's Oct. 17 release said "approximately 4:00 p.m.") | See below (`overtaken_time.json`, `maps/`) | **Hard to reconcile on the model** |
| CFB Wainwright standing orders para. 342: units firing in high-risk months "should plan to conduct early morning shoots" (Rutland, Oct. 22: "a guideline") | Start window 4-6:30 a.m. | Suggestive only |

**"About a kilometre" and "just before 4:00".** On our timing the fire reaches ground about a kilometre from its 3:16 edge in the 3:20s to 3:30s, not just before 4:00. Weighted by fit to the scar, it reaches the Range 2 point at a median 3:21 p.m. (0% of fires in 3:45-4:00) and the road head (1.05-1.11 km from the 3:16 edge) at 3:26 (36% in 3:30-3:45, 4% in 3:45-4:00); 84% of the likely ground (part 2) burns by 3:30. Of the burned ground 600-1,400 m from the fire's edge at 3:16, about 6% is reached 3:45-4:00. Both statements fit together best for a thin strip south-east of the road head on the fire's flank, or a patch by the western lake, reached in 10-30% of fires (`maps/dnd_timing_test.png`, `maps_truthful.py`; branded: `data/graphics_published/oct25_model_v4/`).

Caveats: the model times the front from the CZWN station, about 15 km west of the fire. If the front reached the fire at about 3:25 rather than 3:16 (as allowed for in part 1), every post-front time moves about 9 minutes later (Range 2 about 3:30, road head about 3:35), still well before 4:00; GOES-18 shows the run in full force by 3:30. There are no ground observations. DND's "approximately 4:00 p.m." on Oct. 17 may be a reporting time. Likeliest readings: "just before 4:00" is approximate and the event was in the 3:20s-3:30s (our location is unchanged), or "about a kilometre" was approximate and the pairs range was further away.

## Severity check

See `../model_v3/severity_oct24/ABOUT.md`: the fire burned harder after the shift (median dNBR 0.47 vs 0.40-0.42 before); the Range 2-road head area burned typically for the afternoon run.

## Caveats

- Everything after 3:16 p.m. is modelled from weather, satellite timing and the final scar; no ground observations. The front's arrival at the fire is timed from a station about 15 km west (3:16 p.m.; possibly up to about 3:25 at the fire).
- The smoke model's convection number uses the part 8b hourly spread rates, which are calibrated to the fire's measured pace (and so describe the actual, slow fire rather than its potential).
- Smoke is modelled, not observed.
- DND has not confirmed where C Company was. "Range 2 area / road head" remains an inference (low to moderate confidence, part 2).
- 40 m model grid; 10-30 m imagery. Features smaller than that (tracks, craters, pads) are not resolved.
