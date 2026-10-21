# ADS-B aircraft tracks, Oct. 17–18, 2026

Every aircraft position recorded within roughly 60 km of CFB Wainwright from 10 a.m. MDT Oct. 17 to 8 a.m. MDT Oct. 18, extracted from the [adsb.lol](https://adsb.lol) open archive (`adsblol/globe_history_2026`) by `scripts/adsb_tracks.py`. Original trace files are kept unaltered in `oct17/raw_traces/`; `points.csv`, `aircraft.csv` and `low_slow_near_scar.csv` are derived tables.

**Purpose:** to find where air ambulances and other aircraft landed or hovered near the fire on Oct. 17, as a check on where the incident happened.

**Limits:** ADS-B shows only aircraft that broadcast and were heard by volunteer receivers. Military helicopters such as the CH-146 Griffon often do not broadcast, and low-level flight far from a receiver is often missed. A missing track proves nothing. Flight purposes and patients carried are not known from this data.

Data: adsb.lol, [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Times: `utc` and `mdt` (UTC−6) columns.
