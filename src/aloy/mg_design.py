"""Multi-objective inverse design for Mg alloys.

Mg-specific objectives (density is minimised because lightness is the point):
    maximise YS, maximise ductility, maximise specific strength,
    minimise density, minimise cost

Constraint: keep it a magnesium alloy (Mg >= 70 wt%) and RE fraction civil.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass

from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.lhs import LHS
from pymoo.optimize import minimize

from . import mg as MG
from . import mg_models as MM
from . import elements as el
from . import calphad_check as CC

OUT = MG.OUT if hasattr(MG, "OUT") else None
from pathlib import Path
OUT = Path(__file__).resolve().parents[2] / "outputs"

# Mg alloying elements that are affordable & common in practice
MG_ALLOYS = ["Al", "Zn", "Mn", "Ca", "Sn", "Si", "Zr", "Nd", "Ce", "La",
             "Gd", "Y", "Sr", "Li", "Ag", "Cu"]


@dataclass
class MgSpace:
    mg_min: float = 0.70
    max_total: float = 0.30
    delta_r_max: float = 0.10
    elements: tuple = tuple(MG_ALLOYS)


class MgProblem(Problem):
    def __init__(self, models, space: MgSpace, bounds_max: np.ndarray | None = None):
        self.models = models
        self.space = space
        self.efeats = list(space.elements)
        n = len(self.efeats)
        # data-driven trust region: cap each element at a level actually
        # supported by enough experimental records. For sparse elements we use
        # the maximum observed among the top-decile, not the absolute max, so
        # the optimiser cannot sit on a single outlier point.
        if bounds_max is None:
            df = MG.load_mg()
            ub = np.zeros(n)
            for j, e in enumerate(self.efeats):
                if e in df.columns:
                    obs = pd.to_numeric(df[e], errors="coerce").fillna(0).clip(lower=0)
                    nz = obs[obs > 0]
                    if len(nz) >= 30:
                        # well-sampled element: allow up to its 75th percentile
                        cap = float(nz.quantile(0.75))
                    elif len(nz) >= 5:
                        # sparse: allow its median, but keep it modest
                        cap = float(nz.median())
                    else:
                        cap = 0.0    # too rare to trust -> effectively exclude
                    ub[j] = float(np.clip(cap, 0.0, 0.20))
                else:
                    ub[j] = 0.0
            self.bounds_max = ub
        else:
            self.bounds_max = np.asarray(bounds_max)
        # require a little room so the search is not degenerate
        self.bounds_max = np.maximum(self.bounds_max, 0.0)
        super().__init__(n_var=n, n_obj=5, n_ieq_constr=1,
                         xl=np.zeros(n), xu=self.bounds_max)

    def _comp(self, x):
        # x is already in absolute element-fraction units bounded by bounds_max
        x = np.atleast_2d(x)
        out = np.zeros_like(x)
        for i in range(x.shape[0]):
            f = np.clip(x[i], 0, None)
            s = f.sum()
            total = min(s, self.space.max_total)
            out[i] = total * f / s if s > 0 else 0.0
        return out

    def _features(self, comp):
        comp = np.atleast_2d(comp)
        m = comp.shape[0]
        row = {e: np.zeros(m) for e in MM.ELEMENT_COLS}
        tot = comp.sum(1)
        row["Mg"] = np.clip(1.0 - tot, 0, 1)
        for j, e in enumerate(self.efeats):
            if e in row:
                row[e] = comp[:, j]
        tmp = pd.DataFrame(row)
        feats = MG._mg_features(
            tmp.assign(**{c: tmp[c] for c in MM.ELEMENT_COLS}),
            list(MM.ELEMENT_COLS))
        for c in feats.columns:
            tmp[c] = feats[c].to_numpy()
        tmp["proc"] = 0.7
        return tmp

    def _evaluate(self, x, out, *args, **kwargs):
        z = self._comp(x)
        f = self._features(z)
        ys, _ = self.models["ys_mpa"].predict(f)
        elo, _ = self.models["elong_pct"].predict(f)
        rho = f["rho_rule"].to_numpy()
        cost = (z * np.array([el.COST[e] for e in self.efeats])).sum(1) \
            + np.clip(1 - z.sum(1), 0, None) * el.COST["Mg"]
        elo = np.clip(elo, 0.2, 25.0)
        rho = np.clip(rho, 1.2, 2.5)
        out["F"] = np.column_stack([-ys, -elo, -ys / rho, rho, cost])
        out["G"] = np.column_stack([f["delta_r"].to_numpy() - self.space.delta_r_max])


def run(space: MgSpace | None = None, n_gen: int = 80, pop: int = 160,
        seed: int = 1) -> pd.DataFrame:
    space = space or MgSpace()
    ms = MM.load_or_train()
    ms = {t: ms[t] for t in ("ys_mpa", "uts_mpa", "elong_pct") if t in ms}
    prob = MgProblem(ms, space)
    res = minimize(prob, NSGA2(pop_size=pop, sampling=LHS()), ("n_gen", n_gen),
                   seed=seed, verbose=False)
    if res.X is None:
        return pd.DataFrame()
    X = np.atleast_2d(res.X)
    Z = prob._comp(X)
    f = prob._features(Z)
    ys, ys_u = ms["ys_mpa"].predict(f)
    uts, _ = ms["uts_mpa"].predict(f)
    elo, _ = ms["elong_pct"].predict(f)
    rho = f["rho_rule"].to_numpy()
    rows = pd.DataFrame(Z, columns=space.elements)
    rows.insert(0, "Mg", np.clip(1 - Z.sum(1), 0, 1))
    rows["YS_pred"] = ys
    rows["UTS_pred"] = uts
    rows["elong_pred"] = np.clip(elo, 0.2, 25.0)
    rows["rho_pred"] = rho
    rows["specific"] = ys / rho
    rows["cost"] = (Z * np.array([el.COST[e] for e in space.elements])).sum(1) \
        + np.clip(1 - Z.sum(1), 0, None) * el.COST["Mg"]
    rows["re_fraction"] = f["re_fraction"].to_numpy()
    rows["delta_r"] = f["delta_r"].to_numpy()
    rows["YS_unc"] = ys_u
    return rows


def rank(df: pd.DataFrame, top: int = 20) -> pd.DataFrame:
    d = df.copy()

    def nz(s):
        return (s - s.min()) / (s.max() - s.min() + 1e-9)
    d["score"] = (0.30 * nz(d["YS_pred"]) + 0.25 * nz(d["elong_pred"])
                  + 0.30 * nz(d["specific"]) + 0.15 * (1 - nz(d["cost"])))
    d["confidence"] = 1 / (1 + d["YS_unc"] / 50.0)
    d["final"] = d["score"] * d["confidence"]
    return d.sort_values("final", ascending=False).head(top)


def main():
    df = run()
    df.to_csv(OUT / "mg_pareto.csv", index=False)
    print(f"Mg Pareto solutions: {len(df)}")
    top = rank(df)
    cols = [c for c in ["Mg", "Al", "Zn", "Ca", "Nd", "Ce", "Gd", "Y", "Li",
                        "YS_pred", "elong_pred", "rho_pred", "specific",
                        "cost", "re_fraction"] if c in top.columns]
    print(top[cols].round(3).to_string(index=False))
    return df


if __name__ == "__main__":
    main()
