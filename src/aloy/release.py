"""Prepare a release: integrity manifest, archive, and pre-flight checks.

Usage:
    PYTHONPATH=src python3 -m aloy.release --check      # audit only
    PYTHONPATH=src python3 -m aloy.release --build      # build the zip + manifest

The pre-flight check enforces the honesty requirements of this project: the
release must state that it contains predictions, not measurements, and must
credit the source datasets. It will refuse to build a package that overclaims.
"""
from __future__ import annotations
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {"__pycache__", ".git", ".ipynb_checkpoints", ".pytest_cache"}
SKIP_SUFFIX = {".pyc", ".DS_Store"}


def _iter_files(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix in SKIP_SUFFIX or p.name == "MANIFEST.sha256":
            continue
        yield p


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(root: Path = ROOT) -> Path:
    out = root / "MANIFEST.sha256"
    lines = []
    for p in _iter_files(root):
        rel = p.relative_to(root)
        lines.append(f"{_sha256(p)}  {rel}")
    out.write_text("\n".join(lines) + "\n")
    return out


def preflight(root: Path = ROOT) -> tuple[bool, list[str]]:
    """Check that the package is honest and complete before publication."""
    issues: list[str] = []

    required = ["README.md", "CITATION.md", "CITATION.cff", "LICENSE",
                "REPORT.md", "docs/DATA_SOURCES.md", "docs/RELEASE_GUIDE.md"]
    for f in required:
        if not (root / f).exists():
            issues.append(f"missing required file: {f}")

    readme = (root / "README.md").read_text(errors="ignore").lower() if \
        (root / "README.md").exists() else ""

    # honesty checks: the release must not imply experimental validation
    honesty_terms = ["prediksi", "prediction", "bukan pengganti eksperimen",
                     "not a substitute", "wajib divalidasi", "no experimental"]
    if not any(t in readme for t in honesty_terms):
        issues.append("README does not state that results are predictions, not "
                      "measurements")

    # attribution checks
    if "10.17632/b6br4yk6r3.1" not in readme and \
       "b6br4yk6r3" not in (root / "CITATION.md").read_text(errors="ignore"):
        issues.append("Al source dataset (DOI 10.17632/b6br4yk6r3.1) not attributed")
    if "2fjhmdg5nt" not in (root / "CITATION.md").read_text(errors="ignore"):
        issues.append("Mg source dataset (DOI 10.17632/2fjhmdg5nt.2) not attributed")

    # leftovers
    if (root / "outputs" / "models").exists():
        pass  # models are allowed; note size rather than forbid
    for bad in ("credentials.json", "token.txt", ".env"):
        if (root / bad).exists():
            issues.append(f"possible secret file present: {bad}")

    # at least one derived result must be present
    if not (root / "outputs").exists():
        issues.append("outputs/ directory missing — nothing to release")

    return (len(issues) == 0), issues


def build_archive(root: Path = ROOT) -> Path:
    parent = root.parent
    zip_path = parent / f"aloy-v1.0.0.zip"
    if zip_path.exists():
        zip_path.unlink()
    subprocess.run(
        ["zip", "-r", str(zip_path), root.name,
         "-x", "*/__pycache__/*", "*/.git/*", "*/.DS_Store"],
        cwd=parent, check=True, stdout=subprocess.DEVNULL)
    return zip_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--build", action="store_true")
    args = ap.parse_args()

    print(f"Release root: {ROOT}\n")

    ok, issues = preflight()
    print("PRE-FLIGHT")
    if ok:
        print("  [PASS] package is honest and complete")
    else:
        for i in issues:
            print(f"  [FAIL] {i}")

    if args.check or not args.build:
        if args.check:
            sys.exit(0 if ok else 1)
        return

    if not ok:
        print("\nRefusing to build: fix the issues above first.")
        sys.exit(1)

    mf = write_manifest()
    n = len(mf.read_text().splitlines())
    print(f"\nMANIFEST: {n} files hashed -> {mf.name}")

    zp = build_archive()
    size = zp.stat().st_size / 1e6
    print(f"ARCHIVE : {zp}  ({size:.1f} MB)")
    print("\nNext: follow docs/RELEASE_GUIDE.md step 4 to deposit on Zenodo.")


if __name__ == "__main__":
    main()
