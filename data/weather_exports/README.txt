CFB Wainwright fire, Oct. 17, 2026: weather data in the Prime Rogue archive, as one workbook.
Compiled by Prime Rogue Inc. from public data. Each sheet is also posted as a CSV with the same content.

TIME ZONES. On Oct. 17, 2026 local clock time in Wainwright was MDT = UTC - 6. 21:16 UTC = 3:16 p.m.
Some sources use Local Standard Time, LST = UTC - 7, all year. LST hours read one hour EARLIER than the clock that day.
Every time column is labelled with its zone. Times in a source's own zone are kept, and the others are calculated from it.

SHEETS
CZWN obs Oct 17: base weather station (Wainwright CFB Airfield 21), hourly SWOB observations from the MSC Datamart. Source times are UTC. Each row's gust columns give the strongest gust in the hour BEFORE that observation: the 82 km/h gust at 21:16 UTC (3:16 p.m. MDT) is in the 22:00 UTC row (highlighted). Rows at 02, 10, 12 and 16 UTC were not in the pull and are not filled in.
CYLL obs Oct 17: Lloydminster airport, the three SWOB hours pulled (2-4 p.m. MDT). Gust time not reported in these files.
Climate hourly Oct 2026: Environment Canada historical climate archive, station 301S001, all of October. Published in LST (UTC - 7). time_utc and time_mdt are added. Hourly means only, no gusts. Oct. 17, 1-5 p.m. MDT highlighted. Matches the SWOB hour for hour once the offset is applied.
Wainwright forecasts+warnings: every public forecast (FPCN16 English, FPCN76 French, FPCN54/58 extended) and wind warning (WWCN16/76) naming Wainwright, Oct. 16-18. issued_utc comes from the bulletin's file name. time_printed_on_bulletin is the time Environment Canada prints in the text. Scheduled forecasts carry the scheduled time, which can differ from transmission: the forecast transmitted at 4:30 a.m. MDT on Oct. 17 (10:30 UTC) is printed as '5:00 A.M. MDT' (highlighted, with the warnings).
All bulletins Oct 16-18: index of every bulletin retrieved from the Prairie and Northern storm-prediction offices.
Fire Weather Index: NRCan CWFIS daily values for the stations nearest the base. Computed from noon LST observations = 1 p.m. MDT. Alberta classes: Extreme at FWI 29.5 and above.

SOURCES. Environment and Climate Change Canada (MSC Datamart; Historical Climate Data). Natural Resources Canada (CWFIS). Open Government Licence - Canada.
Originals and scripts: https://github.com/primerogueinc/cfb-wainwright-fire-archive (branch authentic-stoic-alternative-hypothesis), data/eccc and data/nrcan_cwfis.

CSV files: 1_czwn_swob_oct17.csv, 2_cyll_swob_oct17.csv, 3_climate_hourly_czwn_oct2026.csv, 4_wainwright_forecasts_warnings.csv, 5_all_bulletins_index.csv, 6_fwi_nearby_stations_oct10-18.csv
