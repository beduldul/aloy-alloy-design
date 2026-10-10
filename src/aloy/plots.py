"""Visualisations: dataset coverage, model parity, Pareto front, feature
importance (permutation), and a composition heatmap of top candidates."""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from . import models as M
from . import elements as el

plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 130, "font.size": 9,
    "axes.grid": True, "grid.alpha": 0.25, "figure.autolayout": True,
})


def _save(fig, path, name):
    fig.savefig(Path(path) / f"{name}.png", bbox_inches="tight")
    plt.close(fig)


def plot_dataset(df, out):
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.4))
    for ax, (c, lbl) in zip(axes, [("ys_mpa", "Yield strength (MPa)"),
                                   ("uts_mpa", "UTS (MPa)"),
                                   ("elong_pct", "Elongation (%)")]):
        for src, color in [("mendeley_al", "#1f77b4"), ("mpea", "#d62728")]:
            v = pd.to_numeric(df.loc[df["source"] == src, c], errors="coerce").dropna()
            ax.hist(v, bins=35, alpha=0.6, label=src, color=color)
        ax.set_xlabel(lbl); ax.set_ylabel("count"); ax.legend(fontsize=7)
    fig.suptitle("Dataset coverage (real experimental compilations)", y=1.04)
    _save(fig, out, "01_dataset_coverage")


def plot_parity(df, models, out, n=800):
    """GroupKFold out-of-fold parity — recomputed compactly for key targets."""
    from sklearn.model_selection import GroupKFold
    targets = [t for t in ("ys_mpa", "uts_mpa", "elong_pct") if t in models]
    fig, axes = plt.subplots(1, len(targets), figsize=(4 * len(targets), 3.6))
    axes = np.atleast_1d(axes)
    for ax, t in zip(axes, targets):
        y = pd.to_numeric(df[t], errors="coerce")
        sub = df[y.notna()].copy(); y = y[y.notna()].to_numpy(float)
        X, _ = M.assemble_matrix(sub)
        groups = M.composition_groups(sub)
        gkf = GroupKFold(n_splits=5)
        oof = np.full_like(y, np.nan)
        for tr, te in gkf.split(X, y, groups):
            mem = M._members(0)
            for m in mem:
                m.fit(X.iloc[tr].to_numpy(), y[tr])
            oof[te] = np.mean([m.predict(X.iloc[te].to_numpy()) for m in mem], axis=0)
        from sklearn.metrics import r2_score
        r2 = r2_score(y, oof)
        ax.scatter(y, oof, s=6, alpha=0.4, c="#2c7fb8")
        lo, hi = min(y.min(), np.nanmin(oof)), max(y.max(), np.nanmax(oof))
        ax.plot([lo, hi], [lo, hi], "k--", lw=1)
        ax.set_xlabel(f"measured {M.TARGETS.get(t,t)}")
        ax.set_ylabel("predicted (out-of-fold)")
        ax.set_title(f"{t}  R2={r2:.3f}")
    fig.suptitle("Leakage-free cross-validated model parity", y=1.03)
    _save(fig, out, "02_model_parity")


def plot_pareto(pareto, top, out):
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    ax = axes[0]
    sc = ax.scatter(pareto["YS_pred"], pareto["elong_pred"],
                    c=pareto["cost"], s=14, cmap="viridis_r", alpha=0.7)
    ax.scatter(top["YS_pred"], top["elong_pred"], s=40, facecolors="none",
               edgecolors="red", linewidths=1.2, label="top ranked")
    plt.colorbar(sc, ax=ax, label="cost (USD/kg)")
    ax.set_xlabel("Yield strength (MPa)"); ax.set_ylabel("Elongation (%)")
    ax.set_title("Strength vs ductility"); ax.legend(fontsize=7)

    ax = axes[1]
    sc = ax.scatter(pareto["rho_pred"], pareto["specific"],
                    c=pareto["YS_pred"], s=14, cmap="magma", alpha=0.7)
    ax.scatter(top["rho_pred"], top["specific"], s=40, facecolors="none",
               edgecolors="cyan", linewidths=1.2, label="top ranked")
    plt.colorbar(sc, ax=ax, label="YS (MPa)")
    ax.set_xlabel("Density (g/cm^3)"); ax.set_ylabel("Specific strength (MPa/(g/cm^3))")
    ax.set_title("Lightweight trade-off"); ax.legend(fontsize=7)

    ax = axes[2]
    top2 = top.head(12).iloc[::-1]
    lbl = top2.apply(lambda r: "Al" + "".join(
        f"{e}{r[e]*100:.1f}" for e in ["Mg", "Zn", "Cu", "Si", "Mn", "Ti", "Li", "Zr", "Sc"]
        if e in r and r[e] > 0.005), axis=1)
    ax.barh(range(len(top2)), top2["YS_pred"], color="#3182bd")
    ax.set_yticks(range(len(top2))); ax.set_yticklabels(lbl, fontsize=6)
    ax.set_xlabel("Predicted YS (MPa)"); ax.set_title("Top-12 recommended compositions")
    fig.suptitle("Pareto front and recommendations", y=1.04)
    _save(fig, out, "03_pareto_front")


def plot_importance(df, models, out, target="ys_mpa"):
    from sklearn.inspection import permutation_importance
    y = pd.to_numeric(df[target], errors="coerce")
    sub = df[y.notna()].copy(); y = y[y.notna()].to_numpy(float)
    X, cols = M.assemble_matrix(sub)
    m = models[target].members[0]
    r = permutation_importance(m, X.to_numpy(), y, n_repeats=6,
                               random_state=0, n_jobs=-1, scoring="r2")
    order = np.argsort(r.importances_mean)[-20:]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.barh(range(len(order)), r.importances_mean[order],
            xerr=r.importances_std[order], color="#31a354")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([cols[i] for i in order])
    ax.set_xlabel("permutation importance (drop in R2)")
    ax.set_title(f"Feature importance for {M.TARGETS.get(target,target)}")
    _save(fig, out, "04_feature_importance")


def plot_pareto3d(pareto, top, out):
    fig = plt.figure(figsize=(7, 5.5))
    ax = fig.add_subplot(111, projection="3d")
    p = ax.scatter(pareto["YS_pred"], pareto["elong_pred"], pareto["specific"],
                   c=-pareto["cost"], s=12, cmap="viridis", alpha=0.6)
    ax.scatter(top["YS_pred"], top["elong_pred"], top["specific"],
               c="red", s=45, marker="*", label="top")
    ax.set_xlabel("YS (MPa)"); ax.set_ylabel("Elong (%)"); ax.set_zlabel("specific (MPa/rho)")
    ax.set_title("4-objective Pareto front"); ax.legend(fontsize=8)
    _save(fig, out, "05_pareto_3d")


def make_all(df, models, pareto, outdir):
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    plot_dataset(df, outdir)
    plot_parity(df, models, outdir)
    from .design import pareto_front
    top = pareto_front(pareto, {"ys": 0.4, "elo": 0.2, "specific": 0.3, "cost": 0.1}, 30)
    plot_pareto(pareto, top, outdir)
    plot_importance(df, models, outdir)
    plot_pareto3d(pareto, top, outdir)
    print(f"      wrote 5 figures to {outdir}")
