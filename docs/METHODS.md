# Methods

## NASA FIRMS archive

**What it is.** FIRMS (Fire Information for Resource Management System) publishes thermal anomalies ("hotspots") detected by satellites as they pass overhead. A detection means a pixel was unusually hot at that moment. It does not give ignition time, fire size, or cause, and pixels are coarse: about 375 m for VIIRS, 1 km for MODIS, 30 m for Landsat.

**Area.** Bounding box west −111.6, south 52.4, east −110.2, north 53.2 (WGS84), covering CFB Wainwright, the training area, the Town of Wainwright and surrounding land.

**Window.** From 2026-10-01 to the present, so the record shows what was burning on the range before Oct 17.

**Sources.** `VIIRS_SNPP_NRT`, `VIIRS_SNPP_SP`, `VIIRS_NOAA20_NRT`, `VIIRS_NOAA20_SP`, `VIIRS_NOAA21_NRT`, `MODIS_NRT`, `MODIS_SP`, `LANDSAT_NRT`. NRT = near real-time; SP = standard processing, released weeks to months later and generally more accurate. Both are kept.

Suomi NPP data delivery is scheduled to end on Nov 1, 2026 (NOAA NESDIS announcement, date subject to change); NOAA-20 and NOAA-21 continue.

**Process.** `scripts/firms_archive.py` runs every 3 hours via GitHub Actions:

1. Queries the FIRMS area API in 5-day windows (the API maximum) for each source, clipped to the dates each source has available.
2. Saves a response only if it differs from every file already held for that window. Raw files are never edited or deleted. A file containing only a header row means the satellite reported no detections in the box for that window.
3. Rebuilds `data/firms/detections.csv` and `.geojson`, de-duplicated on source, latitude, longitude, date and time. `first_seen_file` records which raw file first contained each detection.
4. Writes a SHA-256 manifest of the new raw files and stamps it with OpenTimestamps.

**Times.** FIRMS `acq_time` is UTC (HHMM). The merged table adds ISO UTC and local MDT (UTC−6) columns.

## Timestamps

OpenTimestamps commits a file's hash to the Bitcoin blockchain through public calendar servers. A new `.ots` proof is pending until the calendar anchors it in a block (usually a few hours); the daily "Upgrade timestamps" workflow then stores the complete proof. `ots verify` checks it independently of Prime Rogue and GitHub.

The timestamp proves a file existed unchanged at that time. It does not prove the data is accurate.

## GOES-18/19 loops and fire timeline

**What it is.** NOAA's geostationary GOES-18 (West, 137.0°W) and GOES-19 (East, 75.2°W) satellites image the whole visible Earth every 10 minutes. Wainwright lies just north of both satellites' 5-minute CONUS sectors, and neither 1-minute mesoscale sector was over Alberta on Oct 17, 2026, so full-disk is the best GOES cadence for this event.

**Data.** NOAA ABI Level-2 products from the public archive (`s3://noaa-goes18`, `s3://noaa-goes19`): Cloud and Moisture Imagery (`ABI-L2-CMIPF`, bands 1, 2, 3, 5, 6, 7, 11, 13, 14, 15), Fire Detection and Characterization (`ABI-L2-FDCF`) and Clear Sky Mask (`ABI-L2-ACMF`). `scripts/goes_loops.py` reads only the window around Wainwright from each file. Every source file used is listed in `data/goes/fire_timeline.csv`, so anyone can re-pull the exact inputs.

**Products.** Imagery is reprojected (nearest neighbour) to a north-up grid at 0.5 km (red visible), 1 km (true colour) or 2 km (Fire Temperature RGB, Dust RGB). Time stamps are each full-disk scan's start time; the scan reaches 53°N within roughly the first two minutes.

**Timeline.** For a box over the base (52.65–52.95°N, 110.65–111.15°W) and each scan: percent of pixels NOAA's cloud mask flags as cloudy; median 10.3 µm brightness temperature (cloud-top temperature when cloudy); the hottest 3.9 µm pixel; and pixels NOAA's fire algorithm classifies as fire, with their summed fire radiative power.

**Limits.** GOES pixels over Alberta are roughly 2–4 km on the ground, and positions are not corrected for parallax, so a GOES fire pixel locates a fire to within a few kilometres. The fire algorithm can see through thin cloud but not thick cloud; a falling signal under cloud does not mean the fire weakened. Fire radiative power is an index of intensity, not of area burned.
