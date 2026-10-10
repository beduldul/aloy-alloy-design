# How to record a tensile result in `outputs/experiment_log.json`

The active-learning loop reads exactly one thing from each record: the
composition (mass fractions) and `measured.ys_mpa`. Use the ingest tool so a
result is validated and the log stays valid JSON.

```bash
# record a measured yield strength (composition as wt% or as a mass fraction)
PYTHONPATH=src python3 -m aloy.experiment_log \
  --comp "Al=87.805,Mg=3.024,Zn=7.803,Cu=1.335,Si=0.013,Fe=0.020" \
  --ys 600 --elong 12.3 --hv 150 --notes "T6, 3 specimens" --run-active
```

Output (the last line is the point of the whole exercise):

```
[filled] record #15  (16 -> 16 records in outputs/experiment_log.json)
  conformal 90% interval: [517.0, 732.1] MPa  (source: lab_protocols.json::Candidate 2 (T6))
  VERDICT: INSIDE [517.0, 732.1] MPa  (nearest bound 83.0 MPa away)  -> conformal interval CONFIRMED
```

`VERDICT` is one of **INSIDE** (interval confirmed), **BELOW 517** (model
over-predicted beyond its uncertainty — a calibration failure), or **ABOVE 732**
(the interval failed to cover — report it as a coverage violation, not a win).

Other forms: `--from-file result.csv` (a CSV row with an element header, or a
JSON fragment); `--force` to overwrite an existing measurement (it reports what
it replaced); `--register-only` to add a planned, still-blank record. A bad
composition or a non-positive/non-numeric `--ys` is **rejected before anything is
written**.
