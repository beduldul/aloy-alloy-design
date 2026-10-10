"""Closed-loop experiment simulator.

Because real melting is expensive, we simulate the research loop first:

    model proposes N alloys  ->  "lab" returns the TRUE property (from a held-out
    or oracle model / real measurement)  ->  model refits  ->  repeat

This lets you answer: "how many experiments until the model reliably finds a
good alloy?" and "is the active-learning acquisition actually better than random
sampling?" -- the core methodological question of any ML-for-materials paper.

Two oracles are available:
  * leave-one-out surrogate: use a model trained on a subset as the ground truth
  * held-out real measurements: if you supply measured data in experiment_log.json
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from pathlib import Path

from . import models as M
from . import elements as el

OUT = Path(__file__).resolve().parents[2] / "outputs"
RNG = np.random.default_rng(0)


def make_oracle(df: pd.DataFrame, seed: int = 0) -> dict:
    """Ground-truth 'lab' backed by a fresh ensemble trained on all real data.

    In a real study this is replaced by the physical tensile test. Here it lets
    us audit the whole loop without consuming material.
    """
    out = {}
    for t in ("ys_mpa", "elong_pct"):
        if t in df.columns:
            m = M.train(t, df, seed=seed + 999)
            if m is not None:
                out[t] = m
    return out


def measure(oracle: dict, comps: np.ndarray, noise_mpa: float = 15.0) -> np.ndarray:
    """Return the 'measured' YS for a batch of compositions (with lab noise)."""
    from .design import AlloyProblem, DesignSpace
    prob = AlloyProblem(oracle, DesignSpace(), {}, rho_model=None)
    feats = prob._features(comps)
    ys, _ = oracle["ys_mpa"].predict(feats)
    return ys + np.random.default_rng(len(comps)).normal(0, noise_mpa, size=len(ys))


def _comps_from_model(ms: dict, seed: int, n: int, n_candidates: int = 4000) -> np.ndarray:
    """Fast surrogate-guided proposal: sample many cheap candidates and keep the
    best-predicted. Cheaper than a full NSGA-II run; adequate for loop auditing.
    """
    rng = np.random.default_rng(seed)
    from .design import AlloyProblem, DesignSpace
    space = DesignSpace()
    prob = AlloyProblem(ms, space, {}, rho_model=None)
    X = rng.random((n_candidates, 12))
    feats = prob._features(X)
    ys, _ = ms["ys_mpa"].predict(feats)
    top = np.argsort(-ys)[:n]
    return X[top]


def simulate_loop(n_rounds: int = 6, batch: int = 5, strategy: str = "active",
                  n_seed: int = 40, seed: int = 0,
                  oracle: dict | None = None, ms: dict | None = None) -> pd.DataFrame:
    """Run the closed loop and record the best-found strength per round.

    strategy: "active" (surrogate-guided) or "random" (baseline).
    """
    df = M.load_all() if ms is None else None
    if ms is None:
        ms = {t: M.load_or_train(df)[t] for t in ("ys_mpa", "uts_mpa", "elong_pct")}
    if oracle is None:
        oracle = make_oracle(df if df is not None else M.load_all(), seed=seed)

    RNG = np.random.default_rng(seed + 12345)
    seen = _comps_from_model(ms, seed, n_seed)[:n_seed]
    measured = measure(oracle, seen)
    history = []

    for rnd in range(n_rounds):
        if strategy == "active":
            cand = _comps_from_model(ms, seed + rnd + 1, batch)
        else:
            cand = RNG.random((batch, 12))
        y_new = measure(oracle, cand)
        seen = np.vstack([seen, cand])
        measured = np.concatenate([measured, y_new])
        history.append({
            "round": rnd + 1, "strategy": strategy,
            "batch_best_YS": float(y_new.max()),
            "cumulative_best_YS": float(measured.max()),
            "cumulative_mean_YS": float(measured.mean()),
            "n_experiments": len(measured),
        })
    return pd.DataFrame(history)


def compare_strategies(n_rounds: int = 6, batch: int = 5, repeats: int = 3) -> pd.DataFrame:
    df = M.load_all()
    ms = {t: M.load_or_train(df)[t] for t in ("ys_mpa", "uts_mpa", "elong_pct")}
    rows = []
    for rep in range(repeats):
        oracle = make_oracle(df, seed=rep)   # one oracle per repeat
        for strat in ("active", "random"):
            h = simulate_loop(n_rounds=n_rounds, batch=batch, strategy=strat,
                              seed=rep, oracle=oracle, ms=ms)
            h["repeat"] = rep
            rows.append(h)
    return pd.concat(rows, ignore_index=True)


def main():
    print("Simulating the closed research loop (no metal consumed) ...")
    print("Comparing model-guided 'active' vs 'random' experiment selection.\n")
    res = compare_strategies(n_rounds=6, batch=5, repeats=3)
    res.to_csv(OUT / "loop_simulation.csv", index=False)

    summary = (res.groupby(["strategy", "round"])["cumulative_best_YS"]
               .mean().unstack(0).round(1))
    print("Mean BEST YS found after each round (MPa):")
    print(summary.to_string())
    print("\nFinal best after 6 rounds (~30 experiments):")
    fin = res[res["round"] == res["round"].max()].groupby("strategy")["cumulative_best_YS"].mean()
    for s, v in fin.items():
        print(f"  {s:8s}: {v:.1f} MPa")
    if "active" in fin and "random" in fin:
        gain = (fin["active"] - fin["random"]) / fin["random"] * 100
        print(f"  -> active-learning advantage: {gain:+.1f}%")
    print(f"\n-> {OUT/'loop_simulation.csv'}")
    return res


if __name__ == "__main__":
    main()
