"""Multi-objective inverse design of new Al/Mg alloys.

Approach
--------
We search the composition simplex with a real NSGA-II (pymoo) to find the
Pareto front trading off:
    maximise  yield strength
    maximise  elongation (ductility)
    maximise  specific strength  (YS / density)
    minimise  raw-material cost
subject to physical manufacturability constraints (Hume-Rothery-style):
    delta_r  < 0.065   (single-phase solid-solution stability)
    -10 <= omega <= 20 (thermodynamic stability window)
    0.85 <= VEC <= 4.2 for Al-base lightness-friendly window (soft)
    Al >= 0.80 mass fraction (Al-based; keep it meltable & cheap)
    sum of alloying additions <= 0.20
Then we rank Pareto points by a user-weighted desirability and by uncertainty
(ensemble spread) so the top recommendations are both strong AND trustworthy.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass

from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.lhs import LHS
from pymoo.optimize import minimize

from . import models as M
from . import data as D
from . import elements as el
from pathlib import Path as _Path

OUT = _Path(__file__).resolve().parents[2] / "outputs"

# elements allowed to vary (Al fixed as base via mass balance)
ALLOY_ELEMENTS = ["Mg", "Zn", "Cu", "Si", "Mn", "Fe", "Ni", "Cr", "Ti", "Zr", "Li", "Sc"]
ALL_INDEX = {e: i for i, e in enumerate(ALLOY_ELEMENTS)}


@dataclass
class DesignSpace:
    al_min: float = 0.80          # minimum Al mass fraction
    max_total: float = 0.20       # max total alloying addition
    delta_r_max: float = 0.075    # Hume-Rothery size criterion (95th pct of real data)
    omega_lo: float = 800.0       # thermodynamic stability window, calibrated to
    omega_hi: float = 12000.0     # the closed-shell proxy's actual scale in the data
    proc: float = 1.0             # aged-peak processing (T6-like)
    test_T: float = 25.0
    elements: tuple = tuple(ALLOY_ELEMENTS)


class AlloyProblem(Problem):
    def __init__(self, models: dict, space: DesignSpace, weights: dict,
                 rho_model=None):
        self.models = models
        self.space = space
        self.weights = weights
        self.rho_model = rho_model
        self.efeats = list(space.elements)
        n = len(self.efeats)
        # x in [0,1]^n -> alloying fractions normalised so total <= max_total
        super().__init__(n_var=n, n_obj=4, n_ieq_constr=3,
                         xl=np.zeros(n), xu=np.ones(n))

    def _to_composition(self, x: np.ndarray) -> np.ndarray:
        f = np.clip(x, 0, None)
        s = f.sum()
        if s <= 1e-9:
            return np.zeros_like(f)
        # total alloying = base_total * (s/(1+s)) style ramp capped at max_total
        total = self.space.max_total * (s / (s + 1.0))
        return total * f / s

    def _features(self, comp: np.ndarray) -> pd.DataFrame:
        """Vectorised: comp is (m, n_efeats) alloying fractions; returns m rows
        with element + physical + process columns matching model features."""
        comp = np.atleast_2d(comp)
        m = comp.shape[0]
        row = {e: np.zeros(m) for e in M.ELEMENT_COLS}
        total = comp.sum(axis=1)
        row["Al"] = np.clip(1.0 - total, 0.0, 1.0)
        for j, e in enumerate(self.efeats):
            if e in row:
                row[e] = comp[:, j]
        tmp = pd.DataFrame(row)
        el_cols = list(D.el.AL_ELEMENTS)
        feats = D.build_physical_features(tmp, el_cols, base="Al")
        for c in feats.columns:
            tmp[c] = feats[c].to_numpy()
        tmp["proc"] = self.space.proc
        tmp["test_T"] = self.space.test_T
        return tmp

    def _rho(self, feats: pd.DataFrame) -> np.ndarray:
        """Density: ML model if trained, else rule-of-mixtures (exact enough)."""
        if self.rho_model is not None:
            return self.rho_model.predict(feats)[0]
        return feats["rho_rule"].to_numpy()

    def _evaluate(self, x, out, *args, **kwargs):
        x = np.atleast_2d(x)                       # (pop, n_var) batch
        z = np.array([self._to_composition(xi) for xi in x])
        feats = self._features(z)
        ys, _ = self.models["ys_mpa"].predict(feats)
        uts, _ = self.models["uts_mpa"].predict(feats)
        elo, _ = self.models["elong_pct"].predict(feats)
        rho = self._rho(feats)
        cost = (z * np.array([el.COST[e] for e in self.efeats])).sum(axis=1) \
            + np.clip(1 - z.sum(axis=1), 0, None) * el.COST["Al"]
        elo = np.clip(elo, 0.5, 60.0)
        rho = np.clip(rho, 1.5, 4.5)
        specific = ys / rho

        out["F"] = np.column_stack([-ys, -elo, -specific, cost])

        dr = feats["delta_r"].to_numpy()
        om = feats["omega"].to_numpy()
        out["G"] = np.column_stack([
            dr - self.space.delta_r_max,
            self.space.omega_lo - om,
            om - self.space.omega_hi,
        ])


def run_design(n_gen: int = 60, pop: int = 120, seed: int = 1,
               space: DesignSpace | None = None,
               weights: dict | None = None) -> pd.DataFrame:
    space = space or DesignSpace()
    weights = weights or {"ys": 0.4, "elo": 0.2, "specific": 0.3, "cost": 0.1}
    ms_all = M.load_or_train()
    ms = {t: ms_all[t] for t in ("ys_mpa", "uts_mpa", "elong_pct") if t in ms_all}
    # Density: rule-of-mixtures is exact enough and does not need a fragile ML
    # model (after Al-domain filtering the MPEA density rows are too few).
    _rho_model = ms_all.get("rho_exp")

    def predict_rho(feats: pd.DataFrame) -> np.ndarray:
        if _rho_model is not None:
            return _rho_model.predict(feats)[0]
        return feats["rho_rule"].to_numpy()

    prob = AlloyProblem(ms, space, weights, rho_model=_rho_model)
    algo = NSGA2(pop_size=pop, sampling=LHS())
    res = minimize(prob, algo, ("n_gen", n_gen), seed=seed, verbose=False)

    if res.X is None:
        return pd.DataFrame()
    X = np.atleast_2d(res.X)
    Z = np.array([prob._to_composition(xi) for xi in X])
    feats = prob._features(Z)
    ys, ys_u = ms["ys_mpa"].predict(feats)
    uts, _ = ms["uts_mpa"].predict(feats)
    elo, _ = ms["elong_pct"].predict(feats)
    rho = prob._rho(feats)
    elo = np.clip(elo, 0.5, 60.0)

    rows = pd.DataFrame(Z, columns=space.elements)
    rows.insert(0, "Al", np.clip(1 - Z.sum(axis=1), 0, 1))
    phys = D.build_physical_features(
        feats[[c for c in M.ELEMENT_COLS if c in feats.columns]].copy(),
        list(D.el.AL_ELEMENTS), base="Al")
    rows["YS_pred"] = ys
    rows["YS_unc"] = ys_u
    rows["UTS_pred"] = uts
    rows["elong_pred"] = elo
    rows["rho_pred"] = rho
    rows["specific"] = ys / rho
    rows["cost"] = (Z * np.array([el.COST[e] for e in space.elements])).sum(axis=1) \
        + np.clip(1 - Z.sum(axis=1), 0, None) * el.COST["Al"]
    rows["delta_r"] = phys["delta_r"].to_numpy()
    rows["omega"] = phys["omega"].to_numpy()
    rows["vec"] = phys["vec"].to_numpy()
    rows["n_elements"] = (Z > 1e-3).sum(axis=1) + 1
    return rows


def desirability(df: pd.DataFrame, weights: dict) -> pd.Series:
    def nz(s, lo=None, hi=None):
        lo = s.min() if lo is None else lo
        hi = s.max() if hi is None else hi
        return (s - lo) / (hi - lo + 1e-9)
    d = (weights["ys"] * nz(df["YS_pred"])
         + weights["elo"] * nz(df["elong_pred"])
         + weights["specific"] * nz(df["specific"])
         + weights["cost"] * (1 - nz(df["cost"])))
    return d / sum(weights.values())


def pareto_front(df: pd.DataFrame, weights: dict, top: int = 25) -> pd.DataFrame:
    df = df.copy()
    df["desirability"] = desirability(df, weights)
    # penalise high-uncertainty predictions
    df["confidence"] = 1.0 / (1.0 + df["YS_unc"] / 100.0)
    df["score"] = df["desirability"] * df["confidence"]
    return df.sort_values("score", ascending=False).head(top)
