"""2:49 p.m. burned-area estimate: spread across good-fitting v3 runs, with an outside estimate marked.
Run from the archive repo root:  python3 scripts/maps/g26_area_1449.py <out.jpg>"""
import sys
sys.path.insert(0, "scripts/maps")
from pr import *
import numpy as np, pandas as pd

OUT = sys.argv[1]
d = pd.read_csv(REPO + "data/authentic-stoic-stress-test/model_v3/fit_shape_all.csv.gz")
best = d.misfit_m.min()
g10 = d[d.misfit_m <= best + 10].area_km2_1449.values
g20 = d[(d.misfit_m > best + 10) & (d.misfit_m <= best + 20)].area_km2_1449.values
mu, sd = g10.mean(), g10.std(ddof=1)
p5, p95 = np.percentile(g10, [5, 95])
v3 = {"v3a": 1.42, "v3b": 1.76, "v3c": 1.44, "v3d": 1.49}
HER, HULL = 1.38, 1.94
AC = 247.105

W, H = 1600, 900
im, dr = canvas(W, H, "CFB WAINWRIGHT FIRE · BURNED AREA AT 2:49 P.M., OCT. 17",
                "About 1.5 km² by the afternoon satellite pass",
                f"Burned area at 2:49 p.m. in the best-fitting runs of working model v3 (n = {len(g10)}).\n"
                "Each dot is one run: a different start point, start time, morning speed or fire width.")
dr = ImageDraw.Draw(im, "RGBA")
X0, X1, LO, HI = 120, W - 120, 0.9, 2.3
sx = lambda v: X0 + (v - LO) / (HI - LO) * (X1 - X0)
AY = 640  # axis y

# mean ± 1 SD band
ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
ImageDraw.Draw(ov).rectangle([sx(mu - sd), 250, sx(mu + sd), AY], fill=GOLD + (46,))
im.alpha_composite(ov); dr = ImageDraw.Draw(im, "RGBA")
dr.line([sx(mu), 250, sx(mu), AY], fill=GOLD, width=4)
label(dr, (sx(mu) + 10, 252), f"Our mean {mu:.2f} km²\n±1 SD {mu - sd:.2f}–{mu + sd:.2f} km²", col=GOLD, size=19)

# dots: wider fits (hollow, muted), best fits (filled gold), jittered in rows
rng = np.random.default_rng(7)
def dots(vals, ycen, spread, r, fill, outline):
    for v in sorted(vals):
        y = ycen + rng.uniform(-spread, spread)
        dr.ellipse([sx(v) - r, y - r, sx(v) + r, y + r], fill=fill, outline=outline, width=2)
dots(g20, 470, 34, 7, None, MUTED + (160,))
dots(g10, 540, 30, 10, GOLD, INK)
dr.text((X0, 384), f"Hollow: wider set, fits within 20 m (another {len(g20)} runs)", font=M(17), fill=MUTED)
dr.text((X0, 600), "Filled: best fits, within 10 m of the best", font=B(17), fill=GOLD)

# the four bracketing cases as ticks
for k, v in v3.items():
    dr.line([sx(v), AY - 22, sx(v), AY], fill=CREAM, width=3)

# her estimate
dr.line([sx(HER), 292, sx(HER), AY], fill=TEAL, width=4)
label(dr, (sx(HER) - 10, 294), f"Other estimate\n{HER} km² (342 acres)", col=TEAL, size=19, anchor="ra")

# upper bound from detection outline
dashed(dr, [(sx(HULL), 330), (sx(HULL), AY)], RED, 4, (14, 10))
label(dr, (sx(HULL) + 10, 332), f"Outer limit of the satellite\ndetections {HULL} km²", col=RED, size=19)

# axis
dr.line([X0, AY, X1, AY], fill=MUTED, width=2)
for t in np.arange(1.0, 2.31, 0.2):
    dr.line([sx(t), AY, sx(t), AY + 10], fill=MUTED, width=2)
    dr.text((sx(t), AY + 16), f"{t:.1f} km²", font=B(18), fill=CREAM, anchor="ma")
    dr.text((sx(t), AY + 42), f"{t * AC:,.0f} acres", font=M(16), fill=MUTED, anchor="ma")
dr.text((X0, AY + 100), "White ticks: the four cases in the article", font=M(16), fill=CREAM, anchor="ls")

footer(im, [
    f"Mean {mu:.2f} km² ({mu * AC:.0f} acres), standard deviation {sd:.2f} km² ({sd * AC:.0f} acres), 90% of runs {p5:.2f}–{p95:.2f} km². "
    "This spread is model sensitivity, not measurement error.",
    "Model: CFFDRS O-1a fit to Landsat 8 burned area at 12:17 p.m. and VIIRS detections at 2:49 p.m. Source: Prime Rogue working model v3.",
], fh=120)
im.convert("RGB").save(OUT, quality=92)
print(OUT, len(g10), len(g20), round(mu, 3), round(sd, 3))
