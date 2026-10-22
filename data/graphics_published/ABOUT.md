# Graphics published by Prime Rogue, Oct. 17–20, 2026

The graphics used in Prime Rogue's live coverage and analysis pages, kept as published so readers can see exactly what was shown and when. Produced with the code in `scripts/first_analysis/`. © Prime Rogue Inc., CC BY-NC 4.0 (underlying data credited on each graphic; Sentinel imagery: contains modified Copernicus Sentinel data [2026]).

| Group | Files |
|---|---|
| Headers and social cards | `*-header*.jpg`, `yt-*.jpg` |
| Satellite detections | `detection-map`, `satellite-map(-v2)`, `satellite-timeline(-v2)`, `all-passes(-v2)`, `week-of-passes`, `firms-osint`, `firms-timebased`, `methodology` |
| Fire behaviour and weather | `fire-geometry`, `weather`, `weather-oct17`, `fire-danger`, `fire-history`, `s3-burn-scar-prelim` |
| Official account vs records | `said-vs-records`, `dnd-timeline`, `two-readings`, `what-we-know*`, `night-timeline` |
| Response | `aircraft-timeline` (Prime Rogue's timeline of air-ambulance and RCAF movements, built from public flight tracking) |
| `oct20_flank_became_the_front/` | The Oct. 20 analysis "CFB Wainwright: The flank became the front": header, flank-to-front animation (GIF 1000 px, MP4), warning timeline, fire speed per km, why 30 seconds, said vs record (v2), Sentinel-2 before/after, Sentinel-2 burn-scar map, cold front by station, burn pattern vs wind shift. `SHA256SUMS` lists their hashes. |
| `early_goes_frames/` | Individual GOES-18 frames, 2:40–4:20 p.m. MDT, from the first GOES analysis. |
| `sentinel2_views/` | Sentinel-2 view crops (true colour, false colour, SWIR, NDVI, moisture, wildfire) used in early graphics. |

**Read with later findings in mind.** These are dated snapshots. Several early graphics (`satellite-header*`, `night-timeline`, `what-we-know*`) refer to an "explosion" or "blast," reflecting reports on Oct. 17–18 that remain unconfirmed; the Canadian Armed Forces have said there is no evidence of an explosion. The preliminary burn area in `s3-burn-scar-prelim` (~8 km² from Sentinel-3) was superseded by the Sentinel-2 measurement of about 10.8 km² (`data/copernicus/`).

The GOES contact sheet and loop are in `data/goes/early_subsets_goes18/`. Two flight-tracking graphics built from Flightradar24 screenshots are not included here pending a rights check.

**Burn-scar threshold in the Oct. 20 graphics.** `s2-burn-scar-map` and `burn-pattern` used a dNBR threshold of 0.2 on Sentinel-2 L1C browser exports, connected to the Oct. 17 detections (about 11 km² main run, 1.5 km² inside the 2:49 p.m. pixels, about 9.6 km² outside). The automated pipeline in `data/copernicus/` uses L2A surface reflectance with a stricter 0.27 threshold and gives about 10.8 km². The two agree within the expected range; the archived figure is the more conservative one.

Note: graphics published before October 21, 2026 show "CC BY 4.0" in their credit line because that was their licence when released. They are kept unaltered as published; see `LICENSE-DATA` for the current licence and the terms that still apply to those copies.
