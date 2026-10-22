# The Authentic Stoic Stress Test, part 4 (preliminary): could they have got out?

*Run Oct. 22, 2026. Prime Rogue Inc. Prompted by @AuthenticStoic: "they would've ran half a mile east and been safe if that's the case, no?"*

**Status: preliminary.** Not yet reviewed or published. The full permutation run below supersedes the first-pass table.

## Method

For each scenario point (A–E, part 3) we tested straight-line routes on foot in 72 directions. For each route we found the latest departure time that still reaches safe ground before the fire.

**Safe ground** is either:
- outside the mapped burn (plus 150 m), or
- ground that had burned at least 5 minutes earlier ("the black").

**Fire arrival** comes from the scar-limited spread runs (8 km/h head spread, front at 3:16 p.m., five wind schedules). A route fails if the fire reaches any point on it within 0.5 minutes of the walker. A second run uses a 3-minute margin.

**Pace:** walk 5 km/h, jog in kit 8 km/h, run 10 km/h. Pace is adjusted for slope (Tobler hiking function on NRCan MRDEM-30).

**Files:**
- `part4_escape.csv` and `part4_escape_margin3.csv`: best route per point and pace.
- `part4_routes.csv`: fixed directions from A and B.

## Preliminary findings (jog in kit, 3-minute margin)

| | Fire arrives | Latest departure | Best direction | Route to safety |
|---|---|---|---|---|
| A, Range 2 | 3:21–3:26 | 3:18–3:23 | East to northeast (60–110°) | 0.6–2.4 km |
| B, road's end | 3:25–3:34 | 3:22–3:31 | East (75–115°) | 0.2–2.0 km |
| C, Jamieson Lake strip | 3:22–4:06 | 3:18–4:03 | South to southwest (185–215°) | 0.7–0.9 km |
| D, range road south | 3:28–4:06 | 3:25–4:03 | East to southeast | 1.8–2.0 km |
| E, south-central run | 3:34–4:36 | 3:31–4:33 | Southeast to southwest | 0.2–0.8 km |

**From A and B,** going back through the flames into the black (northwest) needs 17–34 minutes' notice. Going east or northeast, crosswind to the unburned edge, needs only minutes.

## What it suggests

On this model, people at the most likely locations could have reached unburned ground by heading east, crosswind, if they set off within a few minutes of the 3:16 p.m. gust front. That supports @AuthenticStoic's point.

That four people died and dozens were hurt therefore points to one or more of the following:
- **Not knowing where to go,** or seeing the fire too late. Part 3: flames were in sight only 3–11 minutes before arrival at A and B.
- **Fire behaviour at the edge far worse than this model allows:** smoke, embers, gust-driven surges along the flank.
- **People deeper inside the burn** than A or B.

## Limits (significant)

The model is optimistic for escape:
- **No smoke, visibility loss, embers or spotting.**
- **Uniform grass fuel,** with no barriers.
- **A smooth elliptical spread** with a slow flank.
- **Straight routes,** perfect knowledge of direction, and no time to react or to gather people or vehicles.

Treat the departure times as best-case upper bounds, not as a finding that escape was easy.

---

## Full permutation run (supersedes the first-pass table above)

### Fire

30 spread scenarios:
- **5 wind schedules:** S0–S4, as in the alternative-hypothesis test.
- **3 head-spread rates:** 4.4, 8 and 12 km/h.
- **2 flank behaviours:** steady (length-to-breadth ratio 6.6) and gusty, surging flanks (ratio 3.0).

The front reaches the fire at 3:16 p.m. Spread is limited to the mapped scar plus 150 m. Script: `gen_grids.py`.

### People

Script: `perm.py`.

| Factor | Values |
|---|---|
| Location | A–E |
| Cue to move | the 3:16 gust front; first new flames in sight (terrain line of sight, eye 1.7 m, flames 4 m); fire within 300 m |
| Delay after the cue | 0, 2, 5 or 10 minutes (milling, gathering people, awaiting orders) |
| Pace | jog in kit 8 km/h; walk 5 km/h; slowed by smoke 3 km/h; helping the injured 2 km/h |
| Direction | best route; crosswind east (90°); directly away from the fire (downwind at the moment of leaving); south or north along the range road; random direction |
| Safety margin | reach safe ground 3 minutes (main) or 0.5 minutes before the fire |

**Outcome:** the share of the 30 fire scenarios in which the person reaches safe ground. Full results are in `perm.csv.gz`. Odds by departure minute for A and B are in `clock.csv`.

### Findings at A (Range 2) and B (road's end)

Jogging in kit, 3-minute margin.

| Cue, delay | A, best route | A, away from fire | A, random | B, best route | B, away from fire | B, random |
|---|---|---|---|---|---|---|
| 3:16 gust, +0 | 80% | 60% | 27% | 100% | 80% | 54% |
| Flames in sight, +2 | 43% | 37% | 16% | 73% | 60% | 33% |
| Flames in sight, +5 | 30% | 30% | 10% | 47% | 40% | 21% |
| Fire within 300 m, +2 | 10% | 10% | 3% | 20% | 17% | 6% |
| Any cue, +10 | 0–10% | 0–10% | 0–2% | 0–40% | 0–33% | 0–20% |

Smoke (3 km/h) roughly halves these. Helping an injured person (2 km/h) cuts them further: 10% at A for the best route, flames-in-sight cue with a 2–5 minute delay.

Gusty, surging flanks also lower the odds. At A, the best route after flames in sight with a 2-minute delay falls from 53% (steady) to 33% (gusty).

Heading north along the range road, or back northwest, almost never works (0% at A; 0–33% at B). Those routes lead back into the fire's path.

### What it suggests

1. **Timing dominated direction.** At A, the best route at the 3:16 gust succeeds 80% of the time. Waiting until the fire was within 300 m drops it to 43% with no delay and 10% with a 2-minute delay.
2. **A gap of a few minutes is the difference.** Disaster research finds people rarely "panic". They seek information, gather with others, and use familiar routes (Sime 1984, the affiliation model). A unit waiting for orders behaves the same way. On this model, those ordinary delays were enough to close the window.
3. **Smoke, injury and gusts are each enough on their own** to turn a likely escape into an unlikely one.
4. **Direction mattered less than timing,** but the familiar route north along the road was among the worst.

### Behavioural and safety references used to set the factors

- **Sime, J.D. (1984).** *Escape behaviour in fires: 'panic' or affiliation?* PhD thesis, University of Surrey. People act on the information they have, prefer familiar routes, and seek out their group.
- **Page, W.G. & Butler, B.W. (2017).** *An empirically based approach to defining wildland firefighter safety and survival zone separation distances.* International Journal of Wildland Fire 26: 655–667. Grass fires need far more separation than the old 4× flame-height rule implies.
- **Smoke reduces walking speed sharply** (e.g., Frantzich & Nilsson 2004, smoke-filled tunnel experiments, Lund University). Our 3 km/h smoke pace sits within the reported range.

### Limits

- Best case for escape:
  - **No embers, spot fires, smoke inhalation or heat injury** before the fire front arrives.
  - **Uniform grass** with no fences, berms or vehicles.
  - **Straight-line routes** only.
- **Line-of-sight cues** use a 30 m terrain model.
- **Locations are estimates** (parts 2–3).
- **Power lines and fences** ("high lines") are not in the model. None are mapped near A or B in OpenStreetMap, which needs checking.
