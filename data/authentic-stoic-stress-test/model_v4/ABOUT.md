# Working model v4 (Oct. 25, 2026)

A full re-run of the fire model with a bug fix, new imagery (Sentinel-2 and Landsat 8, Oct. 24), a smoke model, a fit of the post-front fire to the final burn scar, a 240-fire ensemble covering every variation used since part 1, an analysis of competing hypotheses, and the facts DND confirmed at its Oct. 22 briefing (transcript: `data/reference/dnd_briefing_2026-10-22_transcript.txt`). Scripts: `scripts/authentic_stoic_alternative_hypothesis/model_v4/`. This is a working model, not a final finding.

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
| Post-front fires | 30 | 120 (4 cases × 30) | 240 (4 cases × front at the fire 3:16 or 3:25 × 30) |
| Reproduced from scratch | — | — | twice, identical (`REPRODUCIBILITY.md`) |
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
| H0 | No real gap (measurement error) | Re-measure; fire energy; barrier ahead of the head (`pond_stall.json`) | Not supported: the fire was genuinely slow, and the head was not stalled (no water or bare ground ahead of it for 2.9 km; Peterson Pond lies 1.26-1.35 km to the north, beyond where the head got) |
| H1 | Active suppression before 3:16 | DND Oct. 22; straight edges in the scar (`fireguards.py`) | DND says direct suppression was not possible inside permanent danger area 2 ("restricted the firefighters ability to conduct direct suppressive operations... monitored"); indirect work at its boundary is not addressed. Eight straight edges (2.7 km, 8% of the 35.5 km perimeter); none lines up with a mapped road or track by our test (70% within 60 m), and none shows a bare strip before or after the fire. The clearest is the scar's east edge, running north-south for about 1 km, partly along a mapped road (64% within 60 m of the southern half), which comes closest to a guard signature |
| H2 | Patchy ground (craters, bare ground, old burns) | Pre-fire Sentinel-2 along the morning vs afternoon paths (`fuel_paths.json`) | Not supported at 10 m: morning path continuous grass, 0% bare, 0% old burn, 0% patchy 100 m blocks (unburned surroundings: 5% bare, 8% old burn, 20% patchy). Sub-10 m features (craters, short-grazed grass) not ruled out |
| H3 | Grass not fully cured | Same; curing needed (`curing_check.json`) | Not supported as the main cause: morning path slightly *less* green (NDVI 0.42) than the afternoon path (0.44); to explain the gap alone the grass would have had to be about 57% cured |
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

### 9. The full ensemble: every variation since part 1 (`ensemble_all.csv`, `ensemble_summary.json`)

4 pre-front cases (start 4:00-6:30 a.m., morning speed 1.5-3×, width 1.5-3×) × front reaching the fire at 3:16 (station time) or 3:25 (station about 15 km west) × 5 wind schedules (fixed 306°, fixed 315°, fast veer, station veer, slow "authentic stoic" veer) × head speed 4.4 / 8 / 12 km/h × steady or gusty shape = **240 post-front fires**, each with the escape analysis (part 4), the fit to the final scar, the timing tests and smoke. Scripts: `run_all.sh` runs everything.

| All 240 fires | Equal weight | Weighted by fit to the scar |
|---|---|---|
| Fire reaches Range 2 point after the front reaches the fire (median, 10th-90th percentile) | 5.4 min (3.4-10.2) | 5.3 min (3.1-10.0) |
| Fire reaches road head | 10.2 min (6.2-19.9) | 10.1 min (5.9-18.6) |
| Escape from the Range 2 area, jogging: at the gust / +3 / +7 min | 78 / 42 / 12% | 75 / 45 / 9% |
| Escape from the road head | 100 / 82 / 52% | 100 / 78 / 50% |

