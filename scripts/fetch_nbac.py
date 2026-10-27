"""Download NRCan National Burned Area Composite (NBAC) yearly polygons 2012-2025 and keep only those in a box around CFB Wainwright
(-111.4 to -110.5 E, 52.55 to 53.0 N). Usage: python3 fetch_nbac.py REPO SCRATCH. Writes data/nbac/nbac_wainwright_2012-2025.geojson (EPSG:4326)
and data/nbac/sources.csv (zip name, bytes, sha256)."""
import sys, os, glob, zipfile, hashlib, subprocess, pandas as pd, geopandas as gpd
from shapely.geometry import box
REPO, S = sys.argv[1:3]; OUT = os.path.join(REPO, "data/nbac"); os.makedirs(OUT, exist_ok=True)
rows, src = [], []
for y in range(2012, 2026):
    z = os.path.join(S, f"NBAC_{y}_20260513.zip")
    if not os.path.exists(z): subprocess.run(["curl", "-s", "-m", "1800", "-o", z, f"https://cwfis.cfs.nrcan.gc.ca/downloads/nbac/NBAC_{y}_20260513.zip"], check=True)
    h = hashlib.sha256(open(z, "rb").read()).hexdigest(); src.append(dict(file=os.path.basename(z), bytes=os.path.getsize(z), sha256=h))
    d = os.path.join(S, f"nbac{y}"); zipfile.ZipFile(z).extractall(d)
    f = glob.glob(os.path.join(d, "**/*.shp"), recursive=True)[0]; crs = gpd.read_file(f, rows=1).crs
    m = gpd.GeoDataFrame(geometry=[box(-111.4, 52.55, -110.5, 53.0)], crs=4326).to_crs(crs)
    g = gpd.read_file(f, mask=m)
    if len(g): rows.append(g.to_crs(4326))
    print(y, len(g), flush=True)
    subprocess.run(["rm", "-rf", d, z])
gpd.GeoDataFrame(pd.concat(rows, ignore_index=True), crs=4326).to_file(os.path.join(OUT, "nbac_wainwright_2012-2025.geojson"), driver="GeoJSON")
pd.DataFrame(src).to_csv(os.path.join(OUT, "sources.csv"), index=False); print("done")
