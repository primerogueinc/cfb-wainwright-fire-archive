# CFB Wainwright fire, Oct. 17, 2026: where was C Company when the fire overran it?

**Method:** Analysis of Competing Hypotheses (Heuer), with a Quality of Information Check and a Key Assumptions Check.
**Analyst:** independent review. The only data used is the local archive at `/home/claude/cfb-wainwright-fire-archive` (commit b096708, read-only).
**Date:** Oct. 21, 2026.
**Projection for distances:** EPSG:3400 (Alberta 10-TM). All times are MDT (UTC−6).

Supporting files (all in this folder):
- `ach_map.png`: map of burn severity, detections, OSM ranges, GOES footprints, hypothesis zones and the downwind band.
- `ach_matrix.csv`: the ACH matrix with weights and scores.
- `candidate_points.csv`: distances and dNBR at named candidate points.
- `geometry_results.json`: all computed geometry.
- `scar_grid_upwind_distances.csv`: a 50 m grid over the scar, with the upwind distance from each cell to the pre-shift fire.
- `goes_fire_pixels.csv`: GOES fire-pixel centres and footprints, recomputed from the raw netCDF files.
- Scripts: `goes_pixels.py`, `geometry.py`, `points.py`, `ach_matrix.py`, `map.py`.

---

## 0. Bottom line

- **Most likely location (H1):** the casualties were most likely in a band about 0.6–1.5 km southeast of where the fire stood just before the 3:16 p.m. wind shift. That band lies around and south of the spot OpenStreetMap labels "Range 2 (Grenade)", along the north–south range road and track near 110.90° W, at roughly 52.760–52.775° N. This is **likely**, at roughly 55–70%.
- **Main alternative (H4b):** the same downwind band extends southwest to the strip of burned ground just north of Jamieson Lake's northern arm (about 52.760–52.768° N, 110.912–110.92° W). Of the alternatives, H4b is the only one with almost no evidence against it. Most of the evidence that favours H1 over H4b is soft, so H4b is **unlikely but credible** (about 15–25%).
- **Rejected or nearly so:**
  - H2 (Range 3 / north end): **very unlikely**. Fire was already inside or next to the Range 3 polygon at 14:49, the polygon itself did not burn, and the NW wind after the front pushed the fire away from it.
  - H4a (west/northwest interior): **remote**. That ground was already burning or burned before the shift.
  - H3 (east of the boundary road): **very unlikely**. It is 3–4.5 km downwind, mostly outside the base, and may have burned later.
  - H6 (south-central part of the SE run, a hypothesis I added): **unlikely**, about 5–15%.
  - H5 (outside the mapped scar): **unlikely**, about 5–10%. Its most plausible version is a staging spot on the burn's edge at the road end near 52.7705° N, 110.8996° W, which is itself inside the H1 box.
- **Confidence: low to moderate.** The ranking rests on two things nobody has verified:
  - Rutland's account of a wind shift with the fire about 1 km away. His own numbers don't add up: covering 1 km in 30–60 s means 60–120 km/h, which is not physically plausible for a grass fire.
  - Range names and positions that come only from OpenStreetMap.

  The aircraft (ADS-B) data that could show where air ambulances landed is not in the archive yet. Only its ABOUT.md has been committed.

---

## 1. Quality of Information Check

