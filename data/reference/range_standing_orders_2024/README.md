# Wainwright Range Standing Orders, 2024 edition: fire rules and official range locations

Working analysis, Oct. 26, 2026, for working model v4. Script: `scripts/reference/rso_map.py`. Tables: `rso_points.csv` (official grid references converted from MGRS zone 12U, against the Oct. 17 burn), `rso_v4_arrival.csv` (working model v4 arrival times at the official grids). Map: `fig_rso_ranges.png`.

Source: "3 CDSB Edmonton Garrison Wainwright Range Standing Orders, 2024 Edition" (137 pages), digitally signed by Col. R.D. Dove, Base Commander, Sept. 17, 2024; no security marking. The document itself is not in this repository. The orders are "to be reviewed annually and will be re-issued upon any changes of command" (Foreword, para 5), and the record of amendments is blank. Whether this edition was in force on Oct. 17, 2026 is not confirmed.

## Findings

1. **The road head is Range 15's entrance.** Range 15, "Field Firing Range", sits at WD 06783 46728 (ch. 1 para 51l), 20 m from Prime Rogue's inferred road head. Its sentry, flag and swing-barrier point at "Yellow and Fireguard" (Annex H) is 16 m from it. Range 15's other barriers are at the south end of that fireguard (about 5.7 km south) and at the entrance to Range 14. A pairs range is field firing (fire and movement in pairs), so Range 15 is a natural place for one. This remains inference: the orders give Range 15's location, not C Company's.
2. **Range 2 is about 375 m east of the point we used.** The orders put Range 2, "Grenade Range", at WD 06686 46913, 188 m from the road head. Our earlier "Range 2 point" came from OpenStreetMap.
3. **The burn stops at both official grids.** The Oct. 17 burn edge is 10 m from the Range 2 grid and 18 m from the Range 15 grid; neither point is inside the mapped burn. This matches the burn-edge finding in v4 (`edge/`): the fire swept the ground west of the road head and stopped at the track junction, leaving an unburned pocket to the north-east.
4. *(Superseded Oct. 28, 2026: these times assume the front reached the fire at 3:16 p.m.; working model v5 puts it at about 3:28, with the fire at the Range 2 grid about 3:39 (3:34–3:51) and Range 15 about 3:42 (3:36–3:58). See `cfb-wainwright-fire-archive-2/data/rubicon-ridge/model_v5/ABOUT.md`.)* **The model's timing barely moves.** With the front at the fire at 3:16 p.m., the 240-run weighted median arrival is 3:25 p.m. at the official Range 2 grid (10th-90th percentile 3:21-3:32; 0% first reached 3:45-4:00) and 3:26 at Range 15 (3:22-3:35; 4%). That is the same as the road head figures already published. The model reaches both points in every run, although the real fire stopped 10-20 m short of them.
5. **The fire started within the grenade launcher's reach.** Range 11, "Grenade Launcher Range (AGLS and M203)", sits at WD 02612 46459, on the west edge of PDA 2. The back (south-west) end of the 12:17 p.m. Landsat fire line is 1.7 km east of it; a 40 mm automatic grenade launcher reaches about 2.2 km. This fits DND's statement that the fire began on the automatic grenade launcher range.
6. **Fire hazard ratings restrict tracer and pyrotechnics, not high explosive.** At "Extreme", "no pyrotechnics tracer or white phosphorous to be used at any time" (para 341d). At "High", tracer and pyrotechnics need the Base Commander's approval (341c). High-explosive grenades, what an AGL fires, are not mentioned.
7. **August to October is the declared danger season.** "Units firing during high-risk months (Aug-Oct) should plan to conduct early morning shoots. The fire hazard is normally low enough to permit the firing of most ammunition natures before approximately 1000 hrs" (para 342). The modelled ignition (pre-dawn to early morning) fits an early shoot.
8. **Impact-area fires are left to burn; the reporting unit stays with them.** Ground-cover fires go to Range Control, which "will immediately relay the information to the Fire Department and the Range Warden" (343). The reporting unit will "not fight fires in impact areas" and will "ensure the unit does not leave the fire until authorized to do so by Range Control in consultation with Range Warden" (344c, 344e). The Range Warden runs the response; more resources come only if the fire is declared "Out of Control" (345). This matches the Provost Marshal's account that the fire was monitored, not attacked, inside PDA 2.
9. **Weather warnings are to be passed on "immediately".** "A Forecast of Adverse Weather … will be distributed to all concerned agencies immediately when they are known" (214a); the categories are "WEATHER ADVISORY, WEATHER WARNING, WEATHER ALERT, FIRE INDEX RESTRICTIONS" (214b). "The initial decision to cease or modify training rests with the Chain of Command"; the final decision with the Base Commander (215). Range Control receives forecasts at 6 a.m. and 6 p.m.; its own station reports "wind direction/speed and current temperature only" (216). Environment Canada's wind warning was issued at 2:14 p.m. on Oct. 17.
10. **No wind rule.** The orders set no wind-speed limit for firing or for troops near a fire. They have no withdrawal trigger for a fire burning in a danger area, and nothing on wind shifts or fronts. Range Control "will order a unit to check fire or cease other training" if "the unit is about to be endangered by another unit" or "as necessary in emergent situations to co-ordinate a response for activities, such as … firefighting" (para 7c, 7e).
11. **Cattle graze the impact areas.** "During summer months June - November up to 5,000 head of cattle may be found in the training area… Cattle are not required to be moved from impact areas" (170-171). This supports the top-ranked explanation in the v4 competing-hypotheses analysis for why the fire spread at about a sixth of the standard rate before the front: fine-scale fuel effects such as grazing and trampling.
12. **The records exist.** Daily Range Standing Orders are "printed and signed daily at Range Control" (para 11). The Unit Fire Prevention Officer must ensure "the local DND Fire Chief, who is responsible for fire investigation and reporting in accordance with CFAO 30-2, is advised immediately of any fire incident" (Annex P, para 5). Bookings and danger area overlays live in CFRIS (paras 12-16).

## Questions for DND

1. Was this 2024 edition in force on Oct. 17, 2026? If not, which edition was, and what changed?
2. Which range was C Company using on Oct. 17: Range 15, Range 2 or another?
3. What fire hazard condition was posted on Oct. 17?
4. Was Environment Canada's 2:14 p.m. wind warning distributed as a Forecast of Adverse Weather under para 214? To whom, and when?
5. Did Range Control order a check fire or cease-training on Oct. 17 under para 7?
6. Did the firing unit report the fire under para 343? Who directed the response under para 345, and was the fire ever declared "Out of Control"?
7. Were cattle grazing PDA 2 in 2026?

## Records to request

- Daily Range Standing Orders for Oct. 16-17, 2026.
- The DND Fire Chief's fire report(s) under CFAO 30-2 for Oct. 17, 2026.
- Fire hazard condition records (daily sign settings), Aug.-Oct. 2026.
- Every edition and amendment of the Wainwright Range Standing Orders since 2024.
- CFRIS bookings and danger area overlays for Ranges 2, 11 and 15 on Oct. 17, 2026.
- PDA 2 grazing schedule for 2026.
