"""GOES-18/19 ABI Full Disk visible imagery of the CFB Wainwright fire plume, Oct. 17, 2026 (day 290),
14:30-17:30 MDT (20:30-23:30 UTC scan starts).

Reads only the HDF5 chunks covering the crop box via anonymous HTTPS range reads (fsspec + h5netcdf);
no full-disk file is written to disk.

Usage:
  python3 -I goes_visible.py extract OUT_DIR      # writes crops_G18.nc / crops_G19.nc
  python3 -I goes_visible.py render  OUT_DIR      # PNG frames, GIF, MP4 from the crops

Bands: C01 0.47 um (1 km), C02 0.64 um (0.5 km), C03 0.86 um (1 km), C07 3.9 um (2 km).
The ABI fixed grids are nested (one 1 km pixel = 2x2 0.5 km pixels, one 2 km pixel = 4x4), so the
crops are cut on aligned indices and C01/C03 are block-replicated to the C02 grid for the composite.
"""
import datetime as dt
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import xarray as xr
import goes_common as gc

FIRE = (52.7645, -110.9052)
TOWN = (52.8334, -110.8601)
BOX = dict(lat0=52.0, lat1=53.4, lon0=-111.8, lon1=-109.6)
T0, T1 = dt.datetime(2026, 10, 17, 20, 30), dt.datetime(2026, 10, 17, 23, 30)
MDT = dt.timedelta(hours=-6)
CREDIT = "NOAA GOES-18/19 via NOAA Open Data on AWS"


# ----------------------------------------------------------------------------------------------
def keys_for(sat, band):
    out = []
    for h in range(T0.hour, T1.hour + 1):
        for k, _ in gc.list_keys(f"noaa-goes{sat}", f"ABI-L1b-RadF/2026/290/{h:02d}/"):
            if f"M6C{band:02d}_" in k and T0 <= gc.scan_start(k) <= T1 + dt.timedelta(minutes=1):
                out.append(k)
    return {gc.scan_start(k).replace(second=0, microsecond=0): k for k in sorted(out)}


