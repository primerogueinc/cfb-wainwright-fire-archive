# CFB Wainwright Fire Archive (2026)

An open, timestamped archive of raw data and documents on the deadly fire at Canadian Forces Base Wainwright, Alberta, on **October 17, 2026**. Maintained by [Prime Rogue Inc.](https://primerogueinc.com) alongside its [live coverage](https://primerogueinc.com/blog/cfb-wainwright-fire-live-updates/).

The goal is a record anyone can check: every raw file is kept unaltered, hashed, and timestamped on the Bitcoin blockchain via [OpenTimestamps](https://opentimestamps.org), so readers can verify that a file existed in this form at a given time.

## What's here

| Path | Contents | Updated |
|---|---|---|
| `data/firms/raw/` | Unaltered NASA FIRMS API responses (VIIRS S-NPP / NOAA-20 / NOAA-21, MODIS, Landsat) for a box around the base. Never overwritten; a new file is added only when a response changes. | Automatically, every 3 hours |
| `data/firms/detections.csv` | All detections merged and de-duplicated, with UTC and local (MDT) times. | Automatically |
| `data/firms/detections.geojson` | The same detections as a map (GitHub renders it). | Automatically |
| `data/manifests/` | SHA-256 manifests of each batch of new raw files, plus `.ots` timestamp proofs. | Automatically |
| `atip/` | Records released under the *Access to Information Act* and Alberta's *Access to Information Act*. | Within 72 hours of receipt |
| `docs/` | Methods and verification notes. | As needed |
| `scripts/` | The code that does the collecting. | As needed |

Coming next: GOES-18/19 satellite loops of the Oct 17 smoke plume, the Oct 17 Landsat 8 scene, and Sentinel-2 burn-area analysis.

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
| Prime Rogue's own data, analysis and write-ups | [CC BY 4.0](LICENSE-DATA) — credit "Prime Rogue Inc." |
| NASA FIRMS data | NASA open data. Credit: "NASA FIRMS (LANCE)". |
| Copernicus Sentinel data and derivatives | Free, with credit: "Contains modified Copernicus Sentinel data [2026]". |
| USGS Landsat | Public domain. Credit: "USGS". |
| Government records in `atip/` | **No licence is granted by Prime Rogue.** Released under access-to-information law; reproduced for news reporting and public-interest purposes. Crown copyright may apply. |

Commercial imagery (Planet, Vantor/Maxar, Airbus) is never stored here because its licences forbid redistribution. Only Prime Rogue's own measurements derived from it may appear.

## Contributing

Please **do not** open issues or pull requests containing documents, tips or anything that identifies you — GitHub history is permanent and public. Send material through Signal (**Rubicon49.50**) or Proton email instead; see the archive page on primerogueinc.com. Contributors are credited or protected per their preference under the Canadian Association of Journalists' ethics guidelines.

Corrections to code or methods are welcome as issues.
