# Sentinel-2 exports, Oct. 19, 2026 (first post-fire Sentinel-2 pass)

| Path | Contents |
|---|---|
| `L1C/` | **Level-1C (top-of-atmosphere) bands B01, B02, B03, B04, B08, B8A, B12** as float32 GeoTIFF, EPSG:4326, 2500 × 1743 px, covering 52.374–52.988°N, 109.948–111.401°W (a wider frame than the Oct. 4 exports). Plus `…_L1C_True_color.tiff`, which is **truncated**: the export stopped partway, and the file cannot be read past about row 1,088 (the same in both copies uploaded). The single bands are complete. |
| `L2A_blank/` | Level-2A bands and true colour for the same date. **Every value is 0:** the browser had no Level-2A product for Oct. 19 when this was exported. The automated analysis later used the Level-2A scene `S2B_12UWD_20261019_0_L2A` from the public archive (`data/copernicus/`). |
| `preview_swir_crop_B12-B8A-B04.jpg` | Prime Rogue preview made from the L1C bands (SWIR false colour, 52.70–52.82°N, 110.80–111.05°W). Fresh burn shows red. |

**What it shows.** In the SWIR false colour, a large fresh burn covers the ground north and east of Jamieson Lake, with straight edges along roads and fireguards, and reaches the base's eastern boundary road and beyond it. That matches the burn measured from the Level-2A scene (about 10.8 km² for the main run). Older burns south and southwest of the lake, already visible on Oct. 4, also show.

**Probative value: high.** These are the first post-fire Sentinel-2 data, as exported during the first analysis. L1C values are top-of-atmosphere reflectance (no atmospheric correction), so they are not directly comparable number-for-number with the Level-2A Oct. 4 bands; the shapes and locations are.

Two identical uploads of the L1C set were received; one copy is kept. Contains modified Copernicus Sentinel data [2026].