def extract(out):
    import fsspec
    fs = fsspec.filesystem("https", block_size=2 ** 20)
    os.makedirs(out, exist_ok=True)
    for sat in ("18", "19"):
        ks = {b: keys_for(sat, b) for b in (1, 2, 3, 7)}
        times = sorted(set(ks[1]) & set(ks[2]) & set(ks[3]) & set(ks[7]))
        print(f"G{sat}: {len(times)} complete scans", {b: len(v) for b, v in ks.items()}, flush=True)
        geo, data, meta = None, {b: [] for b in (1, 2, 3, 7)}, []
        for t in times:
            rec = {}
            for b in (1, 2, 3, 7):
                url = f"https://noaa-goes{sat}.s3.amazonaws.com/{ks[b][t]}"
                for attempt in (1, 2):
                    try:
                        f = fs.open(url, "rb")
                        ds = xr.open_dataset(f, engine="h5netcdf")
                        if geo is None:            # define the crop once on the 1 km grid
                            assert b == 1
                            sj, si = gc.crop_index(ds, box=BOX, pad=2)
                            j0, j1 = sj.start, sj.stop
                            i0, i1 = si.start - si.start % 2, si.stop + si.stop % 2
                            j0, j1 = j0 - j0 % 2, j1 + j1 % 2   # even -> aligns with 2 km grid
                            geo = dict(j0=j0, j1=j1, i0=i0, i1=i1)
                            sub2 = None
                        fct = {1: 1, 3: 1, 2: 2, 7: 0.5}[b]
                        J = slice(int(geo["j0"] * fct), int(geo["j1"] * fct))
                        I = slice(int(geo["i0"] * fct), int(geo["i1"] * fct))
                        sub = ds.isel(y=J, x=I)
                        rad = sub["Rad"].values.astype("float32")
                        if b == 2 and "lat2" not in geo:
                            geo["lat2"], geo["lon2"] = gc.pixel_latlon(sub)
                            geo["x2"], geo["y2"] = sub["x"].values, sub["y"].values
                            geo["proj"] = {a: ds["goes_imager_projection"].attrs[a] for a in
                                           ("perspective_point_height", "longitude_of_projection_origin",
                                            "sweep_angle_axis", "semi_major_axis", "semi_minor_axis")}
                        if b == 7:
                            fk1, fk2 = float(ds["planck_fk1"]), float(ds["planck_fk2"])
                            bc1, bc2 = float(ds["planck_bc1"]), float(ds["planck_bc2"])
                            with np.errstate(invalid="ignore", divide="ignore"):
                                val = (fk2 / np.log(fk1 / rad + 1) - bc1) / bc2
                        else:
                            val = rad * float(ds["kappa0"])   # reflectance factor (not sun-corrected)
                        if b == 1:
                            rec["t_end"] = str(ds.attrs["time_coverage_end"])
                        rec[b] = val.astype("float32")
                        ds.close(); f.close()
                        break
                    except Exception as e:
                        print("retry" if attempt == 1 else "FAIL", sat, b, t, e, flush=True)
                        if attempt == 2:
                            raise
            for b in (1, 2, 3, 7):
                data[b].append(rec[b])
            meta.append((t, rec["t_end"]))
            print(f"G{sat}", t, "ok", flush=True)
        tt = np.array([np.datetime64(t) for t, _ in meta])
        S = xr.Dataset(
            {"refl_c01": (("t", "y1", "x1"), np.stack(data[1])),
             "refl_c02": (("t", "y", "x"), np.stack(data[2])),
             "refl_c03": (("t", "y1", "x1"), np.stack(data[3])),
             "bt_c07": (("t", "y2k", "x2k"), np.stack(data[7])),
             "lat": (("y", "x"), geo["lat2"].astype("float32")),
             "lon": (("y", "x"), geo["lon2"].astype("float32")),
             "x_rad": (("x",), geo["x2"]), "y_rad": (("y",), geo["y2"]),
             "scan_end": (("t",), np.array([e for _, e in meta]))},
            coords={"t": tt})
        S.attrs.update(source=f"noaa-goes{sat} ABI-L1b-RadF (M6) C01/C02/C03/C07, day 290",
                       crop_1km_index=f"y {geo['j0']}:{geo['j1']}, x {geo['i0']}:{geo['i1']}",
                       box=str(BOX), note="t = scan start UTC (minute). refl = Rad*kappa0, no solar-zenith "
                       "or Rayleigh correction. bt_c07 from planck coefficients. lat/lon on 0.5 km C02 grid.",
                       **{"proj_" + k: v for k, v in geo["proj"].items()})
        enc = {v: {"zlib": True, "complevel": 4} for v in ("refl_c01", "refl_c02", "refl_c03", "bt_c07")}
        for v in ("refl_c01", "refl_c02", "refl_c03"):
            enc[v].update(dtype="int16", scale_factor=1e-4, _FillValue=-32768)
        enc["bt_c07"].update(dtype="int16", scale_factor=0.01, _FillValue=-32768)
        S.to_netcdf(os.path.join(out, f"crops_G{sat}.nc"), encoding=enc)


# ----------------------------------------------------------------------------------------------
def solar_zenith(t_utc, lat, lon):
    """NOAA approximate solar position (deg)."""
    doy = t_utc.timetuple().tm_yday
    hr = t_utc.hour + t_utc.minute / 60 + t_utc.second / 3600
    g = 2 * np.pi / 365 * (doy - 1 + (hr - 12) / 24)
    eqt = 229.18 * (0.000075 + 0.001868 * np.cos(g) - 0.032077 * np.sin(g) - 0.014615 * np.cos(2 * g)
                    - 0.040849 * np.sin(2 * g))
    decl = (0.006918 - 0.399912 * np.cos(g) + 0.070257 * np.sin(g) - 0.006758 * np.cos(2 * g)
            + 0.000907 * np.sin(2 * g) - 0.002697 * np.cos(3 * g) + 0.00148 * np.sin(3 * g))
    tst = hr * 60 + eqt + 4 * lon
    ha = np.radians(tst / 4 - 180)
    la = np.radians(lat)
    cz = np.sin(la) * np.sin(decl) + np.cos(la) * np.cos(decl) * np.cos(ha)
    return np.degrees(np.arccos(np.clip(cz, -1, 1)))


