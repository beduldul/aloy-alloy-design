"""Surrogate models and multi-objective design for MAGNESIUM alloys.

Reuses the ensemble machinery from `models.py` but on the Mg element space and
the Mg feature set (which adds an RE-fraction descriptor, since rare-earth
addition is the dominant lever on Mg strength/ductility).

Objective set is Mg-appropriate:
    maximise yield strength
    maximise ductility      (Mg's weak point -> explicitly reward it)
    maximise specific strength
    minimise density        (the whole point of Mg)
    minimise cost
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field

from sklearn.ensemble import (HistGradientBoostingRegressor,
                              RandomForestRegressor, ExtraTreesRegressor)
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

from . import mg as MG
from . import elements as el

OUT = Path(__file__).resolve().parents[2] / "outputs"
MG_MODELS = OUT / "models_mg"

ELEMENT_COLS = list(el.MG_ELEMENTS)
PHYS_COLS = ["delta_r", "delta_chi", "vec", "mix_entropy", "n_elements",
             "rho_rule", "cost_kg", "avg_Tm", "re_fraction"]

TARGETS = {"ys_mpa": "Yield strength (MPa)", "uts_mpa": "UTS (MPa)",
           "elong_pct": "Ductility (%)"}


def _members(seed: int):
    return [
        HistGradientBoostingRegressor(max_iter=400, learning_rate=0.06,
                                      max_leaf_nodes=31, l2_regularization=1.0,
                                      random_state=seed),
        RandomForestRegressor(n_estimators=400, min_samples_leaf=2, n_jobs=-1,
                              random_state=seed),
        ExtraTreesRegressor(n_estimators=400, min_samples_leaf=2, n_jobs=-1,
                            random_state=seed),
    ]


@dataclass
class MgModel:
    target: str
    feat_cols: list
    members: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    def predict(self, X: pd.DataFrame):
        Xa = X[self.feat_cols].to_numpy()
        preds = np.vstack([m.predict(Xa) for m in self.members])
        return preds.mean(0), preds.std(0)


def assemble(df: pd.DataFrame):
    X = pd.DataFrame(index=df.index)
    for c in ELEMENT_COLS:
        X[c] = df[c].fillna(0.0) if c in df.columns else 0.0
    for c in PHYS_COLS:
        X[c] = df[c].fillna(df[c].median()) if c in df.columns else 0.0
    X["proc"] = 0.7
    return X, list(X.columns)


def _groups(df):
    key = df[[c for c in ELEMENT_COLS if c in df.columns]].fillna(0).round(2) \
        .astype(str).agg("|".join, axis=1)
    return key.factorize()[0]


def train(target, df, n_splits=5, seed=0):
    y = pd.to_numeric(df[target], errors="coerce")
    mask = y.notna()
    if mask.sum() < 50:
        return None
    sub = df[mask]; yv = y[mask].to_numpy(float)
    X, cols = assemble(sub)
    gkf = GroupKFold(n_splits=n_splits)
    oof = np.zeros_like(yv)
    for tr, te in gkf.split(X, yv, _groups(sub)):
        mem = _members(seed)
        for m in mem:
            m.fit(X.iloc[tr].to_numpy(), yv[tr])
        oof[te] = np.mean([m.predict(X.iloc[te].to_numpy()) for m in mem], axis=0)
    m = MgModel(target=target, feat_cols=cols, members=_members(seed))
    for mem in m.members:
        mem.fit(X.to_numpy(), yv)
    m.metrics = {"r2_cv": float(r2_score(yv, oof)),
                 "mae_cv": float(mean_absolute_error(yv, oof)),
                 "n": int(mask.sum()), "y_std": float(yv.std())}
    return m


def train_all(df, seed=0):
    MG_MODELS.mkdir(parents=True, exist_ok=True)
    out = {}
    for t in TARGETS:
        if t not in df.columns:
            continue
        m = train(t, df, seed=seed)
        if m is None:
            continue
        out[t] = m
        joblib.dump(m, MG_MODELS / f"{t}.joblib", compress=3)
        print(f"  {t:10s} n={m.metrics['n']:4d}  R2_cv={m.metrics['r2_cv']:+.3f}  "
              f"MAE_cv={m.metrics['mae_cv']:6.2f}")
    return out


def load_or_train(df=None, seed=0):
    df = MG.load_mg() if df is None else df
    try:
        out, missing = {}, []
        for t in TARGETS:
            p = MG_MODELS / f"{t}.joblib"
            if p.exists():
                out[t] = joblib.load(p)
            else:
                missing.append(t)
        if not out:
            raise FileNotFoundError
        for t in missing:
            m = train(t, df, seed=seed)
            if m:
                out[t] = m
                joblib.dump(m, MG_MODELS / f"{t}.joblib", compress=3)
        return out
    except Exception:
        print("  [mg] retraining models ...")
        return train_all(df, seed=seed)


def main():
    df = MG.load_mg()
    print(f"Training Mg surrogate models on {len(df)} alloys ...")
    ms = train_all(df)
    (MG_MODELS / "metrics.json").write_text(
        json.dumps({t: m.metrics for t, m in ms.items()}, indent=2))
    return ms


if __name__ == "__main__":
    main()
