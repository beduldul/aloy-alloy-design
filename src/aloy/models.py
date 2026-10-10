"""Surrogate models: composition + processing -> mechanical properties.

Design:
- One model per target (ys_mpa, uts_mpa, elong_pct, hardness, E, density).
- Each target is an ensemble of {HistGradientBoosting, RandomForest, ExtraTrees};
  the spread across members gives a cheap epistemic uncertainty estimate.
- Honest CV: GroupKFold on rounded composition so near-duplicate alloys do not
  leak between train and test.
"""
from __future__ import annotations
import json
import os
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field

from sklearn.ensemble import (
    HistGradientBoostingRegressor, RandomForestRegressor, ExtraTreesRegressor,
)
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

from . import data as D

MODELS = Path(__file__).resolve().parents[2] / "outputs" / "models"

ELEMENT_COLS = [
    "Al","Mg","Zn","Cu","Si","Li","Mn","Fe","Ni","Cr","Ti","Zr","Sc","Ag","Sn",
    "V","B","Be","Bi","Cd","Co","Er","Eu","Ga","Pb","Ca","Na","K","Mo","W","Ta",
    "Nb","Hf","Y","Ce","La","Nd",
]
PHYS_COLS = ["delta_r", "delta_chi", "vec", "omega", "mix_entropy",
             "n_elements", "rho_rule", "cost_kg", "avg_Tm", "avg_bulk"]

TARGETS = {
    "ys_mpa": "Yield strength (MPa)",
    "uts_mpa": "Ultimate tensile strength (MPa)",
    "elong_pct": "Elongation (%)",
    "hv": "Vickers hardness (HV)",
    "E_gpa": "Young modulus (GPa)",
    "rho_exp": "Density (g/cm^3)",
}

# surface finish / process effect encoded numerically
_PROC_ENCODE = {
    "as_cast": 0.0, "other": 0.5, "homogenised": 0.6, "annealed": 0.5,
    "solutionised": 0.7, "aged_under": 0.85, "aged_peak": 1.0, "aged_over": 0.8,
    "cold_worked": 0.95, "extruded": 0.8, "forged": 0.8, "sintered": 0.6,
}


def assemble_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    cols = []
    X = pd.DataFrame(index=df.index)
    for c in ELEMENT_COLS:
        X[c] = df[c].fillna(0.0) if c in df.columns else 0.0
        cols.append(c)
    for c in PHYS_COLS:
        X[c] = df[c].fillna(df[c].median()) if c in df.columns else 0.0
        cols.append(c)
    # process encoding
    if "process_class" in df.columns:
        X["proc"] = df["process_class"].map(_PROC_ENCODE).fillna(0.5)
    elif "processing" in df.columns:
        X["proc"] = 0.7
    else:
        X["proc"] = 0.7
    cols.append("proc")
    if "test_T_C" in df.columns:
        X["test_T"] = pd.to_numeric(df["test_T_C"], errors="coerce").fillna(25.0)
    else:
        X["test_T"] = 25.0
    cols.append("test_T")
    return X, cols


def _members(seed: int):
    return [
        HistGradientBoostingRegressor(max_iter=400, learning_rate=0.06,
                                      max_leaf_nodes=31, l2_regularization=1.0,
                                      random_state=seed),
        RandomForestRegressor(n_estimators=400, min_samples_leaf=2,
                              n_jobs=-1, random_state=seed),
        ExtraTreesRegressor(n_estimators=400, min_samples_leaf=2,
                            n_jobs=-1, random_state=seed),
    ]


@dataclass
class TargetModel:
    target: str
    feat_cols: list[str]
    members: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    def predict(self, X: pd.DataFrame):
        Xa = X[self.feat_cols].to_numpy()
        preds = np.vstack([m.predict(Xa) for m in self.members])
        return preds.mean(axis=0), preds.std(axis=0)


