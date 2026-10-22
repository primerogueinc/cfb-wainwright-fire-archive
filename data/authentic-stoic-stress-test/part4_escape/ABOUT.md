# The Authentic Stoic Stress Test, part 4 (preliminary): could they have got out?

*Run Oct. 22, 2026. Prime Rogue Inc. Prompted by @AuthenticStoic: "they would've ran half a mile east and been safe if that's the case, no?"*

**Status: preliminary.** Not yet reviewed or published.

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
