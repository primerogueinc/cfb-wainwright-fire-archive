sat=$1; prod=$2; day=$3; shift 3
for h in "$@"; do
  for k in $(curl -s "https://noaa-$sat.s3.amazonaws.com/?list-type=2&prefix=$prod/2026/$day/$h/" | grep -o '<Key>[^<]*</Key>' | sed 's/<[^>]*>//g'); do
    f=$(basename $k); [ -f $sat/$prod/$f ] || curl -s -o $sat/$prod/$f "https://noaa-$sat.s3.amazonaws.com/$k"
  done
done
