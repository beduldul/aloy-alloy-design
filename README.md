# Aloy — Machine-learning inverse design of low-cost, high-strength aluminium and magnesium alloys

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22844739.svg)](https://doi.org/10.5281/zenodo.22844739)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/beduldul/aloy-alloy-design/actions/workflows/ci.yml/badge.svg)](https://github.com/beduldul/aloy-alloy-design/actions/workflows/ci.yml)

Aloy is a transparent research pipeline that turns two open experimental alloy datasets
into Pareto-optimal candidate compositions — surrogate ML models, NSGA-II multi-objective
inverse design, CALPHAD/Hume-Rothery phase screening, Bayesian active learning, and
split-conformal prediction intervals.

## The finding (and its honesty)

The pipeline predicts a Pareto front of **Al–Zn–Mg–Cu (7xxx-class) candidates reaching
~620 MPa yield strength at ~2.65 USD/kg** — benchmarked against AA7075-T6, AA2024-T4 and
AA6061-T6 — with a **90% split-conformal interval of ±108 MPa** (empirical coverage
90.1%) on every yield-strength prediction.

**None of these predictions has been experimentally validated.** The candidate compositions
exist only as model outputs. The project is explicitly an *experiment-prioritisation tool*,
not a substitute for experiment: yield-strength models are reliable (R² ≈ 0.79
cross-validated), elongation models are weak (R² ≈ 0.27), and the top-candidate prediction
(625 MPa) sits above real AA7075-T6 (503 MPa), which itself is a reason for suspicion until
a melt exists. This honesty is deliberate and is the project's core claim — see
[Limitations](#limitations).

A secondary branch (Magnesium, `mg_*.py`) predicts Mg–Ca–Li candidates reaching
~285 MPa at 1.45 g/cm³, benchmarked against AZ91D, ZK60 and WE43 — likewise unvalidated.

## Pipeline overview

```
public experimental data ──► domain-disciplined curation ──► ensemble surrogates
 (Mendeley CC BY 4.0)         (leakage-free GroupKFold)      (HGB/RF/ET)
        │
        ▼
 NSGA-II multi-objective ──► Hume-Rothery + CALPHAD ──► Bayesian active learning
 inverse design              phase screening             (BoTorch qLogNEI, trust region)
        │
        ▼
 conformal prediction intervals ──► lab protocols ──► experiment log (closed loop)
```

Key domain decision: the Citrine MPEA corpus is dominated by heavy refractory alloys
(median Al fraction 0.08; yield strengths up to 3416 MPa). The pipeline keeps only
**Al ≥ 50 wt%** (7 of 1545 rows retained). This one filter drops the maximum yield
strength in the training data from 3416 → 790 MPa and improves MAE from 160 → 53 MPa —
evidence that domain discipline matters more than model tricks.

## Data & provenance

| Source | Content | Used |
|---|---|---|
| Mendeley — Bhat, Barnard & Birbilis (2023), DOI `10.17632/b6br4yk6r3.1` (CC BY 4.0) | compositions, processing, YS/UTS/elongation of Al alloys | 1151 |
| Mendeley — Ghorbani & Birbilis (2025), DOI `10.17632/2fjhmdg5nt.2` (CC BY 4.0) | 916 Mg alloys, full compositions + properties | 916 |
| Citrine MPEA — Borg et al. (2020), DOI `10.6084/m9.figshare.12642953` (Apache-2.0/Figshare) | multi-principal-element alloys | 7 (after Al-filter) |

Raw files live in `data/raw/` and are redistributed under CC BY 4.0 with attribution
preserved. **Full provenance — sources, licences, sha256 checksums, and the exact
processing applied to every dataset — is recorded in
[`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).** The software is MIT-licensed.

## Install & quickstart

```bash
git clone https://github.com/beduldul/aloy-alloy-design.git
cd aloy-alloy-design
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Python 3.12. Dependencies: numpy, pandas, scipy, scikit-learn, matplotlib, joblib,
openpyxl, pymoo (NSGA-II), pycalphad (phase screening), botorch/torch (active learning).

## Reproduce results

Every module runs standalone with deterministic seeds (0/1/42/99, documented per module):

```bash
PYTHONPATH=src python3 -m aloy.verify          # holdout metrics + physics screening (fast)
PYTHONPATH=src python3 -m aloy.pipeline        # full end-to-end pipeline (~80 s)
PYTHONPATH=src python3 -m aloy.scenarios       # economy vs performance + price sweep
PYTHONPATH=src python3 -m aloy.calphad_check   # CALPHAD phase screening
PYTHONPATH=src python3 -m aloy.credibility     # conformal intervals + cost metrics
PYTHONPATH=src python3 -m aloy.protocol        # Al lab protocol + commercial benchmark
PYTHONPATH=src python3 -m aloy.loop_sim        # closed-loop experiment simulation
# magnesium branch
PYTHONPATH=src python3 -m aloy.mg_models && PYTHONPATH=src python3 -m aloy.mg_design
```

`outputs/` contains the committed CSV results (Pareto fronts, candidate lists, protocols,
figures) so the headline numbers can be inspected without retraining. The trained model
artefacts (`outputs/models*/`) are **not** committed — retrain them with the commands above.

The detailed research report is in [`REPORT.md`](REPORT.md) (Bahasa Indonesia).

## Tests & verification

```bash
PYTHONPATH=src python3 -m pytest tests/ -v
```

The test suite guards the experiment-log tooling; its central invariant is that the 15
pre-existing records in `outputs/experiment_log.json` survive every operation untouched
(each record's sha256 is re-checked). Runs in about one second.

## Lab protocols

**Governing document: [`docs/PROTOCOL_CORRECTED.md`](docs/PROTOCOL_CORRECTED.md)** — where
it disagrees with anything else, it wins. It supersedes the frozen release artefacts
(`outputs/lab_protocols.*`, `outputs/mg_lab_protocols.*`).

⚠️ [`docs/EXPERIMENTAL_DESIGN.md`](docs/EXPERIMENTAL_DESIGN.md) contains an
**[Erratum](docs/EXPERIMENTAL_DESIGN.md#erratum-added-2026-10-06) at the end that
retracts two claims in its body** (the charge-arithmetic item in §11 among them). Read the
body together with the Erratum; a reader of the body alone would take away a wrong impression.

The Mg protocol puts fire safety first: molten magnesium burns in air; cover gas
(SF₆/CO₂) or flux is mandatory, never use water, preheat all tools above 150 °C.

## Limitations

1. **No experimental validation of any prediction.** The 625 MPa candidate must be melted
   and tensile-tested (ASTM E8) before it can be believed; the conformal interval for it is
   [519, 735] MPa.
2. **Elongation models are weak** (R² ≈ 0.21–0.27) — defects and microstructure are not
   captured by composition alone.
3. Elemental costs are **indicative market estimates**, not supplier quotes.
4. CALPHAD here is **screening, not full assessment** — a commercial database
   (Thermo-Calc/COST 507) is still required for final design.
5. No creep or corrosion data (NIMS requires registration).
6. In the closed-loop simulation, the active-learning advantage over random search was
   **small** (+1.3%) because the initial seed set was already near-optimal — reported as
   found, not as a claim.
7. This is an **experiment-prioritisation tool, not a substitute for experiment**.

## Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the full re-scoped plan. In brief:
(1) melt one Al candidate (Al–3.0Mg–7.8Zn–1.3Cu) and one Mg candidate, tensile-test
(ASTM E8), record results in `outputs/experiment_log.json`, and run the closed loop;
(2) plug a full CALPHAD database for quantitative precipitate fractions;
(3) add creep/corrosion and elevated-temperature properties; (4) write the
short communication once validation data exists (a negative result is still publishable
and valuable).

## Citation

Software/citation metadata: [`CITATION.cff`](CITATION.cff) (GitHub renders this as a
"Cite this repository" button).

> Al Kaysan, A. A. (2026). *Aloy: A transparent machine-learning pipeline for inverse
> design of low-cost, high-strength aluminium and magnesium alloys* (Version 1.0.0)
> [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.22844739

Source datasets: Bhat, Barnard & Birbilis (2023), DOI `10.17632/b6br4yk6r3.1`; Ghorbani &
Birbilis (2025), DOI `10.17632/2fjhmdg5nt.2` — both CC BY 4.0.

## License

MIT — see [`LICENSE`](LICENSE). The redistributed datasets in `data/raw/` remain under
their original CC BY 4.0 licences with attribution as recorded in
[`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).
