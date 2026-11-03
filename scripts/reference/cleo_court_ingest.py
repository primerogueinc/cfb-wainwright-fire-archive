#!/usr/bin/env python3
"""Ingest Cleo Energy / Sumerian court documents into the archive.

Usage: python3 cleo_court_ingest.py FILE.pdf [FILE.pdf ...]

For each PDF: SHA-256, page count, first-page metadata (court file number,
document title, clerk's filing stamp date, date pronounced, justice, filer),
proceeding (NOI / receivership / bankruptcy / other). Unique files are copied
to data/reference/sumerian/court/cleo_proceedings/<proceeding>/ with a
dated, slugged name, and their full text goes to .../text/. Byte-identical
duplicates are logged in DUPLICATES.csv and not stored twice.
INDEX.csv is rewritten sorted by proceeding, then date.
"""
import csv, hashlib, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "data/reference/sumerian/court/cleo_proceedings"
INDEX = BASE / "INDEX.csv"
DUPS = BASE / "DUPLICATES.csv"
FIELDS = ["proceeding", "date_filed", "date_pronounced", "document", "court_file",
          "justice", "filed_by", "pages", "stored_as", "sha256", "original_name",
          "on_receiver_site", "notes"]
MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def norm_date(s):
    s = re.sub(r"\s+", " ", s.strip().replace(",", ""))
    for fmt in ("%b %d %Y", "%B %d %Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            pass
    return ""


def meta(pdf):
    first = sh("pdftotext", "-l", "2", "-layout", str(pdf), "-")
    flat = re.sub(r"[ \t]+", " ", first)
    m = {}
    cf = re.search(r"COURT FILE (?:NO\.?|NUMBER)\s+(B\d{3}[- ]?\d{6}|\d{2}[- ]?\d{7}|\d{4}[- ]\d{5})", flat)
    m["court_file"] = cf.group(1).strip().replace(" ", "-") if cf else ""
    if not m["court_file"]:
        cf = re.search(r"\b(B301[- ]\d{6}|25\d{2}[- ]\d{5}|2501[- ]\d{5})\b", flat)
        m["court_file"] = cf.group(1).replace(" ", "-") if cf else ""
    # title: lines after DOCUMENT up to ADDRESS FOR SERVICE
    d = re.search(r"\bDOCUMENT\b(.*?)(?:ADDRESS FOR|DATE ON WHICH|$)", first, re.S)
    title = ""
    if d:
        lines = []
        for ln in d.group(1).splitlines():
            ln = re.sub(r"\s{2,}", "  ", ln.strip())
            # keep the right-hand column text
            parts = [p for p in ln.split("  ") if p.strip()]
            if parts:
                lines.append(parts[-1] if len(parts) > 1 else parts[0])
        title = " ".join(lines).strip()
    m["document"] = re.sub(r"\s+", " ", title)[:200]
    fd = re.search(rf"\b({MONTHS})[a-z]* ?(\d{{1,2}}),? (20\d\d)\b", flat)
    m["date_filed"] = norm_date(" ".join(fd.groups())) if fd else ""
    dp = re.search(r"PRONOUNCED:?\s*([A-Z][a-z]+ \d{1,2},? 20\d\d)", flat)
    m["date_pronounced"] = norm_date(dp.group(1)) if dp else ""
    j = re.search(r"(?:JUSTICE WHO (?:MADE|GRANTED) THIS ORDER:?|NAME OF JUSTICE WHO\s+GRANTED THIS ORDER:?)\s*(?:GRANTED THIS ORDER:?)?\s*(The Honourable[^\n]+)", flat)
    m["justice"] = re.sub(r"\s+in Commercial.*$", "", j.group(1)).strip() if j else ""
    fb = re.search(r"FILING THIS(?: DOCUMENT)?\s+(.*?)\n", first) or re.search(r"ADDRESS FOR\s+([A-Z][^\n]+)", first)
    firm = re.search(r"(Miller Thomson LLP|MILLER THOMSON LLP|Gowling WLG \(Canada\) LLP|MLT Aikins LLP|Lawson Lundell LLP|Alvarez & Marsal Canada Inc\.|McCarthy T[ée]trault LLP|Burnet, Duckworth & Palmer LLP|Bennett Jones LLP|Osler[^\n]*LLP|Dentons Canada LLP|Torys LLP|Fasken[^\n]*LLP|Cassels[^\n]*LLP|Blake, Cassels & Graydon LLP|Norton Rose Fulbright Canada LLP|Stikeman Elliott LLP|Department of Justice|Alberta Justice)", first)
    m["filed_by"] = firm.group(1) if firm else ""
    up = first.upper()
    cfn = m["court_file"]
    if cfn.startswith("2501"):
        m["proceeding"] = "receivership"
    elif cfn.startswith("B301") or "NOTICE OF INTENTION" in up:
        m["proceeding"] = "noi"
    elif "BANKRUPTCY OF" in up or "ESTATE NO" in up:
        m["proceeding"] = "bankruptcy"
    elif "RECEIVERSHIP" in up:
        m["proceeding"] = "receivership"
    else:
        m["proceeding"] = "other"
    m["pages"] = (re.search(r"Pages:\s+(\d+)", sh("pdfinfo", str(pdf))) or [None, ""])[1]
    return m


def slug(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s[:70] or "document"


def load(path):
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def main(files):
    rows, dups = load(INDEX), load(DUPS)
    by_sha = {r["sha256"]: r for r in rows}
    for f in files:
        p = Path(f)
        h = sha(p)
        orig = re.sub(r"^[0-9a-f]{8}-", "", p.name)
        if h in by_sha:
            dups.append({"original_name": orig, "sha256": h, "duplicate_of": by_sha[h]["stored_as"]})
            print(f"DUP  {orig} == {by_sha[h]['stored_as']}")
            continue
        m = meta(p)
        d = m["date_filed"] or m["date_pronounced"] or "undated"
        name = f"{d}_{slug(m['document'] or Path(orig).stem)}"
        dest_dir = BASE / m["proceeding"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{name}.pdf"
        n = 2
        while dest.exists():
            dest = dest_dir / f"{name}_{n}.pdf"; n += 1
        shutil.copyfile(p, dest)
        tdir = BASE / "text" / m["proceeding"]
        tdir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["pdftotext", "-layout", str(dest), str(tdir / (dest.stem + ".txt"))])
        row = {k: "" for k in FIELDS}
        row.update(m)
        row.update({"stored_as": str(dest.relative_to(BASE)), "sha256": h, "original_name": orig})
        rows.append(row); by_sha[h] = row
        print(f"NEW  {row['stored_as']}  [{m['court_file']}] {m['document'][:60]}")
    order = {"noi": 0, "receivership": 1, "bankruptcy": 2, "other": 3}
    rows.sort(key=lambda r: (order.get(r["proceeding"], 9), r["date_filed"] or r["date_pronounced"] or "9999", r["stored_as"]))
    BASE.mkdir(parents=True, exist_ok=True)
    with INDEX.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    with DUPS.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["original_name", "sha256", "duplicate_of"]); w.writeheader(); w.writerows(dups)
    print(f"index: {len(rows)} unique, {len(dups)} duplicates")


if __name__ == "__main__":
    main(sys.argv[1:])
