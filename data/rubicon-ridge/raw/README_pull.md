# Rubicon Ridge raw data pull, Oct. 26, 2026

This pull covers the Oct. 17, 2026 CFB Wainwright fire. The fire centre is at 52.7645 N, -110.9052 W. Range 2 is at 52.772 N, -110.90089 W.

All times are given as MDT (UTC-6) unless marked UTC. Every source was reached anonymously, with no keys or credentials. Nothing has been committed.

Scripts are in `scripts/rubicon_ridge/`. Each script was run as `python3 -I <script> <out_dir> [...]`.

The FIRMS and PurpleAir folders were already done before this pull and were not touched.

Total size of `raw/`: about 44 MB, including the FIRMS and PurpleAir folders.

---

## 1. GOES-18 / GOES-19 ABI (`raw/goes/`)

**Source:** NOAA open data on AWS (`noaa-goes18`, `noaa-goes19`), read anonymously over HTTPS.

**Scripts:** `goes_common.py`, `goes_inventory.py` (from the earlier attempt, reused unchanged) and `goes_fire_extract.py` (new).

**How files were read:** the netCDF files were read lazily with fsspec and h5netcdf. Only the HDF5 chunks covering the crop box were transferred, and no full-disk file was saved.

### Files

| File | Contents |
|---|---|
| `goes_inventory_doy290_19-23z.csv`, `goes_inventory_summary.csv` | Every ABI L1b/L2 key for day 290, 19-23 UTC. Products: Rad, CMIP and MCMIP for F, C and M; FDC; ACM. |
| `goes_sector_coverage.json` | Coverage test of the fire point, using each sector file's own projection. CONUS was sampled 4 times; mesoscale every 5 min. |
| `conus_coverage_check.json` | Scan-angle test of the fire point against the FDCC (CONUS/PACUS) sector for both satellites. |
| `fdcf_crop_G18.nc`, `fdcf_crop_G19.nc` | Full Disk FDC variables `Mask`, `Power` (MW), `Temp` (K), `Area` (m²) and `DQF`. Crop box: 52.45-53.10 N, 111.45-110.35 W. Coverage: every 10-min scan, Oct. 17 16:00 UTC to Oct. 18 00:50 UTC (54 scans per satellite). |
| `radf_c07_crop_G1x.nc`, `radf_c13_crop_G1x.nc` | L1b Full Disk band 7 (3.9 µm) and band 13 (10.3 µm). Radiance plus brightness temperature (BT), computed from each file's Planck constants. Same box and times as the FDC files. |
| `fdc_fire_pixels.csv` | Every pixel in the crop box with a fire mask code (10-15 or 30-35), per scan. |
| `fdc_point_series.csv` | Per scan: FDC values at the pixels containing the fire centre and Range 2; fire-pixel count, total FRP and the mask codes present in the burn box (52.72-52.81 N, 110.98-110.83 W). |
| `rad_point_series.csv` | Per scan: band 7 and band 13 BT at the fire pixel, the burn-box maximum (with its location) and median, and the median of a background box about 25 km WSW. |

### Which sectors cover the fire

- **No 1-minute or 5-minute data exists for the fire.**
  - Neither mesoscale sector of either satellite came near it between 19 and 23 UTC.
    - G18 M1 was centred near 19.5 N, 106.5 W; G18 M2 near 55.8 N, 150 W.
    - G19 M1 was centred near 38.5 N, 75 W; G19 M2 near 37.1 N, 86.6 W.
  - The fire lies just north of the northern edge of both the G18 PACUS and the G19 CONUS sectors. Its scan-angle y is 0.1299 rad (G18) and 0.1288 rad (G19); both sectors end at 0.1282 rad.
- **Full Disk (10-min) is therefore the only GOES coverage.**

### GOES fire power at the fire

Source: G18 FDCF. Times are scan start. The fire's latitude is imaged a few minutes after scan start; the exact line time is not in the files.