| # | Source (repo path) | What it can show | What it cannot show | Reliability | Spatial / temporal precision |
|---|---|---|---|---|---|
| S1 | NASA FIRMS Landsat 8 (`data/firms/detections.csv`) | 59 actively burning 30 m pixels at 12:17. They form a NE-trending line from 52.7704/−110.9367 to 52.7798/−110.9127. | Ignition time, smouldering ground, anything after 12:17 | High (NRT; values match the v2 manual package) | ~30 m; one instant |
| S2 | FIRMS VIIRS NOAA-20 (same file) | 8 hotspots at 14:49, 52.7686–52.7883° N, totalling ~70 MW. One falls inside the OSM Range 3 polygon. | Fire edges between pixel centres. Two pixels sit 39–47 m outside the scar, which is within tolerance. | High | 375 m pixel, geolocation ±~0.4 km; one instant, about 30 min before the front |
| S3 | FIRMS Oct. 18 (SNPP 14:12, NOAA-20 14:32) | Heat still present on Oct. 18 at 52.746/−110.866, inside the scar's east lobe, 565–619 m outside the OSM base boundary | Anything about Oct. 17 | High | 375 m |
| S4 | GOES-18/19 FDCF raw netCDF (`data/goes/fdc_raw/`) and `fire_timeline.csv`. I recomputed the pixels independently and they match the repo. | Timing: fire pixels at 15:10 (76 MW), 15:30 (3 pixels, 1,215 MW), 15:40 (south pixel only, 336 MW). The 3.9 µm anomaly peaks at 15:30 (39.9 K) and fades by 16:00. | Location finer than a few km. Each footprint covers ~11 km², and the footprints are oblique parallelograms. The cloud mask reads 96–100% "cloud" all afternoon, so detections before 15:10 were likely blocked. | High for timing, low for position | Each pixel ~2.6 × 4.4 km. **Terrain parallax is not corrected.** At view zenith 65° and ~660 m elevation, apparent positions sit ~1.4 km NE of the true ones (I computed this). Scans every 10 min. |
| S5 | Sentinel-2 dNBR (`data/copernicus/`) and revised patches (`data/infrastructure/scar_patches_revised.geojson`) | Final burned extent. The main patch is 10.80 km² (EPSG:3400), its axis bears 130°, and it is 6.2 km long. Burn severity per 20 m pixel. | **When** each part burned: the post-fire scene is Oct. 19 and includes Oct. 18 burning. Light burns below dNBR 0.27. The post-fire scene is only 78% clear. | Moderate–high | 20 m; integrates Oct. 4 to Oct. 19 |
| S6 | OSM (`osm_infrastructure_ODbL.geojson`) | Named range polygons, roads, tracks and the base boundary | Whether the names and positions are correct. "Range 2 (Grenade)" has a single version by one contributor (2024-01-16, per `data/topo/run.log`). DND has verified none of it. | **Low–moderate** | Unknown; probably tens of metres |
| S7 | CanVec 1:50k (`data/reference/`) | Collector road dead-ending at 52.7705/−110.8996; building at 52.7701/−110.8963; trails | Current use (the data is dated) | Moderate | ~10–25 m |
| S8 | ECCC SWOB, CZWN (`data/eccc/`) | Wind SW (235°) until the front. Peak gust 82 km/h from 269° at 3:16. 306° by 4 p.m. Temperature fell 10 °C and humidity rose to 43%. | The wind at the fire site, which is 14.7 km at bearing 119° from the station. No minute-by-minute record. | High | One point; hourly snapshots plus peak-gust time |
| S9 | ECCC hourly, other stations (`data/reference/eccc_hourly_oct2026/`) | Front timing across the region | Exact minute of arrival at the fire | High | Hourly |
| S10 | NRCan CWFIS FWI | Fire danger was Extreme (FWI 30.8 at noon) | Location | High | Station, daily |
| S11 | ADS-B (`data/adsb/`) | **Not present.** Only ABOUT.md is committed. | — | — | — |
| S12 | Public statements (DND, Rutland, Carignan, Globe and Mail) as given in the tasking | Claims about times, distances and places | Not verifiable from the repo | Low–moderate. They are self-interested or second-hand, and they contradict each other (see §5). | Vague |

---

## 2. Key Assumptions Check

