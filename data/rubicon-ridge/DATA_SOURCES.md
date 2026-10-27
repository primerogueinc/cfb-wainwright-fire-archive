# Rubicon Ridge: data sources

Rubicon Ridge is the next model of the Oct. 17, 2026 CFB Wainwright fire. It succeeds the "authentic stoic" stress test and its working models v1-v4 (`data/authentic-stoic-stress-test/`), which stay as published.

Status, Oct. 26, 2026: planning. Rubicon Ridge keeps every v4 input and adds the ones below. Each row says what it is for and where it is (or will be) archived. Nothing here changes a published number until Rubicon Ridge is run.

## Carried over from v4

| Input | Source | Archived copy |
|---|---|---|
| Station weather and the 3:16 p.m. gust | Environment and Climate Change Canada, CFB Wainwright (CZWN): raw SWOB records (MSC Datamart) and hourly climate data | `data/weather_exports/` |
| Fire position at 12:17 and 2:49 p.m. | NASA FIRMS: Landsat 8, VIIRS NOAA-20 | `data/firms/detections.csv` |
| Fire power through the afternoon (timing check) | NOAA GOES-18/19 ABI fire detection (FDC), NOAA open data on AWS | `data/goes/fire_timeline.csv` |
| Fuel moisture codes | NRCan CWFIS daily FWI | `data/nrcan_cwfis/` |
| Final burn (fitting) | Copernicus Sentinel-2 L2A, Oct. 4 and 19 | `data/copernicus/manual_exports/`, `data/infrastructure/scar_patches_revised.geojson` |
| Burn-edge checks | USGS Landsat 8, Oct. 24; Sentinel-2, Oct. 24 | `data/authentic-stoic-stress-test/model_v4/edge/` |
| Terrain | NRCan MRDEM-30 | `data/dem/` |
| Tracks, ranges and danger areas (unofficial) | OpenStreetMap contributors (ODbL) | `data/infrastructure/osm_infrastructure_ODbL.geojson` |
| Fire spread | Canadian FBP System, fuel type O-1a (Forestry Canada 1992, ST-X-3) | in code |

## New in Rubicon Ridge: added

| Input | Source | Archived copy | Use |
|---|---|---|---|
| **Official range locations** | 3 CDSB Edmonton Det Wainwright Range and Training Area Standing Orders, 2024 edition (ch. 1 para 51; Annex H), grid references converted from MGRS zone 12U | `data/reference/range_standing_orders_2024/rso_points.csv` and `.geojson`; analysis in `README.md` there | Replace the OSM "Range 2 point" with the official Range 2 grid; add Range 15 (Field Firing Range) and its barrier at "Yellow and Fireguard" (20 m from the road head) as scenario points; place Range 11 (grenade launcher) for the ignition search. The document itself is not in the repository. |
| **Range rules** | Same document: fire hazard conditions (para 339-342), ground cover fires (343-345), weather warnings (214-216), Range Control check-fire powers (para 7), cattle in impact areas (170-171) | quoted in the RSO `README.md` | Context and scenario design: ignition timing in an early-morning shoot (para 342); fires in impact areas left to burn (344c); grazing as a fuel factor (170-171). |
| **Spring 2026 planned burn** | Long-term burn inventory (Landsat dNBR), Apr. 20-21, 2026, read as a likely planned burn; DND spring burn window Apr. 10-May 5, 2026 | `data/fuel/burn_2026-04-20_pda2.geojson` | Separate fuel class: six months of regrowth on about 986 ha, 477 ha of which burned again on Oct. 17 (around the road head and Range 15). Test a lower spread rate there and refit to the scar. |

## New in Rubicon Ridge: requested (pending network access or keys)

| Input | Source | Why |
|---|---|---|
| Weather stations nearer the fire | Alberta Climate Information Service (ACIS), provincial fire-weather stations | When the front reached the fire itself, not the airfield 13-15 km away (the 3:16 vs 3:25 question) |
| Weather radar | ECCC radar covering Wainwright (archived scans may need a request to ECCC) | Gust-front movement and the smoke plume's timing |
| Raw GOES imagery | NOAA GOES-18/19 ABI radiances (visible, 3.9 and 11 µm), every 10 min; check for 5-min or 1-min regional scans | Plume direction and sub-threshold heat between 3:10 and 3:30 |
| Smoke in town | Alberta government air-quality monitors; PurpleAir sensors (API key) | Independent time for smoke reaching Wainwright |
| Sentinel-3 fire power | Copernicus Sentinel-3 SLSTR FRP product (Copernicus Data Space account) | Another heat measurement if a pass covered Oct. 17 |
| Wind at the fire's location | NOAA RAP reanalysis; ECCC HRDPS | Model wind at the fire, as a check on the front's arrival |
| Every satellite pass | NASA FIRMS, all sensors (NOAA-21, S-NPP, Terra, Aqua, VIIRS 750 m) | Confirm no pass was missed on Oct. 17 |

## Records requested from DND (ATIP / request for comment)

Daily Range Standing Orders for Oct. 16-17; the Fire Chief's report under CFAO 30-2; fire hazard condition settings Aug.-Oct. 2026; CFRIS bookings and danger area overlays for Ranges 2, 11 and 15; the spring 2026 burn plan; the PDA 2 grazing schedule; whichever Range Standing Orders edition was in force on Oct. 17.
