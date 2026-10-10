"""Two explicit design scenarios so 'murah' is a real, enforced objective.

Scenario A -- ECONOMY: only cheap, commodity alloying elements (Mg, Zn, Cu, Si,
    Mn, Fe). No Li/Sc/Ag/Be/Bi/Cd. Hard cost ceiling.
Scenario B -- PERFORMANCE: Li/Sc/Zr/Ti allowed (aerospace intent), no cost ceiling.

Also a price-sensitivity sweep: how does the best achievable specific strength
change as the cost ceiling is relaxed? That quantifies the strength-per-dollar
frontier.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from . import design as G
from . import elements as el

CHEAP_ELEMENTS = ["Mg", "Zn", "Cu", "Si", "Mn", "Fe"]
PERF_ELEMENTS = ["Mg", "Zn", "Cu", "Si", "Mn", "Cr", "Ti", "Zr", "Li", "Sc"]

WEIGHTS = {"ys": 0.40, "elo": 0.20, "specific": 0.30, "cost": 0.10}


def run_scenario(name: str, elem_list: list[str], cost_ceiling: float | None,
                 n_gen: int = 80, pop: int = 160, seed: int = 1) -> pd.DataFrame:
    space = G.DesignSpace(elements=tuple(elem_list))
    prob_space = space
    # run base design
    df = G.run_design(n_gen=n_gen, pop=pop, seed=seed, space=space, weights=WEIGHTS)
    if df.empty:
        return df
    if cost_ceiling is not None:
        df = df[df["cost"] <= cost_ceiling].copy()
    df["scenario"] = name
    df["dominant_el"] = df[elem_list].idxmax(axis=1)
    return df


def price_sweep(elem_list, ceilings, n_gen=60, pop=140, seed=3) -> pd.DataFrame:
    rows = []
    for c in ceilings:
        df = run_scenario(f"cap_{c:.0f}", elem_list, c, n_gen, pop, seed)
        if df.empty or len(df) == 0:
            rows.append({"cost_cap": c, "best_specific": np.nan,
                         "best_ys": np.nan, "n": 0})
            continue
        top = G.pareto_front(df, WEIGHTS, top=10)
        rows.append({
            "cost_cap": c,
            "best_specific": float(top["specific"].max()),
            "best_ys": float(top["YS_pred"].max()),
            "max_elong": float(top["elong_pred"].max()),
            "n": int(len(df)),
        })
    return pd.DataFrame(rows)


def main(seed: int = 1):
    print("=" * 70)
    print("Scenario A: ECONOMY  (Mg/Zn/Cu/Si/Mn/Fe only, cost <= 8 USD/kg)")
    print("=" * 70)
    a = run_scenario("economy", CHEAP_ELEMENTS, cost_ceiling=8.0, seed=seed)
    if not a.empty:
        a.to_csv(G.OUT / "candidates_economy.csv", index=False)
        ta = G.pareto_front(a, WEIGHTS, top=12)
        cols = ["Al", "Mg", "Zn", "Cu", "Si", "Mn", "YS_pred", "elong_pred",
                "rho_pred", "specific", "cost", "delta_r", "score"]
        print(ta[[c for c in cols if c in ta.columns]].round(3).to_string(index=False))
    else:
        print("  no feasible economy candidates")

    print("\n" + "=" * 70)
    print("Scenario B: PERFORMANCE  (Li/Sc/Zr/Ti allowed)")
    print("=" * 70)
    b = run_scenario("performance", PERF_ELEMENTS, cost_ceiling=None, seed=seed)
    if not b.empty:
        tb = G.pareto_front(b, WEIGHTS, top=8)
        cols = ["Al", "Mg", "Zn", "Cu", "Li", "Sc", "Zr", "Ti",
                "YS_pred", "elong_pred", "specific", "cost"]
        print(tb[[c for c in cols if c in tb.columns]].round(3).to_string(index=False))

    print("\n" + "=" * 70)
    print("Price-sensitivity sweep (economy elements, cost ceiling -> best)")
    print("=" * 70)
    sw = price_sweep(CHEAP_ELEMENTS, [3, 4, 5, 6, 8, 12], seed=seed)
    sw.to_csv(G.OUT / "price_sweep.csv", index=False)
    print(sw.round(2).to_string(index=False))
    return a, b, sw


if __name__ == "__main__":
    main()
