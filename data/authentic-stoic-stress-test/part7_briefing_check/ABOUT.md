# Part 7: Does the model fit what officials said on Oct. 22?

> **Correction, Oct. 28, 2026:** the DND "approximately 4:00 p.m." release is dated Oct. 18, not Oct. 17, and the station is 14.7 km from the fire, not about 13 km (both fixed below). The front time here (about 3:26) is superseded by working model v5: about 3:28 p.m. (3:27–3:29), in `cfb-wainwright-fire-archive-2`. See [`CORRECTIONS.md`](/CORRECTIONS.md).


At the Oct. 22 DND/CAF briefing, officials said: the fire was reported on the automatic grenade launcher (AGL) range; it initially stayed inside Permanent Danger Area 2, so firefighters could not attack it directly; range control monitored it throughout the day; the AGL range and the section-attack range are two separate ranges; the sudden wind change increased its speed and spread; there is no indication natural gas infrastructure was involved; the weapons-effect simulation and tracking system (WEST) was not in use; topography will be addressed by the investigation.

No model inputs change, so parts 1-6 were not re-run. `briefing_check.py` tests the statements against the existing data (`briefing_check.json`). PDA 2 boundary: OpenStreetMap (volunteer-mapped, not confirmed by DND).

| Statement | Our data | Fit |
|---|---|---|
| Fire stayed in PDA 2 at first | 59/59 Landsat (12:17) and 7/8 VIIRS (2:49) detections inside PDA 2; pre-shift outline 100% inside; final scar 91% inside | Consistent |
| Monitored all day | Satellite detections from about noon; Rutland: "several hours" | Consistent; contradicts DND's Oct. 18 release ("approximately 4:00 p.m.") |
| AGL and section-attack ranges are separate | Fire origin (12:17 centroid, 52.7764, -110.9214) is 1.1 km from Range 2 and 1.6 km from the road head | Consistent with Rutland's "a kilometre away when the wind shifted" |
| Sudden change increased speed | GOES-18 76 MW (3:10) to 1,215 MW (3:30); 82 km/h gust at 21:16Z | Consistent |
| No gas infrastructure | No producing gas wells within 2 km; two abandoned/reclaimed wells inside the scar; no OSM pipelines within 500 m | Consistent |
| WEST not in use | Not testable | No automatic position record expected |

## Refinement

Administrative areas sit outside danger areas. The road head (point B) is 10 m outside PDA 2 and about 20 m from the burn scar's edge; the Range 2 point (A) is 405 m inside PDA 2. The section-attack range's administrative area is therefore more plausibly at or near the road head than at A. A forward group on an attack lane could still have been inside PDA 2, toward the rise. This is an inference from map boundaries, not a confirmed location.

At the road head (part 4, best route, 3-minute margin, jogging): 100% reach safe ground leaving at the 3:16 gust; 73% leaving when flames come into sight (median 3:19) after a 2-minute delay; 20% leaving when the fire is within 300 m (median 3:24) after a 2-minute delay. Median fire arrival about 3:26 (10-90%: 3:22-3:36).

## Full re-run (Oct. 22, evening)

Parts 1-6 were re-run end to end (`spread.py`, `part2_distance.py`, part 3 sightlines, part 4 grids/permutations/clock/surface, part 5 vegetation/posture/smoke, part 6 edge growth). Every output reproduced exactly: no numeric differences from the published versions.

## Briefing-constrained analysis

`constrained.py` splits the part 2 likely ground by PDA 2 (`constrained_summary.json`, `likely_ground_by_pda2.csv`). **All 600 likely-ground cells lie inside PDA 2 as mapped.** The likely ground's visibility, escape and arrival figures are therefore unchanged by the split.

`outside_pda.py` asks where the fire burned outside PDA 2 (`burn_outside_pda2.json`, `burn_outside_pda2.csv`). Of 10.8 km² burned, 0.99 km² lies outside PDA 2:

- one patch of 0.98 km² at the scar's southeast tail, 4.8 km from where the fire started, which the fire reached about 50-85 minutes after the front in our models;
- slivers totalling about 0.002 km² along PDA 2's eastern boundary, 20-700 m from the road head.

If the section-attack range's administrative area lay outside PDA 2 (as admin areas normally do) and the fire overtook it about a kilometre from where the fire was when the wind shifted, the eastern boundary near the road head is the only burned ground that fits. The southeast patch is too far from the fire's position at 3:16. This rests on OpenStreetMap's PDA 2 boundary, which DND has not confirmed.

## Firming up the soft spots (`firm_up.py`, `firm_up.json`)

**When the front reached the fire.** A planar fit to front passage at Edmonton (1:27 p.m. MDT), Red Deer (2:24), Wainwright station (3:16) and Lloydminster (3:49) gives a front moving toward 130° at about 80 km/h. At that speed it would reach the fire, about 15 km (14.7 km) downstream of the station, around 3:26. The fit is loose (residuals up to about 13 minutes), and the GOES-18 southern pixel burning by 3:30 favours an earlier arrival. Bracket: **3:16 to about 3:26**. Parts 1-6 already model both ends (front at 3:16 and 3:25). Clock times may run up to about 10 minutes later than the 3:16-based figures; the minutes between the front and the fire's arrival do not change.

**How fast the fire ran.** The evidence pulls both ways. The GOES-18 southern pixel needs at least 8 km/h. The 3:30 fire power (1,215 MW, under a 100% cloud flag) fits a slower run, about 4 km/h by the Byram estimate, though cloud attenuates fire power. The 4.4-12 km/h range stands. If the fire ran at 8-12 km/h, escape odds are worse:

| Leaving at | Range 2 area, jog (all 30 fires / 8-12 km/h) | Road head, jog (all / 8-12 km/h) |
|---|---|---|
| The gust | 80% / 70% | 100% / 100% |
| +3 min | 43% / 15% | 83% / 75% |
| +5 min | 40% / 10% | 73% / 60% |
| +7 min | 10% / 0% | 53% / 30% |

At 8-12 km/h, the median fire arrival is about 5 minutes after the front at the Range 2 point and about 9 minutes at the road head.

**Rutland's "a kilometre in 30 to 60 seconds".** The gust front itself moved at about 80 km/h, which is a kilometre in about 45 seconds. That matches the wind's arrival, not the flame front, which the data puts at 4.4-12 km/h (5 to 14 minutes per kilometre).
