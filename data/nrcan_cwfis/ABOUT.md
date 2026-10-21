# NRCan Canadian Wildland Fire Information System (CWFIS), Oct. 10–18, 2026

| Path | Contents |
|---|---|
| `original/fwi_2026MMDD.csv` | Daily national fire-weather station files from CWFIS (Natural Resources Canada): noon weather and the Canadian Forest Fire Weather Index (FWI) System codes (FFMC, DMC, DC, BUI, ISI, FWI, DSR) for every reporting station. Unchanged. |
| `original/cwfis-fire-danger-agency-classes.pdf` | CWFIS table of how each province converts FWI values to fire-danger classes (current as of July 24, 2026). |
| `fwi_nearby_stations_oct10-18.csv` | Extract for the stations nearest the base (CFB Wainwright Airfield 21, Lloydminster, Vermilion, Edgerton), with Alberta's fire-danger class added. |

**Alberta's classes (from the PDF):** Low FWI < 4.5; Moderate 4.5–10.5; High 10.5–18.5; Very High 18.5–29.5; **Extreme ≥ 29.5**.

**CFB Wainwright station (Airfield 21), daily values:**
- Oct. 14 (day of the VIIRS hotspot in the training area): FWI 15.6, **High**.
- Oct. 16: FWI 16.3, High.
- **Oct. 17: FWI 30.8, Extreme** (noon temperature 20.2 °C, humidity 23%, wind 14.7 km/h from 225°; FFMC 91.8, DC 461.5). Lloydminster 39.2 and Vermilion 31.9, both Extreme.
- Oct. 18: FWI 37.4, Extreme.

These are the national system's numbers for the base's own weather station. A CAF Strategic Joint Staff memo reported by Global News and the Globe and Mail described the fire index on Oct. 17 as "low"; which scale it used is not public.

FWI codes are computed from noon Local Standard Time observations (1 p.m. MDT), so they describe the afternoon's dryness, not the 3:16 p.m. wind peak. Data: Natural Resources Canada, Open Government Licence – Canada. Extract and notes: Prime Rogue Inc., CC BY 4.0.
