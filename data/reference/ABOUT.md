# Reference data re-fetched Oct. 21, 2026

Inputs used in the first analysis (Oct. 19–20, 2026) whose original downloads were not kept, fetched again from the same public sources by `scripts/refetch_reference_data.py` (workflow "Refetch reference data"). National files are clipped to the area around the base (52.55–52.98°N, 110.45–111.35°W); only the clipped subsets are kept. Log: `refetch.log`.

| Path | Source | Contents |
|---|---|---|
| `eccc_hourly_oct2026/` | Environment Canada historical climate data (climate.weather.gc.ca), hourly, Oct. 2026 | Edmonton International (two station records), Camrose, Vegreville, Coronation, CFB Wainwright Airfield 21 and Lloydminster (two records). `stations.csv` lists IDs and coordinates. Times are **Local Standard Time (UTC − 7): add one hour for MDT**. The CFB Wainwright file matches `data/eccc/climate_hourly/` row for row. |
| `cgndb_geonames_near_site.csv/.json` | NRCan Canadian Geographical Names Database | Official names near the site, including Jamieson Lake (52.755°N, 110.915°W), Peterson Pond (52.787°N, 110.903°W), Williamson Lake and Mott Lake. |
| `canvec50k_transport_near_site.geojson` | NRCan CanVec 1:50,000, Alberta, Transport | Roads, trails, railway, runways. |
| `canvec50k_res_mgt_near_site.geojson` | CanVec, Resource management | Petroleum wells, pipelines, power lines, transformer stations, valves. |
| `canvec50k_manmade_near_site.geojson` | CanVec, Man-made features | Buildings, towers, tanks, storage, dams, landmarks. |
| `aer_pipelines_near_site.geojson` | Alberta Energy Regulator pipeline dataset (static.aer.ca) | All AER-licensed pipeline segments in the area, with licence, licensee, substance and status attributes. |

**Cold-front timing from these stations** (first hourly observation showing a drop of 4 °C or more, converted to MDT): Edmonton International 2 p.m.; Camrose and Vegreville 3 p.m.; CFB Wainwright, Coronation and Lloydminster 4 p.m. Each time is the first observation *after* the front passed; the CFB Wainwright SWOB record (`data/eccc/`) pins its passage at the 3:16 p.m. peak gust.

Licences: ECCC and NRCan data, Open Government Licence – Canada; AER data, published by the Alberta Energy Regulator (credit "Alberta Energy Regulator"). Clipping and notes: Prime Rogue Inc., CC BY-NC 4.0.
