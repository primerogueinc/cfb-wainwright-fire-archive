"""Working model v4, H0 test: was the fire really that slow between 12:17 and 2:49 p.m., or is the 0.43 km/h an artefact?
Usage: python3 h0_speed_check.py REPO
1. Head advance re-measured with pixel uncertainty: Landsat 8 north-east tip at 12:17 (0.08 burned class) to the north-east-most
   NOAA-20 VIIRS detection at 2:49 (480 m pixels, +/-240 m), projected on the strip's axis (55 deg).
2. Energy check: VIIRS fire radiative power (FRP) at 2:49 gives the rate the fire was consuming fuel. Total heat release =
   FRP / radiative fraction (0.10-0.20, grass fires); area burned per hour = heat release / (heat of combustion 18,000 kJ/kg x
   fuel consumed 0.35 kg/m2). Compared with (a) the model's area growth 12:17-2:49 and (b) what a fire spreading at the standard
   rate (about 2.4 km/h head, length-to-breadth 4) would burn per hour.
3. GOES-18 fire power before and after the front (NOAA fire product, 2 km pixels; GOES underestimates small fires, so the
   ratio is indicative only)."""
import sys, os, json, math, numpy as np, pandas as pd
from pyproj import Geod
REPO = sys.argv[1]; G = Geod(ellps="WGS84")
d = pd.read_csv(os.path.join(REPO, "data/firms/detections.csv")); v = d[d.acq_datetime_mdt == "2026-10-17 14:49 MDT"]
tip = (-110.91173, 52.78011)                                   # Landsat 12:17 NE tip, 0.08 class (area1217.json)
lead = v.assign(az=0.0, dist=0.0)
for i, r in v.iterrows():
    az, _, dist = G.inv(tip[0], tip[1], r.longitude, r.latitude); lead.loc[i, "az"] = az; lead.loc[i, "dist"] = dist
lead["along_m"] = lead.dist * np.cos(np.radians(lead.az - 55))
best = lead.sort_values("along_m").iloc[-1]; mins = 152
adv = dict(lead_detection=[round(best.latitude, 5), round(best.longitude, 5)], along_axis_m=round(best.along_m), kmh=round(best.along_m / 1000 / (mins / 60), 2),
           kmh_range_pixel=[round((best.along_m - 240) / 1000 / (mins / 60), 2), round((best.along_m + 240) / 1000 / (mins / 60), 2)],
           note="the north-east-most 2:49 pixel sits at Peterson Pond / Range 3, where the final scar's north tip ends: the head may have reached water and a range clearing before 2:49, so the advance alone is a lower bound")
frp = float(v.frp.sum()); H, w = 18000.0, 0.35
growth = {f"rad_frac_{rf}": round(frp / rf * 1000 / (H * w) * 3600 / 1e6, 2) for rf in (0.10, 0.15, 0.20)}
pg = pd.read_csv(os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4/progression.csv"))
model_growth = ((pg.area_km2_1449 - pg.area_km2_1217) / (mins / 60)).round(2).tolist()
Rh, LB = 2.4, 4.0; t = 1.0; L = Rh * t * (1 + 1 / 12); free_growth = round(math.pi / 4 * L * L / LB * 2 / t, 2)  # dA/dt at t=1 h for an ellipse
gt = pd.read_csv(os.path.join(REPO, "data/goes/fire_timeline.csv"))
g18 = gt[gt.satellite == "GOES-18"][["scan_start_mdt", "fdc_power_mw"]]
gsel = g18[g18.scan_start_mdt.isin(["15:10 MDT", "15:20 MDT", "15:30 MDT", "15:40 MDT"])].set_index("scan_start_mdt").fdc_power_mw.round(0).to_dict()
out = dict(head_advance=adv, viirs_frp_mw_249=round(frp, 1), area_growth_km2_per_h_from_frp=growth, model_area_growth_km2_per_h_1217_1449=model_growth,
           standard_rate_fire_area_growth_km2_per_h_after_1h=free_growth, goes18_fire_power_mw=gsel)
json.dump(out, open(os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4/h0_speed_check.json"), "w"), indent=1); print(json.dumps(out, indent=1))