def load_all(al_based_only: bool = True, al_min: float = 0.50) -> pd.DataFrame:
    """Combine the two sources into one training frame.

    Domain discipline: this pipeline designs *aluminium-based* alloys, so by
    default we keep only compositions with Al >= `al_min` mass fraction.
    The Citrine MPEA corpus is dominated by heavy refractory multi-principal
    alloys (median Al fraction 0.08!) whose 1500-3400 MPa strengths belong to a
    completely different material class. Mixing them corrupts the surrogate and
    makes the optimiser hallucinate impossible strengths for Al alloys.
    """
    al = D.load_mendeley_al()
    mp = D.load_mpea()
    for c in ELEMENT_COLS:
        for d in (al, mp):
            if c not in d.columns:
                d[c] = 0.0
    if al_based_only:
        a0 = len(al) + len(mp)
        al = al[al["Al"].fillna(0) >= al_min]
        mp = mp[mp["Al"].fillna(0) >= al_min]
        kept = len(al) + len(mp)
        import os
        if os.environ.get("ALOY_VERBOSE"):
            print(f"  [domain] kept Al >= {al_min:.0%}: {kept}/{a0} records")
    common = sorted(set(al.columns) | set(mp.columns))
    al = al.reindex(columns=common)
    mp = mp.reindex(columns=common)
    return pd.concat([al, mp], ignore_index=True)


def composition_groups(df: pd.DataFrame) -> np.ndarray:
    key = df[ELEMENT_COLS].fillna(0).round(2).astype(str).agg("|".join, axis=1)
    return key.factorize()[0]


def train(target: str, df: pd.DataFrame, n_splits: int = 5, seed: int = 0) -> TargetModel | None:
    y = pd.to_numeric(df[target], errors="coerce")
    mask = y.notna()
    if mask.sum() < 60:
        return None
    sub = df[mask].copy()
    y = y[mask].to_numpy(dtype=float)
    X, cols = assemble_matrix(sub)

    groups = composition_groups(sub)
    # collapse group-internal duplicates for honest evaluation
    gkf = GroupKFold(n_splits=n_splits)
    oof = np.zeros_like(y)
    oof_std = np.zeros_like(y)
    for tr, te in gkf.split(X, y, groups):
        members = _members(seed)
        for m in members:
            m.fit(X.iloc[tr].to_numpy(), y[tr])
        preds = np.vstack([m.predict(X.iloc[te].to_numpy()) for m in members])
        oof[te] = preds.mean(axis=0)
        oof_std[te] = preds.std(axis=0)

    m = TargetModel(target=target, feat_cols=cols)
    m.members = _members(seed)
    for mem in m.members:
        mem.fit(X.to_numpy(), y)
    m.metrics = {
        "r2_cv": float(r2_score(y, oof)),
        "mae_cv": float(mean_absolute_error(y, oof)),
        "n": int(mask.sum()),
        "mean_unc": float(oof_std.mean()),
        "y_std": float(y.std()),
    }
    return m


def load_or_train(df: pd.DataFrame | None = None, seed: int = 0) -> dict[str, "TargetModel"]:
    """Load pickled models; retrain from scratch if the pickle is unreadable
    (e.g. after a scikit-learn upgrade)."""
    df = load_all() if df is None else df
    try:
        import joblib
        out = {}
        missing = []
        for t in TARGETS:
            p = MODELS / f"{t}.joblib"
            if p.exists():
                out[t] = joblib.load(p)
            else:
                missing.append(t)
        if not out:
            raise FileNotFoundError("no model pickles present")
        # train only the targets that are missing but have enough data
        for t in missing:
            if t in df.columns and pd.to_numeric(df[t], errors="coerce").notna().sum() >= 60:
                m = train(t, df, seed=seed)
                if m is not None:
                    out[t] = m
                    joblib.dump(m, MODELS / f"{t}.joblib", compress=3)
        return out
    except Exception as exc:  # noqa: BLE001
        print(f"  [models] cached pickle unusable ({type(exc).__name__}); retraining...")
        return train_all(df, seed=seed)


def train_all(df: pd.DataFrame, seed: int = 0) -> dict[str, TargetModel]:
    MODELS.mkdir(parents=True, exist_ok=True)
    out = {}
    for t in TARGETS:
        if t not in df.columns:
            continue
        m = train(t, df, seed=seed)
        if m is None:
            continue
        out[t] = m
        joblib.dump(m, MODELS / f"{t}.joblib", compress=3)
        print(f"  {t:10s} n={m.metrics['n']:5d}  R2_cv={m.metrics['r2_cv']:+.3f}  "
              f"MAE_cv={m.metrics['mae_cv']:7.2f}  unc={m.metrics['mean_unc']:6.2f}")
    (MODELS / "metrics.json").write_text(json.dumps(
        {t: m.metrics for t, m in out.items()}, indent=2))
    return out
