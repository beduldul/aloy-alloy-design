"""Safe ingest for measured tensile results into ``outputs/experiment_log.json``.

This is the *feedback* half of the active-learning loop
(``propose -> experiment -> observe -> update -> propose``).  ``aloy.active``
already knows how to *consume* a measurement; this module is the guarded way to
*enter* one.

Design rules (why it is written this way):

* **Validate before writing.**  The composition must normalise to ~100 wt%,
  every value must be finite and physically plausible, and ``measured.ys_mpa``
  must be a positive float.  A bad record is rejected, never written.
* **Never corrupt the log.**  Writes go to a temp file in the same directory and
  are ``os.replace``d into place, so the on-disk file is valid JSON at every
  instant, even if the process is killed mid-write.
* **Never silently clobber.**  An existing non-empty measurement is preserved
  unless ``--force`` is given, in which case the old value is reported.
* **Append only.**  Existing records are never reordered or rewritten.

Consumption contract (verified against ``src/aloy/active.py``)::

    active.py:151   if r.get("measured", {}).get("ys_mpa") is not None:
    active.py:152       comp = r["composition"]
    active.py:153       xv = np.array([comp.get(e, 0.0) / 0.2 for e in M.ELEMENT_COLS])
    active.py:154       extra_x.append(np.clip(xv, 0, 1)); extra_y.append(r["measured"]["ys_mpa"])

i.e. the loop reads exactly ``record["composition"]`` (a flat
``{element_symbol: mass_fraction}`` dict, values in [0, 1]) and
``record["measured"]["ys_mpa"]`` (a bare float in MPa).  Everything else in the
record is metadata that the loop ignores.

CLI
---
    # a tensile result typed on the command line
    PYTHONPATH=src python3 -m aloy.experiment_log \
        --comp "Al=87.805,Mg=3.024,Zn=7.803,Cu=1.335,Si=0.013,Fe=0.020" \
        --ys 600 --elong 12.3 --hv 150 --notes "T6, 3 specimens"

    # a row that arrived as a file (CSV with a header, or a JSON fragment)
    PYTHONPATH=src python3 -m aloy.experiment_log --from-file result.csv --ys 600

    # register the planned (still unmeasured) headline candidate
    PYTHONPATH=src python3 -m aloy.experiment_log --register-only \
        --comp "Al=87.805,Mg=3.024,Zn=7.803,Cu=1.335,Si=0.013,Fe=0.020" \
        --predicted-ys 624.5326077175314
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import sys
import tempfile
from pathlib import Path

# --------------------------------------------------------------------------
# paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
DEFAULT_LOG = OUT / "experiment_log.json"
LAB_PROTOCOLS = OUT / "lab_protocols.json"
CREDIBILITY = OUT / "credibility_report.json"

# a measurement above this is physically absurd for an Al alloy (max real ~790 MPa)
YS_ABSURD_MPA = 5000.0
# composition sum tolerance for the "is this wt% or a mass fraction?" decision
_SUM_WTPCT = (99.0, 101.0)
_SUM_FRAC = (0.99, 1.01)


class IngestError(ValueError):
    """A record was rejected before anything was written."""


# --------------------------------------------------------------------------
# element list (import lazily so the CLI stays light; no torch import here)
# --------------------------------------------------------------------------
def _element_cols() -> list[str]:
    from .models import ELEMENT_COLS
    return list(ELEMENT_COLS)


def _canonical_composition(comp: dict) -> dict:
    """Normalise a composition dict to element -> mass fraction summing to 1.

    Accepts either mass fractions (``{"Al": 0.878, ...}``) or wt% (``{"Al": 87.8,
    ...}``) and returns a clean fraction dict.  Raises :class:`IngestError` on
    anything that does not normalise to ~100 wt%.
    """
    if not isinstance(comp, dict) or not comp:
        raise IngestError("composition must be a non-empty {element: value} mapping")

    known = set(_element_cols())
    values: dict[str, float] = {}
    for el, raw in comp.items():
        if not isinstance(el, str) or not el.strip():
            raise IngestError(f"invalid element symbol: {el!r}")
        sym = el.strip()
        if sym not in known:
            raise IngestError(f"unknown element symbol {sym!r} (not in models.ELEMENT_COLS)")
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise IngestError(f"composition value for {sym} is not numeric: {raw!r}")
        v = float(raw)
        if not math.isfinite(v):
            raise IngestError(f"composition value for {sym} is not finite: {raw!r}")
        if v < 0:
            raise IngestError(f"composition value for {sym} is negative: {v}")
        values[sym] = v

    total = sum(values.values())
    if total <= 0:
        raise IngestError("composition sums to zero")

    # decide the unit from the sum
    if _SUM_WTPCT[0] <= total <= _SUM_WTPCT[1]:
        frac = {k: v / 100.0 for k, v in values.items()}
    elif _SUM_FRAC[0] <= total <= _SUM_FRAC[1]:
        frac = {k: v / total for k, v in values.items()}
    else:
        raise IngestError(
            f"composition does not normalise to ~100 wt%: sum={total:.4f} "
            f"(expected ~100 for wt% or ~1 for a mass fraction)"
        )

    # renormalise to exactly 1 so the record is self-consistent
    s = sum(frac.values())
    frac = {k: v / s for k, v in frac.items()}
    return {k: round(v, 10) for k, v in frac.items() if v > 0}


# --------------------------------------------------------------------------
# schema validation
# --------------------------------------------------------------------------
_ALLOWED_TOP = {"composition", "measured", "predicted", "meta"}


def validate_record(record: dict) -> dict:
    """Validate one log record; return it unchanged or raise IngestError."""
    if not isinstance(record, dict):
        raise IngestError("record must be a JSON object")
    extra = set(record) - _ALLOWED_TOP
    if extra:
        raise IngestError(f"unknown top-level keys: {sorted(extra)}")
    if "composition" not in record or not isinstance(record["composition"], dict):
        raise IngestError("record needs a 'composition' object")
    for key in ("measured", "predicted"):
        if key in record and not isinstance(record[key], dict):
            raise IngestError(f"'{key}' must be an object")
    if "meta" in record and not isinstance(record["meta"], dict):
        raise IngestError("'meta' must be an object")
    validate_measured(record.get("measured") or {})
    validate_composition(record["composition"])
    return record


def validate_composition(comp: dict) -> dict:
    """Validate a stored composition (must already be mass fractions ~1)."""
    if not isinstance(comp, dict) or not comp:
        raise IngestError("composition must be a non-empty mapping")
    known = set(_element_cols())
    total = 0.0
    for el, v in comp.items():
        if el not in known:
            raise IngestError(f"unknown element {el!r}")
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise IngestError(f"composition value for {el} is not a finite number: {v!r}")
        if v < 0:
            raise IngestError(f"composition value for {el} is negative: {v}")
        total += v
    if not (_SUM_FRAC[0] <= total <= _SUM_FRAC[1]):
        raise IngestError(f"stored composition does not sum to ~1 (got {total:.6f})")
    return comp


def validate_measured(measured: dict) -> dict:
    """Validate the ``measured`` block; an empty dict is a legal blank."""
    if not isinstance(measured, dict):
        raise IngestError("'measured' must be an object")
    for key in measured:
        if key not in {"ys_mpa", "elong_pct", "hv", "uts_mpa", "n_specimens"}:
            raise IngestError(f"unexpected measured key {key!r}")
    if "ys_mpa" in measured:
        ys = measured["ys_mpa"]
        if isinstance(ys, bool) or not isinstance(ys, (int, float)):
            raise IngestError(f"measured.ys_mpa must be a number, got {ys!r}")
        if not math.isfinite(float(ys)):
            raise IngestError(f"measured.ys_mpa is not finite: {ys!r}")
        if float(ys) <= 0:
            raise IngestError(f"measured.ys_mpa must be positive, got {ys}")
        if float(ys) > YS_ABSURD_MPA:
            raise IngestError(f"measured.ys_mpa={ys} is physically absurd (> {YS_ABSURD_MPA} MPa)")
    if "elong_pct" in measured:
        e = measured["elong_pct"]
        if isinstance(e, bool) or not isinstance(e, (int, float)) or not (0 < float(e) <= 100):
            raise IngestError(f"measured.elong_pct must be in (0, 100], got {e!r}")
    if "hv" in measured:
        h = measured["hv"]
        if isinstance(h, bool) or not isinstance(h, (int, float)) or not (0 < float(h) < 2000):
            raise IngestError(f"measured.hv must be in (0, 2000), got {h!r}")
    return measured


# --------------------------------------------------------------------------
# I/O
# --------------------------------------------------------------------------
def load_log(path: Path = DEFAULT_LOG) -> list:
    if not Path(path).exists():
        return []
    rows = json.loads(Path(path).read_text())
    if not isinstance(rows, list):
        raise IngestError(f"{path} does not contain a JSON list")
    for r in rows:
        validate_record(r)
    return rows


def _atomic_write_json(path: Path, data: list) -> None:
    """Write JSON atomically: temp file in the same dir, fsync, then rename."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".experiment_log.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)          # atomic on POSIX: never a torn file
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# --------------------------------------------------------------------------
# composition matching
# --------------------------------------------------------------------------
def _same_composition(a: dict, b: dict, tol: float = 1e-4) -> bool:
    keys = set(a) | set(b)
    return all(abs(float(a.get(k, 0.0)) - float(b.get(k, 0.0))) <= tol for k in keys)


