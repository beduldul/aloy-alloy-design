"""Laboratory protocol generator for recommended alloys.

Produces an actionable, physically-grounded experimental plan for a candidate
Al-Zn-Mg-Cu (7xxx-class) alloy:

  * batch composition with charge masses for a target ingot mass
  * melting/casting schedule (temperatures from phase data + Al-Zn-Mg-Cu practice)
  * T6 heat-treatment schedule (solutionise -> quench -> artificial age)
  * predicted properties with conformal uncertainty
  * characterisation checklist (XRD, SEM/EDS, hardness, tensile)

Heat-treatment temperatures are anchored to the commercial 7075 practice and to
the phase-change temperatures reported for the Al-Zn-Mg-Cu system, NOT invented:
  solutionise  465-475 C   (below the 477 C eutectic incipient-melting point)
  artificial age 120 C / 24 h  (T6 peak),  or 160 C / 8 h (T73 overage)
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from pathlib import Path

from . import elements as el

OUT = Path(__file__).resolve().parents[2] / "outputs"

# ---- metallurgical constants for Al-Zn-Mg-Cu (7xxx) -----------------------
_SOLVUS_C = (465.0, 475.0)      # solution treatment window, below incipient melting
_INCIPIENT_MELT_C = 477.0       # Al-Zn-Mg-Cu eutectic
_QUENCH = "cold water (<40 C), transfer < 10 s"
_AGE_PEAK = (120.0, 24.0)       # T6: 120 C for 24 h
_AGE_OVER = (160.0, 8.0)        # T73: 160 C for 8 h (stress-corrosion resistant)
_MELT_C = 700.0                 # melt superheat
_POUR_C = 690.0

# reference commercial alloys for head-to-head comparison (handbook values)
COMMERCIAL = {
    "AA6061-T6":  {"YS": 276, "UTS": 310, "elong": 12.0, "rho": 2.70, "cost": 2.9},
    "AA7075-T6":  {"YS": 503, "UTS": 572, "elong": 11.0, "rho": 2.81, "cost": 3.5},
    "AA2024-T4":  {"YS": 324, "UTS": 469, "elong": 20.0, "rho": 2.78, "cost": 3.3},
    "AA8090-T6":  {"YS": 400, "UTS": 480, "elong": 6.0,  "rho": 2.55, "cost": 12.0},
}


@dataclass
class Protocol:
    name: str
    composition_wt: dict          # mass fractions
    charge_g: dict                # grams to weigh for the target batch
    batch_g: float
    melting_C: float
    pour_C: float
    solutionise_C: tuple
    solutionise_h: float
    quench: str
    age_T_C: float
    age_h: float
    age_label: str
    predicted_YS: float
    predicted_UTS: float
    predicted_elong: float
    predicted_rho: float
    ys_interval90: tuple
    phase_risk: str
    notes: list


def make_protocol(comp_wt: dict, batch_g: float = 500.0, temper: str = "T6",
                  pred: dict | None = None, phase_risk: str = "medium",
                  ys_halfwidth: float | None = None, name: str = "candidate") -> Protocol:
    # charge masses
    charge = {e: round(v * batch_g, 2) for e, v in comp_wt.items() if v > 1e-5}
    # account for typical element loss (Zn and Mg volatilise) -> add 5% overage
    overage = {"Zn": 1.07, "Mg": 1.10}
    charge = {e: round(charge.get(e, v * batch_g) * overage.get(e, 1.0), 2)
              for e, v in comp_wt.items() if v > 1e-5}

    if temper.upper() == "T73":
        age_T, age_h, label = _AGE_OVER[0], _AGE_OVER[1], "T73 (over-aged)"
    else:
        age_T, age_h, label = _AGE_PEAK[0], _AGE_PEAK[1], "T6 (peak-aged)"

    p = pred or {}
    hw = ys_halfwidth if ys_halfwidth is not None else 0.18 * p.get("YS", 0)
    ys = p.get("YS", float("nan"))

    notes = [
        "Zn & Mg overcharged (Zn +7%, Mg +10%) to offset volatilisation losses.",
        f"Do NOT exceed {_SOLVUS_C[1]:.0f} C in solutionising: incipient melting "
        f"of the Al-Zn-Mg-Cu eutectic occurs near {_INCIPIENT_MELT_C:.0f} C -> hot cracking.",
        "Grain refinement: add Al-5Ti-1B master alloy (0.1 wt%) before pouring.",
        "Degas with Ar or C2Cl6 to limit porosity (H2 solubility falls sharply on solidification).",
    ]
    if comp_wt.get("Cu", 0) > 0.01:
        notes.append("Cu-rich: expect Al2Cu/Al7Cu2Fe dispersoids; slow cooling may form "
                     "coarse constituent phases -> minimise with rapid solidification.")
    if phase_risk in ("high", "very_high"):
        notes.append(f"Phase screening flagged {phase_risk} excess-phase risk: "
                     "consider shortening the homogenisation or reducing Cu content.")

    return Protocol(
        name=name, composition_wt=comp_wt, charge_g=charge, batch_g=batch_g,
        melting_C=_MELT_C, pour_C=_POUR_C, solutionise_C=_SOLVUS_C,
        solutionise_h=2.0, quench=_QUENCH, age_T_C=age_T, age_h=age_h, age_label=label,
        predicted_YS=ys, predicted_UTS=p.get("UTS", float("nan")),
        predicted_elong=p.get("elong", float("nan")),
        predicted_rho=p.get("rho", float("nan")),
        ys_interval90=(ys - hw, ys + hw), phase_risk=phase_risk, notes=notes)


def protocol_to_text(p: Protocol) -> str:
    L = []
    L.append("=" * 74)
    L.append(f"LABORATORY PROTOCOL — {p.name}")
    L.append("=" * 74)
    L.append("\n1. TARGET COMPOSITION (wt%)")
    L.append("   " + "  ".join(f"{e}:{v*100:.2f}" for e, v in p.composition_wt.items()
                               if v > 1e-5))
    L.append(f"\n2. CHARGE for a {p.batch_g:.0f} g ingot (with overage)")
    for e, g in sorted(p.charge_g.items(), key=lambda kv: -kv[1]):
        L.append(f"   {e:3s} {g:8.2f} g")
    L.append(f"   (balance = Al, add last to minimise oxidation)")
    L.append("\n3. MELTING & CASTING")
    L.append(f"   Melt at {p.melting_C:.0f} C; pour at {p.pour_C:.0f} C into a steel mould.")
    L.append("   Add Al-5Ti-1B grain refiner at 0.1 wt% just before pouring.")
    L.append("\n4. HOMOGENISATION (optional but recommended)")
    L.append("   465 C / 12 h, then air cool — removes microsegregation.")
    L.append("\n5. SOLUTION TREATMENT")
    L.append(f"   {p.solutionise_C[0]:.0f}-{p.solutionise_C[1]:.0f} C for {p.solutionise_h:.0f} h")
    L.append(f"   Quench: {p.quench}")
    L.append(f"   (stay BELOW {_INCIPIENT_MELT_C:.0f} C to avoid incipient melting)")
    L.append("\n6. ARTIFICIAL AGING")
    L.append(f"   {p.age_label}: {p.age_T_C:.0f} C for {p.age_h:.0f} h, then air cool")
    L.append("\n7. PREDICTED PROPERTIES (model + conformal 90% interval)")
    L.append(f"   Yield strength : {p.predicted_YS:.0f} MPa  "
             f"[{p.ys_interval90[0]:.0f}, {p.ys_interval90[1]:.0f}]")
    L.append(f"   UTS (est.)     : {p.predicted_UTS:.0f} MPa")
    L.append(f"   Elongation     : {p.predicted_elong:.1f} %")
    L.append(f"   Density        : {p.predicted_rho:.3f} g/cm3")
    L.append("\n8. CHARACTERISATION CHECKLIST")
    L.append("   [ ] Optical/SEM + EDS  — grain size, second-phase morphology")
    L.append("   [ ] XRD                — confirm fcc Al matrix (+ MgZn2 / Al2Cu peaks)")
    L.append("   [ ] Vickers HV (10 indent) — before and after ageing")
    L.append("   [ ] Tensile test, 3 specimens, ASTM E8 — YS, UTS, elongation")
    L.append("   [ ] Density (Archimedes) — compare with prediction")
    L.append("\n9. NOTES")
    for n in p.notes:
        L.append(f"   - {n}")
    L.append("")
    L.append("   >>> Feed the measured YS back into outputs/experiment_log.json")
    L.append("       and re-run `python3 -m aloy.active` to update the model. <<<")
    L.append("=" * 74)
    return "\n".join(L)


def commercial_comparison(cands: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in cands.iterrows():
        comp = "Al" + "".join(f"-{e}{r[e]*100:.1f}" for e in ["Mg", "Zn", "Cu", "Si"]
                              if e in r and r[e] > 0.003)
        rows.append({"alloy": comp, "YS": r["YS_pred"], "elong": r["elong_pred"],
                     "rho": r["rho_pred"], "cost": r["cost"],
                     "specific": r["YS_pred"] / r["rho_pred"]})
    for name, v in COMMERCIAL.items():
        rows.append({"alloy": name + " (handbook)", "YS": v["YS"], "elong": v["elong"],
                     "rho": v["rho"], "cost": v["cost"], "specific": v["YS"] / v["rho"]})
    df = pd.DataFrame(rows)
    df["vs_7075_YS"] = (df["YS"] / COMMERCIAL["AA7075-T6"]["YS"]).round(2)
    df["vs_7075_cost"] = (df["cost"] / COMMERCIAL["AA7075-T6"]["cost"]).round(2)
    return df


def main(n_protocols: int = 3, temper: str = "T6"):
    cands = pd.read_csv(OUT / "candidates_final.csv")
    top = cands.sort_values("strength_per_dollar", ascending=False).head(n_protocols)
    rep = json.loads((OUT / "credibility_report.json").read_text())
    hw = rep.get("q_halfwidth", 100.0)

    all_text, protos = [], []
    for i, (_, r) in enumerate(top.iterrows(), 1):
        comp = {e: float(r[e]) for e in ["Al", "Mg", "Zn", "Cu", "Si", "Mn", "Fe", "Ti", "Zr"]
                if e in r and pd.notna(r[e]) and r[e] > 1e-5}
        p = make_protocol(
            comp, batch_g=500.0, temper=temper,
            pred={"YS": r["YS_pred"], "UTS": r.get("UTS_pred", float("nan")),
                  "elong": r["elong_pred"], "rho": r["rho_pred"]},
            phase_risk=r.get("phase_risk", "medium"),
            ys_halfwidth=hw, name=f"Candidate {i} ({temper})")
        protos.append(p)
        all_text.append(protocol_to_text(p))

    (OUT / "lab_protocols.txt").write_text("\n\n".join(all_text))
    (OUT / "lab_protocols.json").write_text(json.dumps(
        [asdict(p) for p in protos], indent=2, default=str))

    comp_df = commercial_comparison(top)
    comp_df.to_csv(OUT / "commercial_comparison.csv", index=False)

    print("\n".join(all_text[:2]))
    print("\n=== VS COMMERCIAL ALLOYS ===")
    print(comp_df.round(2).to_string(index=False))
    print(f"\n-> {OUT/'lab_protocols.txt'}")
    print(f"-> {OUT/'commercial_comparison.csv'}")
    return protos


if __name__ == "__main__":
    main()
