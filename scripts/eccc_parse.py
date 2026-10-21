#!/usr/bin/env python3
"""Parse ECCC MSC Datamart files in data/eccc/original/ into tidy tables.

  * swob_observations.csv  - hourly SWOB-ML station observations (CZWN, CYLL)
  * bulletins_index.csv    - every forecast/warning bulletin: type, office, UTC/MDT issue time,
                             whether it mentions Wainwright, and the warning headline lines
"""
import csv, re, sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data" / "eccc"
FIELDS = ["date_tm", "tc_id", "stn_nam", "lat", "long", "stn_elev", "air_temp", "rel_hum", "dwpt_temp",
          "avg_wnd_spd_10m_pst2mts", "avg_wnd_dir_10m_pst2mts", "avg_wnd_spd_10m_pst10mts",
          "avg_wnd_dir_10m_pst10mts", "max_wnd_spd_10m_pst1hr", "wnd_dir_10m_pst1hr_max_spd",
          "max_wnd_spd_pst1hr_tm", "max_wnd_spd_10m_pst10mts", "wnd_dir_10m_pst10mts_max_spd",
          "pk_wnd_rmk", "stn_pres", "mslp", "pres_tend_amt_pst3hrs", "pcpn_amt_pst1hr", "vis", "data_avail"]


def swob():
    rows = []
    for f in sorted(D.glob("original/**/*swob*.xml")):
        x = f.read_text(errors="replace")
        vals = dict(re.findall(r'name="([a-z_0-9]+)" uom="[^"]*" value="([^"]*)"', x))
        r = {k: vals.get(k, "") for k in FIELDS}
        m = re.search(r"-(C[A-Z0-9]{3})-", f.name)
        if m:
            r["tc_id"] = m.group(1)  # station ID from the file name (some files omit tc_id)
        t = datetime.strptime(r["date_tm"][:16], "%Y-%m-%dT%H:%M")
        r["time_mdt"] = (t - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
        r["file"] = f.relative_to(D).as_posix()
        rows.append(r)
    rows.sort(key=lambda r: (r["date_tm"], r["tc_id"]))
    with (D / "swob_observations.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["time_mdt"] + FIELDS + ["file"], lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    return len(rows)


def bulletins():
    seen, rows = set(), []
    for f in sorted(D.glob("original/**/*")):
        m = re.match(r"([A-Z]{4}\d\d)_([A-Z]{4})_(\d\d)(\d\d)(\d\d)___", f.name)
        if not f.is_file() or not m:
            continue
        hdr, office, dd, hh, mm = m.groups()
        txt = f.read_text(errors="replace")
        key = (f.name, len(txt))
        dup = key in seen
        seen.add(key)
        utc = datetime(2026, 10, int(dd), int(hh), int(mm))
        heads = sorted({l.strip() for l in txt.splitlines()
                        if re.search(r"\b(WARNING|STATEMENT|WATCH|ADVISORY)\b", l) and len(l.strip()) < 90})
        rows.append({"issued_utc": utc.strftime("%Y-%m-%d %H:%M"),
                     "issued_mdt": (utc - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"),
                     "header": hdr, "office": office, "kind": hdr[:2],
                     "mentions_wainwright": "WAINWRIGHT" in txt.upper(),
                     "headlines": " | ".join(heads)[:600], "duplicate_copy": dup,
                     "file": f.relative_to(D).as_posix()})
    rows.sort(key=lambda r: (r["issued_utc"], r["header"], r["file"]))
    with (D / "bulletins_index.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    print("swob rows:", swob(), "bulletins:", bulletins())
