"""Figures for the magnesium design track."""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.25, "figure.autolayout": True})

OUT = Path(__file__).resolve().parents[2] / "outputs"
FIG = OUT / "figures"

# handbook reference values for commercial Mg alloys
MG_COMMERCIAL = {
    "AZ91D": {"YS": 150, "rho": 1.81, "elong": 3.0, "cost": 2.5},
    "AM60":  {"YS": 130, "rho": 1.80, "elong": 8.0, "cost": 2.5},
    "ZK60":  {"YS": 250, "rho": 1.83, "elong": 11.0, "cost": 3.5},
    "WE43":  {"YS": 200, "rho": 1.84, "elong": 7.0, "cost": 12.0},
    "Mg-Li (LA141)": {"YS": 130, "rho": 1.35, "elong": 12.0, "cost": 15.0},
}


def plot_mg_landscape(out=FIG):
    """Density vs strength map: Mg vs Al vs commercial references."""
    from . import mg as MG
    from . import models as AM
    df_mg = MG.load_mg()
    df_al = AM.load_all()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df_al["rho_rule"], pd.to_numeric(df_al["ys_mpa"], errors="coerce"),
               s=8, alpha=0.25, c="#1f77b4", label="Al alloys (training)")
    ax.scatter(df_mg["rho_rule"], df_mg["ys_mpa"], s=8, alpha=0.3, c="#d62728",
               label="Mg alloys (training)")
    for name, v in MG_COMMERCIAL.items():
        ax.scatter(v["rho"], v["YS"], s=70, marker="s", facecolors="none",
                   edgecolors="k", linewidths=1.3)
        ax.annotate(name, (v["rho"], v["YS"]), fontsize=6.5,
                    xytext=(4, -8), textcoords="offset points")

    cand = pd.read_csv(OUT / "mg_pareto.csv")
    top = cand.sort_values("specific", ascending=False).head(20)
    ax.scatter(top["rho_pred"], top["YS_pred"], s=45, marker="*",
               c="gold", edgecolors="k", linewidths=0.5, label="Mg candidates (top)")

    ax.set_xlabel("density (g/cm^3)"); ax.set_ylabel("yield strength (MPa)")
    ax.set_title("Lightweight-structural map: Mg sits far to the left of Al")
    ax.legend(fontsize=7, loc="upper left")
    fig.savefig(out / "13_mg_landscape.png", bbox_inches="tight")
    plt.close(fig)


def plot_mg_specific(out=FIG):
    """Specific strength comparison, Mg candidates vs commercial."""
    cand = pd.read_csv(OUT / "mg_pareto.csv")
    cand = cand[(cand["elong_pred"] > 5) & (cand["rho_pred"] < 1.9)]
    top = cand.sort_values("specific", ascending=False).head(10)
    labels = []
    for _, r in top.iterrows():
        comp = "Mg" + "".join(f"-{e}{r[e]*100:.1f}" for e in
                              ["Al", "Zn", "Ca", "Y", "Li", "Nd", "Gd"]
                              if e in r and r[e] > 0.005)
        labels.append(comp)
    ref = {k: v["YS"] / v["rho"] for k, v in MG_COMMERCIAL.items()}

    fig, ax = plt.subplots(figsize=(9, 4.5))
    y = np.arange(len(top))
    ax.barh(y, top["specific"].values, color="#2ca02c", label="candidates (model)")
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=7)
    for k, v in ref.items():
        ax.axvline(v, ls="--", lw=1, alpha=0.7)
        ax.text(v + 1, len(top) - 0.5, k, fontsize=6, rotation=90, va="top")
    ax.set_xlabel("specific strength (MPa/(g/cm^3))")
    ax.set_title("Mg candidates vs commercial Mg alloys (dashed = handbook)")
    ax.legend(fontsize=8)
    fig.savefig(out / "14_mg_specific.png", bbox_inches="tight")
    plt.close(fig)


def plot_mg_parity(out=FIG):
    """Cross-validated parity for the Mg models."""
    from sklearn.model_selection import GroupKFold
    from sklearn.metrics import r2_score
    from . import mg as MG, mg_models as MM
    df = MG.load_mg()
    targets = ["ys_mpa", "uts_mpa", "elong_pct"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    for ax, t in zip(axes, targets):
        y = pd.to_numeric(df[t], errors="coerce")
        sub = df[y.notna()]; yv = y[y.notna()].to_numpy(float)
        X, _ = MM.assemble(sub)
        oof = np.full_like(yv, np.nan)
        for tr, te in GroupKFold(n_splits=5).split(X, yv, MM._groups(sub)):
            mem = MM._members(0)
            for m in mem:
                m.fit(X.iloc[tr].to_numpy(), yv[tr])
            oof[te] = np.mean([m.predict(X.iloc[te].to_numpy()) for m in mem], 0)
        ax.scatter(yv, oof, s=6, alpha=0.4, c="#d62728")
        lo, hi = min(yv.min(), np.nanmin(oof)), max(yv.max(), np.nanmax(oof))
        ax.plot([lo, hi], [lo, hi], "k--", lw=1)
        ax.set_xlabel(f"measured {t}"); ax.set_ylabel("predicted (OOF)")
        ax.set_title(f"Mg {t}  R2={r2_score(yv, oof):.3f}")
    fig.suptitle("Magnesium model parity (leakage-free 5-fold)", y=1.03)
    fig.savefig(out / "15_mg_parity.png", bbox_inches="tight")
    plt.close(fig)


def plot_mg_value(out=FIG):
    """The honest trade-off: specific strength vs cost for Mg candidates."""
    cand = pd.read_csv(OUT / "mg_pareto.csv")
    fig, ax = plt.subplots(figsize=(7.5, 5))
    sc = ax.scatter(cand["cost"], cand["specific"], c=cand["YS_pred"],
                    s=28, cmap="viridis", alpha=0.85)
    plt.colorbar(sc, ax=ax, label="predicted YS (MPa)")
    ref = {k: (v["cost"], v["YS"] / v["rho"]) for k, v in MG_COMMERCIAL.items()}
    for name, (cost, spec) in ref.items():
        ax.scatter(cost, spec, marker="s", s=70, facecolors="none",
                   edgecolors="red", linewidths=1.4)
        ax.annotate(name, (cost, spec), fontsize=6.5, color="red",
                    xytext=(4, -9), textcoords="offset points")
    ax.set_xlabel("raw-material cost (USD/kg)")
    ax.set_ylabel("specific strength (MPa/(g/cm^3))")
    ax.set_title("Mg value map: model candidates vs commercial Mg alloys")
    fig.savefig(out / "16_mg_value.png", bbox_inches="tight")
    plt.close(fig)


def main():
    plot_mg_landscape()
    plot_mg_specific()
    plot_mg_parity()
    plot_mg_value()
    print("wrote 4 Mg figures")


if __name__ == "__main__":
    main()