| Scan start (MDT) | Sat | Fire pixels | FRP (MW) | Mask / notes |
|---|---|---|---|---|
| 15:00 and earlier | G18 | 0 | 0 | 200 (cloud test) through 14:50; 100 (processed, no fire) at 15:00 |
| **15:10** | G18 | 1 | **76.5** | Mask 10, good-quality fire. Fire temperature 490 K; area 57,357 m² (5.7 ha). Pixel at 52.792, -110.906. |
| 15:20 | G18 | 0 | 0 | Masks 100, 200 and 215 (cloud tests) |
| **15:30** | G18 | 3 | **1,215.4** (278.0 + 517.1 + 420.3) | Mask 33, temporally filtered high-probability fire. No temperature or area retrieved. |
| **15:40** | G18 | 1 | **336.3** | Mask 33. Pixel at 52.754, -110.896. |
| 15:50 onward | G18 | 0 | 0 | Cloud (200) |
| 15:10-15:50 | G19 | 0 | — | Mask 170: "no background value could be computed". G19 never ran a fire test on the fire pixels in this window. |

Band 7 BT shows the heat even where FDC returned nothing. Each cell below is the burn-box maximum, with the background median in brackets.

| Scan (MDT) | 14:50 | 15:00 | 15:10 | 15:20 | 15:30 | 15:40 | 15:50 |
|---|---|---|---|---|---|---|---|
| G18 BT (K) | 295 (291) | 302 (297) | 307 (293) | 303 (292) | **332** (290) | **324** (291) | 302 (291) |
| G19 BT (K) | 273 (272) | 274 (285) | 291 (289) | **305** (285) | 289 (284) | **314** (284) | 295 (286) |

On G19, the 15:20 and 15:40 values are hot signals that FDC did not flag. These FDC results match the existing `data/goes/fire_timeline.csv`.

---

## 2. NOAA RAP (`raw/rap/`)

**Source:** `noaa-rap-pds` on AWS. HRRR could not be reached (see "Blocked or unavailable" below).

**Script:** `rap_pull.py`.

**Product:** RAP hourly analyses (f00) on the 13 km CONUS grid 130 (`awp130pgrb`), Oct. 16 12 UTC to Oct. 18 12 UTC (49 analyses). Only the needed GRIB messages were fetched, as byte ranges taken from the `.idx` files.

**Fields:** 10 m and 80 m U/V (rotated to earth-relative), 2 m temperature, dewpoint and RH, surface gust, surface pressure, HPBL (column `d0c3n196`), precipitation rate and composite reflectivity.

### Files

| File | Contents |
|---|---|
| `grib/rap.YYYYMMDD.tHHz.awp130pgrbf00.sfc.grib2` | Subset GRIB for Oct. 17 15 UTC to Oct. 18 01 UTC (11 files, about 0.9 MB each). |
| `rap_points_f00.csv` | Hourly values at nine points: fire, Range 2, CZWN, CYLL, Wainwright town, Provost, Vermilion, Coronation and Kindersley. Each value is given both as the nearest grid point and as an inverse-distance mean of the 3×3 neighbourhood. Wind speed and direction are derived. |
| `rap_crop_f00.nc` | All fields in the box 51.8-53.8 N, 112.6-109.2 W, for all 49 hours. |

### RAP at the fire (IDW values)

| MDT | T (°C) | RH (%) | 10 m wind | Gust (km/h) |
|---|---|---|---|---|
| 15:00 | 23.8 | 16 | 258° at 44 km/h | 78 |
| 16:00 | 15.4 | 40 | 302° at 60 km/h | 89 |

The front passes the fire between the 15:00 and 16:00 analyses. Hourly analyses cannot resolve it more finely.

---

## 3. ECCC (`raw/eccc_radar/`, `raw/eccc_models/`, `raw/eccc_swob/`)

### 3a. Radar (`eccc_radar/`, script `radar_pull.py`)

The MSC Datamart still holds Oct. 17, but only as GIF imagery: `dd.weather.gc.ca/20261017/WXO-DD/radar/{CAPPI,DPQPE}/GIF`. It holds no volume scans and no ODIM/HDF5 files.

**Pulled:** 6-minute CAPPI GIFs, 16:00-23:54 UTC.
- Radars: Carvel (CASCV) and Radisson (CASRA), both about 235 km from Wainwright; Schuler (CASSU); Strathmore (CASSM). 158 files each: 1.5 km RAIN and 1.0 km SNOW.
- The PNR composite: 80 files.

**Not pulled:** the DPQPE folders. They hold accumulation products with a different file naming that the script's pattern skipped, so no DPQPE files were saved. They are not needed for timing.

