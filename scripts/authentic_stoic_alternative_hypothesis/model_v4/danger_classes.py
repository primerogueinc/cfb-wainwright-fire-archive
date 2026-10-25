"""Working model v4: Oct. 17 against the grass-fire suppression classes of Alexander, Heathcott & Schwanke (2013),
Fire behaviour case study of two early winter grass fires in southern Alberta, 27 November 2011 (Partners in Protection):
head fire rate of spread (HFROS) < 1.0 km/h easy suppression; 1-4.9 km/h challenging; >= 5.0 km/h beyond control.
Usage: python3 danger_classes.py REPO OUT_DIR
Three readings, kept separate because they answer different questions:
  hourly_standard  FBP head-fire spread from CZWN hourly means (part 8b table: FFMC diurnal, ISI, O-1 grass): what the
                   routine hourly fire-danger calculation would have shown
  potential        part 1 fire_models.csv: FBP O-1a/O-1b, CSIRO and Cruz 20% at the 2:49-3:16 p.m. winds, gusts, and
                   just after the front (90-100% curing): the spread the conditions could support
  modelled         working model: 0.43 km/h head advance 12:17-2:49 p.m. (Landsat/VIIRS), 4.4-12 km/h after the front
Same report: Lethbridge fire 8.3 km/h observed in 64-69 km/h winds (FBP O-1b predicted 8.7 km/h); length-to-breadth
L:B = 1.1 x WS^0.464 (Table A1.1), the shape relation used in our spread model since part 1."""
import sys, os, pandas as pd
REPO, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
cls = lambda v: "easy (<1 km/h)" if v < 1 else ("challenging (1-4.9 km/h)" if v < 5 else "beyond control (>=5 km/h)")
wx = pd.read_csv(os.path.join(REPO, "data/authentic-stoic-stress-test/part8b_ignition/weather_hourly_model.csv"))
wx = wx[wx.t >= 0].copy(); wx["hour_mdt"] = wx.t.astype(int).map(lambda h: f"{h:02d}:00")
wx["hfros_kmh"] = (wx.ros_head_m_min * 60 / 1000).round(2); wx["class"] = wx.hfros_kmh.map(cls)
wx[["hour_mdt", "ws", "wd", "rh", "temp", "ffmc", "isi", "hfros_kmh", "class"]].to_csv(os.path.join(OUT, "hourly_standard.csv"), index=False)
fm = pd.read_csv(os.path.join(REPO, "data/location_analysis/fire_models.csv"))
pot = fm.groupby("scenario").head_km_h.agg(["min", "median", "max"]).reset_index()
pot["class_of_median"] = pot["median"].map(cls); pot.to_csv(os.path.join(OUT, "potential.csv"), index=False)
mod = pd.DataFrame([dict(phase="12:17-2:49 p.m. (observed head advance)", kmh=0.43), dict(phase="after 3:16 p.m. front (slow case)", kmh=4.4),
                    dict(phase="after 3:16 p.m. front (middle)", kmh=8.0), dict(phase="after 3:16 p.m. front (fast)", kmh=12.0)])
mod["class"] = mod.kmh.map(cls); mod.to_csv(os.path.join(OUT, "modelled.csv"), index=False)
print(wx[["hour_mdt", "ws", "wd", "isi", "hfros_kmh", "class"]].to_string(index=False)); print(pot.to_string(index=False)); print(mod.to_string(index=False))