| # | Assumption | Rating | If wrong |
|---|---|---|---|
| A1 | The people were overrun by the Oct. 17 main fire (the 10.8 km² patch), not by another fire | **Solid.** It is the only Oct. 17 fire in the FIRMS/GOES record near the base. | The whole analysis would be moot. |
| A2 | The overrun happened on ground that ended up inside the mapped scar | **Supported, with caveats.** A light grass burn can fall below dNBR 0.27, and an admin area on a road or gravel pad can be just outside. | H5 (edge locations) gains. The road end and building just outside the NE flank (20 m and 82 m) become prime candidates. They lie inside the H1 box anyway. |
| A3 | The shift Rutland describes is the cold-front shift: 3:16 p.m. at CZWN, probably reaching the site around 3:20–3:35 | **Supported, with caveats.** The station is 14.7 km WNW, and the GOES jump to 1,215 MW at the 15:30 scan fits this timing. | If he meant the earlier gust-driven veer (246° at 2:48), the downwind direction would be NE. The northern zones (H2) would then gain. Even so, the scar does not extend NE beyond the road. |
| A4 | Rutland's "~1 km" is roughly right (0.5–1.5 km) | **Unsupported / doubtful.** His "30–60 s" gives 60–120 km/h, roughly 5–15 times a plausible grass-fire spread rate. At least one of the two numbers is wrong. | If the real distance was ~100–300 m, the site moves to the SE edge of the pre-shift fire: the west part of H1, or H4b next to the pond and lake. If it was 2–3 km, H6 gains. H3 still needs more than 3 km. |
| A5 | The fire's footprint at the shift ≈ the convex hull of the 12:17 + 14:49 detections, expanded by up to ~400 m | **Supported, with caveats.** It is about 30 min out of date, VIIRS has ±375 m error, and active pixels are not the perimeter. | The downwind band slides SE by a few hundred metres. I tested this: with +400 m, the band's share in H1 drops from 77% to 56%, and H6 rises from 0% to 31%. |
| A6 | The OSM range labels and positions (Range 2 Grenade, Range 3) are correct | **Unsupported.** One volunteer edit, never verified. | The landmark wording of H1 and H2 loses its meaning. The geometric ranking (downwind band) does not depend on the labels. |
| A7 | The Globe's "Range 3" means the same feature as OSM's Range 3 | **Unsupported** | E9 becomes noise. |
| A8 | After the shift, the fire spread with the wind, i.e. SE | **Solid.** The scar axis bears 130°, and the post-front wind came from 306°. | — |
| A9 | The scar shows where the fire was at the time of the incident | **Weak.** The scar covers burning up to Oct. 19, and the east lobe was still hot on Oct. 18. | H3's support from the scar shrinks further, because part of the east lobe may have burned after the incident. |
| A10 | A section-attack admin area is a fixed spot with vehicle access, i.e. near a road or track end | **Supported, with caveats** (doctrinal inference, not data) | E16 drops out. Small effect. |
| A11 | GOES parallax goes ~1.4 km toward the SW | **Supported** (geometry: view zenith 65°, satellite azimuth 212°, ~660 m elevation). ABI navigation error of about 1 km comes on top. | GOES stays non-diagnostic either way. |
| A12 | Time conversions are right: FIRMS UTC−6, ECCC LST UTC−7 → MDT, GOES scan start | **Solid** (checked) | — |
| A13 | The casualties were where the admin area was, and did not move far while fleeing | **Unsupported** | Their positions could differ from the admin area by hundreds of metres, most likely in the SE (downwind) direction. |

---

## 3. Hypotheses and geometry

Hypothesis zones (WGS84 boxes, drawn on `ach_map.png`):

- **H1:** Range 2 / N–S track. Box 110.912–110.895° W, 52.760–52.778° N.
- **H2:** Range 3 / north end. Box 110.915–110.895° W, 52.778–52.795° N.
- **H3:** eastern lobe at or east of the boundary road. Box 110.880–110.850° W, 52.735–52.770° N.
- **H4a** (split from H4): west/northwest interior. West of 110.912° W, north of ~52.768° N.
- **H4b** (split from H4): southwest strip near the lakes. West of 110.912° W, between the pre-shift fire and Jamieson Lake / the pond.
- **H5:** outside the mapped scar.
- **H6** (added): south-central part of the SE run. 110.912–110.880° W, 52.735–52.760° N.

### Key computed facts

**Pre-shift fire.** I used the convex hull of the Landsat (12:17) and VIIRS (14:49) detections:
- Area 2.0 km², of which 97% is inside the scar.
- From 12:17 to 14:49 the fire grew slowly, roughly 1 km northward. The N–S collector road along 110.90° W held its east flank: north of the road's dead end at 52.7705° N, the scar edge follows the road to within ~20 m.

**Wind.** At CZWN the wind blew SW (235°) until the front, then from 269° (82 km/h gust at 3:16), then from 306° (51 km/h average by 4 p.m.).
- Front timing at the site: 14.7 km at bearing 119° from the station, so arrival around 3:20–3:35.
- GOES-18 fits this: fire power went from 76 MW (15:10) to 1,215 MW (15:30). The 3.9 µm anomaly then drifted S and E and had faded by 16:00.

**Post-shift run.**
- The scar's SE lobe starts at the hull's southern edge and runs 4.8 km at a bearing of about 130° to 52.743/−110.865.
- Its NE flank runs from the "Range 2" notch ESE to the boundary road. Its SW flank is Jamieson Lake.
- If the run took 20–40 min, the spread rate was 7–14 km/h, so 1 km would take about 4–9 min, not 30–60 s.
- Nothing burned east of the 110.90° W road north of 52.7705° N. The brief W (269°) phase therefore did not carry fire eastward. The run was driven by the NW wind.

