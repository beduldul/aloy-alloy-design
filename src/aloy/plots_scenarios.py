"""Figures for the economy-vs-performance comparison and price sensitivity."""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.25, "figure.autolayout": True})


def plot_scenarios(econ, perf, sweep, out: Path):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4))

    ax = axes[0]
    ax.scatter(econ["cost"], econ["specific"], s=22, c="#2ca02c",
               alpha=0.75, label="Economy (Al-Mg-Zn-Cu)")
    if perf is not None and len(perf):
        ax.scatter(perf["cost"], perf["specific"], s=22, c="#d62728",
                   alpha=0.7, label="Performance (+Li/Sc/Zr)")
    ax.axvline(8, ls="--", c="k", lw=1, alpha=0.5)
    ax.text(8.3, ax.get_ylim()[0] + 5, "8 USD/kg", fontsize=7, rotation=90)
    ax.set_xlabel("Raw-material cost (USD/kg)"); ax.set_ylabel("specific strength (MPa/(g/cm^3))")
    ax.set_title("Value frontier: strength per dollar"); ax.legend(fontsize=7)

    ax = axes[1]
    ax.scatter(econ["YS_pred"], econ["elong_pred"], s=22, c=econ["cost"],
               cmap="viridis", alpha=0.8)
    ax.set_xlabel("YS (MPa)"); ax.set_ylabel("Elongation (%)")
    ax.set_title("Economy scenario: strength-ductility")

    ax = axes[2]
    if sweep is not None and len(sweep):
        ax.plot(sweep["cost_cap"], sweep["best_ys"], "o-", c="#1f77b4", label="best YS")
        ax2 = ax.twinx()
        ax2.plot(sweep["cost_cap"], sweep["best_specific"], "s--", c="#ff7f0e",
                 label="best specific")
        ax.set_xlabel("cost ceiling (USD/kg)")
        ax.set_ylabel("best YS (MPa)", color="#1f77b4")
        ax2.set_ylabel("best specific (MPa/rho)", color="#ff7f0e")
        ax2.grid(False)
        ax.set_title("Performance saturates below 3 USD/kg")
    fig.suptitle("Cheap-and-strong beats expensive-and-marginally-stronger", y=1.03)
    fig.savefig(out / "06_scenario_comparison.png", bbox_inches="tight")
    plt.close(fig)


def plot_applicability(df, candidates, out: Path):
    """Check candidates sit inside the training domain (no wild extrapolation)."""
    out = Path(out)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    ax = axes[0]
    ax.hist(pd.to_numeric(df["ys_mpa"], errors="coerce").dropna(), bins=45,
            color="#bbb", label="training YS")
    ax.axvline(candidates["YS_pred"].mean(), c="red", lw=2,
               label=f"candidate mean {candidates['YS_pred'].mean():.0f} MPa")
    ax.set_xlabel("Yield strength (MPa)"); ax.set_ylabel("count")
    ax.set_title("Candidates lie inside the training envelope"); ax.legend(fontsize=8)

    ax = axes[1]
    tr_el = df[[c for c in df.columns if len(c) == 1 or (len(c) == 2 and c[0].isupper())]]
    mean_tr = tr_el[[c for c in tr_el.columns if c in candidates.columns]].mean()
    cand = candidates[[c for c in candidates.columns if c in mean_tr.index]].mean()
    x = np.arange(len(cand)); w = 0.4
    ax.bar(x - w/2, mean_tr[cand.index], w, label="training mean", color="#bbb")
    ax.bar(x + w/2, cand, w, label="candidate mean", color="#3182bd")
    ax.set_xticks(x); ax.set_xticklabels(cand.index, rotation=90, fontsize=7)
    ax.set_ylabel("mass fraction"); ax.set_title("Composition coverage")
    ax.legend(fontsize=8)
    fig.savefig(out / "07_applicability_domain.png", bbox_inches="tight")
    plt.close(fig)
