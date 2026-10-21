# Derived tables from the first analysis (Oct. 19–20, 2026)

Working tables built during Prime Rogue's first reconstruction, kept as produced. Most have since been rebuilt by the automated pipeline; where both exist they agree.

| File | What it is | Later / fuller version |
|---|---|---|
| `cfb-wainwright-afternoon-fwi-calc.txt` | **Hour-by-hour Fire Weather Index for the afternoon of Oct. 17** at CFB Wainwright, computed by Prime Rogue (Van Wagner 1977 hourly FFMC from the CWFIS noon value; standard ISI/FWI equations; BUI 77.6 from CWFIS). The noon check reproduces CWFIS exactly (ISI 11.6, FWI 30.8). Results: 1 p.m. FWI 31.1; **2 p.m. 53.6; 3 p.m. 59.4; 4 p.m. (after the front) 91.4**, higher with gusts. Alberta's "Extreme" class starts at 29.5. Times are MDT (converted from ECCC's standard-time stamps). This is Prime Rogue's calculation, not an official product. | – |
| `cfb-wainwright-goes-fdc-oct17.csv` | NOAA GOES-18 Fire Detection product, every scan Oct. 17, nearest pixel to the site plus fire pixels: 3:10 p.m. (76.5 MW), 3:30 p.m. (three pixels, 278 + 517 + 420 MW), 3:40 p.m. (336 MW). | `data/goes/fire_timeline.csv` (identical pixels and values) |
| `cfb-wainwright-goes18-band7-oct17.csv` | GOES-18 3.9 µm brightness temperature at the site and the strongest local anomaly within ~10 km, 2:40–4:20 p.m. Peak anomaly 39.9 K at 3:30 p.m. | `data/goes/early_subsets_goes18/` |
| `cfb-wainwright-hms-fire-oct13-18.csv` | NOAA HMS fire points within ~40 km. | `data/noaa_hms/hms_fire_points_within_40km.csv` |
| `cfb-wainwright-cwfis-fwi-oct10-18.csv` | CWFIS daily fire-weather values for the CFB Wainwright station. | `data/nrcan_cwfis/` |
| `cfb-wainwright-firms-history-3km-2012-2026.csv` | FIRMS detections within 3 km of the site since 2012. | `data/firms/history_2012-2026/` |
| `cfb-wainwright-aer-wells-12km.csv` | Alberta Energy Regulator ST37 wells within 12 km of the site (licence, licensee, status, dates, coordinates). Licensee names are as published by the AER, including historical individual licensees. | `data/infrastructure/wells_within_5km_of_scar.csv` |
| `cfb-wainwright-geography-notes.txt` | Geography checks: official place names (Jamieson Lake, Peterson Pond, Williamson Lake), roads near the Oct. 18 detections, wells and pipelines near the site. | See note below. |

**Superseded in the geography notes:** the notes say no available data showed the base boundary near the Oct. 18 detections. The boundary is now mapped in OpenStreetMap and on the Government of Alberta's Camp Wainwright hunt map; both put the Oct. 18 detections just east of the boundary road (CYR203), outside the base (see `data/infrastructure/` and `data/topo/`). The notes also mention a blog post naming Peterson Pond and Jamieson Lake; that source is unverified.

Three tables in the original bundle were exact copies of files already archived and are not repeated here: the ECCC hourly CSV (`data/eccc/climate_hourly/wain_hourly_2026-10.csv`), the SWOB extract (`data/eccc/original/as_pulled_oct19/ecc_raw_oct_17/cfb-wainwright-swob-czwn-oct17.txt`) and the FIRMS detections table (`data/firms/manual_downloads_v2/cfb-wainwright-firms-detections.csv`; its "-v2" copy was identical).

Sources: NASA FIRMS, NOAA, ECCC, NRCan, AER (open data, see each folder). Tables and calculations: Prime Rogue Inc., CC BY 4.0.
