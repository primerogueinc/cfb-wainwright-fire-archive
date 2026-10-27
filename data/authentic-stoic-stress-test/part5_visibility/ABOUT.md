# Part 5: What could they see?

Tests three things that could have hidden the fire from people on the likely ground (part 2 zone, 600 cells weighted by how many of 20 readings include them).

## 1. Dust
- IEM METAR archive, Oct. 17: no BLDU/DU/FU codes at CYEG, CYLL or CYQF. CYLL (Lloydminster) logged the front at 15:49 MDT (28038G53KT, vis 15 SM, then 10 SM).
- ECCC dust storm warnings (1:30, 2:06, ended 2:38 p.m.) named Lamont, Two Hills, Minburn/Vegreville and Leduc–Camrose–Tofield. None named Wainwright.
- CZWN (Wainwright) has no visibility sensor. Local dust raised by the fire and the gust front cannot be ruled out. GOES-West Dust RGB was not checked (not yet fetched).

## 2. Vegetation
- Meta/WRI 1 m canopy height (resampled to 10 m) and ESA WorldCover 2021.
- Likely ground: 89% grassland, 10% cropland, 1% trees; no cells with canopy ≥2 m. Canopy along sightlines to the pre-shift fire edge changed results by ≤1 point, even treated as opaque.
- Posture and cured grass (0.6 m, blocks after 30 m of ray inside it), flames 2.5 m at the pre-shift edge (posture_visibility.csv):
  - standing: 58% see the edge (52% with grass)
  - kneeling: 52% (45%)
  - prone: 44% (32%)
- With 6 m flames: standing 68% (64%), prone 56% (41%).

## 3. Smoke
- smoke.py: Gaussian line source, Briggs class D, Byram convection number, Koschmieder K=3 (dark objects), K=8 (flames), MEE 4.5 m²/g.
- Nc 0.24–1.18: wind-driven, so a ground-hugging plume is plausible. Low case: dark-object visibility about 15–75 m at 200–500 m downwind; flames about 2.7× that. Lofted case: no ground smoke.
- The likely ground lies downwind of the fire after the shift by construction, so it sat in the smoke path.

## Caveats
Canopy data predate 2026. Grass height is assumed. Smoke is modelled, not observed. Visibility of glow, sound and smoke columns above the horizon is not modelled; people may have seen the smoke column even where flames were hidden.
