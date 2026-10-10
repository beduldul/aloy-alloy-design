# Manuscript Template — *Journal of Alloys and Compounds* short communication

> **How to use this file.** This is a filled-in skeleton based on the work that
> already exists. Every place marked `[[ FILL: ... ]]` requires you to insert a
> real number or a decision. Do NOT submit it while any bracket remains. If you
> have no experimental data yet, this manuscript is not ready — use it as a plan,
> not as a draft to submit.

---

**Title**

Machine-learning-guided inverse design of low-cost, high-strength Al–Zn–Mg–Cu and
Mg–Ca–Li alloys with explicit uncertainty quantification and phase screening

**Authors**

Abdul Afif Al-Kaysan¹, [[ FILL: supervisor name and affiliation if applicable ]]

¹ Metallurgical Engineering, Institut Teknologi Bandung, Indonesia

**Corresponding author:** [[ FILL: email ]]

---

## Abstract

We present a reproducible pipeline for the inverse design of low-cost,
high-strength aluminium- and magnesium-based alloys from published experimental
data. The pipeline couples leakage-free ensemble surrogates, NSGA-II
multi-objective optimisation, Hume-Rothery and CALPHAD phase screening, Bayesian
active learning, and split-conformal prediction intervals. For the Al–Zn–Mg–Cu
system, the model predicts a Pareto-optimal candidate
(Al–3.0Mg–7.8Zn–1.3Cu, wt%) with a yield strength of [[ FILL: measured or predicted
value ]] MPa [[ FILL: ± interval ]] at an estimated raw-material cost of
2.66 USD kg⁻¹, compared with a cross-validated model R² of 0.79 (MAE 53 MPa). For
the Mg–Ca–Li system, candidates reach [[ FILL ]] MPa at 1.45 g cm⁻³. A
price-sensitivity analysis shows saturated returns above ~3 USD kg⁻¹, indicating
that exotic alloying additions are not cost-effective for strength. We report an
honest 90% conformal interval of ±108 MPa with 90.1% empirical coverage, and we
demonstrate that mixing multi-principal-element alloys into an Al-alloy training
set inflates error threefold — a domain-discipline lesson for materials
informatics. **[[ FILL: if experimental validation exists, replace the following
sentence — otherwise delete the manuscript ]] Experimental validation on
[N] cast and heat-treated specimens gave a mean absolute deviation of
[ X ]% between predicted and measured yield strength.**

**Keywords:** aluminium alloys; magnesium alloys; machine learning; alloy design;
multi-objective optimisation; CALPHAD

---

## 1. Introduction

Lightweight structural alloys are central to transport decarbonisation. The
search space of multi-component compositions is far too large for exhaustive
experimental screening, motivating *materials informatics* approaches that
prioritise candidate compositions for costly experiments [ref].

Two failure modes recur in this literature and motivate the present work. First,
**domain contamination**: models trained on pooled datasets that mix chemically
and mechanically distinct material classes produce physically impossible
predictions for the target class. Second, **unquantified prediction error**:
point predictions without honest intervals are unusable for experimental
prioritisation. We describe a pipeline that addresses both explicitly, and apply
it to two lightweight base systems, Al and Mg. [[ FILL: tighten to 2 paragraphs ]]

## 2. Data

### 2.1 Sources

Two open experimental compilations supply the ground truth:
Al alloys from Bhat, Barnard & Birbilis (2023) (DOI 10.17632/b6br4yk6r3.1;
~1150 records) and Mg alloys from Ghorbani & Birbilis (2025)
(DOI 10.17632/2fjhmdg5nt.2; 916 records). Both are CC BY 4.0.

### 2.2 Domain discipline

The Al training set was restricted to compositions with Al ≥ 50 wt%. Without
this filter the pooled set (including the Citrine MPEA corpus,
DOI 10.6084/m9.figshare.12642953) has a median Al fraction of 0.08 and contains
yield strengths up to 3416 MPa from a different material class; the surrogate
then predicted up to ~1700 MPa for Al alloys and its cross-validated MAE
deteriorated from 53 to 160 MPa. This filter changes the record count from 2696
to 1158 and is reported explicitly for reproducibility.

### 2.3 Features

