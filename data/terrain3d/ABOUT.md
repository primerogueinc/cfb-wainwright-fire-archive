# 3D terrain reconstruction (work in progress, Oct. 25–26, 2026)

A 3D model of the CFB Wainwright training area, built from the data already in this archive, for a 3D version of the explainer videos. Code in `scripts/terrain3d/`. **Drafts: nothing here has been published yet.** Part of working model v4. Prime Rogue Inc., CC BY-NC 4.0.

## What's here

| Path | What it is |
|---|---|
| `pov/` | True-scale views from four points at 1.7 m eye height, looking toward the fire line Landsat 8 recorded at 12:17 p.m.: Range 13, Range 2, the roadhead and the garrison (Denwood). Each `pov_*_lab.jpg` marks the 59 Landsat fire pixels (filled = a 3 m flame there is in line of sight on bare earth; open = hidden by terrain). `viewshed_*.png` maps where a 3 m flame would be visible from each point. `pov_sheet.jpg` puts them together. `sightlines.json` has the counts per pixel. |
| `orbit_test/` | First test orbit over the burn (height exaggerated 3x, lighting as at 3:16 p.m.). |
| `fire_draft/` | The animated fire, with a morning prologue of grenadiers firing on Range 11, and representative figures for C Company. Updated as drafts are made. |
| `layers/` | `points.json` (all points used, in the scene grid, EPSG:3400 offsets), `modelled_arrival_minutes.tif` (the modelled time each 10 m cell burned, minutes after midnight MDT), `modelled_arrival_time.png` (a map of it), `fire_meta.json`, and the prone grenadier silhouette drawn for the animation. |

## Sightline results (12:17 p.m. fire line, 59 Landsat pixels)

| From | Distance | 3 m flame, bare earth | 3 m flame, trees as solid | 30 m smoke |
|---|---|---|---|---|
| Range 13 | 1.6–3.3 km | 19 | 19 | 59 |
| Range 2 | 0.9–2.1 km | 7 | 7 | 35 |
| Roadhead | 1.3–2.5 km | 0 | 0 | 35 |
| Garrison | 4.6–6.2 km | 4 | 0 | 51 (10 with trees) |

## Sources and limits

- **Terrain:** NRCan MRDEM-30 (30 m). The HRDEM lidar touches only ~1% of the scene, so rises smaller than ~30 m are not resolved.
- **Trees:** Meta/WRI canopy height model. Mid-October aspen is mostly bare, so "trees as solid" is a pessimistic bound; the truth lies between the two flame columns. Each observer is given a 25 m clearing.
- **Imagery:** Copernicus Sentinel-2 L2A, Oct. 4, 2026 (bands B04/B03/B02; the exported true-colour TIFF is truncated). Burn severity: Sentinel-2 dNBR, Oct. 4 → Oct. 24.
- **Points:** Range 2, Range 11 and Range 13 are OpenStreetMap polygon centroids, not verified by National Defence. Roadhead: CanVec road dead end (52.7705, −110.8996). Garrison: CGNDB "Denwood".

## What in the fire animation is observed and what is modelled

**Observed:** Landsat 8 fire pixels (12:17 p.m.), NOAA-20 VIIRS detections (2:49 p.m.), the CZWN 82 km/h gust and wind shift to the northwest (3:16 p.m.), GOES-18 fire power (3:10–3:40 p.m.), the Sentinel-2 burn scar (Oct. 24).

**Modelled:** before 3:16 p.m., working model v4's best-fit morning fire (case v4b: start about 5:00 a.m., 1.4-2.2 km east of Range 11 along ~80°; v4 window 4:00-6:30, v3 3:30-7:00), read from `model_v4/arrival_prefront_v4b_2x_lb3.0_0500.tif` on the `authentic-stoic-alternative-hypothesis` branch and resampled from 40 m to 10 m (areas within ~5% of v4's); cells of the 12:17/2:49 detection outline not yet reached by v4b burn by distance from the noon line, as v4 joins that outline to its 3:16 fire; after 3:16, the run southeast shown as distance downwind of the footprint, 3:20 → 3:35 p.m. (4.8 km, ~19 km/h); the rest of the scar burns outward at 2 km/h. About 0.8 km² of the scar is not connected to the main fire, including the patch by Range 13 where VIIRS detected heat on **Oct. 14**; it is shown only at the end, as "timing unknown".

The video therefore opens at 8:00 a.m. with the fire already burning in Range 11's impact area. Modelled arrival at the Range 2 point and the road head: about 3:22 and 3:23 p.m. (v4 weighted medians: 3:21 and 3:26).

**Illustrative only:** the AGL firing in the prologue (DND said on Oct. 22 that the fire started on the automatic grenade launcher range; Range 11 is the AGL range per the standing orders as reported; firing positions, targets and times are not public), and all figures: C Company (~30, a platoon-sized slice, in the Range 2–roadhead area named in the location analysis) and twelve prone grenadiers with range staff on Range 11. Their movement is ordinary range activity and **stops at 3:16 p.m.**: no public source says what anyone did once the wind turned, so the animation does not show it. Figures are drawn at a fixed screen size, not to scale.

The silhouette libraries used for the figures are not included here; only the prone grenadier drawn for this animation is.

## Eye-level version (`eye_level/`, Oct. 27)

`cfb-wainwright-3d-eye-level-draft1.mp4`: what someone standing at the Range 2 point (top) and the road head (bottom) could have seen, from 11:30 a.m. until the modelled fire reached each point. True scale, eye height 1.7 m, looking west-northwest to north-northwest (heading 300°, 15 mm lens); terrain NRCan MRDEM-30 plus Meta/WRI canopy. `povcam_*.json` give each camera. Code: `scripts/terrain3d/compose_pov.py` (base renders: `scene.py` mode `povbase`).

- **Fire:** working model v4, case v4b morning fire and its best-fitting post-front fire (wind 315°, 8 km/h): reaches the Range 2 point at about 3:21 and the road head at about 3:25 p.m.
- **Smoke visibility** follows v4's smoke model for that fire (`model_v4/smoke/`): before the front, haze at the Range 2 point from about 3:10 (about 2.7 km), the road head clear; after it, under 1 km at 3:18 at both points, under 100 m at 3:20 (Range 2) and 3:23 (road head). Values between are interpolated on a log scale.
- **Illustrative:** flame heights (2 m before the wind shift, 3-7 m after) and the smoke column before the shift.
- **No people are shown.** Each panel cuts to black just before the modelled fire reaches its point.

## Correction (Oct. 27)

The timeline drafts 3 and 4 and fire drafts 1 and 2 were labelled "height x3", but their terrain was rendered at true scale (only the test orbit is exaggerated 3x). Figures were placed with 3x heights, a few pixels off the ground. Timeline draft 5 fixes the label and the figure placement.
