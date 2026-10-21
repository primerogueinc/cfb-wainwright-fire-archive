PRIME ROGUE INC. | CFB WAINWRIGHT, NASA FIRMS RAW DATA
Version 2, prepared Oct. 19, 2026. (Version 1, Oct. 18, covered downloads 1-4 only.)
Analysis first published 2 a.m. MT, Oct. 18, 2026:
https://primerogueinc.com/blog/cfb-wainwright-satellite-fire-before-explosion/

WHAT THIS IS
Unmodified KMZ and KML files downloaded from NASA FIRMS (https://firms.modaps.eosdis.nasa.gov)
active-fire datasets for Canada and for Alberta, all sensors:
Landsat 8/9 OLI (LANDSAT), VIIRS on Suomi-NPP (SUOMI), NOAA-20 (J1) and NOAA-21 (J2),
and MODIS on Aqua/Terra (MODIS_C61 / MODIS_C6_1). Files are unchanged; only the folder structure
was added and an upload prefix was removed from file names. SHA256SUMS.txt lists checksums for
every file. Identical duplicate downloads were included once.

WHAT'S NEW IN VERSION 2
Downloads 5-7 add the 48-hour, 72-hour and 7-day datasets (covering Oct. 12-18) and the
standard-format KML files. They add three detections that are not in version 1:
  Oct. 14, 2:51 p.m. MDT, 1 detection, NOAA-21 VIIRS, about 2.7 km SW of the Oct. 17 detections
  Oct. 18, 2:12 p.m. MDT, 1 detection, Suomi-NPP VIIRS, about 5 km SE
  Oct. 18, 2:32 p.m. MDT, 1 detection, NOAA-20 VIIRS, same location as 2:12 p.m.
Nothing in versions 1 and 2 conflicts: every detection in version 1 appears unchanged in the
later downloads, and no detection was added, removed or moved for Oct. 17.

FOLDERS (times are Mountain Daylight Time, UTC-6)
1_download_2026-10-17_2350MDT                    Canada + Alberta, 24h
2_download_2026-10-18_0105MDT                    Canada, 24h
3_download_2026-10-18_0112MDT                    Canada + Alberta, 24h
4_download_2026-10-18_0427MDT                    Canada + Alberta, 24h (includes overnight passes)
5_download_2026-10-18_approx2200MDT_standard-kml Canada, 24h and 48h, standard KML format
                                                 (no time stamp in the files; time is approximate)
6_download_2026-10-18_2209MDT                    Canada + Alberta, 24h/48h/72h/7d, FirespotArea format
7_download_2026-10-18_2215MDT                    Alberta repeat download, 24h/48h/72h/7d
Download times for folders 6 and 7 come from the time stamp FIRMS writes into each KML file name.

ALL DETECTIONS WITHIN 40 KM OF CFB WAINWRIGHT, OCT. 12-18 (ref. 52.7767 N, 110.9210 W)
  Oct. 14  2:51 p.m. MDT   NOAA-21 VIIRS     1 detection   Nominal  11.67 MW  west shore of the
                                                                    saline lake in the training area
  Oct. 17 12:17 p.m. MDT   Landsat 8 OLI    59 detections  see confidence note below
  Oct. 17  2:49 p.m. MDT   NOAA-20 VIIRS     8 detections  Nominal  5.83-11.53 MW
  Oct. 18  2:12 p.m. MDT   Suomi-NPP VIIRS   1 detection   Nominal  2.65 MW   about 5 km SE
  Oct. 18  2:32 p.m. MDT   NOAA-20 VIIRS     1 detection   Nominal  3.85 MW   about 5 km SE
No other detection within 40 km from Oct. 12 to the end of the files (about 2:32 p.m. MDT Oct. 18
for VIIRS; 12:11 p.m. MDT Oct. 18 for Landsat). Four overnight VIIRS passes (approx. 2:42, 3:02,
3:46 and 4:22 a.m. MDT, Oct. 18) recorded no fire within 40 km of the base.

WHAT THE DETECTIONS DO AND DON'T SHOW
- The Oct. 17 detections predate the approximately 4 p.m. ignition time first stated by the
  Department of National Defence.
- The Oct. 14 detection shows heat in the training area three days earlier. It does not show
  whether that fire was connected to the Oct. 17 fire.
- The Oct. 18 detections are about 5 km southeast of the Oct. 17 detections. Their position
  appears to be just outside the base boundary. Whether they are from the Oct. 17 fire or
  an unrelated source (such as a farm burn) cannot be determined from this data.
- A Landsat 9 pass at about 12:11 p.m. MDT Oct. 18 recorded no detection near the base; its
  nearest detection was about 240 km away. This data does not show whether that pass covered the base.

CONFIDENCE NOTE (LANDSAT, OCT. 17)
The two FIRMS file formats rate the same 59 Landsat detections differently:
  FirespotArea format: all 59 "Low"
  Standard KML format (LANDSAT_Canada_24h.kml / _48h.kml): 34 "medium", 25 "low"
Both values are given in the CSV. The Oct. 14 detection appears only in the 7-day files,
which were not downloaded in standard format, so it has no standard-format value.

HOW TO CHECK
1. Open any KMZ or KML in Google Earth, or open the KML in a text editor (unzip a KMZ first).
2. Each detection lists latitude, longitude, time (UTC), sensor and confidence.
3. Search near 52.77, -110.92. Convert UTC to MDT by subtracting 6 hours.
Each detection appears in FirespotArea files as both a centre point and a pixel outline, and the
Canada, Alberta and 24h/48h/72h/7d files overlap; de-duplicating by time, sensor and
coordinates gives the counts above.

ALSO INCLUDED
cfb-wainwright-firms-detections.csv   all 70 detections listed above, extracted (UTC and MDT),
                                      with both confidence values, FRP, pixel size, brightness,
                                      distance from the reference point and the number of files
                                      that contain each detection
overnight-passes-oct18.csv            overnight passes and results at the base (unchanged from v1)

LIMITS
Satellite detections show heat, not cause. Detection times are recorded to the minute.
No high-resolution satellite passed over the base between about 3:30 p.m. and nightfall on Oct. 17,
so this data cannot show what happened at or after 4 p.m., including the explosion.
Absence of a detection does not prove absence of fire: cloud, smoke, pixel size and
pass timing all limit what a satellite records.

Contact: Kevin J.S. Duska Jr., President, Prime Rogue Inc.
kevin@primerogueinc.com
