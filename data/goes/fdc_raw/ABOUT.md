# NOAA GOES-18 fire detection files, Oct. 17–18, 2026 (raw)

360 unmodified NOAA GOES-18 ABI **Fire Detection and Characterization** (FDC) files downloaded by Prime Rogue during the first analysis:
- `ABI-L2-FDCC` (CONUS sector, every 5 min): 216 files, scans 12:01 UTC Oct. 17 to 05:56 UTC Oct. 18 (6:01 a.m. Oct. 17 to 11:56 p.m. Oct. 17 MDT).
- `ABI-L2-FDCF` (Full Disk, every 10 min): 144 files, scans 06:00 UTC Oct. 17 to 05:50 UTC Oct. 18 (midnight to 11:50 p.m. Oct. 17 MDT).

**Verified identical to NOAA's archive.** On Oct. 21, 2026, every file's MD5 was compared with the checksum (ETag) NOAA's public S3 archive reports for the same object: **360 of 360 match** (`md5sums_match_noaa_etags.txt`). `sha256sums.txt` lists SHA-256 for each file.

**Where the files are.** All 360 files are committed in `goes18/ABI-L2-FDCC/` and `goes18/ABI-L2-FDCF/`, exactly as used in the analysis. Check them with `sha256sum -c sha256sums.txt` from this folder. `fetch.sh` can also re-download them from NOAA's public archive (`s3://noaa-goes18`) and verify them independently. The original bundle's SHA-256 is in `zip_sha256.txt`.

Note: Wainwright lies just north of the CONUS sector's edge (see `docs/METHODS.md`), so the Full Disk files are the ones that cover the site; the fire pixels at 3:10, 3:30 and 3:40 p.m. MDT come from them (`data/goes/fire_timeline.csv`).

Data: NOAA (public domain). Checksums, script and notes: Prime Rogue Inc. (script MIT, notes CC BY 4.0).
