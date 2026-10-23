"""Ingest a raw Copernicus Browser export (zip) into the archive.

Usage: python3 scripts/ingest_copernicus.py EXPORT.zip [EXPORT2.zip ...]

For each zip it:
  1. identifies the date, processing level (L1C/L2A) and format (TIFF/JPG) from the file names;
  2. checks frame, pixel size, whether the fire area is covered, and how hazy it is;
  3. writes data/copernicus/packages/<date>/<level>_<fmt>/manifest.json with SHA-256 for every file,
     plus two small previews (true colour and SWIR false colour) of the fire area;
  4. records the raw export zip (name, size, SHA-256). The raw files go to the data repo
     primerogueinc/CFB-Wainwright---Full-Satellite-Data---Copernicus- (use its scripts/ingest.py).
"""
import sys, os, re, json, hashlib, zipfile, tempfile, glob, subprocess, shutil
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER_REPO = "primerogueinc/cfb-wainwright-fire-archive"
TAG = "copernicus-s2-packages"
BOX = (-110.96, 52.74, -110.85, 52.80)          # fire area: W, S, E, N
POINTS = {"origin": (-110.9214, 52.7764), "A_range2": (-110.90632, 52.77279), "B_road_head": (-110.89965, 52.77045)}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def assess(files):
    import rasterio
    from rasterio.windows import from_bounds
    tifs = [f for f in files if f.lower().endswith((".tif", ".tiff"))]
    if not tifs:
        return {"georeferenced": False, "note": "JPG export: 8-bit, no georeference. Previews only; not measurable."}
    b02 = next((f for f in tifs if "B02" in f), tifs[0])
    r = rasterio.open(b02)
    out = {"georeferenced": True, "crs": str(r.crs), "pixel_deg": [r.res[0], r.res[1]],
           "pixel_m_approx": [round(r.res[0] * 111320 * np.cos(np.radians(52.77)), 1), round(r.res[1] * 110950, 1)],
           "bounds": [round(v, 5) for v in r.bounds], "shape": list(r.shape), "dtype": r.dtypes[0]}
    a = r.read(1)
    pts = {}
    for k, (lo, la) in POINTS.items():
        try:
            i, j = r.index(lo, la)
            pts[k] = bool(0 <= i < a.shape[0] and 0 <= j < a.shape[1] and a[i, j] > 0)
        except Exception:
            pts[k] = False
    out["covers_points"] = pts
    w = from_bounds(*BOX, r.transform)
    box = r.read(1, window=w, boundless=True, fill_value=0)
    v = box > 0
    out["fire_box_valid_frac"] = round(float(v.mean()), 3)
    if v.any():
        out["fire_box_B02_median"] = round(float(np.median(box[v])), 4)
        lvl = "L2A" if "L2A" in b02 else "L1C"
        thr = 0.12 if lvl == "L2A" else 0.14
        out["haze_flag"] = bool(out["fire_box_B02_median"] > thr)
    out["usable"] = bool(all(pts.values()) and out["fire_box_valid_frac"] > 0.95 and not out.get("haze_flag", False))
    return out


def previews(files, dest):
    from PIL import Image
    made = []
    for key, name in [("True_color", "preview_true_colour.jpg"), ("SWIR", "preview_swir.jpg")]:
        f = next((x for x in files if key in x and "Highlight" not in x), None)
        if not f:
            continue
        try:
            if f.lower().endswith((".tif", ".tiff")):
                import rasterio
                from rasterio.windows import from_bounds
                r = rasterio.open(f)
                x = r.read([1, 2, 3], window=from_bounds(*BOX, r.transform), boundless=True, fill_value=0).astype("float32")
                x = np.moveaxis(x, 0, -1)
                p = np.percentile(x[x > 0], 99.5) if (x > 0).any() else 1
                img = Image.fromarray((np.clip(x / p, 0, 1) * 255).astype("uint8"))
            else:
                img = Image.open(f).convert("RGB")
            img.thumbnail((1200, 1200))
            img.save(os.path.join(dest, name), quality=85)
            made.append(name)
        except Exception as e:
            print("preview failed", f, e)
    return made


def main(zip_in, do_upload):
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_in) as z:
        z.extractall(tmp)
    files = sorted(f for f in glob.glob(os.path.join(tmp, "**", "*"), recursive=True) if os.path.isfile(f))
    groups = {}
    for f in files:
        b = os.path.basename(f)
        m = re.match(r"(\d{4}-\d{2}-\d{2})-\d{2}_\d{2}_\d{4}-\d{2}-\d{2}-\d{2}_\d{2}_Sentinel-2_(L1C|L2A)_(.+)\.(tiff?|jpe?g|png)$", b, re.I)
        if not m:
            print("skip", b); continue
        fmt = "tiff" if m.group(4).lower().startswith("tif") else "jpg"
        groups.setdefault((m.group(1), m.group(2), fmt), []).append(f)
    zsha = sha(zip_in)
    results = []
    for (date, lvl, fmt), fs in sorted(groups.items()):
        dest = os.path.join(REPO, "data/copernicus/packages", date, f"{lvl}_{fmt}")
        os.makedirs(dest, exist_ok=True)
        layers = sorted(re.sub(r".*Sentinel-2_(L1C|L2A)_", "", os.path.splitext(os.path.basename(f))[0]) for f in fs)
        qa = assess(fs)
        prev = previews(fs, dest)
        man = {"source": "Copernicus Browser export (Sentinel Hub), received from Prime Rogue", "date": date, "level": lvl, "format": fmt,
               "layers": layers, "n_files": len(fs), "qa": qa, "previews": prev,
               "files": {os.path.basename(f): {"bytes": os.path.getsize(f), "sha256": sha(f)} for f in fs},
               "package": {"name": os.path.basename(zip_in), "bytes": os.path.getsize(zip_in), "sha256": zsha, "release_tag": TAG,
                           "note": "Raw export zip as downloaded from Copernicus Browser; attach to the release unchanged. Per-file SHA-256 above verify contents whatever the zip is named."},
               "licence": "Contains modified Copernicus Sentinel data [2026]"}
        json.dump(man, open(os.path.join(dest, "manifest.json"), "w"), indent=1)
        results.append((date, lvl, fmt, len(fs), qa.get("usable"), qa.get("fire_box_valid_frac"), qa.get("fire_box_B02_median"), os.path.basename(zip_in)))
    shutil.rmtree(tmp)
    for r in results:
        print("|".join(map(str, r)))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for a in args:
        main(a, "--upload" in sys.argv)