# --------------------------------------------------------------------------
# conformal interval
# --------------------------------------------------------------------------
def conformal_interval(comp: dict, predicted_ys: float | None = None) -> tuple[float, float, str]:
    """Return (lo, hi, source) for the 90% interval of this composition.

    Prefers the per-candidate interval recorded in ``outputs/lab_protocols.json``
    (matched on composition).  Falls back to ``predicted +/- q_halfwidth`` from
    ``outputs/credibility_report.json``.
    """
    if LAB_PROTOCOLS.exists():
        for entry in json.loads(LAB_PROTOCOLS.read_text()):
            cw = entry.get("composition_wt")
            if cw and _same_composition(cw, comp):
                lo, hi = entry["ys_interval90"]
                return float(lo), float(hi), f"lab_protocols.json::{entry.get('name', '?')}"
    if predicted_ys is not None and CREDIBILITY.exists():
        rep = json.loads(CREDIBILITY.read_text())
        q = float(rep["q_halfwidth"])
        return (predicted_ys - q, predicted_ys + q,
                f"credibility_report.json (pred +/- {q:.1f})")
    raise IngestError("no conformal interval available for this composition")


def interval_verdict(ys: float, lo: float, hi: float) -> str:
    """The single most useful line the tool prints."""
    if lo <= ys <= hi:
        margin = min(ys - lo, hi - ys)
        return (f"INSIDE [{lo:.1f}, {hi:.1f}] MPa  "
                f"(nearest bound {margin:.1f} MPa away)  -> conformal interval CONFIRMED")
    if ys < lo:
        return (f"BELOW {lo:.1f} MPa by {lo - ys:.1f} MPa  "
                f"-> model OVER-predicted beyond its stated uncertainty (calibration failure)")
    return (f"ABOVE {hi:.1f} MPa by {ys - hi:.1f} MPa  "
            f"-> interval failed to COVER (coverage violation, not a triumph)")


