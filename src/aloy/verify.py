"""Verification: honest holdout test + physics sanity of recommendations.

Produces a machine-readable report so results are auditable, not just asserted.
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from pathlib import Path

from . import models as M

OUT = Path(__file__).resolve().parents[2] / "outputs"


def holdout_report(df: pd.DataFrame, seed: int = 42) -> dict:
    """Single 80/20 grouped holdout per target, reported honestly."""
    rep = {}
    for t in M.TARGETS:
        if t not in df.columns:
            continue
        y = pd.to_numeric(df[t], errors="coerce")
        mask = y.notna()
        if mask.sum() < 60:
            continue
        sub = df[mask]; yv = y[mask].to_numpy(float)
        X, _ = M.assemble_matrix(sub)
        groups = M.composition_groups(sub)
        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
        tr, te = next(gss.split(X, yv, groups))
        preds = []
        for m in M._members(seed):
            m.fit(X.iloc[tr].to_numpy(), yv[tr])
            preds.append(m.predict(X.iloc[te].to_numpy()))
        p = np.mean(preds, axis=0)
        rep[t] = {
            "n_test": int(len(te)),
            "r2": float(r2_score(yv[te], p)),
            "mae": float(mean_absolute_error(yv[te], p)),
            "rmse": float(np.sqrt(mean_squared_error(yv[te], p))),
        }
    return rep


def physics_sanity(cands: pd.DataFrame) -> pd.DataFrame:
    """Flag metallurgically implausible recommendations."""
    flags = []
    for _, r in cands.iterrows():
        f = []
        if r.get("delta_r", 0) > 0.10:
            f.append("size_mismatch_high")
        if r.get("vec", 3) > 4.2:
            f.append("high_vec_forms_intermetallics")
        if r.get("Mg", 0) > 0.10:
            f.append("mg_over_solubility_(>10%)")
        if r.get("Cu", 0) > 0.06:
            f.append("cu_high_embrittlement_risk")
        if r.get("Zn", 0) > 0.10:
            f.append("zn_high_corrosion_risk")
        if r.get("YS_pred", 0) > 700:
            f.append("strength_beyond_common_data")
        flags.append(";".join(f) if f else "ok")
    out = cands.copy(); out["flags"] = flags
    return out


def main():
    df = M.load_all()
    print("Holdout verification (GroupShuffleSplit 80/20):")
    rep = holdout_report(df)
    for t, m in rep.items():
        print(f"  {t:10s} n_test={m['n_test']:4d}  R2={m['r2']:+.3f}  "
              f"MAE={m['mae']:.2f}  RMSE={m['rmse']:.2f}")
    (OUT / "holdout_report.json").write_text(json.dumps(rep, indent=2))

    econ = pd.read_csv(OUT / "candidates_economy.csv")
    chk = physics_sanity(econ)
    chk.to_csv(OUT / "candidates_economy_flagged.csv", index=False)
    n_bad = (chk["flags"] != "ok").sum()
    print(f"\nPhysics screening: {n_bad}/{len(chk)} economy candidates carry a warning flag")
    print(chk.loc[chk["flags"] != "ok", ["Al", "Mg", "Zn", "Cu", "YS_pred", "flags"]]
          .drop_duplicates("flags").head(10).to_string(index=False))
    return rep


if __name__ == "__main__":
    main()
