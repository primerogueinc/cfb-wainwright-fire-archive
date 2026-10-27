# Reproducibility check (Oct. 25, 2026)

`scripts/authentic_stoic_alternative_hypothesis/model_v4/run_all.sh` was run twice from scratch, in two separate clean checkouts with separate working folders (all model_v4 outputs deleted first except `cases.json` and `cases_line.json`). Each run took about 35 minutes on two cores.

Result: all 87 output files agree between the two runs and with the committed outputs. 77 are byte-identical. The other 10 differ only in row order (`fit_shape_all.csv.gz`, `fit_shape_best.csv`: the morning fit runs in parallel and returns rows in any order; identical when sorted, maximum numeric difference 0) or in gzip timestamps (`escape_perm.csv.gz`, 8 files; contents identical). `fit_shape.py` now writes its rows in a fixed order.

Comparison: SHA-256 per file, then order-insensitive numeric comparison for CSV, JSON equality, raster difference.