def view_geometry(S):
    """Satellite view zenith/azimuth at the fire and along-scan / along-column pixel size (km) for C02."""
    from pyproj import Geod, Proj
    a = S.attrs
    h = float(a["proj_perspective_point_height"])
    lon0 = float(a["proj_longitude_of_projection_origin"])
    re = float(a["proj_semi_major_axis"]) / 1000
    H = h / 1000 + re
    la, lo = np.radians(FIRE[0]), np.radians(FIRE[1] - lon0)
    # vector from ground point to satellite (spherical approx.)
    gp = re * np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    v = np.array([H, 0, 0]) - gp
    up = gp / np.linalg.norm(gp)
    vza = np.degrees(np.arccos(np.dot(v, up) / np.linalg.norm(v)))
    east = np.array([-np.sin(lo), np.cos(lo), 0])
    north = np.cross(up, east)
    vaz = np.degrees(np.arctan2(np.dot(v, east), np.dot(v, north))) % 360
    # pixel footprint from neighbouring C02 pixel centres
    lat, lon = S["lat"].values, S["lon"].values
    j, i = np.unravel_index(np.nanargmin((lat - FIRE[0]) ** 2 + ((lon - FIRE[1]) * 0.6) ** 2), lat.shape)
    g = Geod(ellps="WGS84")
    dx = g.inv(lon[j, i], lat[j, i], lon[j, i + 1], lat[j, i + 1])[2] / 1000
    dy = g.inv(lon[j, i], lat[j, i], lon[j + 1, i], lat[j + 1, i])[2] / 1000
    return dict(vza=vza, vaz=vaz, dx_km=dx, dy_km=dy, j=int(j), i=int(i), lon0=lon0)


def local_grid(res=0.5):
    """Azimuthal-equidistant km grid centred on the fire covering BOX."""
    from pyproj import Proj
    p = Proj(proj="aeqd", lat_0=FIRE[0], lon_0=FIRE[1], ellps="WGS84")
    xs = np.arange(-58, 86 + res / 2, res)
    ys = np.arange(-80, 68 + res / 2, res)
    XX, YY = np.meshgrid(xs, ys[::-1])
    lon, lat = p(XX * 1000, YY * 1000, inverse=True)
    return p, xs, ys, lat, lon


def to_index(S, lat, lon):
    """Fractional (row, col) on the C02 crop grid for given lat/lon."""
    from pyproj import Proj
    a = S.attrs
    h = float(a["proj_perspective_point_height"])
    pr = Proj(proj="geos", h=h, lon_0=float(a["proj_longitude_of_projection_origin"]),
              sweep=a["proj_sweep_angle_axis"], a=float(a["proj_semi_major_axis"]),
              b=float(a["proj_semi_minor_axis"]))
    X, Y = pr(lon, lat)
    x, y = X / h, Y / h
    xr_, yr_ = S["x_rad"].values, S["y_rad"].values
    col = (x - xr_[0]) / (xr_[1] - xr_[0])
    row = (y - yr_[0]) / (yr_[1] - yr_[0])
    return row, col


def stretch(*bands):
    """Display enhancement, per frame: subtract each band's 0.5th percentile (removes most of the
    Rayleigh/haze path radiance, which is large at these view and sun angles), then a common linear
    gain to the 99.7th percentile and gamma 0.75. Not radiometric: brightness is NOT comparable
    between frames."""
    st = np.dstack(bands)
    lo = np.nanpercentile(st, 0.5, axis=(0, 1))
    lo = lo - 0.5 * (lo - lo.min())      # remove only half the inter-band haze difference (keeps a natural tint)
    st = st - lo
    st = st / np.nanpercentile(st, 99.7)
    st = np.nan_to_num(np.clip(st, 0, 1) ** 0.75)
    return st if st.shape[2] == 3 else st[:, :, 0]


def approx_image_time(S, tu):
    """Scan start + approximate offset at which the crop's rows were imaged. Full-disk rows are swept
    north to south over ~9.3 min (Mode 6); y spans +/-0.151872 rad. Linear approximation, +/- ~1 min."""
    frac = (0.151872 - np.nanmean(S["y_rad"].values)) / (2 * 0.151872)
    return tu + dt.timedelta(seconds=float(frac) * 560)


