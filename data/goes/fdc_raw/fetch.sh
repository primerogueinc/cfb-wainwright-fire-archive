#!/usr/bin/env bash
# Re-download the NOAA GOES-18/19 fire-detection files listed in sha256sums.txt from NOAA's public
# archive and verify them. Usage: bash fetch.sh [outdir]
set -euo pipefail
out=${1:-.}; here=$(cd "$(dirname "$0")" && pwd)
while read -r sum path; do
  f=$(basename "$path"); sat=$(echo "$path" | cut -d/ -f1); prod=$(echo "$path" | cut -d/ -f2)
  doy=$(echo "$f" | sed -E 's/.*_s2026([0-9]{3})([0-9]{2}).*/\1/'); hh=$(echo "$f" | sed -E 's/.*_s2026[0-9]{3}([0-9]{2}).*/\1/')
  mkdir -p "$out/$sat/$prod"
  [ -f "$out/$path" ] || curl -sf -o "$out/$path" "https://noaa-$sat.s3.amazonaws.com/$prod/2026/$doy/$hh/$f"
done < "$here/sha256sums.txt"
(cd "$out" && sha256sum -c "$here/sha256sums.txt")
