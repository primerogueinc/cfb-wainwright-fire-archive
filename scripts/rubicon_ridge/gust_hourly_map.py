"""Max gust per station per hour, Oct. 17, 2026, 12:00-17:00 MDT (ECCC SWOB, MSC + Alberta Agriculture partner feed).
Gust = max of the hour's peak wind at 10 m (max_pk_wnd_spd_10m_pst1hr, max_wnd_spd_10m_pst1hr); stations with only a
2 m gauge anemometer (AGCM/LITE) use max_wnd_spd_pcpn_gag_2m_pst1hr, marked with a ring (2 m reads lower than 10 m).
Each SWOB hourly obs at HH:00 MDT covers the hour ending then."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
R = "data/rubicon-ridge/raw/eccc_swob/swob_hourly_key_vars.csv"
OUT = "data/rubicon-ridge/derived/"
import os; os.makedirs(OUT, exist_ok=True)
d = pd.read_csv(R, parse_dates=["obs_time_mdt"])
d = d[(d.obs_time_mdt >= "2026-10-17 13:00") & (d.obs_time_mdt <= "2026-10-17 17:00") & (d.obs_time_mdt.dt.minute == 0)].copy()
d["g10"] = d[["max_pk_wnd_spd_10m_pst1hr", "max_wnd_spd_10m_pst1hr"]].max(axis=1)
d["g2"] = d["max_wnd_spd_pcpn_gag_2m_pst1hr"]
d["gust"] = d.g10.fillna(d.g2); d["height"] = np.where(d.g10.notna(), "10 m", "2 m")
d["hour_end"] = d.obs_time_mdt.dt.hour
t = d.pivot_table(index=["station", "stn_nam", "lat", "long", "height"], columns="hour_end", values="gust", aggfunc="max").reset_index()
fire = (52.7645, -110.9052)
t["km_from_fire"] = np.hypot((t.lat - fire[0]) * 111.2, (t.long - fire[1]) * 111.2 * np.cos(np.radians(fire[0]))).round(0)
hrs = [13, 14, 15, 16, 17]
lab = {13: "12-1 p.m.", 14: "1-2 p.m.", 15: "2-3 p.m.", 16: "3-4 p.m.", 17: "4-5 p.m."}
tab = t.rename(columns={h: f"max_gust_kmh_{lab[h].replace(' ','')}" for h in hrs}).sort_values("km_from_fire")
tab.to_csv(OUT + "max_gust_by_hour_2026-10-17.csv", index=False)
bounds = [0, 30, 45, 60, 75, 90, 105, 135]
cmap = plt.get_cmap("YlOrRd", len(bounds) - 1); norm = BoundaryNorm(bounds, cmap.N)
fig, axs = plt.subplots(1, 5, figsize=(24, 5.6), sharex=True, sharey=True)
fig.subplots_adjust(top=0.86, bottom=0.25, wspace=0.08)
for ax, h in zip(axs, hrs):
    for _, r in t.iterrows():
        v = r[h]
        if pd.isna(v): continue
        ax.scatter(r.long, r.lat, s=150, c=[cmap(norm(v))], edgecolors="k" if r.height == "10 m" else "#1f4e9c",
                   linewidths=0.6 if r.height == "10 m" else 2.0, zorder=3)
        ax.text(r.long, r.lat + 0.055, f"{v:.0f}", ha="center", va="bottom", fontsize=8.5, zorder=4)
    ax.plot(fire[1], fire[0], marker="*", ms=17, mfc="#111", mec="w", zorder=5)
    ax.axvline(-110.005, color="#888", lw=0.8, ls="--")
    ax.set_title(f"{lab[h]} MDT", fontsize=13, weight="bold")
    ax.set_aspect(1 / np.cos(np.radians(52.7))); ax.grid(alpha=0.25)
    ax.set_xlim(-113.0, -108.6); ax.set_ylim(51.55, 53.85)

axs[0].text(-109.97, 51.6, "AB | SK", fontsize=8, color="#666")
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
cb = fig.colorbar(sm, ax=axs, orientation="horizontal", fraction=0.06, pad=0.12, aspect=50, ticks=bounds); cb.set_label("Maximum gust in the hour (km/h)")
fig.suptitle("Maximum wind gust by station and hour, Oct. 17, 2026 (CFB Wainwright fire = star)", fontsize=15, weight="bold", y=0.98)
fig.text(0.5, 0.005, "Black-edged dots: 10 m anemometer. Blue rings: 2 m gauge anemometer (Alberta Agriculture AGCM/LITE), reads lower than 10 m. "
         "Source: ECCC SWOB hourly observations (MSC and Alberta Agriculture partner network). Times MDT; each panel is the hour's maximum.",
         ha="center", fontsize=9, color="#444")
plt.savefig(OUT + "max_gust_by_hour_2026-10-17.png", dpi=130, bbox_inches="tight", facecolor="white")
print(tab.to_string(index=False))