def render(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.ndimage import map_coordinates, median_filter
    from PIL import Image

    p, xs, ys, glat, glon = local_grid()
    ext = [xs[0], xs[-1], ys[0], ys[-1]]
    town_xy = np.array(p(TOWN[1], TOWN[0])) / 1000
    info = {}
    for sat in ("18", "19"):
        fn = os.path.join(out, f"crops_G{sat}.nc")
        if not os.path.exists(fn):
            continue
        S = xr.open_dataset(fn)
        vg = view_geometry(S)
        info[sat] = vg
        row, col = to_index(S, glat, glon)
        r2, c2 = row, col
        r1, c1 = (row + 0.5) / 2 - 0.5, (col + 0.5) / 2 - 0.5     # nested grid
        r7, c7 = (row + 0.5) / 4 - 0.5, (col + 0.5) / 4 - 0.5
        frdir = os.path.join(out, f"frames_G{sat}")
        os.makedirs(frdir, exist_ok=True)
        tc_frames = []
        for k, t in enumerate(S["t"].values):
            tu = dt.datetime.fromisoformat(str(t)[:19])
            t_img = approx_image_time(S, tu)
            tm = t_img + MDT
            R = map_coordinates(S["refl_c02"].values[k], [r2, c2], order=1, cval=np.nan)
            B = map_coordinates(S["refl_c01"].values[k], [r1, c1], order=1, cval=np.nan)
            V = map_coordinates(S["refl_c03"].values[k], [r1, c1], order=1, cval=np.nan)
            T7 = S["bt_c07"].values[k]
            A7 = map_coordinates(T7 - median_filter(T7, 7), [r7, c7], order=0, cval=np.nan)
            G = 0.45 * R + 0.1 * V + 0.45 * B
            rgb, red = stretch(R, G, B), stretch(R)
            # hot-spot outline: 3.9 um BT > 10 K above the 7x7-pixel (2 km grid) local median, within 15 km of fire
            hot = (A7 > 10) & (np.hypot(*np.meshgrid(xs, ys[::-1])) < 15)   # fire is the only target
            sz_f = float(solar_zenith(t_img, *FIRE))
            for kind, img in (("truecolour", rgb), ("red", red)):
                fig = plt.figure(figsize=(7.2, 7.8), dpi=110)
                ax = fig.add_axes([0.08, 0.07, 0.9, 0.84])
                ax.imshow(img, extent=ext, cmap=None if kind == "truecolour" else "gray", vmin=0, vmax=1,
                          interpolation="nearest")
                if hot.any():
                    ax.contour(xs, ys[::-1], hot.astype(float), levels=[0.5], colors="red", linewidths=1.0)
                ax.plot(0, 0, marker="+", color="red", ms=14, mew=1.8)
                ax.plot(*town_xy, marker="s", mfc="none", mec="yellow", ms=7, mew=1.5)
                ax.annotate("Wainwright", town_xy, xytext=(6, 4), textcoords="offset points", color="yellow",
                            fontsize=8)
                ax.annotate("fire centre", (0, 0), xytext=(8, -12), textcoords="offset points", color="red",
                            fontsize=8)
                ax.plot([xs[0] + 5, xs[0] + 15], [ys[0] + 5, ys[0] + 5], color="white", lw=3)
                ax.text(xs[0] + 10, ys[0] + 7, "10 km", color="white", ha="center", fontsize=8)
                ax.set_xlabel("km east of fire centre", fontsize=8)
                ax.set_ylabel("km north of fire centre", fontsize=8)
                ax.tick_params(labelsize=7)
                band = "visible" if kind == "truecolour" else "red band (0.64 µm)"
                ax.set_title(f"GOES-{sat} {band}, Oct. 17, 2026 (MDT)\n"
                             f"~{tm:%H:%M} MDT (scan start {tu + MDT:%H:%M})", fontsize=10)
                fig.text(0.08, 0.015, CREDIT + (" | red outline: 3.9 µm hot pixels" if hot.any() else ""),
                         fontsize=6.5, color="0.3")
                fig.text(0.98, 0.015, f"contrast enhanced per frame | sun zenith {sz_f:.0f}°", fontsize=6.5,
                         color="0.3", ha="right")
                pf = os.path.join(frdir, f"G{sat}_{kind}_{tu:%Y%m%dT%H%MZ}.png")
                fig.savefig(pf)
                plt.close(fig)
                if kind == "truecolour":
                    tc_frames.append(pf)
            print(sat, tm, "hot px", int(hot.sum()), "max local C07 anomaly K",
                  round(float(np.nanmax(A7)), 1), flush=True)
        # animations (true colour)
        ims = [Image.open(f).convert("RGB") for f in tc_frames]
        pal = [im.quantize(colors=200, method=Image.Quantize.MEDIANCUT) for im in ims]
        pal[0].save(os.path.join(out, f"G{sat}_visible_1430-1730MDT.gif"), save_all=True,
                    append_images=pal[1:], duration=600, loop=0)
        lst = os.path.join(frdir, "_list.txt")
        with open(lst, "w") as f:
            for pf in tc_frames:
                f.write(f"file '{os.path.abspath(pf)}'\nduration 0.6\n")
            f.write(f"file '{os.path.abspath(tc_frames[-1])}'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,fps=10", "-pix_fmt", "yuv420p",
                        "-c:v", "libx264", "-crf", "20", os.path.join(out, f"G{sat}_visible_1430-1730MDT.mp4")],
                       check=True)
        os.remove(lst)
    with open(os.path.join(out, "view_geometry.txt"), "w") as f:
        for sat, vg in info.items():
            f.write(f"G{sat}: sub-satellite lon {vg['lon0']}, view zenith at fire {vg['vza']:.1f} deg, "
                    f"direction to satellite (azimuth) {vg['vaz']:.0f} deg, C02 pixel spacing "
                    f"E-W {vg['dx_km']:.2f} km, N-S {vg['dy_km']:.2f} km; parallax per km height "
                    f"{np.tan(np.radians(vg['vza'])):.2f} km toward azimuth {(vg['vaz'] + 180) % 360:.0f} deg\n")
    print(open(os.path.join(out, "view_geometry.txt")).read())
    keyframes(out, plt, map_coordinates, median_filter)


