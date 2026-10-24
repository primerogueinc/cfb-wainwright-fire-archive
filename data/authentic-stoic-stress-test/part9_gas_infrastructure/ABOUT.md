# Part 9: Did gas infrastructure play a part? (working model v2.1)

Tests the public claims that a live-fire round struck a gas line or well, causing an explosion (early Global News report citing military sources, Oct. 17; social posts flagged by the Canadian Press fact check), against everything in the archive, with the fire starting in Range 11's impact area (parts 8 and 8b).

Scripts: `scripts/authentic_stoic_alternative_hypothesis/part9/`. Run from this folder; `maps.py` needs a clone of the [Copernicus data repository](https://github.com/primerogueinc/CFB-Wainwright---Full-Satellite-Data---Copernicus-) (set `COPERNICUS_REPO`). Atmospheric data: [Sentinel-5P repository](https://github.com/primerogueinc/CFB-Wainwright-Sentinel-5P-Archives).

## Findings

| Test | Result | Bears on |
|---|---|---|
| Gas infrastructure in Range 11's firing sector (`sector_test.py`, `sector_test.json`) | No AER-licensed line or well within 2.5 km on any bearing 20°–160°. Nearest operating gas lines are 350–560 m west and south-west, behind or beside the firing point. Range 2 lines and well: 3.5–4.0 km, beyond the C16's ~2.2 km maximum range. | A round from Range 11 striking gas infrastructure |
| Distance from start to gas (`pipelines_vs_fire.py`, `map3`) | Modelled start ~1.4 km, fire at 12:17 p.m. ~0.9 km from the nearest operating gas line. | Gas strike as the cause |
| When the fire reached the lines (parts 8, 8b) | ~3:24–3:26 p.m., after the 3:16 p.m. wind shift. | Any release came after the fire, not before |
| GOES-18 fire power (`goes_figs.py`, `fig4`–`fig6`) | 76.5 MW at 3:10 p.m., 1,215 MW over three pixels at 3:30, 336 MW at 3:40, none after; clear skies from ~7:30 p.m. with no hot spot. Heat spread along the front, not centred on the lines. | Sustained gas fire; rupture signature |
| Burn severity at the lines (`severity_at_lines.py`, `fig7`) | Within 30 m of line 58333-78 median dNBR 0.04, 2% moderate or higher (16–20% at 100–300 m); line 58333-113 0.01. Well 1-11's registered site unburned (−0.05), nothing burned within 100 m. No circular high-severity spot. The burn's north edge follows line 58333-78. | Jet fire at a break |
| Sentinel-5P, Oct. 17, 2:34 p.m. pass | Carbon monoxide and methane masked by cloud over the base; aerosol index no different from Oct. 16. Pass came ~50 minutes before the fire reached the lines. | Not diagnostic |
| Sentinel-5P, Oct. 18, 2:15 p.m. | Methane: good coverage, no enhancement at or downwind of the base. Carbon monoxide at background. | Large leak still venting next day |
| Regulator's record | AER suspension order to Sumerian Oil & Gas (Oct. 5, amended Oct. 9) lists well 1-11 as active; Orphan Well Association given 14 days to shut in. Reported: no wells closed before the fire. AER: no incident reports; not engaged in any response. | Lines probably live on Oct. 17 |

## What this supports

- **Strong:** no gas line or well within reach of Range 11's firing sector; the fire started ~1.4 km from the nearest gas line and burned for hours before reaching any.
- **Strong:** no sustained gas fire (no night hot spot, no scorch circle, well site unburned) and no large leak the next day.
- **Weak:** a brief release (seconds to minutes) as the fire crossed the lines around 3:25 p.m. cannot be excluded by any of these satellites: it would sit inside one GOES scan, below Sentinel-2's 20 m resolution and after the Sentinel-5P pass.

## Correction

Earlier work placed "the wellsite" at the mapped west end of line 58333-78 (~170 m from the Range 2 point). The AER's registered surface location for well 1-11 is ~410 m east-north-east of that point, ~360 m north of the road head and outside the burn. Positions are mapped, not surveyed; both are shown in `map2` and `fig7`.

## Limits

Pipeline and well positions are mapped, not surveyed. Range 11's firing sector is inferred (east into Permanent Danger Area 2). Sentinel-2 severity is at 20 m. Sentinel-5P cannot detect brief or clean-burning releases. The rupture estimate in `fig6` is order-of-magnitude, not site-specific. Some regulatory facts are from news reports, not primary records.
