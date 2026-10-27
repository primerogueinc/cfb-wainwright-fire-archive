# The Authentic Stoic Stress Test, part 3: terrain and sightlines

*Run Oct. 22, 2026. Prime Rogue Inc. The series is named for X user @AuthenticStoic, who asked about terrain: "Running away in flatlands is a lot easier than running away uphill."*

## Question

Did the ground change how the fire moved, what people could see, or where they could go?

## Data

**Elevation:** NRCan MRDEM-30, a bare-earth model at 30 m, from `data/dem/`. It was checked against Copernicus GLO-30.

NRCan's lidar (HRDEM) does not cover the burn scar. The only tile is next to it.

## Findings

### 1. The ground is gentle

| Measure | Value |
|---|---|
| Elevation range across the scar | 650–690 m (about 40 m) |
| Typical slope | 2–3° |
| 95% of slopes under | 6–7° |
| Steepest | about 11° (MRDEM) to 18° (Copernicus) |

Nothing like the steep, chimney-like terrain behind eruptive "blow-up" fires such as Kornati (2007). Slope has only a small effect on spread here.

### 2. A low rise hides part of the likely area

A north–south ridge of about 680 m runs south from Range 2 (OSM centroid, 679 m). East of it is a shallow hollow (about 669 m) at the end of the range road.

We traced sightlines from a standing person (eye height 1.7 m) to the fire's edge before the wind shifted, assuming flames of 2.5 m or 6 m. Files: `zone_visibility.csv` and `zone_visibility_flames6m.csv`.

| Ground (part 2 readings in agreement) | Could see the fire's edge, 2.5 m flames | 6 m flames |
|---|---|---|
| Any reading (1+ of 20) | 67% | 79% |
| Most likely (8+ of 20, 0.17 km²) | **37%** | **54%** |

So 46–63% of the likeliest ground was out of sight of the fire's edge. Nothing on this ground could hide the smoke column, or the gust front's arrival at 3:16 p.m.

### 3. The five scenarios

`scenario_visibility.csv`. Times span five wind schedules at 8 km/h head spread, with the front at 3:16 p.m.

**"Flames in sight"** is the time from when newly burning ground first comes into view to when the fire arrives at the point.

| | Location | Elevation | Fire arrives | Flames in sight | Unburned ground |
|---|---|---|---|---|---|
| A | Range 2 (OSM), on the rise | 679 m | about 3:20–3:25 | 3–8 min | 62 m |
| B | Road's end, in the hollow | 669 m | about 3:24–3:34 | 5–11 min | next to it (outside the scar by about 20 m) |
| C | Strip north of Jamieson Lake | 675 m | about 3:21–4:05 | 4–49 min | 337 m |
| D | Range road, south | 672 m | about 3:28–4:05 | 6–35 min | 738 m |
| E | South-central run | 653 m | about 3:34–4:36 | 2–6 min | next to it |

## What it means

- **No steep-terrain blow-up.** The Kornati-type explanation is very unlikely.
- **Little sight of the flames.** If C Company was in the most likely area, many people there probably could not see the fire's edge from the ground. They would have seen flames only minutes before the fire arrived.
- **Safe ground was close.** Unburned ground lay within tens of metres for scenarios A and B, which sharpens @AuthenticStoic's escape question. That is part 4.
- **The terrain shortened the time to see flames, not the time to know.** Smoke, the 3:16 gust and the day's warnings were not hidden by a 10 m rise.

## Limits

- **Coarse model.** At 30 m, berms, vehicles, vegetation and small hollows are not represented.
- **Assumed heights.** Flame height (2.5–6 m) and eye height are assumptions. Our fire models give flame lengths of roughly 4–8 m after the shift.
- **Locations are estimates** (part 2). DND has not confirmed any of them.
- **Model times.** Arrival and warning times come from a simplified spread model with no barriers or suppression.
- **OSM range polygons** are volunteer-mapped and not verified by DND.
