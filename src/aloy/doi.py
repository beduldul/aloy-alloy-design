"""Insert your real Zenodo DOI everywhere at once, after you publish.

Usage:
    PYTHONPATH=src python3 -m aloy.doi --set 10.5281/zenodo.1234567
    PYTHONPATH=src python3 -m aloy.doi --check

Why this exists: a DOI appears in several files (README badge, CITATION.md,
CITATION.cff, the manuscript template). Forgetting one leaves broken links in a
published artefact. This script replaces all of them and verifies none remain.
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLACEHOLDER = "10.5281/zenodo.XXXXXXX"
DOI_RE = re.compile(r"^10\.5281/zenodo\.\d+$")

# files that legitimately mention the placeholder as an instruction
EXPLANATORY = {
    "release/PUBLICATION_PACKAGE.md",
    "docs/RELEASE_GUIDE.md",
    "src/aloy/doi.py",
    "src/aloy/release.py",
}
TARGET_SUFFIX = {".md", ".cff", ".txt", ".json", ".py", ".rst"}


def _iter_targets():
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix not in TARGET_SUFFIX:
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel in EXPLANATORY:
            continue
        if any(part in {"__pycache__", ".git"} for part in p.parts):
            continue
        yield p, rel


def find_placeholders() -> dict[str, int]:
    hits = {}
    for p, rel in _iter_targets():
        try:
            n = p.read_text(errors="ignore").count(PLACEHOLDER)
        except Exception:
            continue
        if n:
            hits[rel] = n
    return hits


def check() -> bool:
    hits = find_placeholders()
    if not hits:
        print("  [OK] no DOI placeholders remain outside explanatory docs")
        return True
    print("  [PENDING] DOI still a placeholder in:")
    for rel, n in hits.items():
        print(f"      {rel}  ({n}x)")
    print("\n  After publishing on Zenodo, run:")
    print("      PYTHONPATH=src python3 -m aloy.doi --set 10.5281/zenodo.<your-id>")
    return False


def set_doi(doi: str) -> int:
    doi = doi.strip()
    if not DOI_RE.match(doi):
        print(f"  [ERROR] '{doi}' is not a valid Zenodo DOI.")
        print("          Expected form: 10.5281/zenodo.1234567")
        return 0
    total = 0
    for p, rel in _iter_targets():
        try:
            t = p.read_text(errors="ignore")
        except Exception:
            continue
        if PLACEHOLDER in t:
            n = t.count(PLACEHOLDER)
            p.write_text(t.replace(PLACEHOLDER, doi))
            print(f"  updated {rel}  ({n} replacement{'s' if n > 1 else ''})")
            total += n
    print(f"\n  {total} placeholder(s) replaced with {doi}")
    remaining = find_placeholders()
    if remaining:
        print("  [WARN] placeholders still present in:")
        for rel, n in remaining.items():
            print(f"      {rel} ({n}x)")
    else:
        print("  [OK] every placeholder replaced")
    print("\n  Next: rebuild the release archive ->")
    print("      PYTHONPATH=src python3 -m aloy.release --build")
    return total


def main():
    ap = argparse.ArgumentParser(description="Insert your real Zenodo DOI everywhere.")
    ap.add_argument("--set", metavar="DOI", help="e.g. 10.5281/zenodo.1234567")
    ap.add_argument("--check", action="store_true", help="report remaining placeholders")
    args = ap.parse_args()

    if args.set:
        sys.exit(0 if set_doi(args.set) else 1)
    ok = check()
    sys.exit(0 if (args.check and ok) else (0 if args.check or ok else 0))


if __name__ == "__main__":
    main()