# --------------------------------------------------------------------------
# ingest operations
# --------------------------------------------------------------------------
def find_record(rows: list, comp: dict) -> int | None:
    for i, r in enumerate(rows):
        if _same_composition(r["composition"], comp):
            return i
    return None


def append_record(path: Path, record: dict, *, force: bool = False) -> dict:
    """Append (or update) a record.  Returns a summary dict of what happened."""
    validate_record(record)
    comp = record["composition"]
    measured = record.get("measured") or {}

    rows = load_log(path)
    n_before = len(rows)
    idx = find_record(rows, comp)
    action = "appended"
    replaced = None

    if idx is not None:
        existing = rows[idx].get("measured") or {}
        if existing.get("ys_mpa") is not None and not force:
            raise IngestError(
                f"record {idx} already has measured.ys_mpa={existing['ys_mpa']} "
                f"(use --force to overwrite)"
            )
        if existing.get("ys_mpa") is not None and force:
            replaced = existing.get("ys_mpa")
            action = "overwrote"
        else:
            action = "filled" if measured else "unchanged"
        # merge: keep existing meta, add new fields
        merged = dict(rows[idx])
        merged_measured = dict(existing)
        merged_measured.update(measured)
        merged["measured"] = merged_measured
        if record.get("meta"):
            merged["meta"] = {**(merged.get("meta") or {}), **record["meta"]}
        if record.get("predicted"):
            merged["predicted"] = {**(merged.get("predicted") or {}), **record["predicted"]}
        rows[idx] = merged
        final = merged
    else:
        rows.append(record)
        final = record

    _atomic_write_json(path, rows)          # only now does anything hit disk
    return {
        "action": action, "index": idx if idx is not None else n_before,
        "n_before": n_before, "n_after": len(rows),
        "replaced_ys": replaced, "record": final,
    }


