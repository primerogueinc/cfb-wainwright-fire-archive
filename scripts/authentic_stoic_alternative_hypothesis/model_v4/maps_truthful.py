"""Working model v4: inputs for the 'both DND statements true' map. Usage: python3 maps_truthful.py REPO P4_DIR_PREFIX
For each 40 m cell: P = share of the 120 post-front fires (weighted by fit to the final scar, as weighted.py) reaching it between
3:45 and 4:00 p.m.; D = distance from the 3:16 p.m. starting fire (mean of the four cases). Writes model_v4/maps/truthful_reading.npz
and prints the share of ground 600-1,400 m from the edge reached 3:45-4:00 and the peak P in that band."""
import sys, os, glob, numpy as np, pandas as pd
from scipy import ndimage
REPO, P4 = sys.argv[1], sys.argv[2]; M = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4")
fit = pd.read_csv(os.path.join(M, "fit_post/fit_post_all.csv")); fit["w"] = np.exp((fit.jaccard - fit.jaccard.max()) / 0.05)
P = 0; den = 0; Ds = []
for d in sorted(glob.glob(P4 + "*")):
    case = os.path.basename(d)[len(os.path.basename(P4)):]; minx, maxy, R, H, W = np.load(d + "/meta.npy")
    Ds.append(ndimage.distance_transform_edt(~np.load(d + "/start316.npy")) * R)
    for f in glob.glob(d + "/arr_*.npy"):
        run = os.path.basename(f)[4:-4]; w = float(fit[(fit.case == case) & (fit.run == run)].w.iloc[0]); A = np.load(f)
        P = P + w * ((A >= 45) & (A < 60)); den += w
P = P / den; D = np.mean(Ds, 0); band = (D >= 600) & (D <= 1400)
os.makedirs(os.path.join(M, "maps"), exist_ok=True)
np.savez_compressed(os.path.join(M, "maps", "truthful_reading.npz"), P=P, D=D, m=band & (P >= 0.15), meta=np.array([minx, maxy, R, H, W]))
print("band 600-1400 m: mean share reached 3:45-4:00", round(float(P[band].mean()), 3), " peak", round(float(P[band].max()), 3))