**Limitations:**
- No radar is within 200 km of the fire.
- At about 235 km, the 1.5 km CAPPI beam is far above the boundary layer, so a gust front or smoke plume near the surface will not show. A frontal precipitation band is visible on CASCV at 21:30 UTC.
- The GIFs are 1 km/pixel imagery and have not been georeferenced.
- Volume scans would need a request to ECCC. The `hpfx.collab.science.gc.ca/20261017/radar/` folder returns HTTP 401 (credentials required).

### 3b. HRDPS (`eccc_models/`, script `hrdps_pull.py`)

**Source:** HRDPS continental 2.5 km, archived on the Datamart for Oct. 17.

**Runs:**
- 06Z, leads f011-f018
- 12Z, leads f000-f012
- 18Z, leads f000-f006

**Fields:**
- 10 m: WIND, WDIR, GUST and GUST-Max
- 80 m: WIND and WDIR
- 2 m: TMP, RH and DPT
- surface: PRES

Each full-domain file was cropped to 52.3-53.4 N, 111.8-110.0 W and then deleted.

**Outputs:**
- `hrdps_crop_{06Z,12Z,18Z}.nc`: the cropped fields.
- `hrdps_points_long.csv` and `hrdps_points_wide.csv`: values at the nearest grid point for the fire, Range 2, CZWN, CYLL, the six nearest ACIS stations and the town.
- Units: K, %, m/s, degrees true and Pa.

**Note:** HRDPS is hourly. It puts the wind shift at the fire between 15:00 and 16:00 MDT in the 12Z and 18Z runs, and between 16:00 and 17:00 in the 06Z run. It is much too moist before the front: RH 43-50% against 16-17% observed.

### 3c. SWOB-ML observations (`eccc_swob/`, scripts `swob_pull.py` and `swob_tidy.py`)

**Coverage:** Oct. 17 00 UTC to Oct. 18 06 UTC.

**Stations:**
- All 9 MSC stations within 160 km of the fire.
- All 29 Alberta Agriculture and Irrigation (ACIS, network `AB-MAI`) partner stations within 110 km.

**Files:**
- `stations_pulled.csv`: the station list.
- `swob_hourly_key_vars.csv`: hourly files.
- `swob_minute_key_vars.csv`: **1-minute data** for Coronation (CWCT), Waseca SK (CPWX), Esther (CWGY), Camrose (CWRV) and Scott SK (CWTS).
- `swob_long.csv.gz`: every element.
- `swob_xml_raw.tar.gz`: the raw XML.
- The station-list CSVs.

**Gaps:**
- CZWN, CPNX and CWVI have only hourly SWOB files; no 1-minute files are published for them.
- CYLL includes the 15:41 and 15:48 MDT special observations (SPECIs).
- Camrose has a 1-minute data gap from 20:01 to 01:06 UTC.
- None of Provost, Vermilion (MSC), Kindersley or a Wainwright-town ECCC station publishes SWOB. Kindersley (CYKY) is in the network but outside 160 km.
- Vermilion AGDM, Edgerton and other ACIS stations are covered under section 4.

---

## 4. Alberta ACIS (`raw/acis/`, empty)

**Blocked:** the ACIS weather data viewer (`acis.alberta.ca/acis/weather-data-viewer.jsp`) releases data only after a CAPTCHA, so it was not used.

**Substitute:** the same ACIS stations (AGCM/AGDM/LITE, provider "AB-MAI") are published hourly on the ECCC Datamart SWOB partner feed `partners/ab_agriculture`. They were pulled there; see `eccc_swob/`.

- 5-minute ACIS data is not on that feed.
- AGCM stations report wind from a 2 m precipitation-gauge anemometer, with the time of the peak 2 m gust. AGDM and LITE stations report 10 m wind without a gust time.
- The `ab-firewx` partner network has no station within 160 km of the fire.

---

## 5. Alberta air quality (`raw/alberta_aq/`)

**Source:** the Alberta Environment open OData service (`data.environment.alberta.ca/EdwServices/aqhi/odata`), which works without a key.

**Files:**
- `stations.json`: all 90 stations.
- `st<key>_<date>.json`: raw OData responses.
- `ab_aq_station_measurements_oct16-18.csv`: hourly values for Oct. 16-18. Parameters include PM2.5, wind speed and direction, temperature, RH, O3 and NOx.

**Stations:** the six nearest that operate. **None is within 140 km.**
- Hanna 143 km
- St. Lina 166 km
- Elk Island 167 km
- Lamont 168 km
- Ardrossan 175 km
- Cold Lake South 189 km

