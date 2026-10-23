# Sentinel-2 packages

Raw Copernicus Browser exports for the CFB Wainwright fire area, one folder per date and processing level. Each folder holds `manifest.json` (every file's SHA-256, frame, pixel size, coverage of the origin, Range 2 point A and road head B, and a haze check) and small previews.

The raw export zips are attached unchanged to the GitHub release **`copernicus-s2-packages`**, so the repo stays small. To verify a download, unzip it and compare each file's SHA-256 with the manifest.

Added with `scripts/ingest_copernicus.py`. "Usable" means the export covers all three points, at least 95% of the fire box has data, and the blue band shows no haze.

| Date | Level | Format | Files | Usable | Why | Release asset |
|---|---|---|---|---|---|---|
| 2026-10-16 | L1C | JPG | 23 | Preview only | JPG, not georeferenced | `3fc9ebf6-Browser_images_19.zip` |
| 2026-10-16 | L2A | TIFF | 23 | No | Haze or thin cloud over fire area | `Browser_images__18_.zip` |
| 2026-10-19 | L2A | TIFF | 23 | Yes | ~10 m pixels, clear | `Browser_images__17_.zip` |
| 2026-10-21 | L1C | TIFF | 17 | No | Fire area outside swath | `Browser_images__14__5114e1.zip` |
| 2026-10-21 | L2A | TIFF | 17 | No | Fire area outside swath | `Browser_images__16_.zip` |

The Oct. 19 L2A GeoTIFFs were briefly committed under `manual_exports/2026-10-19/L2A_10m/` (commit 47ec973) and then moved to the release; the analysis images and notes stay there. Older exports from the first analysis remain under `manual_exports/`.

Contains modified Copernicus Sentinel data [2026].
