# Sentinel-3 OLCI exports, Oct. 4, 16, 17 and 18, 2026

Sentinel-3's OLCI instrument images the area daily at about 300 m resolution, much coarser than Sentinel-2 but more often. Exported by hand from the Copernicus Browser during the first analysis.

| Path | Contents |
|---|---|
| `461672e1-Browser_images_11/` | Oct. 4 (clear, pre-fire): bands B01–B04, B08, B10, B12 and true colour as GeoTIFF. |
| `07ee7e4a-Browser_images_10/` | Oct. 16: same, cloud-covered. |
| `f599aa34-Browser_images_9/` | Oct. 17: same, cloud-covered over the site (Sentinel-3 passes in the late morning, before the fire's afternoon run). |
| `9f3cd561-Browser_images_8/` | **Oct. 18 (mostly clear, post-fire):** bands B01–B10, B12 and true colour. |
| `s3.py` | Regrids each date's true colour and bands 8 and 12 onto a common lat/lon grid (52.68–52.86°N, 110.72–111.10°W, 120 × 160 cells; `grid.npy` holds the grid). |
| `s3_panel.jpg` | Four-date true-colour panel. |
| `ratio.npy`, `ratio_map.jpg`, `dndvi.npy`, `patch_0.8.npy`, `patch_0.85.npy` | Intermediate arrays from the first burn test: an Oct. 18 / Oct. 4 band ratio, NDVI change, and burned-patch masks at ratio thresholds 0.80 and 0.85. |

**Why it matters:** the Oct. 18 image is the **earliest clear post-fire satellite view** in the archive, a day before the Sentinel-2 scene used for the burn-scar measurement. The dark burn north and east of Jamieson Lake is already visible on Oct. 18, at the same place and in the same shape the Sentinel-2 analysis later measured in detail.

`s3.py` writes a `s3grid.pkl` that is not included; rerun the script to regenerate it. Contains modified Copernicus Sentinel data [2026].
