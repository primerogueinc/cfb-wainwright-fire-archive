"""PurpleAir PM1 / PM2.5 / PM10 by tranche, Oct. 17, 2026: hourly tranches 11 a.m.-5 p.m. MDT plus a +/-10 min window
around each sensor's front passage. Dust indicator: coarse = PM10 - PM2.5; smoke indicator: fine share = PM1 / PM10."""
import json, pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = "data/rubicon-ridge/raw/purpleair/size_fractions_{}.json"; OUT = "data/rubicon-ridge/derived/"
S = {107254: ("Wainwright Town Hall", "8 km NNE", "15:28"), 27475: ("Castor", "~90 km SW", "15:07"),
     195401: ("Lloydminster College Park", "~80 km NE", "15:49"), 204385: ("Lloydminster LPSD", "~80 km NE", "15:49")}
rows = []
for sid, (nm, where, front) in S.items():
    j = json.load(open(R.format(sid))); d = pd.DataFrame(j["data"], columns=j["fields"])
    d["t"] = pd.to_datetime(d.time_stamp, unit="s", utc=True).dt.tz_convert("America/Edmonton").dt.tz_localize(None)
    d = d.sort_values("t"); f = pd.Timestamp("2026-10-17 " + front)
    tr = [(f"{h}:00-{h+1}:00", pd.Timestamp(f"2026-10-17 {h}:00"), pd.Timestamp(f"2026-10-17 {h+1}:00")) for h in range(11, 17)]
    tr.insert(0, None); tr = tr[1:]
    tr.append((f"front {front} +/-10 min", f - pd.Timedelta("10min"), f + pd.Timedelta("10min")))
    for lab, a, b in tr:
        x = d[(d.t >= a) & (d.t < b)]
        if x.empty: continue
        pm1, pm25, pm10 = x["pm1.0_atm"].mean(), x["pm2.5_atm"].mean(), x["pm10.0_atm"].mean()
        rows.append(dict(sensor=nm, location=where, tranche=lab, n=len(x), pm1=round(pm1, 1), pm25=round(pm25, 1), pm10=round(pm10, 1),
                         pm10_max=round(x["pm10.0_atm"].max(), 1), coarse_pm10_minus_pm25=round(pm10 - pm25, 1),
                         fine_share_pm1_over_pm10=round(pm1 / pm10, 2) if pm10 > 0.3 else np.nan,
                         count_0p3um=round(x["0.3_um_count"].mean()), count_2p5um=round(x["2.5_um_count"].mean(), 1),
                         count_10um=round(x["10.0_um_count"].mean(), 2)))
t = pd.DataFrame(rows); t.to_csv(OUT + "purpleair_pm_tranches_2026-10-17.csv", index=False)
fig, axs = plt.subplots(1, 4, figsize=(22, 5.8), sharey=True)
for ax, (sid, (nm, where, front)) in zip(axs, S.items()):
    x = t[t.sensor == nm]; i = np.arange(len(x))
    ax.bar(i - 0.27, x.pm1, 0.27, label="PM1 (fine: smoke)", color="#5b6c8f")
    ax.bar(i, x.pm25, 0.27, label="PM2.5", color="#e3a33b")
    ax.bar(i + 0.27, x.pm10, 0.27, label="PM10 (coarse: dust)", color="#9c4a1f")
    ax.set_xticks(i, [s.replace(" +/-10 min", "\n±10 min").replace("front ", "front\n") for s in x.tranche], fontsize=8.5)
    ax.set_title(f"{nm}\n({where}; front {front} MDT)", fontsize=11, weight="bold"); ax.grid(axis="y", alpha=0.3)
    ax.axvspan(len(x) - 1.5, len(x) - 0.5, color="#f4e3c1", zorder=0)
axs[0].set_ylabel("Mean concentration (µg/m³)"); axs[0].legend(fontsize=9, loc="upper left")
fig.suptitle("PurpleAir particulates by hour, and in the 20 minutes around the front, Oct. 17, 2026 (MDT)", fontsize=14, weight="bold")
fig.text(0.5, -0.02, "Bars: mean PM1, PM2.5, PM10 (atm). Smoke is mostly PM1; wind-blown dust is mostly coarse (PM10). Shaded: ±10 min around each sensor's front passage. "
         "Wainwright Town Hall's temperature and pressure sensors are faulty; its particle counters are not. Source: PurpleAir API, 2-min data.", ha="center", fontsize=9, color="#444")
plt.tight_layout(); plt.savefig(OUT + "purpleair_pm_tranches_2026-10-17.png", dpi=130, bbox_inches="tight", facecolor="white")
pd.set_option("display.width", 250); print(t.drop(columns=["location", "count_0p3um"]).to_string(index=False))
