"""Working model v4: where could the pairs range be, given DND's statements? Usage: python3 location_update.py REPO P4_DIR_PREFIX [TAG]
Starts from the part 2 likely ground (cells weighted by how many of 20 readings of 'about a kilometre' include them) and asks, for
each cell, using the 120 post-front fires weighted by fit to the final scar:
  near   600-1,400 m from the fire's edge when the front reached it ('about a kilometre away when the wind shifted', Oct. 18)
  late   at least 15% of fires reach it 3:45-4:00 p.m. ('overtook the pairs range just before 4:00', Oct. 22)
Reports the share of the likely ground (weighted) meeting each, and the weighted median arrival of the ground meeting each."""
import sys, os, glob, json, numpy as np, pandas as pd
from scipy import ndimage
from pyproj import Transformer
REPO, P4 = sys.argv[1], sys.argv[2]; TAG = sys.argv[3] if len(sys.argv) > 3 else ""; SFX = f"_{TAG}" if TAG else ""
M = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4")
fit = pd.read_csv(os.path.join(M, f"fit_post{SFX}/fit_post_all.csv")); fit["w"] = np.exp((fit.jaccard - fit.jaccard.max()) / 0.05)
zone = pd.read_csv(os.path.join(REPO, "data/authentic-stoic-stress-test/part2/part2_core_frequency.csv")); zone = zone[zone.n_scenarios_in_core > 0].reset_index(drop=True)
tf = Transformer.from_crs(4326, 3400, always_xy=True).transform
late = 0; den = 0; D = []; arr = []; ws = []
for d in sorted(glob.glob(P4 + "*")):
    case = os.path.basename(d)[len(os.path.basename(P4)):]; minx, maxy, R, H, W = np.load(d + "/meta.npy")
    zi = np.array([(int((maxy - tf(x, y)[1]) // R), int((tf(x, y)[0] - minx) // R)) for x, y in zip(zone.x, zone.y)])
    D.append((ndimage.distance_transform_edt(~np.load(d + "/start316.npy")) * R)[zi[:, 0], zi[:, 1]])
    for f in glob.glob(d + "/arr_*.npy"):
        run = os.path.basename(f)[4:-4]; w = float(fit[(fit.case == case) & (fit.run == run)].w.iloc[0]); a = np.load(f)[zi[:, 0], zi[:, 1]]
        late = late + w * ((a >= 45) & (a < 60)); den += w; arr.append(a); ws.append(w)
late = late / den; D = np.mean(D, 0); arr = np.array(arr); ws = np.array(ws)
def wmed_cells(mask):
    if not mask.any(): return None
    a = arr[:, mask].ravel(); w = np.repeat(ws, mask.sum()) * np.tile(zone.n_scenarios_in_core.values[mask], len(ws))
    o = np.argsort(a); m = float(a[o][np.searchsorted(np.cumsum(w[o]) / w.sum(), .5)]); return f"{3 + int(m // 60)}:{int(m % 60):02d}"
zw = zone.n_scenarios_in_core.values.astype(float)
sets = {"all likely ground": np.ones(len(zone), bool), "near (600-1,400 m)": (D >= 600) & (D <= 1400), "late (>=15% of fires 3:45-4:00)": late >= 0.15}
sets["near and late"] = sets["near (600-1,400 m)"] & sets["late (>=15% of fires 3:45-4:00)"]
out = {k: dict(share_of_likely_ground=round(float(zw[m].sum() / zw.sum()), 3), median_arrival=wmed_cells(m)) for k, m in sets.items()}
json.dump(out, open(os.path.join(M, f"location_update{SFX}.json"), "w"), indent=1); print(json.dumps(out, indent=1))
