"""Magnesium-alloy data pipeline and design (Mg is ~35% lighter than Al).

Source: Mendeley "Magnesium Alloy Mechanical Property Database"
(Ghorbani & Birbilis, 2025, DOI 10.17632/2fjhmdg5nt.2) -- 916 cast/wrought Mg
alloys with full composition (sums to 100 wt%), YS, UTS and ductility.

Magnesium is the structural-metal frontier: density 1.74 g/cm3 vs Al 2.70.
The trade-off is poor room-temperature ductility (HCP slip limitation) and
corrosion; RE (rare-earth) additions are the classic remedy, which is exactly
why the database is rich in Nd/Ce/La/Gd/Y.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path

from . import elements as el

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"


def load_mg() -> pd.DataFrame:
    df = pd.read_excel(RAW / "mendeley_mg_alloys.xlsx")
    df = df.rename(columns={
        "YS(MPa)": "ys_mpa", "UTS(MPa)": "uts_mpa", "Ductility": "elong_pct",
        "Process-Heat treatment": "processing", "Name": "name",
    })
    el_cols = [c for c in el.MG_ELEMENTS if c in df.columns]

    # compositions are in wt% summing to 100 -> convert to mass fractions
    s = df[el_cols].sum(axis=1)
    df[el_cols] = df[el_cols].div(s, axis=0).clip(lower=0)

    # drop physically impossible / duplicated records
    df = df[(df["Mg"] > 0.5)].copy()
    df = df[df["ys_mpa"].notna() | df["uts_mpa"].notna()].copy()

    feats = _mg_features(df, el_cols)
    df = pd.concat([df.reset_index(drop=True), feats.reset_index(drop=True)], axis=1)
    df["source"] = "mendeley_mg"
    return df


def _mg_features(df: pd.DataFrame, el_cols: list[str]) -> pd.DataFrame:
    X = df[el_cols].fillna(0.0).to_numpy()
    s = X.sum(axis=1, keepdims=True); s[s == 0] = 1.0
    X = X / s

    r = np.array([el.RADIUS_PM[e] for e in el_cols])
    chi = np.array([el.ELECTRONEG[e] for e in el_cols])
    rho = np.array([el.DENSITY[e] for e in el_cols])
    Tm = np.array([el.T_MELT[e] for e in el_cols])
    mass = np.array([el.MASS[e] for e in el_cols])
    cost = np.array([el.COST[e] for e in el_cols])

    rbar = X @ r
    delta_r = np.sqrt((X * (1 - r / np.where(rbar[:, None] == 0, 1, rbar[:, None])) ** 2).sum(1))
    chibar = X @ chi
    delta_chi = np.sqrt((X * (chi - chibar[:, None]) ** 2).sum(1))
    vec = X @ np.array([_vec(e) for e in el_cols])

    # c/a axial ratio proxy: RE elements raise it toward 1.633 (better ductility)
    re_frac = X[:, [i for i, e in enumerate(el_cols)
                    if e in ("Nd", "Ce", "La", "Gd", "Y", "Dy", "Pr", "Tb", "Ho", "Er")]].sum(1)
    inv_rho = (X / rho[None, :]).sum(1)
    rho_rule = 1.0 / np.where(inv_rho == 0, np.nan, inv_rho)

    return pd.DataFrame({
        "delta_r": delta_r, "delta_chi": delta_chi, "vec": vec,
        "mix_entropy": -8.314 * (np.where(X > 0, X * np.log(np.where(X > 0, X, 1)), 0)).sum(1),
        "n_elements": (X > 1e-4).sum(1).astype(float),
        "rho_rule": rho_rule, "cost_kg": X @ cost,
        "avg_Tm": X @ Tm, "re_fraction": re_frac,
        "w_Mg": X[:, el_cols.index("Mg")],
    })


def _vec(e: str) -> float:
    from .data import _VEC_TABLE
    return float(_VEC_TABLE.get(e, np.nan))


MG_TARGETS = {"ys_mpa": "Yield strength (MPa)", "uts_mpa": "UTS (MPa)",
              "elong_pct": "Ductility (%)"}


def summary():
    df = load_mg()
    print(f"Mg alloys: {df.shape[0]} records, {len(el.MG_ELEMENTS)} element columns")
    print(f"  density range: {df['rho_rule'].min():.2f}-{df['rho_rule'].max():.2f} g/cm3")
    print(f"  YS: {df['ys_mpa'].min():.0f}-{df['ys_mpa'].max():.0f} MPa  "
          f"(mean {df['ys_mpa'].mean():.0f})")
    print(f"  RE fraction: mean {df['re_fraction'].mean()*100:.1f}%, "
          f"max {df['re_fraction'].max()*100:.0f}%")
    return df


if __name__ == "__main__":
    summary()
