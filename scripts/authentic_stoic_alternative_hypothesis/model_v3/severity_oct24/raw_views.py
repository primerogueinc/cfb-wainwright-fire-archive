"""Plain Sentinel-2 L2A renders (no overlays) of the scar and of a ~1.3 km window around Range 2 and the road head.
True colour = B04/B03/B02 stretched 0-0.16; SWIR false colour = B12/B8A/B04 stretched 0-0.35; gamma 1/1.4; zoomed-in views
upscaled with nearest neighbour (one block = one ~10 m pixel). Usage: python3 raw_views.py COPERNICUS_REPO OUT_DIR"""
import sys, rasterio, numpy as np
from rasterio.windows import from_bounds
from PIL import Image
CP, OUT = sys.argv[1] + "/sentinel-2/", sys.argv[2]
cx, cy = (-110.9063 - 110.8996) / 2, (52.7728 + 52.7705) / 2
VIEWS = {"zoomed-out": (-110.965, 52.735, -110.845, 52.800), "zoomed-in": (cx - 0.0095, cy - 0.0058, cx + 0.0095, cy + 0.0058)}
def win(d, bb, bands):
    out = []
    for b in bands:
        r = rasterio.open(f"{CP}{d}/L2A_tiff/{d}-00_00_{d}-23_59_Sentinel-2_L2A_{b}.tiff")
        out.append(r.read(1, window=from_bounds(*bb, r.transform), boundless=True, fill_value=np.nan))
    return np.dstack(out)
def save(a, lo, hi, path):
    im = Image.fromarray((np.clip((np.nan_to_num(a) - lo) / (hi - lo), 0, 1) ** (1 / 1.4) * 255).astype(np.uint8))
    k = max(1, int(1600 / im.size[0]))
    im = im.resize((im.size[0] * k, im.size[1] * k), Image.NEAREST) if k > 1 else im.resize((1600, int(1600 * im.size[1] / im.size[0])), Image.LANCZOS)
    im.save(path)
for name, bb in VIEWS.items():
    save(win("2026-10-24", bb, ["B04_(Raw)", "B03_(Raw)", "B02_(Raw)"]), 0, 0.16, f"{OUT}/sentinel2-20261024-true-colour-{name}.png")
    save(win("2026-10-24", bb, ["B12_(Raw)", "B8A_(Raw)", "B04_(Raw)"]), 0, 0.35, f"{OUT}/sentinel2-20261024-swir-false-colour-{name}.png")
for d in ("2026-10-04", "2026-10-19"):
    save(win(d, VIEWS["zoomed-in"], ["B04_(Raw)", "B03_(Raw)", "B02_(Raw)"]), 0, 0.16, f"{OUT}/sentinel2-{d.replace('-', '')}-true-colour-zoomed-in.png")
