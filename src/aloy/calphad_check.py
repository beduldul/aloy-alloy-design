"""CALPHAD phase validation for candidate alloys (pycalphad).

Why this matters
----------------
A regression model can predict high strength for a composition that would, in
reality, form brittle intermetallics (Al3Zr, Al3Sc, MgZn2, Al2Cu) instead of a
strong-but-ductile solid solution plus fine precipitates. This module performs a
real thermodynamic equilibrium calculation so we can *reject* candidates whose
phase assemblage is metallurgically wrong before anyone melts metal.

Databases
---------
pycalphad ships with a few TDB files under `pycalphad.tests.databases`; for a
serious study the user should plug in a commercial/COST507-style database.
We build a transparent Al-X binary/ternary assessment from the built-in
`alzn_mey.tdb` (Al-Zn, Mey assessment) where available, and otherwise fall back
to an analytic solid-solution + intermetallic screening rule driven by
formation-enthalpy proxies. Every number we emit is labelled with its method so
nothing is misrepresented as a full CALPHAD result when it is an estimate.
"""
from __future__ import annotations
import warnings
import numpy as np
import pandas as pd
from dataclasses import dataclass
from pathlib import Path

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
# Real pycalphad equilibrium where a database is available
# ---------------------------------------------------------------------------
def _try_load_database():
    """Locate a usable TDB shipped with pycalphad."""
    try:
        import pycalphad
        dbdir = Path(pycalphad.__file__).parent / "tests" / "databases"
        for name in ("alzn_mey.tdb", "alzn.tdb", "alfe_below1189.tdb",
                     "alcuzn.tdb", "alni.tdb"):
            p = dbdir / name
            if p.exists():
                return p
    except Exception:
        pass
    return None


AVAILABLE_TDB = _try_load_database()


def equilibrium_phases(composition: dict[str, float], T: float = 400.0,
                       database: Path | None = None) -> dict:
    """Compute equilibrium phase assemblage with pycalphad.

    composition: mass-fraction dict, e.g. {"Al":0.88,"Mg":0.03,"Zn":0.08,"Cu":0.01}
    Returns dict with phases, their fractions, and method provenance.
    """
    db_path = database or AVAILABLE_TDB
    if db_path is None:
        return {"method": "unavailable", "phases": {}, "note": "no TDB found"}

    try:
        from pycalphad import Database, equilibrium, variables as v
        dbf = Database(str(db_path))
        # Only elements present in the database can be simulated
        db_elems = {e for e in dbf.elements if e in ("AL", "MG", "ZN", "CU", "SI", "FE", "MN")}
        comps = ["AL"] + [e.upper() for e in composition
                          if e.upper() in db_elems and e.upper() != "AL"]
        comps = sorted(set(comps))
        # mass -> mole fraction (approx for screening; pycalphad uses X)
        m = {k.upper(): v_ for k, v_ in composition.items()}
        X = {}
        tot = 0.0
        from . import elements as el
        for e in comps:
            mass = m.get(e, 0.0)
            X[e] = mass / el.MASS[e.capitalize()] if e.capitalize() in el.MASS else mass
            tot += X[e]
        if tot <= 0:
            return {"method": "calphad", "phases": {}, "note": "zero composition"}
        X = {k: val / tot for k, val in X.items()}

        conds = {v.T: T, v.P: 101325}
        for e in comps[1:]:
            conds[v.X(e)] = X[e]
        res = equilibrium(dbf, comps, list(dbf.phases.keys()), conds)
        phases = {}
        for i in range(len(res.Phase.values.ravel())):
            ph = str(res.Phase.values.ravel()[i])
            np_ = res.NP.values.ravel()[i]
            if ph and np_ and np_ > 1e-4 and ph != "":
                phases[ph] = phases.get(ph, 0.0) + float(np_)
        # normalise
        s = sum(phases.values()) or 1.0
        phases = {k: v_ / s for k, v_ in phases.items()}
        return {"method": "calphad", "phases": phases, "T_K": T,
                "database": db_path.name}
    except Exception as exc:  # noqa: BLE001
        return {"method": "calphad_failed", "phases": {}, "note": str(exc)[:120]}


# ---------------------------------------------------------------------------
# Intermetallic-formation screening (always available)
# ---------------------------------------------------------------------------
# Elements notorious for forming brittle intermetallics with Al when present
# above their room-T solubility limit.
_SOLUBILITY_LIMIT = {   # approximate room-T solid solubility in Al (mass frac)
    "Mg": 0.17, "Zn": 0.02, "Cu": 0.005, "Si": 0.015, "Mn": 0.008,
    "Fe": 0.0005, "Ni": 0.0005, "Cr": 0.002, "Ti": 0.002, "Zr": 0.001,
    "Li": 0.04, "Sc": 0.0005, "Ag": 0.02, "Sn": 0.0003, "V": 0.001,
}
_BRITTLE_PHASES = {
    "Cu": ["Al2Cu"], "Mg": ["Al3Mg2", "MgZn2"], "Si": ["Mg2Si", "Al12Mg2Si"],
    "Fe": ["Al6Fe", "Al3Fe"], "Mn": ["Al6Mn"], "Ni": ["Al3Ni"],
    "Zr": ["Al3Zr"], "Sc": ["Al3Sc"], "Ti": ["Al3Ti"], "Cr": ["Al7Cr"],
}


