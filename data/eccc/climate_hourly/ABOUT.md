# ECCC historical hourly data, CFB Wainwright, October 2026

`wain_hourly_2026-10.csv` is the unmodified hourly CSV for **Wainwright CFB Airfield 21** (Climate ID 301S001, 52.83°N 111.10°W), downloaded from Environment Canada's Historical Climate Data service (climate.weather.gc.ca) for Oct. 1–31, 2026.

**Watch the time zone.** ECCC climate data is stamped in **Local Standard Time (LST = UTC − 7)** all year, not daylight time. On Oct. 17, 2026 Alberta was on MDT (UTC − 6), so every LST time is **one hour behind** the clock time people used that day: the row labelled 15:00 LST is the 4:00 p.m. MDT observation. `wain_hourly_2026-10_with_mdt.csv` adds `time_utc`, `time_mdt` and `wind_dir_deg` columns; the original columns are unchanged. Cross-checked against the SWOB observations in `../swob_observations.csv` (temperature and humidity match hour for hour once the offset is applied).

**Oct. 17 in MDT:** temperature peaked at 23.3 °C with 16–17% humidity at 2–3 p.m. under 30–32 km/h southwest winds; by 4 p.m. it was 12.9 °C, 43% humidity, 48 km/h from the northwest (310°). Hourly means only; gusts are in the SWOB file.

Data: Environment and Climate Change Canada, Open Government Licence – Canada.