- **Front time barely matters for the odds** (at 3:16: 80 / 42 / 10%; at 3:25: 77 / 42 / 13%) but it moves the clock: with the front at the fire at 3:25, Range 2 burns at a median 3:30 p.m. and the road head 3:34 (`overtaken_time_f325.json`).
- **Fire speed matters most:** at 4.4 km/h everyone in the Range 2 area who leaves within 3 minutes of the gust gets out (35% at +7); at 8 km/h, 100 / 20 / 0%; at 12 km/h, 35 / 8 / 0%.
- **Wind schedule and shape matter less;** the start case hardly at all (78 / 40-43 / 12% in all four).
- **The weighting is not driving the result** (`weighting_sensitivity*.json`): from strict (scale 0.02) to loose (0.20) or equal weights, the Range 2 escape odds stay within 68-81% / 36-48% / 2-14%. With the front at 3:25 the scar again favours fixed north-west winds (315° 57%, 306° 21%, slow veer under 1%).
- **Smoke** (front at 3:25, `smoke_f325/`): haze reaches Range 2 at 3:27 and thick smoke at 3:30, with the fire at 3:30; road head 3:28 / 3:32 / 3:34. Same pattern as at 3:16, nine minutes later.
- **Location** (`location_update*.json`): of the part 2 likely ground, 54% is "about a kilometre" (600-1,400 m) from the fire's edge when the front reaches it; ground that at least 15% of fires reach 3:45-4:00 is 2% (front 3:16) to 10% (3:25) of it; ground meeting both is 0% to 3%.

### 10. Further checks

- **National system's station data** (CWFIS, CFB Wainwright Airfield 21, Oct. 17, noon): FFMC 91.8, ISI 11.6, FWI 30.8, Alberta class **Extreme**. Its ISI is on the corrected scale (our corrected 1 p.m. value 7.9 with the model's lower hourly FFMC; the uncorrected part 8b table gave 1.6), an independent confirmation of the bug fix. The standard grass spread from the station's noon ISI alone is about 1.9 km/h (`curing_check.json`).
- **Head stall** (`pond_stall.json`): see H0 above.
- **Curing** (`curing_check.json`): see H3 above.

### 11. Competing hypotheses (`ach.py`, `ach/`)

Analysis of competing hypotheses after Heuer (1999, *Psychology of Intelligence Analysis*, ch. 8): every item of evidence rated against every hypothesis (CC/C strongly consistent/consistent, N neutral, I/II inconsistent/strongly inconsistent), each item weighted by credibility (high 1.0, medium 0.7, low 0.4), and hypotheses ranked by the weight of evidence **against** them. Ratings are our judgements; each cites its source in `ach/ach_*.csv`. Graphic: `data/graphics_published/oct25_model_v4/cfb-wainwright-competing-hypotheses.jpg`.

#### Why did the fire spread at about a sixth of the standard rate between 12:17 and 2:49 p.m.?

| Evidence | Credibility | H0 | H1 | H1b | H2 | H2b | H3 | H4 |
|---|---|---|---|---|---|---|---|---|
| Head advance re-measured 0.33-0.52 km/h allowing for VIIRS pixel size | high | I | C | C | C | C | C | C |
| Fire energy (VIIRS FRP 75 MW) implies 0.2-0.4 km2/h burned vs 2.7 km2/h at the standard rate | medium | II | C | C | C | C | C | C |
| No water or bare ground ahead of the head for 2.9 km (head not stalled at Peterson Pond) | high | I | N | N | I | N | N | N |
| DND, Oct. 22: PDA 2 'restricted the firefighters ability to conduct direct suppressive operations'; monitored all day | medium | N | II | N | N | N | N | N |
| DND, Oct. 22: the fire 'initially remained within permanent danger area 2' | medium | N | N | C | N | C | N | N |
| No unmapped straight edge with a guard signature (bare strip) before or after the fire at 10-20 m | medium | N | I | I | N | N | N | N |
| Morning path: 0% bare, 0% old burn, 0% patchy 100 m blocks (surroundings 5 / 8 / 20%) | high | N | N | N | II | N | N | N |
| Morning path not greener than afternoon path (NDVI 0.42 vs 0.44) | high | N | N | N | N | N | I | N |
| Curing alone would have to be about 57% to close the gap; mid-October prairie grass is normally 90-100% | medium | N | N | N | N | N | II | N |
| CWFIS station Oct. 17: FFMC 91.8, FWI 30.8 (Extreme); afternoon humidity 16-23% | high | N | N | N | N | N | N | I |
| Closing the gap by moisture/wind alone needs e.g. FFMC -6 with wind at 60%, or FFMC -10 at full wind | medium | N | N | N | N | N | N | I |
| After the front the same kind of grass burned at or near the standard rate (4.4-12 km/h; GOES power x16) | medium | C | C | C | N | C | I | C |
| Lower burn severity where it burned before the shift (median dNBR 0.40-0.42 vs 0.47) | medium | N | N | N | C | C | C | C |
| **Weighted evidence against** | | **-3.4** | **-2.1** | **-0.7** | **-3.0** | **0.0** | **-3.1** | **-1.7** |

