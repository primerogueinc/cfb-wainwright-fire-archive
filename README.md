# CFB Wainwright Fire Archive (2026)

An open, timestamped archive of raw data and documents on the deadly fire at Canadian Forces Base Wainwright, Alberta, on **October 17, 2026**. Maintained by [Prime Rogue Inc.](https://primerogueinc.com) alongside its [live coverage](https://primerogueinc.com/blog/cfb-wainwright-fire-live-updates/).

The goal is a record anyone can check: every raw file is kept unaltered, hashed, and timestamped on the Bitcoin blockchain via [OpenTimestamps](https://opentimestamps.org), so readers can verify that a file existed in this form at a given time.

## What's here

| Path | Contents | Updated |
|---|---|---|
| `data/firms/raw/` | Unaltered NASA FIRMS API responses (VIIRS S-NPP / NOAA-20 / NOAA-21, MODIS, Landsat) for a box around the base. Never overwritten; a new file is added only when a response changes. | Automatically, every 3 hours |
| `data/firms/detections.csv` | All detections merged and de-duplicated, with UTC and local (MDT) times. | Automatically |
| `data/firms/detections.geojson` | The same detections as a map (GitHub renders it). | Automatically |
| `data/firms/manual_downloads_v2/` | Prime Rogue's first evidence package: hand-downloaded FIRMS KMZ/KML files from Oct. 17–18, preserved byte-for-byte with their original README and checksums. | Fixed (archival) |
| `data/firms/history_2012-2026/` | Every FIRMS detection around the site since 2012 (raw API responses, logs, merged table, yearly summary): fire on this part of the range is routine, including in October. | Fixed (archival) |
| `data/goes/` | GOES-18/19 loops of Oct 17 (11 a.m.–7 p.m. MDT): red visible, true colour, Fire Temperature RGB, Dust RGB (MP4 + GIF), key stills, and `fire_timeline.csv/.png` (cloud cover, 3.9 µm heat and NOAA fire power over the base every 10 minutes). | On demand |
| `data/goes/early_subsets_goes18/` | First GOES-18 analysis (Oct. 18–19): band subsets, extraction/render code, and the early published frames and loop. | Fixed (archival) |
| `data/noaa_hms/` | NOAA Hazard Mapping System fire points and smoke outlines, Oct. 13–18 (originals), with a summary of points near the base and a smoke-coverage check. | Fixed (archival) |
| `data/eccc/` | Environment Canada forecasts, warnings and hourly station observations (CFB Wainwright, Lloydminster), Oct. 16–18, from the MSC Datamart (originals), with parsed tables. | Fixed (archival) |
| `data/nrcan_cwfis/` | NRCan fire-weather station files, Oct. 10–18 (originals), Alberta fire-danger classes, and an extract for stations near the base: Oct. 17 FWI 30.8 at CFB Wainwright, "Extreme". | Fixed (archival) |
| `data/copernicus/` | Burn scar from Copernicus Sentinel-2 (dNBR, before/after), with NASA FIRMS and NOAA GOES detections overlaid: `burn_scar_map.png`, `before_after.png`, `burn_scar.geojson`, `fire_progression.geojson` (opens as a map on GitHub), `dnbr.tif`, `summary.json`. | Automatically, daily (when a clearer scene appears) |
| `data/copernicus/manual_exports/` | Sentinel-2 scenes exported by hand from the Copernicus Browser during the first analysis (bands as GeoTIFF, browser views), by date. | Fixed (archival) |
| `data/reference/` | Reference data re-fetched from public sources: Environment Canada hourly records for the stations used to time the cold front, official place names, CanVec roads/wells/pipelines/buildings and AER pipelines around the base. | Fixed (archival) |
| `data/derived_tables_oct19-20/` | Working tables from the first analysis, including Prime Rogue's hour-by-hour fire-weather calculation for Oct. 17 (FWI 53.6 at 2 p.m., 59.4 at 3 p.m., 91.4 at 4 p.m.). | Fixed (archival) |
| `data/graphics_published/` | Every graphic Prime Rogue published on the fire, Oct. 17–20, kept as published (dated snapshots). | Fixed (archival) |
| `data/adsb/` | ADS-B positions of every aircraft heard near the base on Oct. 17–18 (adsb.lol open archive, ODbL), with the original trace files, to find where aircraft landed near the fire. | On demand |
| `data/location_analysis/` | Prime Rogue's estimate of where C Company was, the competing-hypotheses analysis, fire-behaviour model runs and the stress test (Oct. 21). | Fixed (archival) |
| `data/terrain3d/` | 3D terrain reconstruction (work in progress): true-scale views and sightlines from Range 13, Range 2, the roadhead and the garrison; a test orbit; the animated fire draft; the modelled arrival-time layer. Code in `scripts/terrain3d/`. | As drafts are made |
| `data/manifests/` | SHA-256 manifests of each batch of new raw files, plus `.ots` timestamp proofs. | Automatically |
| `atip/` | Records released under the *Access to Information Act* and Alberta's *Access to Information Act*. | Within 72 hours of receipt |
| `docs/` | Methods and verification notes. | As needed |
| `scripts/` | The code that does the collecting. `scripts/first_analysis/` holds the original code behind the first published graphics. | As needed |

Coming next: the Oct 17 Landsat 8 scene.

## Times

Alberta was on Mountain Daylight Time (UTC−6) on Oct 17, 2026. Satellite data is in UTC. 12:17 p.m. MDT = 18:17 UTC; 4:00 p.m. MDT = 22:00 UTC.

## Verifying a file

```bash
pip install opentimestamps-client
sha256sum -c data/manifests/firms_<timestamp>.sha256   # files match the manifest
ots verify data/manifests/firms_<timestamp>.sha256.ots  # manifest existed at the attested time
```

Proofs are complete a few hours after stamping, once they are anchored in a Bitcoin block. See [`docs/METHODS.md`](docs/METHODS.md).

## Licences

| Material | Licence |
|---|---|
| Code (`scripts/`, `.github/`) | [MIT](LICENSE) |
| Prime Rogue's own data, analysis and write-ups | [CC BY-NC 4.0](LICENSE-DATA) — credit "Prime Rogue Inc." Commercial use (including commercial media) needs written permission. |
| NASA FIRMS data | NASA open data. Credit: "NASA FIRMS (LANCE)". |
| NOAA GOES and HMS data | Public domain (U.S. government). Credit: "NOAA". |
| Copernicus Sentinel data and derivatives | Free, with credit: "Contains modified Copernicus Sentinel data [2026]". |
| USGS Landsat | Public domain. Credit: "USGS". |
| Environment Canada and NRCan data | Open Government Licence – Canada. Credit: "Environment and Climate Change Canada" / "Natural Resources Canada". |
| Government records in `atip/` | **No licence is granted by Prime Rogue.** Released under access-to-information law; reproduced for news reporting and public-interest purposes. Crown copyright may apply. |

Prime Rogue's material was CC BY 4.0 until October 21, 2026; copies obtained before then keep that licence (see [`LICENSE-DATA`](LICENSE-DATA)).

Commercial imagery (Planet, Vantor/Maxar, Airbus) is never stored here because its licences forbid redistribution. Only Prime Rogue's own measurements derived from it may appear.

## Contributing

Please **do not** open issues or pull requests containing documents, tips or anything that identifies you — GitHub history is permanent and public. Send material through Signal (**Rubicon49.50**) or Proton email instead; see the archive page on primerogueinc.com. Contributors are credited or protected per their preference under the Canadian Association of Journalists' ethics guidelines.

Corrections to code or methods are welcome as issues.