def build_record(comp: dict, measured: dict | None = None,
                 predicted: dict | None = None, meta: dict | None = None) -> dict:
    """Build a validated record in the exact on-disk schema."""
    record: dict = {
        "composition": _canonical_composition(comp),
        "measured": dict(measured or {}),
        "predicted": dict(predicted or {}),
    }
    if meta:
        record["meta"] = dict(meta)
    validate_record(record)
    return record


# --------------------------------------------------------------------------
# input parsing (command line + files)
# --------------------------------------------------------------------------
def parse_comp_arg(text: str) -> dict:
    """Parse ``"Al=87.8,Mg=3.0"`` or ``"Al:87.8;Mg:3.0"`` into a dict."""
    text = text.strip()
    if text.startswith("{"):
        return json.loads(text)
    out: dict[str, float] = {}
    for part in text.replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        sep = "=" if "=" in part else (":" if ":" in part else None)
        if sep is None:
            raise IngestError(f"cannot parse composition token {part!r} (use Al=87.8,Mg=3.0)")
        k, v = part.split(sep, 1)
        try:
            out[k.strip()] = float(v)
        except ValueError:
            raise IngestError(f"non-numeric value in {part!r}") from None
    if not out:
        raise IngestError("empty composition")
    return out


def load_input_file(path: Path) -> tuple[dict, dict]:
    """Read a CSV row or a JSON fragment; return (composition, measured)."""
    text = Path(path).read_text().strip()
    if not text:
        raise IngestError(f"{path} is empty")

    if text[0] in "[{":
        obj = json.loads(text)
        if isinstance(obj, list):
            obj = obj[0]
        if not isinstance(obj, dict):
            raise IngestError(f"{path}: expected a JSON object")
        if "composition" in obj:                       # a full record
            return obj["composition"], obj.get("measured") or {}
        # a flat mapping: element names + optional measured keys
        comp = {k: v for k, v in obj.items() if k in set(_element_cols())}
        measured = {k: v for k, v in obj.items()
                    if k in {"ys_mpa", "elong_pct", "hv", "uts_mpa", "n_specimens"}}
        return comp, measured

    rows = [r for r in csv.reader(io.StringIO(text)) if any(c.strip() for c in r)]
    if not rows:
        raise IngestError(f"{path}: no CSV rows")
    header = rows[0]
    if not any(h.strip() in set(_element_cols()) for h in header):
        raise IngestError(
            f"{path}: CSV needs a header row naming the elements "
            f"(e.g. Al,Mg,Zn,Cu) plus optional ys_mpa/elong_pct/hv columns"
        )
    data = rows[1] if len(rows) > 1 else None
    if data is None:
        raise IngestError(f"{path}: header present but no data row")
    row = dict(zip([h.strip() for h in header], data))
    comp = {k: float(v) for k, v in row.items()
            if k in set(_element_cols()) and v not in ("", None)}
    measured = {}
    for k in ("ys_mpa", "elong_pct", "hv", "uts_mpa", "n_specimens"):
        if row.get(k) not in ("", None):
            measured[k] = float(row[k])
    return comp, measured


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def _print_summary(summary: dict, log_path: Path, show_interval: bool = True) -> None:
    rec = summary["record"]
    print(f"[{summary['action']}] record #{summary['index']}  "
          f"({summary['n_before']} -> {summary['n_after']} records in {log_path})")
    if summary["replaced_ys"] is not None:
        print(f"  replaced measured.ys_mpa = {summary['replaced_ys']}")
    comp = rec["composition"]
    print("  composition (mass fraction): "
          + ", ".join(f"{k}={v:.4f}" for k, v in comp.items()))
    print(f"  predicted: {rec.get('predicted') or '{}'}")
    measured = rec.get("measured") or {}
    if not measured:
        print("  measured:  (blank - awaiting tensile test)")
        return
    print(f"  measured:  {measured}")
    ys = measured.get("ys_mpa")
    if ys is not None and show_interval:
        try:
            lo, hi, src = conformal_interval(comp, rec.get("predicted", {}).get("ys_mpa"))
            print(f"  conformal 90% interval: [{lo:.1f}, {hi:.1f}] MPa  (source: {src})")
            print(f"  VERDICT: {interval_verdict(float(ys), lo, hi)}")
        except IngestError as exc:
            print(f"  conformal interval unavailable: {exc}")


