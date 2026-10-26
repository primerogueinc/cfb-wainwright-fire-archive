# Sentinel-3 SLSTR fire radiative power (SL_2_FRP___), Oct. 16-18, 2026

Source: Copernicus Data Space Ecosystem (non-time-critical "NT" products). Files: `FRP_in.nc` (1 km MWIR), `FRP_an.nc` / `FRP_bn.nc` (500 m SWIR), plus each product's manifest. Script: `scripts/rubicon_ridge/sentinel3_frp_download.py`.

All six passes imaged the fire area (nearest swath pixel within 0.7 km of the fire centre, 52.7645 N, -110.9052 W). Detections within 60 km of the fire:

| Pass (MDT) | Pass (UTC) | Satellite | Fire detections within 60 km |
|---|---|---|---|
| Oct. 16, 10:23 p.m. | Oct. 17 04:23 | S3A | none |
| Oct. 16, 11:22 p.m. | Oct. 17 05:22 | S3B | none |
| Oct. 17, 11:30 a.m. | Oct. 17 17:30 | S3B | none |
| Oct. 17, 12:09 p.m. | Oct. 17 18:09 | S3A | none |
| Oct. 17, 10:56 p.m. | Oct. 18 04:56 | S3B | 1: SWIR (500 m) pixel at 52.7539, -110.9233, FRP 0.65 MW, at the south-west edge of the burn (pixel centre 0.57 km outside the mapped scar; within one pixel of it) |
| Oct. 17, 11:35 p.m. | Oct. 18 05:35 | S3A | none |

Reading:
- No overnight fire on Oct. 16-17 was detected by Sentinel-3 (two night passes), consistent with VIIRS and MODIS (FIRMS).
- The 12:09 p.m. pass did not detect the fire that Landsat imaged eight minutes later (12:17 p.m., 59 hot 30 m pixels). A low-intensity grass fire line can stay below SLSTR's 1 km daytime detection threshold; this is consistent with the fire being small and slow before the front, not evidence that it was out.
- The only detection is a small (0.65 MW) residual hot spot about 7 hours after the run, at the burn's edge.
