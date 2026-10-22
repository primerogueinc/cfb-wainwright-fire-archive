# Part 7: Does the model fit what officials said on Oct. 22?

At the Oct. 22 DND/CAF briefing, officials said: the fire was reported on the automatic grenade launcher (AGL) range; it initially stayed inside Permanent Danger Area 2, so firefighters could not attack it directly; range control monitored it throughout the day; the AGL range and the section-attack range are two separate ranges; the sudden wind change increased its speed and spread; there is no indication natural gas infrastructure was involved; the weapons-effect simulation and tracking system (WEST) was not in use; topography will be addressed by the investigation.

No model inputs change, so parts 1-6 were not re-run. `briefing_check.py` tests the statements against the existing data (`briefing_check.json`). PDA 2 boundary: OpenStreetMap (volunteer-mapped, not confirmed by DND).

| Statement | Our data | Fit |
|---|---|---|
| Fire stayed in PDA 2 at first | 59/59 Landsat (12:17) and 7/8 VIIRS (2:49) detections inside PDA 2; pre-shift outline 100% inside; final scar 91% inside | Consistent |
| Monitored all day | Satellite detections from about noon; Rutland: "several hours" | Consistent; contradicts DND's Oct. 17 release ("approximately 4:00 p.m.") |
| AGL and section-attack ranges are separate | Fire origin (12:17 centroid, 52.7764, -110.9214) is 1.1 km from Range 2 and 1.6 km from the road head | Consistent with Rutland's "a kilometre away when the wind shifted" |
| Sudden change increased speed | GOES-18 76 MW (3:10) to 1,215 MW (3:30); 82 km/h gust at 21:16Z | Consistent |
| No gas infrastructure | No producing gas wells within 2 km; two abandoned/reclaimed wells inside the scar; no OSM pipelines within 500 m | Consistent |
| WEST not in use | Not testable | No automatic position record expected |

## Refinement

Administrative areas sit outside danger areas. The road head (point B) is 10 m outside PDA 2 and about 20 m from the burn scar's edge; the Range 2 point (A) is 405 m inside PDA 2. The section-attack range's administrative area is therefore more plausibly at or near the road head than at A. A forward group on an attack lane could still have been inside PDA 2, toward the rise. This is an inference from map boundaries, not a confirmed location.

At the road head (part 4, best route, 3-minute margin, jogging): 100% reach safe ground leaving at the 3:16 gust; 73% leaving when flames come into sight (median 3:19) after a 2-minute delay; 20% leaving when the fire is within 300 m (median 3:24) after a 2-minute delay. Median fire arrival about 3:26 (10-90%: 3:22-3:36).
