# Environment and Climate Change Canada (ECCC) bulletins and observations, Oct. 16–18, 2026

Retrieved from the MSC Datamart (dd.weather.gc.ca) on Oct. 19, 2026, before the Datamart's short retention window expired.

| Path | Contents |
|---|---|
| `original/bul/YYYYMMDD/{FP,WO,WW}/{CWWG,CWNT}/HH/` | Raw text bulletins, unchanged: public forecasts (FP), warnings and statements (WW), other (WO), from the Prairie (CWWG) and Northern (CWNT) storm-prediction offices. File names carry the UTC issue time (DDHHMM). |
| `original/as_pulled_oct19/ecc_raw_oct_17/` | The first pull as originally organized: forecasts, warnings, and hourly SWOB-ML station observations for CFB Wainwright (CZWN) and Lloydminster (CYLL), with a short readable extract. Some bulletins appear in both folders. |
| `swob_observations.csv` | All station observations parsed to one table (built by `scripts/eccc_parse.py`). |
| `bulletins_index.csv` | Every bulletin: type, office, UTC and MDT issue time, whether it mentions Wainwright, warning headlines, and whether it duplicates another copy. |

**Key readings, Oct. 17 (MDT).** The CFB Wainwright station (CZWN, "Wainwright CFB Airfield 21", 52.829°N 111.096°W) is about 12 km west-northwest of the fire site.
- Morning to 1 p.m.: south-southwest winds, 2-minute average 12–21 km/h, gusts to about 30 km/h; relative humidity falling to 23%.
- 2 p.m. and 3 p.m. observations: southwest winds (235–236°) averaging about 31 km/h; peak gusts 46 km/h at 1:34 p.m. (from 232°) and 51 km/h at 2:48 p.m. (from 246°); temperature 23 °C, humidity 16–17%.
- **Peak gust 82 km/h at 3:16 p.m. from 269° (west).** By the 4 p.m. observation the 2-minute average was 51 km/h from 306° (northwest), temperature had dropped about 10 °C to 12.9 °C and humidity risen to 43%: the cold front.
- Lloydminster (CYLL, ~50 km northeast): peak gust 98 km/h from 269° in the hour to 4 p.m.
- **Warnings naming Wainwright:** yellow-level wind warning issued 2:14 p.m. MDT, updated 3:05 p.m., ended 6:18 p.m. (WWCN16 CWWG). See `bulletins_index.csv` for every issue, including dust-storm wording in the region.

Station observations are hourly snapshots plus the hour's peak; they do not give minute-by-minute wind at the fire. Data: Environment and Climate Change Canada (Open Government Licence – Canada). Parsed tables and notes: Prime Rogue Inc., CC BY 4.0.
