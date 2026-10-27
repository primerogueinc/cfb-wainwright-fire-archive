#!/bin/bash
# Pull ECCC hourly (station 301S001, Wainwright CFB Airfield 21) for April-October 2012-2026, and the CWFIS station FWI history for
# Wainwright (filtered from the national decade files). Usage: scripts/fetch_history.sh REPO
R=$1; H=$R/data/eccc/climate_hourly/history; C=$R/data/nrcan_cwfis/history; mkdir -p $H $C
for y in $(seq 2012 2026); do for m in 4 5 6 7 8 9 10; do f=$H/301S001_${y}-$(printf %02d $m)_LST.csv
  [ -s "$f" ] || curl -s -m 120 -o "$f" "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&climate_id=301S001&Year=$y&Month=$m&Day=1&time=LST&timeframe=1&submit=Download+Data"; done; done
U=https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs
# CWFIS rows are keyed by the station's AES/climate ID (301S001)
curl -s -m 3600 $U/cwfis_fwi2010s.csv | awk -F, 'NR==1 || $1=="301S001"' > $C/cwfis_fwi2010s_301S001.csv
curl -s -m 3600 $U/cwfis_fwi2020s.csv.bz2 | bzcat | awk -F, 'NR==1 || $1=="301S001"' > $C/cwfis_fwi2020s_301S001.csv
curl -s -m 600 $U/cwfis_allstn2026.csv | awk -F, 'NR==1 || $1=="301S001"' > $C/cwfis_station_301S001.csv
curl -s -m 120 $U/current/cwfis_fwi_20261001.csv | head -1 > $C/cwfis_fwi_2026_wainwright.csv
for d in $(python3 -c "import pandas as pd;print(' '.join(x.strftime('%Y%m%d') for x in pd.date_range('2026-04-01','2026-10-24')))"); do
  curl -s -m 120 $U/current/cwfis_fwi_$d.csv | grep ",301S001," >> $C/cwfis_fwi_2026_wainwright.csv; done
echo done
