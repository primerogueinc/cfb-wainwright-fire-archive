# Oct. 25 graphics: working model v4

All from working model v4 (`data/authentic-stoic-stress-test/model_v4/ABOUT.md`). House style; scripts in `scripts/maps/`.

| File | Script | Shows |
|---|---|---|
| `cfb-wainwright-held-back.jpg` | `g28_held_back.py` | Hourly head-fire speed the weather could support (FBP O-1a, 95% curing, corrected ISI) vs the fire's measured 0.43 km/h (12:17-2:49 p.m.) and the modelled 4.4-12 km/h after the front, on the Alexander et al. (2013) suppression classes |
| `cfb-wainwright-smoke-vs-fire.jpg` | `g29_smoke_timeline.py` | When haze (< 1 km), thick smoke (< 100 m) and fire reached four points, front at the fire 3:16 and 3:25 (weighted medians) |
| `cfb-wainwright-edge-range2-road-head.jpg` | `g30_edge_map.py` | Sentinel-2, Oct. 24, natural colour, with the burn edge; Range 2 inside the burn, road head on its edge |
| `cfb-wainwright-escape-robustness.jpg` | `g31_ensemble.py` | Escape odds from the Range 2 point across the 240-fire ensemble, by front time, wind, speed, shape and start case |
| `cfb-wainwright-competing-hypotheses.jpg` | `g32_ach.py` | Analysis of competing hypotheses: why the fire was slow; where and when the pairs range was overtaken |
| `cfb-wainwright-dnd-timeline-test.jpg` | `g27_dnd_timing.py` | DND's "about a kilometre away" (Oct. 18) and "just before 4:00" (Oct. 22) against the model; maps show the 3:16 case, times for 3:25 in brackets |

`cfb-wainwright-dnd-timeline-test.jpg` reading: on the model, ground about a kilometre downwind burns in the 3:20s-3:30s (Range 2 median 3:21, road head 3:26; 3:30 and 3:34 if the front reached the fire at 3:25). Both statements fit together only for a thin strip south-east of the road head on the fire's flank, or a patch by the western lake, reached in 10-30% of modelled fires. Inputs: `model_v4/maps/truthful_reading*.npz`, `overtaken_time*.json`.

## Header, social card and thumbnail (working title)

| File | Size | Use |
|---|---|---|
| cfb-wainwright-v4-header.jpg | 1600×900 | Article header |
| cfb-wainwright-v4-og.jpg | 1200×630 | Social share card |
| cfb-wainwright-v4-thumbnail.jpg | 1280×720 | Video thumbnail |

Working title "Monitored for hours, beyond control in minutes". Background: Sentinel-2 true colour, Oct. 24, 2026. Rebuild with another title: `python3 scripts/maps/g33_v4_hero.py "LINE 1|LINE 2"`.

## DND's clock (`cfb-wainwright-dnd-clock.jpg`, g34_dnd_clock.py)

DND's Oct. 22 wording ("Just before 4:00 local time, uncommonly high winds took a pre-existing range fire towards the pairs range and it overtook their position") against ECCC CZWN (peak gust 82 km/h at 3:16 p.m.; 10.4 °C drop between the 3 and 4 p.m. readings), GOES-18 fire power (76 MW at the 3:10 scan, 1,215 MW at the 3:30 scan) and model v4 arrival medians. The first two rows need no model. GOES times are scan start times (10-minute scans).
