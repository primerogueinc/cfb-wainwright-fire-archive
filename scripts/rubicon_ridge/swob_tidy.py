"""Make a wide key-variable table from swob_long.csv (output of swob_pull.py).

Usage: python3 -I swob_tidy.py SWOB_DIR
Writes SWOB_DIR/swob_hourly_key_vars.csv (hourly files) and SWOB_DIR/swob_minute_key_vars.csv (1-minute files)
Times: obs_time_utc and obs_time_mdt (UTC-6).
"""
import os
import sys

import pandas as pd

D = sys.argv[1]
KEEP = ["air_temp", "rel_hum", "dwpt_temp", "stn_pres",
        "avg_wnd_spd_10m_pst1mt", "avg_wnd_dir_10m_pst1mt", "max_wnd_spd_10m_pst1mt", "wnd_dir_10m_pst1mt_max_spd",
        "avg_wnd_spd_10m_pst2mts", "avg_wnd_dir_10m_pst2mts",
        "avg_wnd_spd_10m_pst10mts", "avg_wnd_dir_10m_pst10mts", "max_wnd_spd_10m_pst10mts", "wnd_dir_10m_pst10mts_max_spd",
        "max_wnd_gst_spd_10m_pst10mts",
        "avg_wnd_spd_10m_pst1hr", "avg_wnd_dir_10m_pst1hr", "max_wnd_spd_10m_pst1hr", "wnd_dir_10m_pst1hr_max_spd",
        "max_wnd_spd_pst1hr_tm", "max_pk_wnd_spd_10m_pst1hr", "max_pk_wnd_tm_pst1hr", "pk_wnd_rmk",
        "avg_wnd_spd_pcpn_gag_pst1hr", "avg_wnd_dir_pcpn_gag_pst1hr", "avg_wnd_spd_pcpn_gag_pst10mts",
        "avg_wnd_dir_pcpn_gag_pst10mts", "max_wnd_spd_pcpn_gag_2m_pst1hr", "wnd_dir_max_spd_2m_pst1hr",
        "max_wnd_spd_2m_pst1hr_tm", "max_air_temp_pst1hr", "min_air_temp_pst1hr", "min_rel_hum_pst1hr",
        "max_rel_hum_pst1hr", "pcpn_amt_pst1hr", "rnfl_amt_pst1hr", "lat", "long", "stn_nam"]
src = os.path.join(D, "swob_long.csv")
df = pd.read_csv(src if os.path.exists(src) else src + ".gz", dtype=str)
df = df[df.element.isin(KEEP)]
df["kind"] = df.file.str.contains("-minute-").map({True: "minute", False: "hourly"})
df["man"] = df.file.str.contains("-MAN-")
df = df[~df.man]
for kind, g in df.groupby("kind"):
    w = g.pivot_table(index=["network", "station", "obs_time_utc", "file"], columns="element", values="value",
                      aggfunc="first").reset_index()
    t = pd.to_datetime(w.obs_time_utc, utc=True)
    w.insert(3, "obs_time_mdt", (t - pd.Timedelta(hours=6)).dt.strftime("%Y-%m-%d %H:%M"))
    w["obs_time_utc"] = t.dt.strftime("%Y-%m-%d %H:%M")
    cols = [c for c in ["network", "station", "stn_nam", "lat", "long", "obs_time_utc", "obs_time_mdt"] if c in w] + \
           [c for c in KEEP if c in w and c not in ("lat", "long", "stn_nam")] + ["file"]
    w[cols].sort_values(["station", "obs_time_utc"]).to_csv(os.path.join(D, f"swob_{kind}_key_vars.csv"), index=False)
    print(kind, len(w))
