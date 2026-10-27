# ACIS hourly data (Alberta AgroClimatic Information Service)

Downloaded by hand from acis.alberta.ca (CAPTCHA), Oct. 26, 2026. Hourly only; ACIS offers no sub-hourly data for these stations. Times are Local Standard Time (MST, UTC-7); add one hour for MDT. Each row is the hour ending at that time.

Front passage, estimated from the hourly mean humidity in the hour the front passed (fraction of the hour still dry = (mean - before) / (after - before)):

| Station | From fire | Hour of passage (MDT) | Temp. drop | Mean RH that hour (before / after) | Estimated passage (MDT) |
|---|---|---|---|---|---|
| Hughenden AGCM | 22 km S | 3:00-4:00 p.m. | 23.6 -> 13.8 C | 25.9% (17.8 / ~41) | ~3:39 p.m. (peak-gust hour proxy 3:43) |
| Albert Hall AGCM | 43 km NNW | 3:00-4:00 p.m. | 22.9 -> 12.7 C | 45.6% (~21 / ~46): already post-front for nearly all the hour | ~3:00-3:05 p.m. (peak gust 3:07) |
| Bellshill AGCM | 39 km W | 3:00-4:00 p.m. | 23.1 -> 12.7 C | 40.8% (~18 / ~40): post-front for nearly all the hour | ~3:00-3:05 p.m. |
| Gilt Edge North AGCM | 43 km NNE | 3:00-4:00 p.m. | 23.7 -> 14.1 C | 30.3% (~17 / ~43.5) | ~3:30 p.m. (peak gust 3:28) |

Both fit the station-plane estimate of the front at the fire, about 3:29 p.m. MDT (README_pull.md).

Also in the file: Wainwright CFB Airfield 21, the same ECCC station (CZWN, 301S001) already used from ECCC/SWOB as the primary record (82 km/h peak gust at 3:16 p.m. MDT). ACIS republishes its hourly values; nothing new.
