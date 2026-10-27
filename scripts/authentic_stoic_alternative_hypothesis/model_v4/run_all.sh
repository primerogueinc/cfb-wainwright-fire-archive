#!/bin/bash
# Working model v4: run everything from scratch. Usage: bash run_all.sh REPO_DIR SCRATCH_DIR
# REPO_DIR: a checkout of cfb-wainwright-fire-archive; SCRATCH_DIR: an empty folder for intermediate grids.
# Needs the Copernicus and Landsat raw-data repos at /home/claude/ (CP, LS below).
set -euo pipefail
REPO=$(cd "$1" && pwd); SC=$(mkdir -p "$2" && cd "$2" && pwd)/; S=$REPO/scripts/authentic_stoic_alternative_hypothesis/model_v4; M=$REPO/data/authentic-stoic-stress-test/model_v4
CP=/home/claude/cfb-wainwright---full-satellite-data---copernicus-; LS=/home/claude/cfb-wainwright-landsat-8-9
export P4ROOT=$SC; mkdir -p $SC/v4/edge $SC/v4/smoke $SC/v4/smoke_f325
cd $REPO
log(){ echo "[$(date +%H:%M:%S)] $*"; }
log fit_shape;   python3 $S/fit_shape.py $REPO 2 > $SC/fit_shape.log 2>&1
log progression; python3 $S/progression.py $REPO > $SC/progression.log 2>&1
CASES=$(python3 -c "import json;print(' '.join(c[0] for c in json.load(open('$M/cases.json'))))")
for F in 15:16 15:25; do for c in $CASES; do log post_front $F $c; FRONT=$F python3 $S/post_front.py $REPO $M/arrival_prefront_$c.tif $c > $SC/post_front_${F/:/}_$c.log 2>&1; done; done
log edge_check;  python3 $S/edge_check.py $CP $LS $SC/v4/edge > $SC/edge.log 2>&1; mkdir -p $M/edge; cp $SC/v4/edge/edge_check.json $M/edge/
log edge_quadrants; python3 $S/edge_quadrants.py $SC/v4/edge $M/edge > $SC/edgeq.log 2>&1
log fit_post;    FRONT=15:16 python3 $S/fit_post.py $REPO ${SC}p4_v4_ $SC/v4/edge $M/fit_post > $SC/fit_post.log 2>&1
log fit_post_f325; FRONT=15:25 python3 $S/fit_post.py $REPO ${SC}p4_v4f325_ $SC/v4/edge $M/fit_post_f325 > $SC/fit_post_f325.log 2>&1
for T in "" f325; do P=${SC}p4_v4${T}_
  log weighted $T;  python3 $S/weighted.py $REPO $T > $SC/weighted$T.log 2>&1
  log sensitivity $T; python3 $S/weighting_sensitivity.py $REPO $T > $SC/sens$T.log 2>&1
  log overtaken $T; python3 $S/overtaken_time.py $REPO $P $T > $SC/over$T.log 2>&1
  log truthful $T;  python3 $S/maps_truthful.py $REPO $P $T > $SC/truth$T.log 2>&1
  log location $T;  python3 $S/location_update.py $REPO $P $T > $SC/loc$T.log 2>&1
done
log maps;        python3 $S/maps_dnd_timing.py $REPO $M/maps > $SC/maps.log 2>&1
log ensemble;    python3 $S/ensemble_summary.py $REPO > $SC/ens.log 2>&1
log smoke_check; python3 $S/smoke_check.py $LS $SC/v4/smoke > $SC/smoke_check.log 2>&1
log smoke;       FRONT_MIN=16 python3 $S/smoke.py $REPO ${SC}p4_v4_ $SC/v4/smoke model_v4 > $SC/smoke.log 2>&1
log smoke_sum;   python3 $S/smoke_summary.py $REPO ${SC}p4_v4_ $SC/v4/smoke > $SC/smoke_sum.log 2>&1
log smoke_f325;  FRONT_MIN=25 python3 $S/smoke.py $REPO ${SC}p4_v4f325_ $SC/v4/smoke_f325 model_v4 > $SC/smoke_f325.log 2>&1
log smoke_sum_f325; python3 $S/smoke_summary.py $REPO ${SC}p4_v4f325_ $SC/v4/smoke_f325 f325 > $SC/smoke_sum_f325.log 2>&1
log danger;      python3 $S/danger_classes.py $REPO $M/danger > $SC/danger.log 2>&1
log moisture;    python3 $S/moisture_wind.py $REPO > $SC/moist.log 2>&1
log h0;          python3 $S/h0_speed_check.py $REPO > $SC/h0.log 2>&1
log curing;      python3 $S/curing_check.py $REPO > $SC/curing.log 2>&1
log pond;        python3 $S/pond_stall.py $REPO $CP > $SC/pond.log 2>&1
log fuel;        python3 $S/fuel_paths.py $REPO $CP > $SC/fuel.log 2>&1
log fireguards;  python3 $S/fireguards.py $REPO $CP > $SC/fireguards.log 2>&1
log DONE
