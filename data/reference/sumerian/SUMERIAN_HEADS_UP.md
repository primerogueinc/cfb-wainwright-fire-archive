# Sumerian Oil & Gas wells and pipelines near the Oct. 17 fire

Prime Rogue Inc., Nov. 2, 2026. This is a public data note. It is built from public regulator records and our own mapping, and it makes no claim that any well or pipeline played a part in the fire. The AER told Bloomberg it had received no reports of incidents involving oil and gas infrastructure.

## What the public records say

- **Oct. 5, 2026.** The AER issued a suspension order to Sumerian Oil & Gas Inc. It cited missed site-care orders (April and September), two releases (Environmental Protection Orders, August and September), and an unpaid closure-quota security deposit (July). The AER authorized the Orphan Well Association (OWA) to suspend the wells and facilities. Within **14 calendar days**, the OWA had to ensure the listed wells, facilities and pipelines were "shut-in, secured, discontinued and rendered safe." That window ran to about **Oct. 19**. The fire was **Oct. 17**.
- **Oct. 9, 2026.** An amendment replaced the order's appendix, which the AER said was "inadvertently incomplete." The new appendix lists all of Sumerian's well, pipeline and facility licences. It includes ten licences in township 044-06W4 that sit inside our 12 km area (0070022, 0192613, 0215570, 0216226, 0275007, 0275273, 0294052, 0294542, 0294699, 0295292). Townships 044-07W4 and 045-07W4 should also be checked against the full appendix.
- **Oct. 14.** The AER announced the order publicly.
- **Oct. 19 to 22.** Bloomberg and Canada's National Observer reported that the wells on the base had been ordered closed before the fire.
  - Bloomberg counted about 260 licensed well sites inside the base, about two-thirds of them Sumerian's.
  - Sumerian told Bloomberg that an OWA contact said no Sumerian wells there had been closed, and that the OWA did not plan to visit until **Oct. 27**. If that is right, the shut-in had not happened by the day of the fire.
- **Aug. 18, 2026.** An earlier Environmental Protection Order, made at Wainwright, concerned a crude oil release at Sumerian facility F2927 (15-35-021-07W4). That site is not near the fire.

## Licence history: Cleo becomes Sumerian

The AER's Abandoned Well Map (January 2025) lists **55** of these wells under **Cleo Energy Corp.** The October 2026 ST37 well list has the same wells, at the same positions, under **Sumerian Oil & Gas Inc.**

Cleo's public record:
- **Dec. 8, 2024.** Cleo filed a notice of intention to make a proposal.
- **June 3, 2025.** Cleo went into receivership, with Alvarez & Marsal as receiver.
- **Oct. 6, 2025.** The receiver's First Report lists "Greater Wainwright" among the remaining assets. It says the receiver was in contact with the Department of National Defence about "certain assets and wells located at the CFB Wainwright military base." It describes a proposed reverse-vesting sale to 2698902 Alberta Corp.
- **Oct. 31, 2025.** Global Restructuring Review reported that the court refused that reverse-vesting order.
- **Nov. 14, 2025.** The receiver's court page lists a later "Transaction Approval and RVO" order.
- **Dec. 18, 2025.** The page also lists an "Order (Department of Justice)."

We have **not** confirmed how the licences passed from Cleo to Sumerian. It could have been a transfer or a renamed company after a reverse-vesting sale.

## What our mapping shows (12 km around the site)

- **Wells.** 418 licensed wells are within 12 km, and **152 (36%) are Sumerian's**:
  - 61 issued, 26 suspended, 7 amended, 52 abandoned, 3 reclamation-certified, 3 cancelled;
  - 12 are classed as single wells with some H2S (under 0.01 m3/s release rate); 32 are classed as sweet (0.00 mol/kmol H2S).
- **Pipelines.** Every pipeline segment Sumerian holds in our area carries natural gas: about **363 km operating**, out of 525 km in total.
- **Nearest well to Range 15.** It is Sumerian's: **licence 0223643**, issued (not abandoned), about **370 m** from Range 15 and about **95 m** outside the burn outline.
- **Next nearest.** Sumerian **0271510** is issued and classed as a single well with H2S below 0.01 m3/s release rate. It is about **630 m** from Range 15 and about 290 m outside the burn.
- **Wells inside the burn.** No Sumerian well is inside the burn outline. Six are within 500 m of it, nine within 1 km and 18 within 2 km.
- **Pipeline inside the burn.** The only pipeline segment that crosses the burn is Sumerian's: licence 58333 line 78, a 114.3 mm natural-gas line, operating, with a maximum operating pressure of 4,140 kPa.
  - About 50 m of it lies inside the outline.
  - It passes about **170 m** from Range 15.
  - Line 113 (88.9 mm, operating) passes at a similar distance.