def _run_active() -> None:
    print("\n[--run-active] running aloy.active ...")
    from . import active
    active.main()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python3 -m aloy.experiment_log",
        description="Safely record a measured tensile result into outputs/experiment_log.json",
    )
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--comp", help="composition, e.g. 'Al=87.805,Mg=3.024,Zn=7.803,Cu=1.335'")
    src.add_argument("--from-file", type=Path, help="CSV row or JSON fragment with the composition")
    ap.add_argument("--ys", type=float, help="measured 0.2%%-offset yield strength, MPa")
    ap.add_argument("--elong", type=float, help="measured elongation, %%")
    ap.add_argument("--hv", type=float, help="measured Vickers hardness")
    ap.add_argument("--uts", type=float, help="measured UTS, MPa")
    ap.add_argument("--notes", help="free-text note stored in meta.notes")
    ap.add_argument("--source", default="manual", help="provenance string (default: manual)")
    ap.add_argument("--date", help="ISO date of the measurement")
    ap.add_argument("--register-only", action="store_true",
                    help="append a blank (unmeasured) record for a planned experiment")
    ap.add_argument("--predicted-ys", type=float,
                    help="predicted YS to store when registering a new record")
    ap.add_argument("--force", action="store_true", help="overwrite an existing measurement")
    ap.add_argument("--run-active", action="store_true", help="run aloy.active after ingest")
    ap.add_argument("--log", type=Path, default=DEFAULT_LOG, help="log file (default: outputs/experiment_log.json)")
    args = ap.parse_args(argv)

    try:
        if args.from_file:
            comp, file_measured = load_input_file(args.from_file)
        elif args.comp:
            comp, file_measured = parse_comp_arg(args.comp), {}
        else:
            ap.error("one of --comp or --from-file is required")

        cli_measured = {k: v for k, v in
                        (("ys_mpa", args.ys), ("elong_pct", args.elong),
                         ("hv", args.hv), ("uts_mpa", args.uts)) if v is not None}
        measured = {**file_measured, **cli_measured}

        if args.register_only and measured:
            raise IngestError("--register-only cannot be combined with a measurement")

        predicted = {}
        if args.predicted_ys is not None:
            predicted["ys_mpa"] = args.predicted_ys

        meta = {"source": args.source, "entry": "aloy.experiment_log"}
        if args.date:
            meta["date"] = args.date
        if args.notes:
            meta["notes"] = args.notes
        if args.register_only:
            meta["status"] = "planned; no data yet"

        record = build_record(comp, measured, predicted, meta)
        summary = append_record(args.log, record, force=args.force)
        _print_summary(summary, args.log)
    except IngestError as exc:
        print(f"REJECTED (nothing written): {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"REJECTED (bad JSON input): {exc}", file=sys.stderr)
        return 2

    if args.run_active:
        _run_active()
    return 0


def _cli() -> int:
    """Entry point that tolerates a closed pipe (e.g. ``| head``)."""
    try:
        return main()
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except BrokenPipeError:
            pass
        return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
