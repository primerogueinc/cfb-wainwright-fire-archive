"""Collect the per-fire summaries (model_fire.py) and the Oct. 17 working model v4 into one comparison table.
Usage: python3 compare.py REPO -> data/fire_compare/comparison.csv"""
import sys, os, json, pandas as pd
REPO = sys.argv[1]; FC = os.path.join(REPO, "data/fire_compare")
rows = []
for f, area in (("aug27_28", "PDA 3A F1"), ("sept16", "outside the mapped danger areas"), ("sept18_20", "PDA 2"), ("sept21", "PDA 3A F1"), ("oct14", "PDA 2 (Range 13)")):
    p = os.path.join(FC, f, "summary.json")
    if not os.path.exists(p): continue
    s = json.load(open(p)); d = s.get("dusk") or {}; r = s.get("free24h") or {}
    best = max((d.get("weight_by_K") or {"-": 0}).items(), key=lambda kv: kv[1])[0] if d else None
    rows.append(dict(fire=f, area_osm=area, dates=f"{s['date']}" + (f" (+{len(s['passes_mdt'])} passes)" if s else ""), detections=s["detections"], passes=len(s["passes_mdt"]),
                     first_last_pass_mdt=f"{s['passes_mdt'][0]}-{s['passes_mdt'][-1]}", detection_span_h=s["detection_span_h"], night_detections=s["night_detections"],
                     max_pass_frp_mw=s["max_pass_frp_mw"], fwi=";".join(f"{c['fwi']}" for c in s["cwfis_days"]), max_wind_kmh=s["max_wind_kmh"], min_rh=s["min_rh"],
                     peak_standard_spread_kmh=s["peak_std_ros_kmh"], scar_km2=s["scar_km2"],
                     standard_rate_km2_by_dusk_p50=(d.get("standard_rate_km2_p10_p50_p90") or [None] * 3)[1], ratio_dusk=d.get("ratio_standard_to_observed"),
                     standard_rate_km2_24h_p50=(r.get("standard_rate_km2_p10_p50_p90") or [None] * 3)[1], ratio_24h=r.get("ratio_standard_to_observed"),
                     best_rate_factor_dusk=best, best_overlap_dusk=d.get("best_jaccard"), ignition_weighted_median_h=d.get("ignition_weighted_median_h")))
rows.append(dict(fire="oct17", area_osm="PDA 2", dates="2026-10-17", detections=67, passes=2, first_last_pass_mdt="12:17-14:49", detection_span_h=2.53, night_detections=0,
                 max_pass_frp_mw=75, fwi="30.8", max_wind_kmh=48, min_rh=16, peak_standard_spread_kmh=7, scar_km2=10.79, standard_rate_km2_by_dusk_p50=None, ratio_dusk=None,
                 best_rate_factor_dusk="0.17 before the 3:16 p.m. front", best_overlap_dusk=None, ignition_weighted_median_h=5.0))
pd.DataFrame(rows).to_csv(os.path.join(FC, "comparison.csv"), index=False); print(pd.DataFrame(rows).T.to_string())
