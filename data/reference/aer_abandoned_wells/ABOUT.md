# AER abandoned wells: two datasets supplied by Kevin Duska (Nov. 2, 2026)

## What these are

| File | What it is | Date |
|---|---|---|
| `original/ABNDWells_SHP.zip` | The Alberta Energy Regulator's **Abandoned Well Map**: every abandoned or reclamation-certified/exempt well in Alberta, 238,158 wells, with licence, licensee, status, fluid and surface legal location. Supplied in two projections. | Shapefile written Jan. 30, 2025 |
| `original/Revised_Abandoned_Well_Locations_Shapefile.zip` | The AER's **Revised Abandoned Well Locations**: abandoned wells whose post-abandonment location, reported under Directive 079, differs from the location originally reported under Directive 056. 147 wells province-wide. | Data Oct. 2, 2026 (metadata Mar. 4, 2024) |
| `abandoned_wells_near_site.geojson` / `.csv` | Clip of the Abandoned Well Map to 52.60–52.95° N, 111.20–110.60° W: 1,116 wells. Positions are from the shapefile geometry. | – |
| `abandoned_wells_12km_vs_st37_input.csv` | The 186 abandoned-map wells within 12 km of the Oct. 17 detection centroid, used for the comparison below. | – |

## Is it the right data for the wells?

**Yes. It's the same AER well data the models already use. But it covers only abandoned and reclaimed wells, and it's older.** The models use the AER's ST37 well list (Oct. 1, 2026): `data/derived_tables_oct19-20/cfb-wainwright-aer-wells-12km.csv` and `data/infrastructure/wells_within_5km_of_scar.csv`.

**Positions are identical.** All 185 wells that appear in both datasets within 12 km of the site sit at exactly the same coordinates (0 m difference).

**Coverage is a subset.** Within 12 km, the ST37 list has 418 wells of every status. The abandoned map has 186, of which 185 are also in ST37; the extra one is a reclaimed-exempt well right on the 12 km line. The abandoned map doesn't include the 114 issued (active), 48 suspended or 25 amended licences that ST37 lists.

**It's out of date in places.**
- 11 wells it lists as "Abandoned" have since been reclamation-certified (ST37 dates March 2025 to January 2026).
- 19 wells that ST37 lists as abandoned are missing from it, because they were abandoned after January 2025. Among them are Sequoia Resources wells abandoned Jan. 16, 2026, including a multiwell pad on the burn.

**No revised locations near the base.** None of the 147 revised abandoned-well locations falls within the area, so no abandoned well near the fire has a corrected post-abandonment position. Our positions stand.

**Data quirk.** The shapefile's Lat and Long attribute columns are truncated to whole degrees (53.0, −111.0) because of a DBF field-width problem. Use the geometry, not those columns. The clip here does.

## What it changes in our work

Nothing. It confirms the earlier tests with an independent copy of the abandoned-well layer:

- No abandoned well lies within 700 m downrange of Range 10, 11, 13 or 22. The nearest are 512 m from Range 13, 644 m from Range 10, about 1.4 km from Range 11 and about 1.6 km from Range 22, none in the firing sector.
- The only abandoned well inside the Oct. 17 burn is Obsidian Energy licence 0224104, reclamation-certified (2010 in ST37), with no surface equipment.
- The nearest abandoned gas well to the road head is Cleo Energy licence 0216226, about 1.85 km away.

On the "buried wellhead" idea: abandoned wells are cut and capped below ground (Directive 020). They are buried, but not normally pressurized. Gas migration from such wells is a known, slow-leak issue (Directive 079). It is not a source of a blast.

## Licence and terms

AER data. The Abandoned Well Map metadata says: purchasers may use the files for internal or client use and may release small portions; copying a complete file or a large portion for resale is not permitted. The originals are kept here unchanged, as supplied, for provenance only; this archive is non-commercial (CC BY-NC 4.0 for Prime Rogue's work).

Credit: Alberta Energy Regulator. Clip and comparison: Prime Rogue Inc.
