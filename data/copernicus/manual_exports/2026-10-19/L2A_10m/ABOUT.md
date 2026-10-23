# Sentinel-2 L2A, Oct. 19, 2026, full-resolution export (received Oct. 22)

The GeoTIFFs themselves now live in the [full Copernicus data repository](https://github.com/primerogueinc/CFB-Wainwright---Full-Satellite-Data---Copernicus-/tree/main/sentinel-2/2026-10-19/L2A_tiff) (see `data/copernicus/packages/2026-10-19/L2A_tiff/manifest.json`). All 13 bands plus scene classification and index layers, float32 GeoTIFF, EPSG:4326, about 10 m pixels (0.000146° × 0.0000883°), covering 52.686-52.841°N, 110.660-111.024°W. Unlike the earlier `L2A_blank/` export, this one has data: the browser now holds the Level-2A product for Oct. 19. Full coverage of the burn area.

`oct19_10m_panel.jpg`: true colour, SWIR false colour and burn severity (dNBR, Oct. 4 L2A export resampled to this grid, B8A/B12) around the origin, Range 2 point A (12U WD 0632 4700) and road head B (12U WD 0677 4674). `ab_zoom.jpg`: true-colour close-up of A to B.

Note: B8A and B12 are 20 m bands, so dNBR on this grid is 20 m information resampled, not 10 m severity. B02/B03/B04/B08 are native 10 m.

First reading (Oct. 22):
- A and B both sit 10-20 m from pixels classed burned (dNBR ≥ 0.27); dNBR at A 0.18 (5×5 mean 0.24), at B 0.23. Low-severity values at the points themselves.
- A pale, apparently unburned tongue of ground runs from A east-southeast to the range road just north of B, bounded on the north by a curved track. Bright, highly reflective spots sit at A's western tip and about 70 m southeast of B: bare ground, gravel or structures; not identifiable at 10 m.
- North of the east-west track at B, east of the range road, the ground is largely unburned; south of it the burn crosses east of the road.
- Burn area in the 0.11° × 0.06° box at dNBR ≥ 0.27: about 13.2 km² (includes older burns south of Jamieson Lake).

Interpretation pending a sub-metre pre-fire image of A-B (Esri Wayback / Google Earth). Contains modified Copernicus Sentinel data [2026].
