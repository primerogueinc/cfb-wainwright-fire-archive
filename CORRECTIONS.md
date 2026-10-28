# Corrections

Prime Rogue corrects errors in this archive in new commits, so the history shows what changed and when. The working-model v4 material is also preserved exactly as published under the [`v4-published`](https://github.com/primerogueinc/cfb-wainwright-fire-archive/tree/v4-published) tag. Later work is in [part 2](https://github.com/primerogueinc/cfb-wainwright-fire-archive-2), which carries the same list.

## Oct. 28, 2026

| # | What we published | Correct figure | Where fixed |
|---|---|---|---|
| 1 | The cold front reached the fire at 3:16 p.m. (v4; Range Standing Orders analysis) | About **3:28 p.m.** (3:27–3:29). 3:16 is the gust at the CFB Wainwright station (CZWN), not at the fire. Working model v5 fits a moving front to nine stations and sensors: toward 114.5° at about 77 km/h. Arrival at the official Range 2 grid moves to about 3:39 (3:34–3:51), Range 15 about 3:42 (3:36–3:58). | Notes added to `data/authentic-stoic-stress-test/model_v4/ABOUT.md`, `part7_briefing_check/ABOUT.md`, `data/reference/range_standing_orders_2024/README.md` (finding 4). Details: part 2, `data/rubicon-ridge/model_v5/ABOUT.md`. |
| 2 | The CZWN station is "about 12 km", "about 13 km", "13–15 km" or "about 15 km west" from the fire | **14.7 km west-northwest** (bearing 299° from the fire centre, 52.7645 N, 110.9052 W, to CZWN, 52.8294 N, 111.0956 W) | `data/eccc/ABOUT.md`, `data/rubicon-ridge/DATA_SOURCES.md`, `part7_briefing_check/ABOUT.md`; v4 note |
| 3 | GOES pixels about 2 km across | **Several km: about 2.6 × 5 km** for the 3.9 µm heat channel at the fire, because of the steep viewing angle. 2 km is the nominal size. | `data/rubicon-ridge/derived/goes_visible/README.md` (both repos) |
| 4 | Several burn-area totals (11.71, 11.54, 10.79 km²) | **About 1,050–1,100 ha for the Oct. 17 burn.** 11.71 km² is the raw dNBR output (31 patches); 11.54 km² is the 8 revised patches, including a 0.57 km² patch that matches the Oct. 14 fire; 10.79 km² is the Oct. 17 main run on Sentinel-2. The 70 cm Oct. 20 outline gives 1,049.8 ha net of unburned islands inside the image, about 1,075 ha for the whole burn. Method: `docs/METHODS.md` ("Revised scar"). | This file |
| 5 | DND's "approximately 4:00 p.m." release was dated Oct. 17 | **Dated Oct. 18** | `part7_briefing_check/ABOUT.md` |

**Wording, same date:** Environment Canada's 2:14 p.m. bulletin did not issue a new warning; it added Wainwright to a wind warning in force for areas to the west since 11:42 a.m. (`data/eccc/ABOUT.md`).

Errors can be reported as issues, or privately through the channels in the README.