There is no provincial AQ monitor at Wainwright, Lloydminster or Vermilion in this service.

**Also pulled:** ECCC AQHI site observations for the Prairies (`eccc_aqhi_pnr_siteobs/`, 16-23 UTC, with the site list XML). The nearest site is Lamont County, 168 km away.

**Assessment:** neither source can time the smoke reaching the town. PurpleAir, already pulled, remains the only nearby smoke sensor.

---

## Blocked or unavailable

**Refused by the proxy (HTTP 403 on CONNECT).** Each was tried once or twice, then left.
- `noaa-hrrr-bdp-pds.s3.amazonaws.com` (HRRR)
- `nomads.ncep.noaa.gov`
- `www.ncei.noaa.gov`
- `thredds.ucar.edu`
- `mesonet.agron.iastate.edu`
- `www.airnow.gov`
- `api.openaq.org`
- `airdata.alberta.ca` (Alberta Air Data Warehouse)
- `www.alberta.ca`
- `dd.alpha.weather.gc.ca`
- `noaa-nexrad-level2.s3.amazonaws.com`
- `msc-open-data.s3.amazonaws.com`

**Requires credentials or a human step:**
- ACIS data download (CAPTCHA)
- `hpfx.collab.science.gc.ca/20261017/radar/` (HTTP 401)

**Not archived anywhere reachable:**
- ECCC radar volume scans, and GeoMet WMS radar layers. These only keep the last few hours.
- GOES mesoscale or CONUS coverage of the fire.
- ACIS 5-minute data.

**Intermittent:** `dd.weather.gc.ca`, `hpfx.collab.science.gc.ca` and `api.weather.gc.ca` often reset connections. The scripts retry up to 3-4 times with backoff, and every Datamart file finally downloaded (no failures logged).

---

## Front-passage times (MDT)

**Sources:**
- The 1-minute stations come from `eccc_swob/swob_minute_key_vars.csv`.
- Everything else comes from `swob_hourly_key_vars.csv`.

**Peak-gust times as a proxy:** for hourly stations, "peak gust" is the time of the hour's maximum gust (`max_wnd_spd_pst1hr_tm` or `max_wnd_spd_2m_pst1hr_tm`). At the 1-minute stations the hour's peak gust fell 0-2 min after the wind shift, so peak-gust time is a reasonable proxy for arrival.

**Distances:** distance and bearing are from the fire to the station.

