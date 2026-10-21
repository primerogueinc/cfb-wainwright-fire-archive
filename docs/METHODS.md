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