- **What the satellite images show.** The before-and-after Sentinel-2 images (Oct. 4 and Oct. 19) show no visible change at well pads outside the burn. They can't show whether a well was shut in. Cloud covers the eastern part of the Oct. 19 scene.

## Suggested questions

1. **To the OWA.** Which Sumerian wells, pipelines and facilities on CFB Wainwright had been shut in, isolated or depressurized by Oct. 17? When was its first site visit?
2. **To the AER.** Was line 58333-78 operating and pressured on Oct. 17? Were wells 0223643 and 0271510 producing or shut in? Has the AER or OWA inspected the burned area since?
3. **To DND.** Was range control told about the Oct. 5 order and the 14-day shut-in window? Did it change any range clearances or safety distances?
4. **To Sumerian.** Who had operational control of the wells and lines on Oct. 17? Has it received an answer to its letter to the AER?
5. **To the receiver or the court record.** How did Cleo's Wainwright licences pass to Sumerian, and what did DND say about the base wells during the receivership?

## Files

- `wells_sumerian_before_oct04.png` and `wells_sumerian_after_oct19.png`: full-bleed 10 m maps of all wells and pipelines within 12 km, with Sumerian wells ringed and Sumerian lines in magenta.
- `wells_sumerian_before_after.jpg`: the same two maps side by side.
- `closeup_burn_r15_before_oct04.jpg`, `closeup_burn_r15_after_oct19.jpg`, `closeup_burn_r15_before_after.jpg`: 2x close-ups of the burn, Range 2 and Range 15 area, cropped from the full maps.
- `wells_12km_sumerian_flagged.csv`: every well within 12 km, with:
  - a Sumerian flag;
  - distances to the burn outline and to Ranges 15, 2 and 11;
  - the January 2025 Abandoned Well Map licensee and status;
  - membership in the Oct. 9 order extract.
- Script: `scripts/reference/wells_fullbleed_sumerian.py`. The old-vs-new comparison is in `../aer_abandoned_wells/map_st37_vs_abandoned.png` (`scripts/reference/abandoned_vs_st37_map.py`).

## Sources

- AER, Order amendment, Oct. 9, 2026: https://www1.aer.ca/compliancedashboard/enforcement/202610-001_Sumerian_Oil_Gas_Inc_Order_Amendment_1.pdf
- AER, Environmental Protection Order, Aug. 18, 2026: https://www1.aer.ca/compliancedashboard/enforcement/202608-010_Sumerian_Oil_Gas_Inc_Order.pdf
- AER, Order, July 20, 2026: https://www1.aer.ca/compliancedashboard/enforcement/202607-011_Sumerian_Oil_Gas_Inc_Order.pdf
- AER, Order, April 22, 2026: https://www1.aer.ca/compliancedashboard/enforcement/202604-010_Sumerian%20Oil%20&%20Gas%20Inc_Order.pdf
- BOE Report, Oct. 14, 2026: https://boereport.com/2026/10/14/alberta-energy-regulator-issues-suspension-order-to-sumerian-oil-gas-inc/
- Bloomberg, Oct. 19, 2026: https://www.bloomberg.com/news/articles/2026-10-19/alberta-regulator-seized-gas-wells-on-army-base-days-before-fire
- Canada's National Observer, Oct. 22, 2026: https://www.nationalobserver.com/2026/10/22/news/operational-gas-wells-cfb-wainwright-aer-owa-sumerian
- Alvarez & Marsal, Cleo Energy Corp. receivership, First Report and court orders: https://www.alvarezandmarsal.com/content/cleo-energy-corp-receivership-court-orders
- Global Restructuring Review, Oct. 31, 2025: https://globalrestructuringreview.com/article/alvarez-marsal-fails-secure-rvo-canadian-oil-and-gas-group
- Insolvency Insider, Cleo Energy NOI: https://insolvencyinsider.ca/p/cleo-energy-corp-noi
- AER ST37 well list (Oct. 1, 2026), AER Abandoned Well Map (Jan. 30, 2025) and AER pipelines: see `../aer_abandoned_wells/ABOUT.md`.