| Station | Dist / bearing | Wind shift | Peak gust | T drop | RH jump | Source |
|---|---|---|---|---|---|---|
| Camrose CWRV | 132 km W | 14:00-14:01 (255° → 285°) | 66.5 km/h 14:01 | — | — | 1-min. Data gap after 14:01, so the T drop was not observed. |
| Ranfurly CPNX | 92 km NW | 14:00-15:00 | 72 km/h 14:33 | 22.9 → 12.3 by 15:00 | 19 → 51% | hourly |
| Gladstone GLAD | 95 km W | 14:00-15:00 | 75 km/h (2 m) 14:37 | 23.1 → 11.4 | 18 → 55% | ACIS hourly |
| Viking VIKI | 72 km NW | 14:00-15:00 | 76 km/h (2 m) 14:40 | 22.0 → 12.6 | 21 → 48% | ACIS hourly |
| Mannville MVIL | 80 km N | 14:00-15:00 | 76 km/h (2 m) 14:53 | 21.6 → 15.3 | 24 → 42% | ACIS hourly |
| Killam, Forestburg, Kinsella | 54-86 km W/NW | 14:00-15:00 | 101-104 km/h | to about 13 | to about 48% | ACIS hourly, no gust time |
| Albert Hall ALBE | 43 km NNW | 15:00-16:00 | 82 km/h (2 m) 15:07 | 22.9 → 12.7 | 19 → 46% | ACIS hourly |
| **CFB Wainwright CZWN** | 15 km WNW | 15:00-16:00 (236° → 307°) | **82 km/h 15:16** from 269° | 23.3 → 12.9 | 17 → 43% | hourly |
| Bellshill BELL | 43 km W | 15:00-16:00 | 81 km/h (2 m) 15:25 | 23.0 → 12.7 | 17 → 40% | ACIS hourly |
| Gilt Edge N GILT | 39 km NNE | 15:00-16:00 | 83 km/h (2 m) 15:28 | 23.5 → 14.1 | 16 → 43% | ACIS hourly |
| Kitscoty KITS | 73 km NE | 15:00-16:00 | 70 km/h (2 m) 15:30 | 22.5 → 13.7 | 21 → 48% | ACIS hourly |
| **Coronation CWCT** | 85 km SSW | **15:31** (272° → 313°) | 94.6 km/h 15:33 | 22.1 → 13.7 by 15:33 | 18 → 33% by 15:33 (47% by 15:40) | 1-min |
| **Hughenden HUGH** | 22 km S | 15:00-16:00 (246° → 308°) | 77 km/h (2 m) **15:43** | 23.1 → 13.8 | 18 → 43% | ACIS hourly (nearest station to the fire) |
| **Lloydminster CYLL** | 82 km NE | 15:41-15:48 SPECIs | 98 km/h at the 15:48 SPECI | 22.8 → 20.6 at 15:48, 15.1 by 16:00 | 19 → 28 → 42% | SPECI |
| Rivercourse RIVE | 61 km ENE | 15:00-16:00 | 75 km/h (2 m) 15:51 | 22.4 → 15.0 | 19 → 42% | ACIS hourly |
| Kessler KESS | 55 km SSW | 15:00-16:00 | 85 km/h (2 m) 15:52 | 21.9 → 12.4 | 18 → 46% | ACIS hourly |
| Lloydminster LLDM | 88 km NE | 15:00-16:00 | 69 km/h (2 m) 15:55 | 22.1 → 15.7 | 21 → 41% | ACIS hourly |
| Edgerton EDGE | 32 km E | 15:00-16:00 (243° → 303°) | 95 km/h | 23.0 → 14.6 | 17 → 42% | ACIS hourly, no gust time |
| Ribstone S RIBS | 43 km ESE | Near 16:00 (19.6 °C at 16:00) | 94 km/h | 22.8 → 19.6 → 13.3 | 19 → 28 → 37% | ACIS hourly |
| Cadogan CADO | 55 km SSE | Near 16:00 | 91 km/h | 22.0 → 16.7 | 16 → 34% | ACIS hourly |
| **Waseca CPWX** | 108 km ENE | **16:19** (251° → 277°) | 69.4 km/h 16:21 (day max 81.7 at 17:08) | 21.6 → 16.5 by 16:29 | 21 → 37% | 1-min |
| **Esther CWGY** | 131 km SSE | **16:34** (269° → 294°) | 98.9 km/h 16:34 | 22.9 → 15.1 by 16:38 | 18 → 36% | 1-min |
| Bodo, Consort | 90-93 km SE/S | 16:00-17:00 | 99-107 km/h | to about 13 | to about 37% | ACIS hourly |
| **Scott CWTS** | 147 km ESE | **17:11** (254° → 273°, then 308°) | 83.6 km/h 17:12 | 21.4 → 15.3 by 17:23 | 21 → 40% | 1-min |
| RAP, at the fire | — | 15:00-16:00 analyses | 78 → 89 km/h | 23.8 → 15.4 | 16 → 40% | model, hourly |
| HRDPS 12Z and 18Z, at the fire | — | 15:00-16:00 | — | — | — | model, hourly |

### Estimated arrival at the fire

I fitted a plane to arrival time, t = a + b·x + c·y, using the five 1-minute shift times plus CZWN (15:16) and CYLL (about 15:45).

- **Front motion:** about 87 km/h toward 116°, coming from about 296°.
- **Predicted arrival at the fire:** about **15:29 MDT**. Residuals are within ±3 min.
- **With all peak-gust proxies included:** 15:32.
- **From CZWN alone:** the fire is about 14.7 km downstream of CZWN along the direction of motion. At 87 km/h that is about 10 min after 15:16, so **about 15:26**.

So the best estimate of the front's arrival at the fire is **15:25-15:32 MDT**. That is about 10-15 min after the CZWN gust. HUGH, 22 km south, peaked at 15:43 (2 m gust), which fits.

**Reading this against GOES:** G18 already detected the fire at the 15:10 scan (76 MW), before the front arrived. Fire power peaked at the 15:30 scan (1,215 MW over 3 pixels), as the front was crossing. It was still 336 MW at 15:40. Cloud then hid the fire.

This is a first-pass reading for the main session to check; nothing here has been fed into the model.
