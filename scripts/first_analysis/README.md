# First-analysis code (Oct. 18–20, 2026)

The scripts behind Prime Rogue's first published analysis and graphics, kept as written. Licensed MIT like the rest of `scripts/`. For current, reproducible processing use the scripts one level up (`firms_archive.py`, `goes_loops.py`, `sentinel2_burn.py`, `eccc_parse.py`, `infrastructure_map.py`, `topo_overlay.py`).

| Group | Scripts |
|---|---|
| Data retrieval | `pull.py` (FIRMS area API; set your own key in `K`), `sub.py` (GOES subsets by HTTP range request), `dl.sh` (NOAA S3 bulk download), `rget.sh` (recursive MSC Datamart download) |
| Calculations | `fdc.py` (GOES fire product at the site), `fwi.py` (hourly Fire Weather Index from noon CWFIS codes; see `data/derived_tables_oct19-20/cfb-wainwright-afternoon-fwi-calc.txt`) |
| Graphics | `g1_hero.py`–`g6_header.py`, `make_*.py`, `render.py`, `style.py`: headers, timelines, weather and fire-danger charts, detection maps, Sentinel-2 maps, collages and social cards |

**Running them:** paths are hard-coded to the original working folder (`/home/claude/...`, `/mnt/user-data/uploads/...`) and some read the Prime Rogue logo, which is not included. Edit the paths before running.

**Read with later findings in mind:** a few graphics scripts (`make_know*.py`, `make_method.py`, `make_night.py`, `make_passes*.py`) carry text written on Oct. 17–19 that refers to a reported explosion. Those reports are unconfirmed, and the Canadian Armed Forces have said there is no evidence of an explosion.
