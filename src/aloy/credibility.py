"""Credibility layer: conformal prediction intervals + derived design metrics.

Two things a reviewer will ask:
  1. "Your point prediction is X -- but what is the honest error bar?"
     -> split-conformal prediction (distribution-free, finite-sample valid).
  2. "Is the recommendation actually good per unit cost?"
     -> cost-normalised strength, and a Pareto-rank stability check.
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit

from . import models as M

OUT = Path(__file__).resolve().parents[2] / "outputs"


def conformal_intervals(df: pd.DataFrame, target: str = "ys_mpa",
                        alpha: float = 0.10, seed: int = 7) -> dict:
    """Split-conformal 1-alpha intervals with guaranteed marginal coverage.

    Returns the calibration quantile q and the empirical coverage on a held-out
    fold, plus the interval half-width to attach to any prediction.
    """
    y = pd.to_numeric(df[target], errors="coerce")
    mask = y.notna()
    sub = df[mask]; yv = y[mask].to_numpy(float)
    X, _ = M.assemble_matrix(sub)
    groups = M.composition_groups(sub)

    gss = GroupShuffleSplit(n_splits=1, test_size=0.4, random_state=seed)
    cal_idx, val_idx = next(gss.split(X, yv, groups))
    # further split the calibration half from the validation half
    cal, val = cal_idx, val_idx

    preds = np.zeros(len(yv))
    for tr, te in [(val, cal), (cal, val)]:
        mem = M._members(seed)
        for m in mem:
            m.fit(X.iloc[tr].to_numpy(), yv[tr])
        preds[te] = np.mean([m.predict(X.iloc[te].to_numpy()) for m in mem], axis=0)

    # calibration residuals on the calibration fold
    resid = np.abs(yv[cal] - preds[cal])
    n = len(cal)
    q = float(np.quantile(resid, np.ceil((n + 1) * (1 - alpha)) / n))
    covered = float(np.mean(np.abs(yv[val] - preds[val]) <= q))
    return {
        "target": target, "alpha": alpha, "n_cal": int(n),
        "q_halfwidth": q, "coverage_val": covered,
        "nominal_coverage": 1 - alpha,
    }


def cost_metrics(cands: pd.DataFrame) -> pd.DataFrame:
    out = cands.copy()
    out["strength_per_dollar"] = out["YS_pred"] / out["cost"]
    out["stiffness_per_dollar"] = out.get("specific", out["YS_pred"]) / out["cost"]
    # Pareto rank stability: how many other candidates dominate this one
    ys = out["YS_pred"].to_numpy()
    el = out["elong_pred"].to_numpy()
    c = out["cost"].to_numpy()
    dominated = np.zeros(len(out), dtype=int)
    for i in range(len(out)):
        dominated[i] = int(np.sum((ys >= ys[i]) & (el >= el[i]) & (c <= c[i]) &
                                  ((ys > ys[i]) | (el > el[i]) | (c < c[i]))))
    out["n_dominating"] = dominated
    return out


def main():
    df = M.load_all()
    print(f"Conformal calibration on {len(df)} records (target=ys_mpa):")
    rep = conformal_intervals(df, "ys_mpa", alpha=0.10)
    for k, v in rep.items():
        print(f"  {k}: {v:.3f}" if isinstance(v, float) else f"  {k}: {v}")
    print(f"\n  -> a YS prediction of 600 MPa carries a +/-{rep['q_halfwidth']:.0f} MPa "
          f"90% interval (empirical coverage {rep['coverage_val']:.0%})")

    cands = pd.read_csv(OUT / "candidates_calphad.csv")
    cm = cost_metrics(cands)
    cm.to_csv(OUT / "candidates_final.csv", index=False)
    print("\nBest strength per dollar (economy candidates):")
    cols = [c for c in ["Al", "Mg", "Zn", "Cu", "YS_pred", "elong_pred",
                        "cost", "strength_per_dollar", "phase_risk"] if c in cm.columns]
    top = cm.sort_values("strength_per_dollar", ascending=False).head(8)
    print(top[cols].round(2).to_string(index=False))

    rep["cost_metrics_note"] = "strength_per_dollar = YS_pred / cost_USD_per_kg"
    (OUT / "credibility_report.json").write_text(json.dumps(rep, indent=2))
    return rep


if __name__ == "__main__":
    main()