def keyframes(out, plt, map_coordinates, median_filter):
    """Close-up (60 x 60 km) true-colour panels, both satellites, 15:10-16:00 MDT scans."""
    p, xs, ys, glat, glon = local_grid(0.25)
    wx, wy = (xs >= -20) & (xs <= 40), (ys >= -40) & (ys <= 20)
    ext = [xs[wx][0], xs[wx][-1], ys[wy][0], ys[wy][-1]]
    town_xy = np.array(p(TOWN[1], TOWN[0])) / 1000
    want = [dt.datetime(2026, 10, 17, 21, m) for m in (10, 20, 30, 40, 50)] + [dt.datetime(2026, 10, 17, 22, 0)]
    fig, axs = plt.subplots(2, len(want), figsize=(3.3 * len(want), 7.4))
    for a, sat in enumerate(("18", "19")):
        S = xr.open_dataset(os.path.join(out, f"crops_G{sat}.nc"))
        row, col = to_index(S, glat, glon)
        cut = lambda z: z[np.ix_(wy[::-1], wx)]
        for n, t in enumerate(want):
            k = int(np.where(S["t"].values == np.datetime64(t))[0][0])
            R = cut(map_coordinates(S["refl_c02"].values[k], [row, col], order=1))
            B = cut(map_coordinates(S["refl_c01"].values[k], [(row + .5) / 2 - .5, (col + .5) / 2 - .5], order=1))
            V = cut(map_coordinates(S["refl_c03"].values[k], [(row + .5) / 2 - .5, (col + .5) / 2 - .5], order=1))
            T7 = S["bt_c07"].values[k]
            A7 = cut(map_coordinates(T7 - median_filter(T7, 7), [(row + .5) / 4 - .5, (col + .5) / 4 - .5], order=0))
            ax = axs[a, n]
            A7 = np.where(np.hypot(*np.meshgrid(xs[wx], ys[wy][::-1])) < 15, A7, 0)
            ax.imshow(stretch(R, 0.45 * R + 0.1 * V + 0.45 * B, B), extent=ext, interpolation="nearest")
            if (A7 > 10).any():
                ax.contour(xs[wx], ys[wy], (A7 > 10)[::-1].astype(float), levels=[0.5], colors="red", linewidths=1)
            ax.plot(0, 0, "+", color="red", ms=11, mew=1.6)
            ax.plot(*town_xy, "s", mfc="none", mec="yellow", ms=5, mew=1.2)
            ax.plot([-17, -7], [-37, -37], color="white", lw=2.5)
            ax.set_title(f"GOES-{sat}  ~{approx_image_time(S, t) + MDT:%H:%M} MDT", fontsize=9)
            ax.tick_params(labelsize=6)
    fig.suptitle("GOES-18 (top) and GOES-19 (bottom) visible, Oct. 17, 2026 (MDT): 60 x 60 km around the fire "
                 "(+), Wainwright (square), 10 km bar, red outline = 3.9 µm hot pixels", fontsize=9)
    fig.text(0.01, 0.005, CREDIT + " | axes: km from fire centre | contrast enhanced per panel", fontsize=7,
             color="0.3")
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    fig.savefig(os.path.join(out, "keyframes_1510-1600MDT_closeup.png"), dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    {"extract": extract, "render": render}[sys.argv[1]](sys.argv[2])
