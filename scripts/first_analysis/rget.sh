# recursive get of a datamart dir
url=$1; out=$2; mkdir -p "$out"
for h in $(curl -s "$url" | grep -o 'href="[^?"/][^"]*"' | sed 's/href="//;s/"$//'); do
  case "$h" in */) bash "$0" "$url$h" "$out/$h";; *) [ -f "$out/$h" ] || curl -s -o "$out/$h" "$url$h";; esac
done
