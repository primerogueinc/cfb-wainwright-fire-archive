# Sentinel-2 packages

Raw Copernicus Browser exports for the CFB Wainwright fire area, one folder per date and processing level. Each folder holds `manifest.json` (every file's SHA-256, frame, pixel size, coverage of the origin, Range 2 point A and road head B, and a haze check) and small previews.

The raw files themselves live in a separate data repository, **[CFB Wainwright: full satellite data (Copernicus)](https://github.com/primerogueinc/CFB-Wainwright---Full-Satellite-Data---Copernicus-)**, under `sentinel-2/<date>/<level>_<format>/`, with the same manifests. This repo keeps only the manifests and previews, so it stays small.

Added with `scripts/ingest_copernicus.py`. "Usable" means the export covers all three points, at least 95% of the fire box has data, and the blue band shows no haze.

| Date | Level | Format | Files | Usable | Why | Source zip |
|---|---|---|---|---|---|---|
| 2026-10-04 | L1C | TIFF | 23 | Yes | ~10 m pixels, clear | `Browser_images__20_.zip` |
| 2026-10-16 | L1C | JPG | 23 | Preview only | JPG, not georeferenced | `3fc9ebf6-Browser_images_19.zip` |
| 2026-10-16 | L1C | TIFF | 23 | No | Haze or thin cloud over fire area | `Browser_images__21_.zip` |
| 2026-10-16 | L2A | TIFF | 23 | No | Haze or thin cloud over fire area | `Browser_images__18_.zip` |
| 2026-10-19 | L2A | TIFF | 23 | Yes | ~10 m pixels, clear | `Browser_images__17_.zip` |
| 2026-10-21 | L1C | TIFF | 17 | No | Fire area outside swath | `Browser_images__14__5114e1.zip` |
| 2026-10-21 | L2A | TIFF | 17 | No | Fire area outside swath | `Browser_images__16_.zip` |

The Oct. 19 L2A GeoTIFFs were briefly committed under `manual_exports/2026-10-19/L2A_10m/` (commit 47ec973) and then moved to the data repository; the analysis images and notes stay there. Older exports from the first analysis remain under `manual_exports/`.

Contains modified Copernicus Sentinel data [2026].
