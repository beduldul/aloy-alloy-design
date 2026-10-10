"""Active-learning / Bayesian-optimisation loop for alloy development.

This turns the pipeline from a one-shot predictor into a *research loop*:

    propose  ->  (you run the experiment)  ->  observe  ->  update  ->  propose

Batch acquisition (qEI / qLogNEI) selects the next N compositions that maximise
expected improvement under a Gaussian-Process surrogate, balancing
exploitation (high predicted YS) with exploration (high uncertainty).

Runs on CPU with BoTorch; if an MPS GPU is present the GP fitting uses it for
the torch linear algebra.
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field

import torch
from botorch.models import SingleTaskGP
from botorch.fit import fit_gpytorch_mll
from botorch.models.transforms.outcome import Standardize
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch.acquisition.logei import qLogNoisyExpectedImprovement
from botorch.optim import optimize_acqf

from . import models as M

OUT = Path(__file__).resolve().parents[2] / "outputs"
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
# MPS does not support float64; GPs run fine in float32 here.
DTYPE = torch.float32

# design bounds: total alloying 20%, each element [0,1] of that budget
A_BOUNDS = torch.tensor([[0.0] * len(M.ELEMENT_COLS),
                       [1.0] * len(M.ELEMENT_COLS)], dtype=DTYPE)


@dataclass
class ExperimentLog:
    """Persistent record of proposed and measured alloys."""
    path: Path = OUT / "experiment_log.json"
    rows: list = field(default_factory=list)

    def load(self):
        if self.path.exists():
            self.rows = json.loads(self.path.read_text())
        return self

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.rows, indent=2))

    def add(self, comp: dict, measured: dict | None = None, predicted: dict | None = None):
        self.rows.append({"composition": comp, "measured": measured or {},
                          "predicted": predicted or {}})
        self.save()

    def as_frame(self):
        return pd.DataFrame(self.rows)


def _features_from_x(X: np.ndarray) -> np.ndarray:
    """Map raw alloying fractions (n, n_el) to model feature matrix (n, d)."""
    n = X.shape[0]
    rows = []
    for i in range(n):
        comp = np.clip(X[i], 0, None)
        tot = comp.sum()
        total = 0.20 * (tot / (tot + 1.0)) if tot > 0 else 0.0
        frac = total * comp / tot if tot > 0 else np.zeros_like(comp)
        row = {e: 0.0 for e in M.ELEMENT_COLS}
        row["Al"] = max(0.0, 1.0 - frac.sum())
        for e, v in zip(M.ELEMENT_COLS, frac):
            if e in row:
                row[e] = v
        rows.append(row)
    tmp = pd.DataFrame(rows)
    from . import data as D
    feats = D.build_physical_features(tmp, list(D.el.AL_ELEMENTS), base="Al")
    for c in feats.columns:
        tmp[c] = feats[c].to_numpy()
    tmp["proc"] = 1.0
    tmp["test_T"] = 25.0
    return tmp


def _predict_mean_std(X: np.ndarray, ms: dict) -> tuple[np.ndarray, np.ndarray]:
    feats = _features_from_x(X)
    preds = np.vstack([ms["ys_mpa"].predict(feats)[0]])
    stds = np.vstack([ms["ys_mpa"].predict(feats)[1]])
    return preds.mean(0), stds.mean(0)


def seed_from_data(df: pd.DataFrame, ms: dict, n: int = 200, seed: int = 0,
                   max_cost: float | None = 8.0) -> tuple[torch.Tensor, torch.Tensor]:
    """Bootstrap GP training set from REAL data, as alloying fractions.

    We use the full Al-relevant manifold (not just one source) so the GP's
    length-scale reflects the true composition space, and we optionally drop
    very expensive alloys so the surrogate is not anchored on Li/Sc outliers.
    """
    from . import elements as el
    rng = np.random.default_rng(seed)
    y = pd.to_numeric(df["ys_mpa"], errors="coerce")
    sub = df[y.notna()].copy()
    y = y[y.notna()]
    if max_cost is not None:
        keep = []
        for _, r in sub.iterrows():
            c = sum(float(r.get(e, 0) or 0) * el.COST.get(e, 0) for e in M.ELEMENT_COLS)
            keep.append(c <= max_cost)
        sub = sub[np.array(keep)]
        y = y.loc[sub.index]
    if len(sub) > n:
        idx = np.random.default_rng(seed).choice(len(sub), n, replace=False)
        sub = sub.iloc[idx]; y = y.iloc[idx]
    yv = y.to_numpy(float)
    X = np.zeros((len(sub), len(M.ELEMENT_COLS)))
    for j, e in enumerate(M.ELEMENT_COLS):
        if e in sub.columns:
            X[:, j] = np.clip(sub[e].fillna(0).to_numpy(float) / 0.2, 0, 1)
    return torch.tensor(X, dtype=DTYPE), torch.tensor(yv, dtype=DTYPE).unsqueeze(-1)


def propose_next(df: pd.DataFrame, ms: dict, n_propose: int = 5,
                 n_train: int = 200, seed: int = 0,
                 max_cost: float = 8.0, allowed_elements: list[str] | None = None,
                 n_restarts: int = 16, raw_samples: int = 256) -> pd.DataFrame:
    """Fit a GP on real YS and propose the next batch by qLogNEI.

    allowed_elements restricts the search to practical, affordable elements
    (default: the economy set), so proposals are directly meltable.
    """
    torch.manual_seed(seed)
    allowed = allowed_elements or ["Mg", "Zn", "Cu", "Si", "Mn", "Fe", "Cr", "Ti", "Zr"]
    Xtr, Ytr = seed_from_data(df, ms, n=n_train, seed=seed, max_cost=max_cost)

    # BoTorch's qLogNEI needs float64 eigen-decomposition; Apple MPS forbids
    # float64. GP fitting is cheap at this scale, so we run the acquisition in
    # float64 on CPU and keep the heavy surrogate predictions on-device.
    acq_device = torch.device("cpu")
    Xtr, Ytr = Xtr.to(acq_device, dtype=torch.double), Ytr.to(acq_device, dtype=torch.double)

    # include any logged measurements
    log = ExperimentLog().load()
    extra_x, extra_y = [], []
    for r in log.rows:
        if r.get("measured", {}).get("ys_mpa") is not None:
            comp = r["composition"]
            xv = np.array([comp.get(e, 0.0) / 0.2 for e in M.ELEMENT_COLS])
            extra_x.append(np.clip(xv, 0, 1)); extra_y.append(r["measured"]["ys_mpa"])
    if extra_x:
        Xtr = torch.cat([Xtr, torch.tensor(np.array(extra_x), dtype=torch.double)], 0)
        Ytr = torch.cat([Ytr, torch.tensor(np.array(extra_y), dtype=torch.double).unsqueeze(-1)], 0)

    # freeze elements we do not want the optimizer to use
    bounds = A_BOUNDS.clone().to(torch.double)
    for j, e in enumerate(M.ELEMENT_COLS):
        if e not in allowed:
            bounds[1, j] = 0.0

    # --- trust region: keep proposals inside the data-supported envelope ---
    # GP extrapolation into empty composition space produces fantasy predictions
    # (YS >> 1000 MPa). We cap each element at its observed upper quantile in the
    # training data, and require a minimum of one solute so the alloy is real.
    from . import elements as el
    for j, e in enumerate(M.ELEMENT_COLS):
        if bounds[1, j] == 0.0:
            continue
        if e in df.columns:
            obs = pd.to_numeric(df[e], errors="coerce").clip(lower=0)
            q = float(obs.quantile(0.98)) / 0.2      # budget units
            bounds[1, j] = float(np.clip(min(bounds[1, j], max(q, 0.05)), 0.0, 1.0))
    total_cap = 1.0            # 20% total alloying == 1.0 budget units
    bounds[1, :] = torch.clamp(bounds[1, :], max=total_cap)

    try:
        gp = SingleTaskGP(Xtr, Ytr, outcome_transform=Standardize(m=1))
        mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
        fit_gpytorch_mll(mll)
        acq = qLogNoisyExpectedImprovement(model=gp, X_baseline=Xtr,
                                           prune_baseline=True)
        cands, acq_val = optimize_acqf(
            acq, bounds=bounds, q=n_propose,
            num_restarts=n_restarts, raw_samples=raw_samples)
        method = "botorch_qLogNEI"
    except Exception as exc:  # noqa: BLE001
        print(f"  [active] BoTorch acquisition failed ({type(exc).__name__}); "
              f"falling back to uncertainty-weighted sampling")
        cands = torch.rand(n_propose, len(M.ELEMENT_COLS), dtype=torch.double)
        method = "fallback_random"

    Xn = cands.detach().cpu().numpy()
    feats = _features_from_x(Xn)
    ys, unc = ms["ys_mpa"].predict(feats)
    elo, _ = ms["elong_pct"].predict(feats)
    cost = np.array([(np.clip(Xn[i], 0, None) / max(Xn[i].sum(), 1e-9)
                      * 0.20 * (Xn[i].sum() / (Xn[i].sum() + 1.0))
                      * np.array([__import__("aloy.elements", fromlist=["COST"]).COST[e]
                                  for e in M.ELEMENT_COLS])).sum() for i in range(len(Xn))])

    rows = []
    from . import calphad_check as C
    for i in range(len(Xn)):
        comp = {e: float(np.clip(Xn[i][j], 0, None)) for j, e in enumerate(M.ELEMENT_COLS)}
        s = sum(comp.values()) or 1.0
        tot = 0.20 * (s / (s + 1.0))
        comp = {e: v / s * tot for e, v in comp.items()}
        comp["Al"] = max(0.0, 1.0 - sum(comp.values()))
        vd = C.screen_intermetallics({e: v for e, v in comp.items() if v > 1e-4})
        # flag predictions beyond the experimental envelope (max real Al YS ~790)
        ood = ys[i] > 900 or unc[i] > 120
        rows.append({
            **{e: round(comp.get(e, 0.0), 4) for e in M.ELEMENT_COLS if comp.get(e, 0) > 0},
            "YS_pred": float(ys[i]), "YS_unc": float(unc[i]),
            "elong_pred": float(elo[i]), "cost": float(cost[i]),
            "phase_risk": vd.risk, "im": ";".join(vd.predicted_intermetallics),
            "out_of_domain": bool(ood),
            "acquisition_method": method,
        })
    out = pd.DataFrame(rows).fillna(0.0)
    # save proposals to log
    for _, r in out.iterrows():
        log.add({e: float(r[e]) for e in M.ELEMENT_COLS if e in r and pd.notna(r[e]) and r[e] > 0},
                predicted={"ys_mpa": float(r["YS_pred"])})
    return out


def main():
    print(f"Active learning: surrogate on {DEVICE}, GP acquisition on cpu/float64")
    df = M.load_all()
    ms = M.load_or_train()
    print("\nProposing next experiments (batch of 5) ...")
    props = propose_next(df, ms, n_propose=5, seed=0)
    props.to_csv(OUT / "next_experiments.csv", index=False)
    cols = [c for c in ["Al", "Mg", "Zn", "Cu", "Si", "Mn", "Li", "Sc",
                        "YS_pred", "YS_unc", "elong_pred", "cost",
                        "phase_risk", "acquisition_method"] if c in props.columns]
    print(props[cols].round(3).to_string(index=False))
    print(f"\n-> {OUT/'next_experiments.csv'}")
    return props


if __name__ == "__main__":
    main()
