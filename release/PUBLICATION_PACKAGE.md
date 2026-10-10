# Publication Package — Ready to Deposit

Everything needed to obtain a citable DOI for this work. Follow the numbered
steps; total time under an hour. **No experiments are required for this release.**

---

## What is being released

| Item | Content | Licence |
|---|---|---|
| Software | 22 Python modules, reproducible pipeline | MIT |
| Derived data | Pareto-optimal Al and Mg candidate lists, benchmark tables | MIT |
| Figures | 16 publication-quality graphs | MIT |
| Docs | Method, data provenance, limitations, manuscript template | MIT |
| Raw inputs | Two published experimental datasets (redistributed) | CC BY 4.0 |

**Archive:** `../aloy-v1.0.0.zip` (62.7 MB, 80 files)
**Integrity:** `MANIFEST.sha256` (SHA-256 of every included file)

---

## The three documents you need, in order

1. **`docs/RELEASE_GUIDE.md`** — the step-by-step Zenodo procedure (steps 0–8).
2. **`CITATION.md`** — how others must cite you, and the required credit to the
   two source datasets.
3. **`docs/MANUSCRIPT_TEMPLATE.md`** — a filled skeleton for the *journal* paper
   you would write **after** you have experimental data.

---

## Abstract for the Zenodo deposit (copy-paste ready)

> Aloy is a reproducible, open-source pipeline for the inverse design of
> low-cost, high-strength aluminium- and magnesium-based alloys from published
> experimental data. It combines (i) domain-disciplined data curation,
> (ii) leakage-free ensemble surrogates, (iii) NSGA-II multi-objective design,
> (iv) Hume-Rothery and CALPHAD phase screening, (v) Bayesian active learning
> with trust regions, and (vi) split-conformal prediction intervals.
>
> For aluminium, it predicts Pareto-optimal Al-Zn-Mg-Cu candidates reaching
> ~620 MPa yield strength at ~2.65 USD/kg, benchmarked against commercial
> AA7075, AA2024 and AA6061. For magnesium, it predicts Mg-Ca-Li candidates
> reaching ~285 MPa at ~1.45 g/cm³, benchmarked against AZ91D, ZK60 and WE43.
> A price-sensitivity analysis shows the value curve saturates below 3 USD/kg,
> i.e. exotic additions (Li, Sc) are not cost-effective for strength.
>
> Every prediction carries an honest error bar (90% conformal interval of
> ±108 MPa for Al yield strength, with 90.1% empirical coverage), and all
> limitations are documented: yield-strength models are reliable (R² ≈ 0.79
> cross-validated) while elongation models are weak (R² ≈ 0.27). **No
> experimental validation is included.** The package is explicitly an
> experiment-prioritisation tool, not a substitute for experiment. It ships
> ready-to-execute laboratory protocols (including magnesium fire-safety
> procedures) and machine-readable candidate lists.
>
> Source experimental data: Bhat, Barnard & Birbilis (2023), DOI
> 10.17632/b6br4yk6r3.1, and Ghorbani & Birbilis (2025), DOI
> 10.17632/2fjhmdg5nt.2, both CC BY 4.0.

---

## Zenodo metadata (copy-paste)

| Field | Value |
|---|---|
| Upload type | Software |
| Title | Aloy: A transparent machine-learning pipeline for inverse design of low-cost, high-strength aluminium and magnesium alloys |
| Authors | Al-Kaysan, Abdul Afif (Institut Teknologi Bandung) |
| Version | 1.0.0 |
| Language | English |
| Licence | MIT (code/data); bundled raw datasets remain CC BY 4.0 |
| Keywords | materials informatics; aluminium alloys; magnesium alloys; multi-objective optimisation; Bayesian optimisation; CALPHAD; alloy design |
| Related — Al source | DOI 10.17632/b6br4yk6r3.1 — "is derived from" |
| Related — Mg source | DOI 10.17632/2fjhmdg5nt.2 — "is derived from" |

---

## Before you click Publish — final checklist

- [x] Pre-flight check passes (`python3 -m aloy.release --check`)
- [x] README states results are predictions, not measurements
- [x] Limitations section is specific and honest
- [x] Both source datasets cited in `CITATION.md`
- [x] MIT (code) vs CC BY 4.0 (data) clearly separated in `LICENSE`
- [x] `MANIFEST.sha256` generated (80 files)
- [ ] Replace every `10.5281/zenodo.XXXXXXX` placeholder **after** publishing
- [ ] (Optional) Connect GitHub repo so Zenodo archives the exact commit

## Add a DOI badge to the README after publishing

Replace the placeholder with your real DOI, then paste near the top of `README.md`:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```