Hypotheses: **H0** Not really slow: a measurement artefact; **H1** Direct suppression held it; **H1b** Indirect containment: guards or roads at the boundary of permanent danger area 2; **H2** Patchy ground at 10 m scale or larger (bare ground, old burns, gaps); **H2b** Fine-scale fuel reduction below 10 m (grazing, trampling, cratering, short grass); **H3** Grass not fully cured (still partly green); **H4** Damper fine fuel and lighter wind at grass height than the station implies.

Least contradicted first: H2b > H1b > H4 > H1 > H2 > H3 > H0.

#### Where was the pairs range, and when was it overtaken?

| Evidence | Credibility | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| Rutland, Oct. 18: fire about a kilometre away when the wind shifted | medium | C | I | C | C |
| Rutland, Oct. 22: overtook the pairs range 'just before 4:00' | medium | I | C | C | C |
| DND release, Oct. 17: 'approximately 4:00 p.m.' | low | I | C | C | C |
| CZWN front 3:16 p.m., 82 km/h gust; station about 15 km west (front at the fire 3:16-3:25) | high | C | C | C | II |
| GOES-18 fire power 76 MW (3:10) -> 1,215 MW (3:30); 336 MW at 3:40 in the southern pixel only | medium | C | C | N | II |
| Model (240 fires): Range 2 median 3:21-3:30, road head 3:26-3:34; 0-9% of fires reach either 3:45-4:00 | medium | C | N | I | I |
| Model: ground 600-1,400 m from the edge that also burns 3:45-4:00 is 0-3% of the likely ground | medium | N | N | I | N |
| Part 2: 'about a kilometre' read 20 ways lands mostly around Range 2 and the road head (low-moderate confidence) | low | C | I | C | C |
| CBC (Oct. 22 briefing question): commander said they went from not seeing the fire to it being on top of them | low | C | C | N | C |
| Terrain: a rise of about 10 m hides the fire's edge from much of the ground near the road head (part 5) | medium | C | N | N | C |
| **Weighted evidence against** | | **-1.1** | **-1.1** | **-1.4** | **-4.1** |

Hypotheses: **L1** Range 2 / road head area, overtaken about 3:20-3:35 ('just before 4:00' approximate); **L2** Further south-east, 2-3 km from the fire at the shift, overtaken about 3:40-3:55 ('about a kilometre' approximate); **L3** On the fire's flank (strip south-east of the road head or by the western lake): both statements literal; **L4** The front reached the fire much later than the station (about 3:45), so Range 2 burned just before 4:00.

Least contradicted first: L1 > L2 > L3 > L4.


**Reading.**
- *Why was the fire slow?* The evidence rules out a measurement artefact (H0), patchy ground visible at 10 m (H2) and green grass (H3), and weighs against direct firefighting (H1). Least contradicted: fine-scale fuel reduction below 10 m (H2b: grazing, trampling, craters, short grass), containment by the boundary of permanent danger area 2 (H1b), and damper fuel / lighter wind at grass height (H4, as a contributor). H2b scores best partly because our imagery cannot test it: unfalsified is not confirmed. DND's answer on grazing, a map of the PDA 2 boundary, or sub-metre imagery would discriminate.
- *Where and when?* A front reaching the fire much later than the station (L4) is strongly contradicted by the station record and GOES. Range 2 / road head overtaken about 3:20-3:35 (L1) and a pairs range further south-east overtaken about 3:40-3:55 (L2) carry the same weight of evidence against them (L1 contradicts "just before 4:00"; L2 contradicts "about a kilometre" and part 2); L1 has more evidence for it. Both statements literal (L3) fits only a sliver of ground. DND's answer to "how was 'just before 4:00' established" would discriminate L1 from L2.

## Severity check

See `../model_v3/severity_oct24/ABOUT.md`: the fire burned harder after the shift (median dNBR 0.47 vs 0.40-0.42 before); the Range 2-road head area burned typically for the afternoon run.

## Caveats

- Everything after 3:16 p.m. is modelled from weather, satellite timing and the final scar; no ground observations. The front's arrival at the fire is timed from a station about 15 km west (3:16 p.m.; possibly up to about 3:25 at the fire).
- The smoke model's convection number uses the part 8b hourly spread rates, which are calibrated to the fire's measured pace (and so describe the actual, slow fire rather than its potential).
- Smoke is modelled, not observed.
- DND has not confirmed where C Company was. "Range 2 area / road head" remains an inference (low to moderate confidence, part 2).
- 40 m model grid; 10-30 m imagery. Features smaller than that (tracks, craters, pads) are not resolved.