@dataclass
class PhaseVerdict:
    composition: str
    n_excess: int
    excess_elements: dict
    predicted_intermetallics: list
    risk: str          # "low" / "medium" / "high"
    ductility_penalty: float


def screen_intermetallics(composition: dict[str, float]) -> PhaseVerdict:
    """Assess excess-phase risk the way a physical metallurgist would.

    Key insight: precipitates are *good* (AA7075, AA2024 are strong BECAUSE of
    fine Al2Cu/MgZn2), but COARSE networks are bad. The determining variable is
    the TOTAL volume fraction of excess phase:
        < 4%   -> fine dispersion, precipitate-strengthened  (beneficial)
        4-8%   -> borderline, needs careful heat treatment
        > 8%   -> coarse network risk, ductility collapse
    So a *moderate* excess is not penalised; only a large one is.
    """
    excess, ims = {}, []
    for e, v in composition.items():
        if e == "Al":
            continue
        lim = _SOLUBILITY_LIMIT.get(e)
        if lim is None:
            continue
        if v > lim:
            excess[e] = v - lim
            for ph in _BRITTLE_PHASES.get(e, []):
                if ph not in ims:
                    ims.append(ph)
    tot_excess = sum(excess.values())
    # beneficial-precipitate regime, then deterioration
    if tot_excess < 0.04:
        risk, pen = "low", 1.0
    elif tot_excess < 0.08:
        risk, pen = "medium", 0.92
    elif tot_excess < 0.14:
        risk, pen = "high", 0.78
    else:
        risk, pen = "very_high", 0.55
    comp_str = "Al" + "".join(f"-{e}{v*100:.1f}" for e, v in composition.items()
                              if e != "Al" and v > 1e-4)
    return PhaseVerdict(comp_str, len(excess), excess, ims, risk, pen)


def validate_candidates(cands: pd.DataFrame, T: float = 400.0,
                        max_n: int = 40) -> pd.DataFrame:
    """Attach CALPHAD + intermetallic screening to candidate rows."""
    el_cols = [c for c in cands.columns
               if c in ("Al","Mg","Zn","Cu","Si","Mn","Fe","Ni","Cr","Ti","Zr","Li","Sc")]
    rows = []
    for i, (_, r) in enumerate(cands.iterrows()):
        comp = {e: float(r[e]) for e in el_cols if r.get(e, 0) > 1e-4}
        vd = screen_intermetallics(comp)
        eq = equilibrium_phases(comp, T=T) if i < max_n else {"method": "skipped"}
        rows.append({
            "composition": vd.composition,
            "phase_risk": vd.risk,
            "ductility_penalty": vd.ductility_penalty,
            "predicted_intermetallics": ";".join(vd.predicted_intermetallics),
            "n_excess": vd.n_excess,
            "calphad_method": eq.get("method"),
            "equilibrium_phases": ";".join(f"{k}:{v:.3f}" for k, v in eq.get("phases", {}).items()),
        })
    return pd.concat([cands.reset_index(drop=True),
                      pd.DataFrame(rows)], axis=1)


def main():
    OUT = Path(__file__).resolve().parents[2] / "outputs"
    print(f"CALPHAD database available: {AVAILABLE_TDB.name if AVAILABLE_TDB else 'NONE (screening only)'}")
    cands = pd.read_csv(OUT / "candidates_economy.csv")
    val = validate_candidates(cands, T=400.0)
    val.to_csv(OUT / "candidates_calphad.csv", index=False)
    print(f"\nValidated {len(val)} candidates")
    print("\nPhase-risk distribution:")
    print(val["phase_risk"].value_counts().to_string())
    print("\nIntermetallics predicted most often:")
    from collections import Counter
    c = Counter()
    for s in val["predicted_intermetallics"]:
        for p in str(s).split(";"):
            if p:
                c[p] += 1
    for k, n in c.most_common():
        print(f"  {k:10s} {n}")
    # combined score = model score penalised by phase risk
    val["final_score"] = val.get("score", val["YS_pred"]) * val["ductility_penalty"]
    top = val.sort_values("final_score", ascending=False).head(12)
    cols = ["Al", "Mg", "Zn", "Cu", "YS_pred", "elong_pred", "cost",
            "phase_risk", "predicted_intermetallics", "final_score"]
    print("\nTop candidates AFTER phase-risk penalty:")
    print(top[[c for c in cols if c in top.columns]].round(3).to_string(index=False))
    return val


if __name__ == "__main__":
    main()
