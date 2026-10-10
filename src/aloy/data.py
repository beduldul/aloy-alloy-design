"""Data loading, cleaning, harmonisation, and physical feature engineering.

Public sources (all real experimental compilations):
  1. Mendeley "Aluminium alloy dataset for supervised learning" (Bhat, Barnard,
     Birbilis, 2023, DOI 10.17632/b6br4yk6r3.1) -- composition, processing route,
     YS, UTS, elongation for ~1150 Al alloys.
  2. Citrine MPEA_dataset (Borg et al., 2020, DOI 10.6084/m9.figshare.12642953)
     -- multi-principal-element alloys: YS, UTS, elongation, density, E, HV.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path

from . import elements as el

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
PROC = Path(__file__).resolve().parents[2] / "data" / "processed"


# --------------------------------------------------------------------------
# Mendeley Al alloys
# --------------------------------------------------------------------------
_PROCESS_MAP = {
    # normalise free-text processing into a small categorical set + numeric temps
    "Solutionised  + Artificially peak aged": ("aged_peak", 1),
    "Solutionised + Artificially peak aged": ("aged_peak", 1),
    "Solutionised + Artificially over aged": ("aged_over", 1),
    "Solutionised + Artificially under aged": ("aged_under", 1),
    "Solutionised + Artificially under aged ": ("aged_under", 1),
    "Solutionised": ("solutionised", 0),
    "As Cast": ("as_cast", 0),
    "As cast": ("as_cast", 0),
    "Homogenised": ("homogenised", 0),
    "Homogenised ": ("homogenised", 0),
    "Annealed": ("annealed", 0),
    "Cold rolled": ("cold_worked", 0),
    "Rolled": ("cold_worked", 0),
    "Extruded": ("extruded", 0),
    "Forged": ("forged", 0),
    "Sintered": ("sintered", 0),
    "Sintered + T6": ("aged_peak", 1),
    "Cast + T6": ("aged_peak", 1),
    "Cast + T7": ("aged_over", 1),
    "As-cast + T6": ("aged_peak", 1),
}


def load_mendeley_al() -> pd.DataFrame:
    df = pd.read_csv(RAW / "mendeley_al_alloys.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    df = df[df["class"].astype(str) != "outlier"].copy()

    # keep only rows with a usable composition (Al present, sums ~1)
    el_cols = [c for c in el.AL_ELEMENTS if c in df.columns]
    s = df[el_cols].sum(axis=1)
    df = df[(s > 0.95) & (s < 1.05)].copy()

    df = df.rename(columns={
        "Yield Strength (MPa)": "ys_mpa",
        "Tensile Strength (MPa)": "uts_mpa",
        "Elongation (%)": "elong_pct",
        "Processing": "processing",
    })

    proc = df["processing"].astype(str).str.strip()
    df["process_class"] = proc.map(lambda p: _PROCESS_MAP.get(p, ("other", 0))[0])
    df["is_aged"] = proc.map(lambda p: _PROCESS_MAP.get(p, ("other", 0))[1]).astype(int)

    # physical features
    feats = build_physical_features(df, el_cols, base="Al")
    df = pd.concat([df.reset_index(drop=True), feats.reset_index(drop=True)], axis=1)
    df["source"] = "mendeley_al"

    keep = el_cols + [
        "ys_mpa", "uts_mpa", "elong_pct", "process_class", "is_aged", "source",
        "w_Al", "delta_r", "delta_chi", "vec", "omega", "mix_entropy",
        "n_elements", "rho_rule", "cost_kg", "avg_Tm", "avg_bulk",
    ]
    return df[[c for c in keep if c in df.columns]]


# --------------------------------------------------------------------------
# Citrine MPEA
# --------------------------------------------------------------------------
def load_mpea() -> pd.DataFrame:
    df = pd.read_csv(RAW / "mpea_dataset.csv", low_memory=False)
    ren = {
        "PROPERTY: YS (MPa)": "ys_mpa",
        "PROPERTY: UTS (MPa)": "uts_mpa",
        "PROPERTY: Elongation (%)": "elong_pct",
        "PROPERTY: Exp. Density (g/cm$^3$)": "rho_exp",
        "PROPERTY: Calculated Density (g/cm$^3$)": "rho_calc",
        "PROPERTY: HV": "hv",
        "PROPERTY: Exp. Young modulus (GPa)": "E_gpa",
        "PROPERTY: Test temperature ($^\\circ$C)": "test_T_C",
        "PROPERTY: Processing method": "processing",
        "FORMULA": "formula",
    }
    df = df.rename(columns={k: v for k, v in ren.items() if k in df.columns})

    # parse FORMULA like "AlCoCrFeNi" or "Al0.5CoCrFeNi" into wt/at fractions
    comp = parse_formula_column(df["formula"])
    el_cols = [c for c in comp.columns]
    df = pd.concat([df.reset_index(drop=True), comp.reset_index(drop=True)], axis=1)

    feats = build_physical_features(df, el_cols, base=None)
    df = pd.concat([df.reset_index(drop=True), feats.reset_index(drop=True)], axis=1)
    df["source"] = "mpea"

    keep = el_cols + [
        "ys_mpa", "uts_mpa", "elong_pct", "rho_exp", "rho_calc", "hv", "E_gpa",
        "test_T_C", "processing", "source",
        "delta_r", "delta_chi", "vec", "omega", "mix_entropy", "n_elements",
        "rho_rule", "cost_kg", "avg_Tm", "avg_bulk",
    ]
    return df[[c for c in keep if c in df.columns]]


_F = __import__("re").compile(r"([A-Z][a-z]?)([0-9]*\.?[0-9]*)")


def parse_formula_column(series: pd.Series) -> pd.DataFrame:
    """Parse alloy formula strings into atomic-fraction matrix."""
    rows, all_els = [], set()
    for f in series.fillna("").astype(str):
        d = {}
        for sym, num in _F.findall(f):
            if not sym:
                continue
            try:
                v = float(num) if num else 1.0
            except ValueError:
                v = 1.0
            d[sym] = d.get(sym, 0.0) + v
        rows.append(d)
        all_els.update(d)
    # keep only elements we have physical tables for (drop C/H/O/N/B* artefacts)
    el_cols = sorted(e for e in all_els if e in el.RADIUS_PM)
    mat = np.zeros((len(rows), len(el_cols)))
    for i, d in enumerate(rows):
        tot = sum(d.values())
        if tot <= 0:
            continue
        for j, e in enumerate(el_cols):
            mat[i, j] = d.get(e, 0.0) / tot
    return pd.DataFrame(mat, columns=el_cols)


# --------------------------------------------------------------------------
# Physical feature engineering (Hume-Rothery + rule-of-mixtures)
# --------------------------------------------------------------------------
def build_physical_features(df: pd.DataFrame, el_cols: list[str], base: str | None) -> pd.DataFrame:
    # restrict to compositions whose sum is ~1
    X = df[el_cols].fillna(0.0).to_numpy()
    s = X.sum(axis=1, keepdims=True)
    s[s == 0] = 1.0
    X = X / s

    r = np.array([el.RADIUS_PM[e] for e in el_cols])
    chi = np.array([el.ELECTRONEG[e] for e in el_cols])
    rho = np.array([el.DENSITY[e] for e in el_cols])
    Tm = np.array([el.T_MELT[e] for e in el_cols])
    Bm = np.array([el.BULK[e] for e in el_cols])
    cost = np.array([el.COST[e] for e in el_cols])
    mass = np.array([el.MASS[e] for e in el_cols])

    rbar = X @ r
    delta_r = np.sqrt(((X * (1 - r / np.where(rbar[:, None] == 0, 1, rbar[:, None])) ** 2)).sum(axis=1))
    chibar = X @ chi
    delta_chi = np.sqrt((X * (chi - chibar[:, None]) ** 2).sum(axis=1))

    # Valence Electron Concentration
    vec = X @ np.array([_vec(e) for e in el_cols])
    # thermodynamic Omega parameter: Tm*dSm / |dH_mix|
    dH = _mixing_enthalpy(X, el_cols)
    dS = -8.314 * (np.where(X > 0, X * np.log(np.where(X > 0, X, 1)), 0)).sum(axis=1)
    Tmb = X @ Tm
    omega = (Tmb * dS) / np.where(np.abs(dH) < 1e-6, 1e-6, np.abs(dH))

    # rule-of-mixtures density (mass-weighted)
    inv_rho = (X / rho[None, :]).sum(axis=1)
    rho_rule = 1.0 / np.where(inv_rho == 0, np.nan, inv_rho)

    return pd.DataFrame({
        "delta_r": delta_r,
        "delta_chi": delta_chi,
        "vec": vec,
        "omega": omega,
        "mix_entropy": dS,
        "n_elements": (X > 1e-4).sum(axis=1).astype(float),
        "rho_rule": rho_rule,
        "cost_kg": X @ cost,
        "avg_Tm": Tmb,
        "avg_bulk": X @ Bm,
        "w_Al": X[:, el_cols.index(base)] if base and base in el_cols else np.nan,
    })


# approximate VEC by group number
_VEC_TABLE = {
    "Al": 3, "Mg": 2, "Zn": 2, "Cu": 1, "Si": 4, "Li": 1, "Mn": 7, "Fe": 8,
    "Ni": 10, "Cr": 6, "Ti": 4, "Zr": 4, "Sc": 3, "Ag": 1, "Sn": 4, "V": 5,
    "B": 3, "Be": 2, "Bi": 5, "Cd": 2, "Co": 9, "Er": 3, "Eu": 2, "Ga": 3,
    "Pb": 4, "Ca": 2, "Na": 1, "K": 1, "Mo": 6, "W": 6, "Ta": 5, "Nb": 5,
    "Hf": 4, "Y": 3, "Ce": 4, "La": 3, "Nd": 3, "Pr": 3, "Gd": 3, "Tb": 3,
    "Dy": 3, "Ho": 3, "Yb": 2, "Sr": 2, "Sb": 5, "Th": 4,
}


def _vec(e: str) -> float:
    return float(_VEC_TABLE.get(e, np.nan))


# Miedema-style pair mixing enthalpies (kJ/mol), coarse but physically motivated
def _mixing_enthalpy(X: np.ndarray, el_cols: list[str]) -> np.ndarray:
    n = len(el_cols)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            H[i, j] = _pair_h(el_cols[i], el_cols[j])
    out = np.zeros(X.shape[0])
    for i in range(n):
        for j in range(i + 1, n):
            out += X[:, i] * X[:, j] * H[i, j]
    return out


_PAIR_H: dict[tuple[str, str], float] = {}


def _pair_h(a: str, b: str) -> float:
    """Coarse pair enthalpy proxy from electronegativity + size mismatch.

    Real Miedema enthalpies are large tables; this proxy captures the sign and
    rough magnitude: large chi difference -> strongly negative (compound forming);
    large size mismatch -> positive strain contribution.
    """
    key = tuple(sorted((a, b)))
    if key in _PAIR_H:
        return _PAIR_H[key]
    if a not in el.ELEMENTS or b not in el.ELEMENTS:
        _PAIR_H[key] = 0.0
        return 0.0
    dchi = abs(el.ELECTRONEG[a] - el.ELECTRONEG[b])
    dr = abs(el.RADIUS_PM[a] - el.RADIUS_PM[b]) / (el.RADIUS_PM[a] + el.RADIUS_PM[b])
    val = -80.0 * dchi + 60.0 * dr
    _PAIR_H[key] = val
    return val