**Upwind distance from each scar cell to the pre-shift fire** (search toward 306°). The "≈1 km" band is the set of burned cells 0.6–1.5 km downwind:

| Pre-shift footprint assumed | Band area | H1 | H4b/H4 | H6 | H2 | H3 |
|---|---|---|---|---|---|---|
| Hull (wind 306°) | 1.47 km² | 77% | 23% | 0% | 0% | 0% |
| Hull + 400 m (306°) | 1.60 km² | 56% | 13% | 31% | 0% | 0% |
| Hull + 800 m ∩ scar (306°) | 1.65 km² | 23% | 5% | 72% | 0% | 0% |
| Hull (wind 269°) | 0.47 km² | 96% | 2% | 0% | 2% | 0% |

**Candidate points** (`candidate_points.csv`):

| Point | In scar? | Upwind distance to hull at 306° | dNBR (60 m) |
|---|---|---|---|
| OSM Range 2 (Grenade) centroid | yes, 62 m inside the edge | 0.59 km | 0.24 (low) |
| CanVec road dead end 52.7705/−110.8996 | 20 m outside | 1.12 km | 0.22 |
| CanVec building 52.7701/−110.8963 | 82 m outside | 1.34 km | 0.18 |
| Track at 52.763 / 52.760 | yes | 1.56 / 1.49 km | 0.50 / 0.52 |
| SW strip north of the lake (52.763, −110.915) | yes | 0.99 km | 0.49 |
| OSM Range 3 centroid | **no**: polygon 0% burned | 0.14 km (VIIRS pixel inside it at 14:49) | 0.20 |
| East lobe at the boundary road (52.755, −110.875) | edge | 3.45 km | 0.24 |
| Oct. 18 VIIRS point in the east lobe | yes, outside the base | 4.46 km | 0.43 |

**Zone burn severity (mean dNBR):** H6 0.52, H1 0.50, H4 0.44, H3 0.44, H2 0.39. The highest severity is in the post-shift run.

**GOES footprints** (parallax-corrected; `goes_fire_pixels.csv`):
- The northern pixel (15:10 and 15:30) covers both Range 2 and Range 3.
- The southern pixel (15:30 and 15:40) covers H6/H4b and the lake.

At this scale GOES does not discriminate between the hypotheses.

---

## 4. ACH matrix

Ratings: C = consistent, N = neutral or not applicable, I = inconsistent, II = strongly inconsistent.

Weight = credibility × relevance, with H = 1.0, M = 0.7, L = 0.4.

Score = −(sum of weights for I) − 2 × (sum of weights for II). Only disconfirming ratings count, per Heuer; a score closer to 0 is better.

| ID | Evidence | Cred | Rel | Wt | H1 | H2 | H3 | H4a | H4b | H5 | H6 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | Landsat 8, 12:17: 59 hotspots in NW lobe (52.770–52.780 N, −110.937 to −110.913) | H | H | 1.0 | N | I | N | II | N | N | N |
| E2 | VIIRS 14:49: 8 hotspots 52.769–52.788 N; one inside OSM Range 3; hull 0.59 km from Range 2 | H | H | 1.0 | C | II | N | II | C | N | N |
| E3 | Sentinel-2 scar: Range 2 inside (60 m from edge); Range 3 0% burned; zone burned fractions | H | H | 1.0 | C | I | N | C | C | I | C |
| E4 | Scar morphology: axis 130°, SE run starts at S edge of pre-shift fire; NE flank passes Range 2; road held E flank N of 52.7705 | M | H | 0.7 | C | I | C | I | C | N | C |
| E5 | ECCC CZWN: SW to 3:16; 82 km/h gust from 269° at 3:16; 306° by 4 p.m. | H | H | 1.0 | C | I | C | I | C | N | C |
| E6 | Rutland: fire ~1 km away at the shift (computed upwind distances) | M | H | 0.7 | C | II | II | II | C | C | I |
| E7 | Rutland: covered it in 30–60 s (= 60–120 km/h, implausible) | L | M | 0.28 | N | N | N | N | N | N | N |
| E8 | Rutland: section-attack admin area; grenade range "not affected" | M | M | 0.49 | N | N | N | N | N | N | N |
| E9 | Globe and Mail (unverified): "Range 3" | L | M | 0.28 | N | C | I | I | I | N | I |
| E10 | Carignan: "far removed from the training area" | L | L | 0.16 | N | N | N | N | N | N | N |
| E11 | DND release: fire ~4 p.m. | L | L | 0.16 | N | N | N | N | N | N | N |
| E12 | GOES-18 FDC 15:10 / 15:30 (1,215 MW) / 15:40 (south pixel only) | H | L | 0.4 | N | N | N | N | N | N | N |
| E13 | Spread rate: 4.8 km run in ~20–40 min (7–14 km/h), so far-SE sites had 15–30 min warning | M | M | 0.49 | C | N | I | N | C | N | I |
| E14 | Base boundary: 82% of the H3 zone is outside CFB Wainwright | M | M | 0.49 | N | N | I | N | N | N | N |
| E15 | dNBR severity highest in the SE run (H6 0.52, H1 0.50; H2 0.39) | M | L | 0.28 | C | I | N | N | N | I | C |
| E16 | Access: road dead end + building 1.1–1.3 km downwind on the burn edge; Range 3 has a building | M | L | 0.28 | C | C | N | N | N | C | N |
| | **Weighted inconsistency** | | | | **0.00** | **−7.38** | **−2.66** | **−7.38** | **−0.28** | **−1.28** | **−1.47** |
| | Count of I/II | | | | 0 | 7 | 4 | 6 | 1 | 2 | 3 |

