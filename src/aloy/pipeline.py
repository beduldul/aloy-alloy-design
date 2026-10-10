"""End-to-end pipeline: data -> models -> inverse design -> rankings -> figures.

Usage:  PYTHONPATH=src python3 -m aloy.pipeline
"""
from __future__ import annotations
import warnings, time
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from pathlib import Path

from . import models as M, design as G, plots as P

OUT = Path(__file__).resolve().parents[2] / "outputs"


WEIGHTS = {"ys": 0.40, "elo": 0.20, "specific": 0.30, "cost": 0.10}


def main():
    t0 = time.time()
    print("=" * 70)
    print("Aloy: Al/Mg alloy discovery pipeline")
    print("=" * 70)

    print("\n[1/5] Loading public data ...")
    df = M.load_all()
    print(f"      {df.shape[0]} records, {df['source'].value_counts().to_dict()}")

    print("\n[2/5] Training surrogate ensembles (GroupKFold, leakage-free) ...")
    ms = M.train_all(df)

    print("\n[3/5] Multi-objective inverse design (NSGA-II) ...")
    pareto = G.run_design(n_gen=80, pop=160, seed=1)
    pareto.to_csv(OUT / "pareto_raw.csv", index=False)
    print(f"      {len(pareto)} Pareto-optimal candidates")

    print("\n[4/5] Ranking by desirability x confidence ...")
    top = G.pareto_front(pareto, WEIGHTS, top=30)
    top.to_csv(OUT / "top_candidates.csv", index=False)

    print("\n[5/5] Figures ...")
    P.make_all(df, ms, pareto, OUT / "figures")

    print(f"\nDone in {time.time()-t0:.1f}s")
    print(f"  -> {OUT/'top_candidates.csv'}")
    print(f"  -> {OUT/'figures'}/")
    return top


if __name__ == "__main__":
    top = main()
    cols = ["Al", "Mg", "Zn", "Cu", "Si", "Mn", "Ti", "Li", "Zr", "Sc",
            "YS_pred", "elong_pred", "rho_pred", "specific", "cost", "delta_r"]
    cols = [c for c in cols if c in top.columns]
    print("\nTOP 12 CANDIDATES")
    print(top[cols].round(3).head(12).to_string(index=False))
