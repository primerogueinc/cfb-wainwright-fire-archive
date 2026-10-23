# Sentinel-1 radar change, Oct. 14 (before) to Oct. 19 (after)

Made with `scripts/sentinel1/change_oct14_oct19.py` from the raw exports in the [Sentinel-1 repository](https://github.com/primerogueinc/CFB-Wainwright-Fire-Sentinel-1). Both passes resampled onto the 10 m grid of the matched Sentinel-2 severity map; 3×3 mean filter before the ratio to reduce speckle. `s1_vv_change_db_oct14_oct19.tif` and `s1_vh_change_db_oct14_oct19.tif` hold the change in dB; `summary.json` the figures below.

**The burn shows in radar.** Burned ground (by the Sentinel-2 map) darkened by a median 4.4 dB in VV and 3.2 dB in VH. Unburned ground darkened too, by 2.4 dB and 1.3 dB, so the burn's own signal is about 2 dB in each channel on top of a scene-wide drop.

**Why everything darkened.** The two passes are five days apart, which on Sentinel-1's 6- and 12-day cycles means they were most likely taken from different orbit tracks, at different viewing angles. Drying of the surface may also contribute. A pre-fire pass on the same track as Oct. 19 (most likely Oct. 7) would remove most of this.

**Limits.** With the geometry mismatch and radar speckle, single points are not reliable: values at Range 2 point A (VV −0.9, VH −3.2 dB) and road head B (VV −1.0, VH −4.9 dB) disagree between channels. Radar here confirms the burn at the scale of hundreds of metres; it cannot settle what the unburned strip between A and B is. Acquisition times and orbit directions were not recorded in the exports.

Contains modified Copernicus Sentinel data [2026].
