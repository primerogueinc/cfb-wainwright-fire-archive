# Cleo Energy Corp. / Sumerian Oil & Gas: court record

Public court filings from the three Cleo Energy Corp. proceedings, archived by Prime Rogue Inc. as they are collected. Copies were obtained from the court officer's public website (Alvarez & Marsal Canada Inc., https://www.alvarezandmarsal.com/CLEO).

| Folder | Proceeding | Court / estate file |
|---|---|---|
| `noi/` | Notice of intention to make a proposal (BIA), Dec. 2024 – June 2025 | Court of King's Bench of Alberta B301-163430; estate 25-3163430 |
| `receivership/` | Receivership of Cleo Energy Corp., then of 2755857 Alberta Ltd. (ResidualCo), June 2025 – | 2501-09028 |
| `bankruptcy/` | Bankruptcy of 2755857 Alberta Ltd., July 2026 – | to be added |

- `INDEX.csv`: one row per unique document. Columns: proceeding, clerk's filing date, date pronounced, title, court file, justice, filing firm, pages, stored path, SHA-256, original file name, whether it is on the receiver's site, notes. Fields are read from each document's first page by script and may need hand-checking.
- `DUPLICATES.csv`: byte-identical copies received more than once (not stored twice).
- `SITE_LISTING.csv`: the documents the receiver's site lists, section by section, used to check what is still missing. Incomplete until every section page is captured.
- `text/`: full text of each PDF (pdftotext), for searching.
- Script: `scripts/reference/cleo_court_ingest.py`.

Confidential appendices sealed by the court are not here unless the seal has lifted and the court officer has published them.