### Notes on ratings

- **E8:** "Grenade range not affected" is rated N, but it is a mild warning sign for the OSM labels. OSM's "Range 2 (Grenade)" lies inside the mapped scar, 60 m from its edge. The local dNBR there is 0.24, which is below the burn threshold, so the spot was probably lightly burned or just at the edge. Three readings are possible:
  - The OSM position or label is wrong.
  - "Not affected" means operationally, e.g. not the ignition source.
  - The range sat on an unburned or lightly burned flank, which the low dNBR supports.
- **E6:** H5 is rated C because the road end and building are 1.1–1.3 km downwind.

### Sensitivity (`ach_matrix.py` output)

| Evidence removed | H1 | H4b | H6 | H5 | H3 | H2 | H4a |
|---|---|---|---|---|---|---|---|
| E6 (Rutland's 1 km) | 0 | −0.28 | −0.77 | −1.28 | −1.26 | −5.98 | −5.98 |
| E6 and E9 | 0 | 0 | −0.49 | −1.28 | −0.98 | −5.98 | −5.70 |
| E2 | 0 | −0.28 | −1.47 | −1.28 | −2.66 | −5.38 | −5.38 |
| E3 | 0 | −0.28 | −1.47 | −0.28 | −2.66 | −6.38 | −7.38 |

H2 and H4a are rejected however these items are handled.

Caveats on the matrix:
- **H1 and H4b are not separated by any strong item.** The only evidence against H4b is the weak Globe "Range 3" reference. H1's advantages are soft:
  - Most of the ≈1 km downwind band falls in H1 (56–96%, depending on assumptions).
  - The admin area plausibly sits at the road end.
  - Rutland's mention of the grenade range suggests it was a nearby landmark.
- **H3, H6 and H5 are separated from H1 mainly by E6** (Rutland's 1 km, credibility M). E13 and E14 are independent of him and still count against H3.

---

## 5. Inconsistencies found

### In the public statements

1. **Fire timing.** DND says the fire was reported or ignited at about 4 p.m. Yet Landsat shows active fire at 12:17, and Rutland says range control knew of it "for several hours." The 4 p.m. time cannot be the ignition time. It may be when the incident was reported.
2. **"1 km in 30–60 s."** That is 60–120 km/h. The scar and GOES timing imply a run of roughly 7–14 km/h, perhaps briefly faster in 80 km/h gusts. The distance, the time, or both are wrong. Possibly the distance was much shorter, or the time was minutes.
3. **Carignan vs. Rutland.** Carignan said the fire was "far removed from the training area." Rutland put it about 1 km away, and the satellite data shows it burning among the OSM-mapped ranges: inside Range 3 at 14:49, 0.6 km from Range 2.
4. **Grenade range.** Rutland said the grenade range was "not affected," but OSM puts "Range 2 (Grenade)" inside the scar edge (with low local dNBR).
5. **"Range 3" (Globe and Mail)** conflicts with the scar: OSM Range 3 is 0% burned. If C Company was at Range 3, it was not overrun on that polygon.
6. **Fire danger.** The CAF memo reportedly called the fire index "low" (repo note in `data/nrcan_cwfis/ABOUT.md`). CWFIS gives FWI 30.8, Extreme, for the base's own station. This doesn't bear on location, but it shows how far official accounts diverge from the data.

### In the repo

1. **Lloydminster distance.** `data/eccc/ABOUT.md` says Lloydminster (CYLL) is "~50 km northeast." I compute 82 km from the fire and 87 km from CZWN.
2. **Scar area.** `copernicus/summary.json` gives 11.71 km² in 31 patches. `scar_patches_revised.geojson` has 8 patches summing to about 11.54 km² (main 10.79). I did not find the revision documented in the files I read; it is a minor gap.
3. **"Fire site" reference.** `scar_vs_infrastructure.json` and the ADS-B script use different reference points (e.g. SCAR = 52.775/−110.905 vs. the detection centroid 52.7767/−110.9210 in the geography notes). This is harmless, but distances such as "km_from_ref" in the GOES table depend on which one is used.
4. **ADS-B.** The README/ABOUT describe outputs (points.csv, traces) that are not committed.
5. **GOES cloud mask.** The cloud mask reads 96–100% cloud during the fire-pixel scans. Smoke or dust may be classed as cloud, so the GOES "no fire" scans before 15:10 do not show that the fire was absent. (`fire_timeline.csv` doesn't make this explicit.)
6. **Range 3 and the scar.** Two VIIRS 14:49 pixels lie 39–47 m outside the scar, one of them inside OSM Range 3, which itself did not burn. Within VIIRS geolocation error this is consistent, but it means the 14:49 pixel there may reflect heat just west of Range 3.
7. **Overlap of GOES pixels.** The GOES 15:10 pixel and the first 15:30 pixel are the same pixel, so they are not two independent locations.

---

## 6. Conclusions

### Ranking

| Rank | Hypothesis | Likelihood | Probability |
|---|---|---|---|
| 1 | **H1**: around and SE of OSM "Range 2", N–S road/track ~110.90° W, 52.760–52.775° N | **likely** | ~55–70% |
| 2 | **H4b**: SW strip north of Jamieson Lake's north arm (~52.760–52.768° N, 110.912–110.92° W) | unlikely, credible alternative | ~15–25% |
| 3 | **H6**: south-central SE run (52.74–52.76° N) | unlikely | ~5–15% |
| 4 | **H5**: just outside the scar. Mainly the road end/building at the NE flank, which overlaps H1 spatially. | unlikely | ~5–10% |
| 5 | **H3**: east lobe at or beyond the boundary road | very unlikely | <5% |
| 6 | **H2**: Range 3 / north end | very unlikely | <5% |
| 7 | **H4a**: W/NW interior (burned before the shift) | remote | <3% |

Taken together, H1 + H4b (the ~1 km downwind band SE of the pre-shift fire, between the 110.90° W road and Jamieson Lake) is **very likely**, about 80%.

**Confidence: low to moderate.**
- **What drives the ranking:** three physically grounded pieces of evidence that are independent of the officials:
  - Wind direction before and after the front.
  - The burn-scar shape, with its post-shift run.
  - The positions of the pre-shift detections.
- **What limits it:**
  - Fine placement within the downwind band depends on Rutland's "1 km," and his numbers contradict each other.
  - The pre-shift perimeter is inferred from detections taken 30 min before the shift.
  - Range names come only from OSM.
  - Nothing in the archive directly marks the casualty site (no ADS-B, no imagery from the time, no ground data).

### Five most diagnostic missing items

1. **The official location of the section-attack admin area** (DND grid reference, Board of Inquiry or range-booking record), plus DND's range numbering. Together these would settle H1 vs. H4b vs. H6 and test the OSM labels and the Globe's "Range 3."
2. **Air-ambulance or helicopter landing points and times** (the ADS-B pull is described but not committed; also STARS/AHS records). Where the casualties were picked up marks the site to within a few hundred metres.
3. **The fire perimeter and wind at the site around 15:00–15:35**: range control and fire-department logs, a range weather station, any aerial or commercial imagery (e.g. Planet), or geolocated photos and video. These would fix where the fire was at the shift and whether "1 km" is right.
4. **A clarified transcript of Rutland's briefing**: the exact distance and time, which shift he meant (the 2:48 veer, the 3:16 W gust, or the NW turn), and what "grenade range not affected" meant.
5. **High-resolution post-fire imagery** (sub-metre) of the H1/H4b band and the road end, showing burned vehicles, equipment or a disturbed staging area. Also a timeline separating the Oct. 17 and Oct. 18 burning in the east lobe.
