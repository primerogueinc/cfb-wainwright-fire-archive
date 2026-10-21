# Location analysis, fire models and stress test (Oct. 21, 2026)

Prime Rogue's estimate of where C Company was when the Oct. 17 fire reached it, the fire-behaviour model runs, and the stress test. Code in `scripts/location_analysis/`.

| File | What it is |
|---|---|
| `ach_report.md`, `ach_matrix.csv` | Independent Analysis of Competing Hypotheses: sources, key assumptions, evidence matrix, ranking |
| `geometry_results.json`, `candidate_points.csv`, `goes_fire_pixels.csv` | Geometry behind the ranking (distances, burn severity at named points, GOES pixel footprints) |
| `scar_grid_upwind_distances.csv` | 50 m grid over the burn: upwind distance from each cell to the fire's outline before the 3:16 p.m. wind shift |
| `sensitivity.csv` | Share of each distance band in each candidate area, across wind directions 270–325° and fire growth of 0, 400 and 800 m |
| `stress_results.json` | Infrastructure (AER wells and pipelines, CanVec roads, buildings) per candidate area and near the 12:17 p.m. fire line |
| `fire_models.csv`, `fire_model_tests.json` | Canadian FBP (O-1a, O-1b), CSIRO grassland (natural, grazed) and Cruz et al. (2022) runs on the base's Oct. 17 weather |

Range names come from OpenStreetMap and are not verified by National Defence. Estimates, not findings. CC BY 4.0, Prime Rogue Inc.
