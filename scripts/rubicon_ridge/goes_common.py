"""Shared helpers for Rubicon Ridge GOES pulls (anonymous NOAA open-data S3 over HTTPS)."""
import re
import xml.etree.ElementTree as ET
import numpy as np
import requests
from pyproj import Proj

NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
FIRE_LAT, FIRE_LON = 52.775, -110.92
BURN_BOX = dict(lat0=52.74, lat1=52.79, lon0=-110.94, lon1=-110.86)
# Background box: same latitude band, ~25 km west-south-west, off the range, same size
BG_BOX = dict(lat0=52.68, lat1=52.73, lon0=-111.32, lon1=-111.24)
CROP = dict(lat0=51.8, lat1=53.8, lon0=-112.6, lon1=-109.2)
SESSION = requests.Session()


def list_keys(bucket, prefix):
    keys, token = [], None
    while True:
        url = f"https://{bucket}.s3.amazonaws.com/?list-type=2&prefix={prefix}"
        if token:
            url += "&continuation-token=" + requests.utils.quote(token, safe="")
        r = SESSION.get(url, timeout=60)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        for c in root.findall("s3:Contents", NS):
            keys.append((c.find("s3:Key", NS).text, int(c.find("s3:Size", NS).text)))
        if root.find("s3:IsTruncated", NS).text == "true":
            token = root.find("s3:NextContinuationToken", NS).text
        else:
            return keys


def download(bucket, key, dest):
    r = SESSION.get(f"https://{bucket}.s3.amazonaws.com/{key}", timeout=300)
    r.raise_for_status()
    with open(dest, "wb") as f:
        f.write(r.content)
    return dest


def scan_start(key):
    m = re.search(r"_s(\d{4})(\d{3})(\d{2})(\d{2})(\d{2})(\d)", key)
    import datetime as dt
    y, doy, H, M, S, t = map(int, m.groups())
    return dt.datetime(y, 1, 1) + dt.timedelta(days=doy - 1, hours=H, minutes=M, seconds=S + t / 10)


def goes_proj(ds):
    p = ds["goes_imager_projection"]
    h = float(p.perspective_point_height)
    proj = Proj(proj="geos", h=h, lon_0=float(p.longitude_of_projection_origin),
                sweep=p.sweep_angle_axis, a=float(p.semi_major_axis), b=float(p.semi_minor_axis))
    return proj, h


def latlon_to_xy(ds, lat, lon):
    """Return scan angles (rad) for lat/lon; NaN if off-disk."""
    proj, h = goes_proj(ds)
    X, Y = proj(lon, lat)
    X = np.where(np.abs(X) > 1e29, np.nan, X)
    Y = np.where(np.abs(Y) > 1e29, np.nan, Y)
    return np.asarray(X) / h, np.asarray(Y) / h


def covers(ds, lat, lon):
    x, y = latlon_to_xy(ds, lat, lon)
    xs, ys = ds["x"].values, ds["y"].values
    if np.isnan(x):
        return False
    return (min(xs) <= x <= max(xs)) and (min(ys) <= y <= max(ys))


def pixel_latlon(ds):
    proj, h = goes_proj(ds)
    xx, yy = np.meshgrid(ds["x"].values * h, ds["y"].values * h)
    lon, lat = proj(xx, yy, inverse=True)
    lon = np.where(np.abs(lon) > 1e29, np.nan, lon)
    lat = np.where(np.abs(lat) > 1e29, np.nan, lat)
    return lat, lon


def crop_index(ds, box=CROP, pad=2):
    """Index slices of x/y covering a lat/lon box (computed from the box corners & edges)."""
    lats = np.r_[np.linspace(box["lat0"], box["lat1"], 25), np.full(25, box["lat0"]), np.full(25, box["lat1"]),
                 np.linspace(box["lat0"], box["lat1"], 25)]
    lons = np.r_[np.full(25, box["lon0"]), np.linspace(box["lon0"], box["lon1"], 25),
                 np.linspace(box["lon0"], box["lon1"], 25), np.full(25, box["lon1"])]
    x, y = latlon_to_xy(ds, lats, lons)
    xs, ys = ds["x"].values, ds["y"].values
    dx = xs[1] - xs[0]
    dy = ys[1] - ys[0]  # negative
    i0 = int(np.floor((np.nanmin(x) - xs[0]) / dx)) - pad
    i1 = int(np.ceil((np.nanmax(x) - xs[0]) / dx)) + pad
    j0 = int(np.floor((np.nanmax(y) - ys[0]) / dy)) - pad
    j1 = int(np.ceil((np.nanmin(y) - ys[0]) / dy)) + pad
    i0, j0 = max(i0, 0), max(j0, 0)
    i1, j1 = min(i1, len(xs) - 1), min(j1, len(ys) - 1)
    return slice(j0, j1 + 1), slice(i0, i1 + 1)
