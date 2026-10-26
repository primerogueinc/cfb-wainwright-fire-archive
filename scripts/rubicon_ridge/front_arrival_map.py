"""Simple map: when the Oct. 17, 2026 cold front reached each station / sensor (MDT), with fitted arrival lines."""
import numpy as np, geopandas as g, matplotlib, subprocess
matplotlib.use("Agg"); import matplotlib.pyplot as plt
# name, lat, lon, minutes after 15:00 MDT, source, label offset (dx, dy in deg)
P = [("CFB Wainwright weather stn", 52.8294, -111.0956, 16, "ECCC", (-0.05, 0.05), "r"),
     ("Albert Hall", 53.1134, -111.1812, 2, "AB Ag", (0.05, 0.03), "l"),
     ("Bellshill", 52.5824, -111.4654, 2, "AB Ag", (0.05, -0.06), "l"),
     ("Castor (air sensor)", 52.2197, -111.9063, 7, "PurpleAir", (0.05, 0.03), "l"),
     ("Coronation", 52.0743, -111.4492, 31, "ECCC", (0.05, 0.03), "l"),
     ("Wainwright town (air sensor)", 52.8334, -110.8601, 28, "PurpleAir", (0.05, 0.05), "l"),
     ("Gilt Edge North", 53.0710, -110.6210, 30, "AB Ag", (0.05, 0.03), "l"),
     ("Hughenden", 52.5782, -110.7837, 39, "AB Ag", (0.05, -0.07), "l"),
     ("Lloydminster", 53.3106, -110.0740, 45, "ECCC", (-0.05, 0.05), "r"),
     ("Waseca, Sask.", 53.1315, -109.4055, 79, "ECCC", (-0.05, 0.05), "r")]
FIRE = (52.7645, -110.9052)
mk = {"ECCC": ("o", "Environment Canada weather station"), "AB Ag": ("s", "Alberta Agriculture weather station"),
      "PurpleAir": ("^", "PurpleAir air sensor (front = dust spike)")}
def hm(m): h = 15 + int(m // 60); mm = int(round(m % 60)); return f"{h - 12}:{mm:02d}"
# plane fit t = a + b*x + c*y (km)
lat0 = FIRE[0]; kx = 111.32 * np.cos(np.radians(lat0)); ky = 110.57
X = np.array([[1, (p[2] - FIRE[1]) * kx, (p[1] - FIRE[0]) * ky] for p in P]); T = np.array([p[3] for p in P])
coef, *_ = np.linalg.lstsq(X, T, rcond=None); tf = coef[0]
fig, ax = plt.subplots(figsize=(11, 8.6))
xs = np.linspace(-112.15, -109.2, 300); ys = np.linspace(51.95, 53.5, 300); XX, YY = np.meshgrid(xs, ys)
TT = coef[0] + coef[1] * (XX - FIRE[1]) * kx + coef[2] * (YY - FIRE[0]) * ky
lv = [0, 15, 30, 45, 60, 75]
cs = ax.contour(XX, YY, TT, levels=lv, colors="#3b6ea8", linewidths=1.1, linestyles="--", alpha=0.75)
ax.clabel(cs, fmt=lambda v: hm(v) + " p.m.", fontsize=9, inline_spacing=4)
try:
    sc = g.read_file(subprocess.run(["git", "ls-files", "*scar_patches_revised.geojson"], capture_output=True, text=True).stdout.split()[0]).to_crs(4326)
    sc.plot(ax=ax, color="#b33a1a", alpha=0.85, zorder=3)
except Exception: pass
ax.plot(FIRE[1], FIRE[0], "o", ms=22, mfc="none", mec="#8a2a10", mew=1.6, zorder=6)
ax.annotate("THE FIRE\nfront arrives about 3:30 p.m.\n(best estimate 3:27-3:31, fitted\nfrom all these points)", (FIRE[1], FIRE[0]), xytext=(-110.55, 52.25),
            fontsize=11, weight="bold", color="#8a2a10", arrowprops=dict(arrowstyle="->", color="#8a2a10"), zorder=7,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#8a2a10"))
for nm, la, lo, m, src, (dx, dy), al in P:
    ax.plot(lo, la, mk[src][0], ms=10, mfc="#222" if src != "PurpleAir" else "#e3a33b", mec="k", zorder=5)
    ax.text(lo + dx, la + dy, f"{nm}\n{hm(m)} p.m.", fontsize=9, ha="left" if al == "l" else "right", va="center", zorder=6,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))
for s, (m, lab) in mk.items():
    ax.plot([], [], m, ms=9, mfc="#222" if s != "PurpleAir" else "#e3a33b", mec="k", ls="none", label=lab)
ax.plot([], [], "--", color="#3b6ea8", label="Where the front was, by time (fitted)")
ax.legend(loc="upper left", fontsize=9, framealpha=0.95)
ax.axvline(-110.005, color="#999", lw=0.8); ax.text(-109.99, 51.98, "SASK.", fontsize=8, color="#777"); ax.text(-110.02, 51.98, "ALTA.", fontsize=8, color="#777", ha="right")
ax.set_xlim(-112.15, -109.2); ax.set_ylim(51.95, 53.5); ax.set_aspect(1 / np.cos(np.radians(lat0)))
ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
x0, y0 = -112.05, 52.03; d50 = 50 / kx
ax.plot([x0, x0 + d50], [y0, y0], "k-", lw=3); ax.text(x0 + d50 / 2, y0 + 0.03, "50 km", ha="center", fontsize=9)
ax.set_title("When the cold front arrived, Oct. 17, 2026", fontsize=16, weight="bold", loc="left")
fig.text(0.125, 0.06, f"Times are MDT, when each station's wind shifted (peak gust, temperature drop or humidity jump). The front moved from the north-west to the south-east.\n"
         f"Satellite (NOAA GOES-18): fire small at 3:10 p.m. (76 MW), 16 times bigger at 3:30 p.m. (1,215 MW). Burn scar in red (circled). Environment Canada wind warning issued 2:14 p.m.\n"
         f"Sources: Environment and Climate Change Canada; Alberta Agriculture (ACIS); PurpleAir; NOAA.", fontsize=8.6, color="#333", va="top")
plt.savefig("data/rubicon-ridge/derived/front_arrival_map_2026-10-17.png", dpi=140, bbox_inches="tight", facecolor="white")
print("fire", hm(tf), "resid", np.round(T - X @ coef, 1))
