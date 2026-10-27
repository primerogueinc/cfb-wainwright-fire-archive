# Burn severity on Oct. 24 compared with working model v3

Sentinel-2 L2A, Oct. 24, 2026 (clear except a few small cumulus clouds), against the Oct. 4 pre-fire baseline and the Oct. 19 pass. Raw bands: [Copernicus data repository](https://github.com/primerogueinc/CFB-Wainwright---Full-Satellite-Data---Copernicus-), `sentinel-2/2026-10-24/L2A_tiff/`. Severity is dNBR = NBR(Oct. 4) − NBR(date), NBR = (B8A − B12)/(B8A + B12). It measures how much vegetation changed, not how hot the fire was; fuel type also affects it.

Scripts: `scripts/authentic_stoic_alternative_hypothesis/model_v3/severity_oct24/` (`sev_vs_model.py`, `zoom.py`, `raw_views.py`). The model inputs (`p4_v3_v3b_2x_lb1.5_0630`, the 30 post-front arrival grids from `model_v3/post_front.py`) live in the working directory, not in the repo; rerun `post_front.py` to regenerate them.

## No change since Oct. 19 (`severity_oct19_vs_oct24.png`)

Within 500 m of the mapped 11.7 km² scar, ground at dNBR ≥ 0.27 measures 11.8 km² on Oct. 24 against 13.2 km² on Oct. 19. Median severity inside the scar is 0.45 vs 0.46; the median pixel change is −0.01. Spots that look worse on Oct. 24 are cloud and cloud shadow; blue rings round the lakes are water levels. No new burning after Oct. 19.

## Severity by phase of the fire (`sev_vs_model.png`, `sev_vs_model.json`)

40 m model grid; pixels where Oct. 24 and Oct. 19 disagree by more than 0.12 (cloud or shadow, 0.58 km²) dropped. Model: case v3b, median arrival of the 30 post-front fires.

| Phase | Area | Median dNBR | Share ≥ 0.44 |
|---|---|---|---|
| Burned by 12:17 p.m. (Landsat central class) | 0.42 km² | 0.40 | 22% |
| 12:17-3:16 p.m. (model v3 + detections) | 1.83 km² | 0.42 | 42% |
| After the 3:16 p.m. wind shift | 8.91 km² | 0.47 | 59% |

After the shift, median severity is 0.45 for ground the model reaches in the first 9 minutes, 0.50-0.53 from 9 to 54 minutes (the corridor through Range 2, the road head and point D), and 0.39-0.40 after 54 minutes (toward the lakes and the southeast end).

Reading: the fire burned harder after the wind shift, as the model's slow morning fire and fast afternoon run predict. This is independent of the model, which used no severity data. Within the afternoon run, severity barely tracks the model's local spread rate (Spearman 0.10) or arrival time (−0.04), so at this resolution it does not test where the head or flanks ran; fuel dominates.

## Our area against the rest (`our_area_vs_rest.png`, `our_area_vs_rest.json`)

10 m grid. "Our area" = within 300 m of the line from the Range 2 point to the road head (0.42 km² of burned pixels).

| | Median dNBR | Share ≥ 0.44 |
|---|---|---|
| Our area | 0.49 | 64% |
| Rest of the scar | 0.45 | 55% |
| Rest of the afternoon run | 0.47 | 58% |
| Rest of the afternoon run, reached 0-20 min after the shift | 0.48 | 65% |

Against 1,320 same-size patches placed at random in the afternoon run, our area ranks at the 34th percentile (patch medians 0.39-0.57, 5th-95th). Allowing for pre-fire vegetation (regression of dNBR on Oct. 4 NBR and NDVI), our area's residual is +0.028 against +0.016 for the rest. Reading: our area burned hard but typically for the afternoon run; nothing local made it burn hotter, and there is no anomalous hot spot.

**The edge.** The road head lies inside, and the Range 2 point about 70 m from, a pocket of at least 17 ha outside the mapped scar (dNBR 0.19 on Oct. 19, 0.10 on Oct. 24: unburned or lightly burned; light burning in grass can read this low). Pre-fire it had the same vegetation as the burned ground (NDVI 0.46), so it is not a bare pad. In the raw view it follows the curved access track from Range 2 to the main north-south road. Whether the track acted as a firebreak cannot be told at 10-20 m; higher-resolution imagery is needed. This places the two points at the northeast edge (flank) of the afternoon run, which fits the model's northwest wind after the shift. It does not show that safety was within reach: pixels are 20 m, and who was where, when, is not known.

## Raw views (`raw_views/`)

No overlays. Oct. 24 true colour and SWIR false colour (B12/B8A/B04), zoomed out (whole scar) and zoomed in (~1.3 km round Range 2 and the road head; one block = one ~10 m pixel); Oct. 4 and Oct. 19 true colour zoomed in for comparison. The two bright white spots at the Range 2 point and the road head are present on Oct. 4: permanent structures or pads, not fire effects.

Note: the Oct. 24 B08 band is corrupt as exported (re-export pending). Nothing here uses it.
