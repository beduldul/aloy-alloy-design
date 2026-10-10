"""Laboratory protocol generator for MAGNESIUM alloys.

Magnesium is far more hazardous to melt than aluminium:
  * Mg powder/fines are pyrophoric; the melt oxidises rapidly and can BURN
    (white flame, ~3000 C) if unprotected.
  * Flux or SF6/CO2 cover gas is mandatory -- never melt Mg in open air.
  * Molten Mg reacts violently with water, rust, and some oxides.
This module produces a safety-first protocol plus the T6/T4 schedules used for
Mg-RE and Mg-Al-Zn alloys.
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from pathlib import Path

from . import elements as el

OUT = Path(__file__).resolve().parents[2] / "outputs"

# Mg alloy melting/casting practice
_MELT_C = 720.0
_POUR_C = 700.0
_COVER_GAS = "SF6/CO2 (0.5-1% SF6) or protective flux (e.g. RJ-1) -- MANDATORY"
_FLUX = "RJ-1 or KCl-MgCl2 flux for refining; skim before pouring"

# heat-treatment schedules for common Mg systems
_HT = {
    "mg_al_zn":   {"solutionise": (415.0, 18.0), "age": (175.0, 16.0), "label": "T6 (Mg-Al-Zn)"},
    "mg_re":      {"solutionise": (525.0, 8.0),  "age": (200.0, 16.0), "label": "T6 (Mg-RE)"},
    "mg_li":      {"solutionise": (340.0, 2.0),  "age": (None, None),  "label": "T4/anneal (Mg-Li)"},
    "default":    {"solutionise": (415.0, 12.0), "age": (175.0, 12.0), "label": "T6"},
}

# reference commercial Mg alloys (handbook)
MG_COMMERCIAL = {
    "AZ91D-T6": {"YS": 150, "UTS": 230, "elong": 3.0, "rho": 1.81, "cost": 2.5},
    "AM60-T4":  {"YS": 130, "UTS": 220, "elong": 8.0, "rho": 1.80, "cost": 2.5},
    "ZK60-T5":  {"YS": 250, "UTS": 305, "elong": 11.0, "rho": 1.83, "cost": 3.5},
    "WE43-T6":  {"YS": 200, "UTS": 280, "elong": 7.0, "rho": 1.84, "cost": 12.0},
    "LA141-T4": {"YS": 130, "UTS": 200, "elong": 12.0, "rho": 1.35, "cost": 15.0},
}


@dataclass
class MgProtocol:
    name: str
    composition_wt: dict
    charge_g: dict
    batch_g: float
    melting_C: float
    pour_C: float
    cover_gas: str
    flux: str
    solutionise_C: tuple
    solutionise_h: float
    age_T_C: float
    age_h: float
    heat_treatment: str
    predicted_YS: float
    predicted_elong: float
    predicted_rho: float
    specific: float
    safety: list
    notes: list


def _classify(comp: dict) -> str:
    if comp.get("Li", 0) > 0.03:
        return "mg_li"
    if sum(comp.get(e, 0) for e in ("Nd", "Ce", "La", "Gd", "Y", "Dy")) > 0.02:
        return "mg_re"
    if comp.get("Al", 0) > 0.03:
        return "mg_al_zn"
    return "default"


def make_protocol(comp_wt: dict, batch_g: float = 300.0, pred: dict | None = None,
                  name: str = "Mg candidate") -> MgProtocol:
    family = _classify(comp_wt)
    ht = _HT[family]
    # Mg oxidises and volatilises: overcharge reactive/low-boiling elements
    overage = {"Zn": 1.10, "Ca": 1.05, "Li": 1.15, "Mg": 1.03, "Y": 1.05, "Nd": 1.05}
    charge = {e: round(v * batch_g * overage.get(e, 1.0), 2)
              for e, v in comp_wt.items() if v > 1e-5}

    safety = [
        "NEVER melt Mg without SF6/CO2 cover gas or flux -- molten Mg BURNS in air.",
        "Keep dry sand / class-D extinguisher at hand; NEVER use water on an Mg fire.",
        "Preheat all tools, moulds and charge to >150 C to avoid moisture (explosion risk).",
        "Work in a fume hood / well-ventilated area -- MgO fume and SF6 decomposition products.",
        "No rust or iron oxide in contact with the melt (thermite-type reaction).",
    ]
    notes = [
        f"Family detected: {family} -> heat treatment {ht['label']}.",
        "Grain refinement / texture control matters more for Mg than for Al "
        "(HCP has few slip systems): consider Zr (Mg-Zn-Zr) or Ca (weak texture).",
        "Mg-RE alloys form Mg-RE intermetallics at grain boundaries -> creep resistance.",
    ]
    if family == "mg_li":
        notes.append("Mg-Li is the lightest structural metal (rho ~1.35-1.6); "
                     "Li is volatile -- expect loss, and handle Li dry (reacts with moisture).")
    if comp_wt.get("Y", 0) > 0.02:
        notes.append("Yttrium is expensive (~30 USD/kg): check the cost budget.")

    p = pred or {}
    rho = p.get("rho", float("nan"))
    ys = p.get("YS", float("nan"))
    return MgProtocol(
        name=name, composition_wt=comp_wt, charge_g=charge, batch_g=batch_g,
        melting_C=_MELT_C, pour_C=_POUR_C, cover_gas=_COVER_GAS, flux=_FLUX,
        solutionise_C=ht["solutionise"], solutionise_h=ht["solutionise"][1],
        age_T_C=ht["age"][0] if ht["age"][0] else float("nan"),
        age_h=ht["age"][1] if ht["age"][1] else float("nan"),
        heat_treatment=ht["label"],
        predicted_YS=ys, predicted_elong=p.get("elong", float("nan")),
        predicted_rho=rho, specific=ys / rho if rho else float("nan"),
        safety=safety, notes=notes)


def protocol_to_text(p: MgProtocol) -> str:
    L = ["=" * 74, f"MAGNESIUM LABORATORY PROTOCOL — {p.name}", "=" * 74]
    L.append("\n1. TARGET COMPOSITION (wt%)")
    L.append("   " + "  ".join(f"{e}:{v*100:.2f}" for e, v in p.composition_wt.items()
                               if v > 1e-5))
    L.append(f"\n2. CHARGE for a {p.batch_g:.0f} g ingot")
    for e, g in sorted(p.charge_g.items(), key=lambda kv: -kv[1]):
        L.append(f"   {e:3s} {g:8.2f} g")
    L.append("\n3. MELTING & CASTING  (SAFETY CRITICAL)")
    L.append(f"   Melt at {p.melting_C:.0f} C; pour at {p.pour_C:.0f} C.")
    L.append(f"   COVER GAS: {p.cover_gas}")
    L.append(f"   FLUX: {p.flux}")
    L.append("   Preheat mould and tools to >150 C.")
    L.append(f"\n4. SOLUTION TREATMENT\n   {p.solutionise_C[0]:.0f} C for {p.solutionise_h:.0f} h")
    L.append("   Quench in warm water or air (Mg quench-sensitive; avoid cold-water cracking).")
    if p.age_T_C and not np.isnan(p.age_T_C):
        L.append(f"\n5. ARTIFICIAL AGING\n   {p.age_T_C:.0f} C for {p.age_h:.0f} h  [{p.heat_treatment}]")
    else:
        L.append(f"\n5. AGING\n   none ({p.heat_treatment})")
    L.append("\n6. PREDICTED PROPERTIES (model)")
    L.append(f"   Yield strength : {p.predicted_YS:.0f} MPa")
    L.append(f"   Ductility      : {p.predicted_elong:.1f} %")
    L.append(f"   Density        : {p.predicted_rho:.3f} g/cm3")
    L.append(f"   Specific str.  : {p.specific:.0f} MPa/(g/cm3)")
    L.append("\n7. SAFETY (READ BEFORE STARTING)")
    for s in p.safety:
        L.append(f"   !! {s}")
    L.append("\n8. NOTES")
    for n in p.notes:
        L.append(f"   - {n}")
    L.append("\n   >>> Record measured YS in outputs/experiment_log_mg.json <<<")
    L.append("=" * 74)
    return "\n".join(L)


def compare(cands: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in cands.iterrows():
        comp = "Mg" + "".join(f"-{e}{r[e]*100:.1f}" for e in
                              ["Al", "Zn", "Ca", "Li", "Y", "Nd", "Gd"]
                              if e in r and r[e] > 0.004)
        rows.append({"alloy": comp, "YS": r["YS_pred"], "elong": r["elong_pred"],
                     "rho": r["rho_pred"], "cost": r["cost"],
                     "specific": r["YS_pred"] / r["rho_pred"]})
    for name, v in MG_COMMERCIAL.items():
        rows.append({"alloy": name + " (handbook)", "YS": v["YS"], "elong": v["elong"],
                     "rho": v["rho"], "cost": v["cost"], "specific": v["YS"] / v["rho"]})
    df = pd.DataFrame(rows)
    df["vs_AZ91_YS"] = (df["YS"] / MG_COMMERCIAL["AZ91D-T6"]["YS"]).round(2)
    return df


def main(n=3):
    from . import mg_design as MD
    cands = pd.read_csv(OUT / "mg_pareto.csv")
    # pick top candidates that are NOT pinned at the ductility clip, per family
    top = MD.rank(cands, top=40)
    picked, seen_f = [], set()
    for _, r in top.iterrows():
        comp = {e: float(r[e]) for e in el.MG_ELEMENTS
                if e in r and pd.notna(r[e]) and r[e] > 1e-5}
        fam = _classify(comp)
        if fam in seen_f:
            continue
        seen_f.add(fam)
        picked.append((r, comp))
        if len(picked) >= n:
            break

    texts, protos = [], []
    for i, (r, comp) in enumerate(picked, 1):
        p = make_protocol(comp, batch_g=300.0,
                          pred={"YS": r["YS_pred"], "elong": r["elong_pred"],
                                "rho": r["rho_pred"]},
                          name=f"Mg Candidate {i}")
        protos.append(p)
        texts.append(protocol_to_text(p))

    (OUT / "mg_lab_protocols.txt").write_text("\n\n".join(texts))
    (OUT / "mg_lab_protocols.json").write_text(
        json.dumps([asdict(p) for p in protos], indent=2, default=str))
    cmp_df = compare(top.head(5))
    cmp_df.to_csv(OUT / "mg_commercial_comparison.csv", index=False)

    print("\n\n".join(texts[:2]))
    print("\n=== Mg CANDIDATES VS COMMERCIAL ===")
    print(cmp_df.round(2).to_string(index=False))
    return protos


if __name__ == "__main__":
    main()
