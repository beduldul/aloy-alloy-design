"""Figures for lab protocols, commercial benchmarking, and the loop simulation."""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path

plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.25, "figure.autolayout": True})


def plot_commercial(comp_csv: Path, out: Path):
    df = pd.read_csv(comp_csv)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))

    ax = axes[0]
    colors = ["#d62728" if "handbook" in a else "#1f77b4" for a in df["alloy"]]
    ax.barh(df["alloy"], df["YS"], color=colors)
    for i, (v, e) in enumerate(zip(df["YS"], df["elong"])):
        ax.text(v + 8, i, f"{v:.0f} MPa ({e:.0f}%)", va="center", fontsize=7)
    ax.set_xlabel("Yield strength (MPa)")
    ax.set_title("Predicted candidates vs commercial alloys\n(red = handbook)")
    ax.set_xlim(0, df["YS"].max() * 1.25)

    ax = axes[1]
    ax.scatter(df["cost"], df["specific"], s=90, c=colors, zorder=3)
    for _, r in df.iterrows():
        ax.annotate(r["alloy"].replace(" (handbook)", ""),
                    (r["cost"], r["specific"]), fontsize=6.5,
                    xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("cost (USD/kg)"); ax.set_ylabel("specific strength (MPa/(g/cm^3))")
    ax.set_title("Value map: up-and-left is better")
    fig.suptitle("Benchmarking against commercial aluminium alloys", y=1.03)
    fig.savefig(out / "10_commercial_benchmark.png", bbox_inches="tight")
    plt.close(fig)


def plot_heat_treatment(out: Path):
    """Visualise the T6 thermal cycle."""
    fig, ax = plt.subplots(figsize=(8, 4.2))
    t = [0, 2, 2.3, 23, 25.3, 24 + 12, 60, 62]
    # time axis in hours, temperature profile
    steps = [
        (0, 25, "start"), (0.5, 700, "melt/pour"), (1.5, 25, "solidify"),
        (3.5, 465, "homogenise 465C"), (15.5, 465, ""), (16, 25, "cool"),
        (18, 470, "solutionise 465-475C"), (20, 470, ""), (20.1, 25, "quench"),
        (21, 120, "age T6 120C"), (45, 120, ""), (46, 25, "air cool"),
    ]
    xs = [s[0] for s in steps]; ys = [s[1] for s in steps]
    ax.plot(xs, ys, "-o", color="#1f77b4", ms=4)
    # incipient melting line
    ax.axhline(477, ls="--", c="red", lw=1.2)
    ax.text(30, 490, "477 C incipient melting limit", color="red", fontsize=7)
    ax.axhspan(465, 477, color="green", alpha=0.08)
    # place labels with alternating offsets to avoid collisions
    offs = {"start": (0, -20), "melt/pour": (0, 8), "solidify": (18, -22),
            "homogenise 465C": (0, 10), "cool": (0, -18),
            "solutionise 465-475C": (0, 10), "quench": (0, -18),
            "age T6 120C": (0, 10), "air cool": (0, 10)}
    for x, y, lab in steps:
        if lab:
            ax.annotate(lab, (x, y), fontsize=6.5, xytext=offs.get(lab, (0, 8)),
                        textcoords="offset points", ha="center")
    ax.set_xlabel("time (hours, schematic)"); ax.set_ylabel("temperature (C)")
    ax.set_title("T6 thermal cycle for the recommended Al-Zn-Mg-Cu alloy")
    ax.set_ylim(0, 780)
    fig.savefig(out / "11_heat_treatment.png", bbox_inches="tight")
    plt.close(fig)


def plot_loop(loop_csv: Path, out: Path):
    if not Path(loop_csv).exists():
        return
    df = pd.read_csv(loop_csv)
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for strat, g in df.groupby("strategy"):
        agg = g.groupby("round")["cumulative_best_YS"].agg(["mean", "std"]).reset_index()
        ax.errorbar(agg["round"], agg["mean"], yerr=agg["std"], marker="o",
                    capsize=3, label=strat)
    ax.set_xlabel("experiment round"); ax.set_ylabel("best YS found (MPa)")
    ax.set_title("Closed-loop simulation: active learning vs random screening")
    ax.legend()
    fig.savefig(out / "12_loop_simulation.png", bbox_inches="tight")
    plt.close(fig)


def main():
    out = Path(__file__).resolve().parents[2] / "outputs" / "figures"
    root = Path(__file__).resolve().parents[2] / "outputs"
    plot_commercial(root / "commercial_comparison.csv", out)
    plot_heat_treatment(out)
    plot_loop(root / "loop_simulation.csv", out)
    print("wrote commercial, heat-treatment, and loop figures")


if __name__ == "__main__":
    main()
