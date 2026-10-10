"""Tests for the experiment-log ingest tooling (``aloy.experiment_log``).

The single most important property under test: **the 15 pre-existing records in
``outputs/experiment_log.json`` must survive every operation untouched.**  Every
test therefore works on a fresh copy of the real file and re-checks the original
15 record hashes afterwards.

Run with::

    PYTHONPATH=src python3 -m pytest tests/ -v
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from aloy import experiment_log as EL

ROOT = Path(__file__).resolve().parents[1]
REAL_LOG = ROOT / "outputs" / "experiment_log.json"

# sha256 of json.dumps(record, sort_keys=True, separators=(",", ":")) for each of
# the 15 original records, captured from the released file before any change.
EXPECTED_ORIGINAL_HASHES = (
    "16eae4cc55c421c9cf3b414ebf4fb3210753569f64ec49a4474c82d210899983",
    "fd048d87853a0dc20f063e6d38221d2b3160f218504636f882f403598e7687be",
    "c442d2c8a22c17ecbf99621e9ba071d0e336390ffe5aae451a7292a499806f1f",
    "e7781b04fadcfd8c0ba800588eaa0a7e00428117644e900ccccd3ec02a610dc4",
    "230089733617725a2bef77c6aefbeef72d386c2c47fc1c2221fdb7da32102d00",
    "18e2df0e93d4c3231b5e79bd546c6e5f851ff0d3c6a64b1b9eea47dfca5df981",
    "8ef1064ed2fe10fc82153aae3c828c742d6344040e8c8c5d23094ce5a5d878e3",
    "406df47f31aaf6c0e9919bfd353b07c41957bd3a112ebc5bdc4efa6a161b2d4d",
    "c1253bcf5668d178f648267c83e6ad1cc1dcc47ee5fae7739ae527412fef710f",
    "36d58b9ff2578a40a78bedc3c67fc99287033d9bfcd9ad952920092cdb33fad9",
    "41c8452673e6c63d1382a9baa4f4033c34909969f7f7f1384117d3557bec2f70",
    "61cd816d4754eb3b1899d5e34f56a49349ac27814db856a97e9c80460ddfa10d",
    "c442d2c8a22c17ecbf99621e9ba071d0e336390ffe5aae451a7292a499806f1f",
    "bc99dcfff778a835c3b2d91232bce085fe344f6844e5c4d41f864edb9f607288",
    "cbbe9be71917a175f3fab18d47de3eeb944d1de9f3b9a851bfeff77b4370bf48",
)

HEADLINE = {          # Al-3.0Mg-7.8Zn-1.3Cu, candidates_final.csv row 121
    "Al": 0.8780529253222041, "Mg": 0.0302391663265414, "Zn": 0.0780331868820703,
    "Cu": 0.0133462688714121, "Si": 0.0001306291702535, "Fe": 0.0001951194876558,
}


def record_hash(record: dict) -> str:
    blob = json.dumps(record, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()


def assert_originals_survived(path: Path) -> None:
    """The first 15 records must still be present, in order, byte-identical."""
    rows = json.loads(path.read_text())
    assert len(rows) >= 15, "an original record was deleted"
    got = tuple(record_hash(r) for r in rows[:15])
    assert got == EXPECTED_ORIGINAL_HASHES, "an original record was mutated or reordered"


def assert_valid_json(path: Path) -> list:
    """Re-parse from disk; a torn write would raise here."""
    rows = json.loads(path.read_text())
    assert isinstance(rows, list)
    return rows


@pytest.fixture()
def log(tmp_path: Path) -> Path:
    """A fresh working copy of the real, released log."""
    dst = tmp_path / "experiment_log.json"
    shutil.copy(REAL_LOG, dst)
    return dst


# ---------------------------------------------------------------------------
# the real file itself is untouched by this suite
# ---------------------------------------------------------------------------
def test_real_log_still_has_15_originals() -> None:
    assert_originals_survived(REAL_LOG)
    assert len(json.loads(REAL_LOG.read_text())) >= 15


# ---------------------------------------------------------------------------
# valid ingest
# ---------------------------------------------------------------------------
def test_valid_ingest_appends_and_reports(log: Path) -> None:
    rec = EL.build_record(HEADLINE, {"ys_mpa": 610.0, "elong_pct": 12.5},
                          {"ys_mpa": 624.5326077175314}, {"source": "test"})
    summary = EL.append_record(log, rec)
    assert summary["action"] in {"appended", "filled"}
    rows = assert_valid_json(log)
    assert rows[-1]["measured"]["ys_mpa"] == 610.0
    assert rows[-1]["predicted"]["ys_mpa"] == 624.5326077175314
    assert_originals_survived(log)


def test_ingest_via_cli_main(log: Path, capsys: pytest.CaptureFixture) -> None:
    code = EL.main(["--log", str(log),
                    "--comp", json.dumps(HEADLINE),
                    "--ys", "600", "--notes", "T6, 3 specimens"])
    out = capsys.readouterr().out
    assert code == 0
    assert "VERDICT: INSIDE [517.0, 732.1]" in out
    assert_valid_json(log)
    assert_originals_survived(log)


def test_verdict_below_interval(log: Path, capsys: pytest.CaptureFixture) -> None:
    assert EL.main(["--log", str(log), "--comp", json.dumps(HEADLINE), "--ys", "480"]) == 0
    assert "BELOW 517.0" in capsys.readouterr().out


def test_verdict_above_interval(log: Path, capsys: pytest.CaptureFixture) -> None:
    assert EL.main(["--log", str(log), "--comp", json.dumps(HEADLINE), "--ys", "800"]) == 0
    assert "ABOVE 732.1" in capsys.readouterr().out


def test_register_only_leaves_measured_blank(log: Path) -> None:
    code = EL.main(["--log", str(log), "--comp", json.dumps(HEADLINE),
                    "--register-only", "--predicted-ys", "624.5"])
    assert code == 0
    rows = assert_valid_json(log)
    assert rows[-1]["measured"] == {}
    assert_originals_survived(log)


# ---------------------------------------------------------------------------
# composition normalisation failures
# ---------------------------------------------------------------------------
def test_composition_that_does_not_normalise_is_rejected(log: Path,
                                                          capsys: pytest.CaptureFixture) -> None:
    n = len(json.loads(log.read_text()))
    code = EL.main(["--log", str(log), "--comp", "Al=50,Mg=3", "--ys", "600"])
    assert code == 2
    assert "does not normalise" in capsys.readouterr().err
    assert len(assert_valid_json(log)) == n          # nothing written
    assert_originals_survived(log)


def test_unknown_element_is_rejected(log: Path, capsys: pytest.CaptureFixture) -> None:
    code = EL.main(["--log", str(log), "--comp", "Al=87,Xx=3,Zn=7", "--ys", "600"])
    assert code == 2
    assert "unknown element" in capsys.readouterr().err
    assert_originals_survived(log)


def test_wt_percent_and_fraction_are_equivalent() -> None:
    wt = EL._canonical_composition({"Al": 87.805, "Mg": 3.024, "Zn": 7.803, "Cu": 1.335})
    fr = EL._canonical_composition({"Al": 0.87805, "Mg": 0.03024, "Zn": 0.07803, "Cu": 0.01335})
    assert wt.keys() == fr.keys()
    for k in wt:
        assert wt[k] == pytest.approx(fr[k], abs=1e-4)


# ---------------------------------------------------------------------------
# bad yield-strength values
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("bad", ["-5", "0", "9999"])
def test_bad_ys_is_rejected(log: Path, bad: str, capsys: pytest.CaptureFixture) -> None:
    n = len(json.loads(log.read_text()))
    code = EL.main(["--log", str(log), "--comp", json.dumps(HEADLINE), "--ys", bad])
    assert code == 2
    assert capsys.readouterr().err
    assert len(assert_valid_json(log)) == n          # nothing written
    assert_originals_survived(log)


def test_non_numeric_ys_is_rejected(log: Path) -> None:
    n = len(json.loads(log.read_text()))
    with pytest.raises(SystemExit):          # argparse rejects before any write
        EL.main(["--log", str(log), "--comp", json.dumps(HEADLINE), "--ys", "abc"])
    assert len(assert_valid_json(log)) == n          # nothing written
    assert_originals_survived(log)


def test_non_numeric_ys_in_builder_raises() -> None:
    with pytest.raises(EL.IngestError, match="must be a number"):
        EL.build_record(HEADLINE, {"ys_mpa": "abc"})


def test_negative_ys_in_builder_raises() -> None:
    with pytest.raises(EL.IngestError, match="must be positive"):
        EL.build_record(HEADLINE, {"ys_mpa": -5.0})


# ---------------------------------------------------------------------------
# overwrite protection
# ---------------------------------------------------------------------------
def _fill(log: Path, ys: float) -> None:
    EL.append_record(log, EL.build_record(HEADLINE, {"ys_mpa": ys}))


def test_refuses_to_overwrite_without_force(log: Path, capsys: pytest.CaptureFixture) -> None:
    _fill(log, 600.0)
    code = EL.main(["--log", str(log), "--comp", json.dumps(HEADLINE), "--ys", "601"])
    assert code == 2
    assert "use --force" in capsys.readouterr().err
    assert json.loads(log.read_text())[-1]["measured"]["ys_mpa"] == 600.0
    assert_originals_survived(log)


def test_force_overwrites_and_reports_replacement(log: Path,
                                                  capsys: pytest.CaptureFixture) -> None:
    _fill(log, 600.0)
    code = EL.main(["--log", str(log), "--comp", json.dumps(HEADLINE),
                    "--ys", "605", "--force"])
    out = capsys.readouterr().out
    assert code == 0
    assert "replaced measured.ys_mpa = 600.0" in out
    rows = assert_valid_json(log)
    assert rows[-1]["measured"]["ys_mpa"] == 605.0
    assert_originals_survived(log)


def test_force_does_not_duplicate_the_record(log: Path) -> None:
    _fill(log, 600.0)
    EL.append_record(log, EL.build_record(HEADLINE, {"ys_mpa": 601.0}), force=True)
    rows = assert_valid_json(log)
    matches = [r for r in rows if EL._same_composition(r["composition"], HEADLINE)]
    assert len(matches) == 1
    assert_originals_survived(log)


# ---------------------------------------------------------------------------
# file input
# ---------------------------------------------------------------------------
def test_ingest_from_csv_file(log: Path, tmp_path: Path) -> None:
    csv = tmp_path / "row.csv"
    csv.write_text("Al,Mg,Zn,Cu,Si,Fe,ys_mpa,elong_pct,hv\n"
                   "87.805,3.024,7.803,1.335,0.013,0.020,610,12.5,148\n")
    comp, measured = EL.load_input_file(csv)
    assert measured["ys_mpa"] == 610.0
    assert EL.main(["--log", str(log), "--from-file", str(csv)]) == 0
    rows = assert_valid_json(log)
    assert rows[-1]["measured"]["hv"] == 148.0
    assert_originals_survived(log)


def test_ingest_from_json_fragment(log: Path, tmp_path: Path) -> None:
    frag = tmp_path / "frag.json"
    frag.write_text(json.dumps({**HEADLINE, "ys_mpa": 615}))
    assert EL.main(["--log", str(log), "--from-file", str(frag)]) == 0
    rows = assert_valid_json(log)
    assert rows[-1]["measured"]["ys_mpa"] == 615
    assert_originals_survived(log)


# ---------------------------------------------------------------------------
# atomicity / JSON validity
# ---------------------------------------------------------------------------
def test_file_is_valid_json_after_every_operation(log: Path) -> None:
    assert_valid_json(log)
    EL.append_record(log, EL.build_record(HEADLINE, {"ys_mpa": 600.0}))
    assert_valid_json(log)
    with pytest.raises(EL.IngestError):
        EL.append_record(log, EL.build_record(HEADLINE, {"ys_mpa": 601.0}))
    assert_valid_json(log)
    EL.append_record(log, EL.build_record(HEADLINE, {"ys_mpa": 602.0}), force=True)
    assert_valid_json(log)
    assert_originals_survived(log)


def test_atomic_write_leaves_no_temp_files(log: Path) -> None:
    EL.append_record(log, EL.build_record(HEADLINE, {"ys_mpa": 600.0}))
    leftovers = [p.name for p in log.parent.iterdir() if p.name.startswith(".experiment_log.")]
    assert leftovers == []


def test_atomic_write_survives_a_crash_mid_write(log: Path, monkeypatch) -> None:
    """If json.dump blows up, the original file must be untouched."""
    before = log.read_text()
    real_dump = json.dump

    def boom(*a, **k):
        raise RuntimeError("simulated crash")

    monkeypatch.setattr(json, "dump", boom)
    with pytest.raises(RuntimeError):
        EL.append_record(log, EL.build_record(HEADLINE, {"ys_mpa": 600.0}))
    monkeypatch.setattr(json, "dump", real_dump)
    assert log.read_text() == before
    assert_originals_survived(log)
    assert [p.name for p in log.parent.iterdir() if p.name.startswith(".experiment_log.")] == []


def test_load_log_rejects_corrupt_file(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text('[{"composition": {"Al": 1.0}, "measured": {}, "predicted": {}}, ')
    with pytest.raises(json.JSONDecodeError):
        EL.load_log(bad)


# ---------------------------------------------------------------------------
# conformal interval logic
# ---------------------------------------------------------------------------
def test_interval_matches_lab_protocols() -> None:
    lo, hi, src = EL.conformal_interval(HEADLINE, 624.5326077175314)
    assert (round(lo), round(hi)) == (517, 732)
    assert "lab_protocols" in src


def test_interval_falls_back_to_credibility() -> None:
    lo, hi, src = EL.conformal_interval({"Al": 0.99, "Mg": 0.01}, 600.0)
    assert lo == pytest.approx(600.0 - 107.52285128151688)
    assert "credibility" in src


@pytest.mark.parametrize("ys,expect", [(600, "INSIDE"), (480, "BELOW"), (800, "ABOVE")])
def test_interval_verdict(ys: float, expect: str) -> None:
    assert expect in EL.interval_verdict(ys, 517.0, 732.0)
