# NOAA GOES-18 and GOES-19 fire detection files, Oct. 17–18, 2026 (raw)

684 unmodified NOAA ABI **Fire Detection and Characterization** (FDC) files downloaded by Prime Rogue during the first analysis.

**GOES-18 (West), 360 files:**
- `ABI-L2-FDCC` (CONUS sector, every 5 min): 216 files, scans 12:01 UTC Oct. 17 to 05:56 UTC Oct. 18 (6:01 a.m. Oct. 17 to 11:56 p.m. Oct. 17 MDT).
- `ABI-L2-FDCF` (Full Disk, every 10 min): 144 files, scans 06:00 UTC Oct. 17 to 05:50 UTC Oct. 18 (midnight to 11:50 p.m. Oct. 17 MDT).

**GOES-19 (East), 324 files:**
- `ABI-L2-FDCC` (CONUS, every 5 min): 216 files, 12:01 UTC Oct. 17 to 05:56 UTC Oct. 18 (6:01 a.m. to 11:56 p.m. Oct. 17 MDT).
- `ABI-L2-FDCF` (Full Disk, every 10 min): 108 files, 12:00 UTC Oct. 17 to 05:50 UTC Oct. 18 (6:00 a.m. to 11:50 p.m. Oct. 17 MDT).

**Verified identical to NOAA's archive.** On Oct. 21, 2026, every file's MD5 was compared with the checksum (ETag) NOAA's public S3 archive reports for the same object: **684 of 684 match** (360 GOES-18, 324 GOES-19) (`md5sums_match_noaa_etags.txt`). `sha256sums.txt` lists SHA-256 for each file.

**Where the files are.** All 684 files are committed in `goes18/` and `goes19/` (each with `ABI-L2-FDCC/` and `ABI-L2-FDCF/`), exactly as used in the analysis. Check them with `sha256sum -c sha256sums.txt` from this folder. `fetch.sh` can also re-download them from NOAA's public archive (`s3://noaa-goes18`, `s3://noaa-goes19`) and verify them independently. The original bundles' SHA-256 values are in `zip_sha256.txt`.

Note: Wainwright lies just north of the CONUS sector's edge (see `docs/METHODS.md`), so the Full Disk files are the ones that cover the site; the GOES-18 fire pixels at 3:10, 3:30 and 3:40 p.m. MDT come from them. GOES-19 flagged no fire pixel at the site that afternoon, though its 3.9 µm channel showed heat at 3:20 and 3:40 p.m. (`data/goes/fire_timeline.csv`).

Data: NOAA (public domain). Checksums, script and notes: Prime Rogue Inc. (script MIT, notes CC BY 4.0).
