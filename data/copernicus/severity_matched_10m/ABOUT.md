# Burn severity at 10 m from matched exports (Oct. 4 vs Oct. 19, both Sentinel-2 L2A)

Made with `scripts/copernicus/severity_matched.py` from the full exports in the [Copernicus data repository](https://github.com/primerogueinc/CFB-Wainwright---Full-Satellite-Data---Copernicus-) (`sentinel-2/2026-10-04/L2A_tiff`, `sentinel-2/2026-10-19/L2A_tiff`). Both scenes resampled onto one 10 m UTM 12N grid over 52.74-52.80°N, 110.85-110.96°W.

- `dnbr_10m_oct04_oct19.tif`: dNBR (B8A/B12, 20 m native bands, bilinear to 10 m), **seasonal offset of 0.151 subtracted**. Grass cured between the two dates, so unburned ground drifted positive; the offset is the median dNBR of the north-east third of the box, unburned in every source (standard practice, Key & Benson).
- `dndvi_10m_oct04_oct19.tif`: change in NDVI from the native 10 m bands B04/B08. No offset.
- `severity_matched_summary.json`: class areas and values at the origin, Range 2 point A and road head B.
- `ab_severity_10m.jpg`: close-up of A to B.

## What it shows

- **A and B read as unburned at their own pixels**: offset dNBR 0.055 at A and 0.045 at B. Burned ground (≥ 0.27) lies 28 m from A and 22 m from B.
- **A tongue of unburned ground runs from A east-southeast to the range road at B.** Its southern edge is a sharp line: the burn runs right along it. North of the tongue, a lightly burned band; south, the main burn, with patches of moderate-high severity.
- **B sits at the corner** where the burn edge meets the range road and turns east along the east-west track.
- The origin reads 0.32 (moderate-low), typical of a grass fire.

## Limits

- Grass fires produce low dNBR; severity classes from forest studies understate grass burns. Area at ≥ 0.27 (7.8 km²) is therefore **not** a replacement for the 10.8 km² burn measured in the first analysis; "low" pixels (0.10-0.27) are largely burned grass too.
- B8A and B12 are 20 m bands; edges on this grid are good to about one 20 m pixel. Values at a single point mix in neighbouring ground.
- What the unburned tongue is (cleared ground, gravel, a firebreak, mown range, or ground disturbed after the fire) cannot be told from 10-20 m data. A sub-metre pre-fire image is needed.

Contains modified Copernicus Sentinel data [2026].