Composition plus physics-derived descriptors: atomic-size mismatch (Hume-Rothery
δr), electronegativity difference (Δχ), valence electron concentration (VEC), the
thermodynamic Ω parameter, mixing entropy, rule-of-mixtures density, a
rare-earth fraction (for Mg), and a numerical encoding of the processing route.

## 3. Methods

### 3.1 Surrogate models

Per-property ensembles of histogram gradient boosting, random forest and
extremely randomised trees. Model selection uses **GroupKFold grouped by
composition** so that near-duplicate alloys cannot leak between train and test.
Ensemble spread provides an epistemic-uncertainty proxy.

### 3.2 Multi-objective design

NSGA-II optimises yield strength, ductility, specific strength and cost (Al) or
yield strength, ductility, specific strength, density and cost (Mg), subject to a
Hume-Rothery size criterion and, for Mg, **data-driven trust-region bounds**:
each element is capped at the level supported by ≥30 experimental records,
preventing the optimiser from exploiting single-outlier compositions.

### 3.3 Phase screening

A calibrated intermetallic-excess metric, cross-checked against pycalphad
equilibrium calculations where a database is available. The metric was validated
by confirming that commercial AA7075 and AA2024 are classified "medium risk"
(consistent with their fine strengthening precipitates) rather than rejected.

### 3.4 Active learning

A Gaussian-process surrogate with qLogNoisyExpectedImprovement acquisition and a
trust region selects successive experimental batches.

### 3.5 Uncertainty quantification

Split-conformal prediction provides distribution-free, finite-sample-valid
intervals; empirical coverage is verified on a held-out fold.

## 4. Results

### 4.1 Candidate alloys

Table 1. Predicted Pareto-optimal candidates. [[ FILL: choose final table; state
clearly these are predictions, and add a column for measured values if available ]]

### 4.2 Benchmarking against commercial alloys

[[ FILL: reproduce values from outputs/commercial_comparison.csv and
outputs/mg_commercial_comparison.csv. Verify the handbook values against a
primary source (e.g. ASM Handbook Vol. 2) before submission. ]]

### 4.3 Cost sensitivity

Sweeping a cost ceiling from 3 to 12 USD kg⁻¹ changed the best achievable yield
strength by only ~1%, demonstrating saturation.

### 4.4 Active-learning assessment

In a closed-loop simulation the surrogate-guided strategy exceeded random
selection by only 1.3% once seeded with 40 alloys. We report this *negative*
result deliberately: active learning confers little benefit when the initial
surrogate is already well-constrained. [[ FILL: keep — reviewers value this ]]

## 5. Discussion

[[ FILL: 2–3 paragraphs. Key points to make: (a) the Al candidates are chemically
consistent with the 7xxx family and their computed density (2.798 g cm⁻³ for the
7075 composition) agrees with the handbook value (2.81 g cm⁻³), supporting the
feature construction; (b) elongation predictions are weak (R² ≈ 0.27) because
texture and defects are absent from the input; (c) the approach is an
experiment-prioritisation tool. ]]

## 6. Limitations

1. No experimental validation is included in the current release. [[ FILL:
   delete once you add data ]]
2. Yield-strength models are reliable (R² ≈ 0.79, Al); elongation models are weak
   (R² ≈ 0.27).
3. CALPHAD usage is screening, not a full thermodynamic assessment.
4. Material costs are indicative market estimates, not procurement quotes.
5. No creep or corrosion data are modelled.

## 7. Conclusion

A transparent, reproducible pipeline prioritises low-cost, high-strength Al- and
Mg-based alloy candidates with honest uncertainty. The dominant practical finding
is that exotic additions are unnecessary for strength: performance saturates
below ~3 USD kg⁻¹. Future work will experimentally validate the leading
candidates and feed measurements back into the active-learning loop.

## Data and code availability

Software, derived candidate data and documentation are archived at
https://doi.org/10.5281/zenodo.22844739 under an MIT licence (code); bundled raw
datasets remain CC BY 4.0 with attribution to their original authors.

## CRediT author contributions

[[ FILL: Conceptualisation, Methodology, Software, Validation, Writing — original
draft, Supervision, etc. ]]

## Declaration of competing interest

The authors declare no competing interests.

## References

[[ FILL: 25–40 references. Must include both source datasets, ASM Handbook,
pymoo, BoTorch, pycalphad, and 15–25 recent (last 5 years) papers on
ML-guided alloy design. Use the journal's reference style. ]]
