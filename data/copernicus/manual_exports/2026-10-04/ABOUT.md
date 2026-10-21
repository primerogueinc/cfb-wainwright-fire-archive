# Sentinel-2 manual exports, Oct. 4, 2026 (pre-fire baseline)

Exported by hand from the Copernicus Browser (Copernicus Data Space Ecosystem) during the first analysis of the fire, Oct. 19–20, 2026. This is the clear pre-fire scene also used by the automated burn-scar analysis (`data/copernicus/`, scene `S2C_12UWD_20261004_0_L2A`).

| Files | What they are |
|---|---|
| `…_L2A_B02/B03/B04/B08/B8A/B12_(Raw).tiff` | Level-2A surface reflectance, single bands, float32 GeoTIFF, EPSG:4326, 2500 × 1717 px covering 52.570–52.880°N, 110.597–111.343°W (~20 m by ~20 m pixels). |
| `…_L2A_True_color.tiff` | Level-2A true-colour composite, same grid. |
| `L1C_Browser/*.jpg` | Level-1C browser visualizations (individual bands and standard composites: false colour, SWIR, NDVI, NDWI, NDSI, moisture index, wildfire). For viewing only; not georeferenced. |
| `tc_crop.jpg`, `nbr_crop.jpg` | Crops made for the first published graphics: true colour and Normalized Burn Ratio. |

File names are as exported. Contains modified Copernicus Sentinel data [2026]. Free to reuse with that credit.
