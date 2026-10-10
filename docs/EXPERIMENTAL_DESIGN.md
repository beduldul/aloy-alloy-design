# Experimental Design: Validation of the Al–3.0Mg–7.8Zn–1.3Cu Prediction

**Project:** *Aloy* — machine-learning inverse design of low-cost, high-strength Al alloys
**Software DOI:** [10.5281/zenodo.22844739](https://doi.org/10.5281/zenodo.22844739)
**Document status:** design only — no experimental data exists yet
**Author:** Abdul Afif Al-Kaysan, Metallurgical Engineering, Institut Teknologi Bandung
**Date:** 2026-10-06

---

## 0. How to read this document

This is an experimental **design**, not a proposal and not a manuscript. Every number
below is either (a) derived here from a stated formula, (b) read out of the *Aloy*
release, or (c) cited with a URL. Anything I could not verify is labelled
**[ASSUMPTION]** in bold. Section 11 lists the items that **must be confirmed with the
ITB laboratories before any of this is scheduled** — I do not assume access to any
equipment.

The central honest conclusion, stated up front: **the experiment as originally
conceived (cast one heat of the ML candidate, pull three bars, compare with 625 MPa)
cannot test the claim the project makes.** It measures one heat, at one processing
route, with no control, and the processing route it uses is outside the training
distribution of the model. Sections 3–5 rebuild the design so that *every* outcome —
high, low, or in-between — is interpretable.

---

## 1. The falsifiable hypothesis

### 1.1 What the model actually claims

The *Aloy* release reports, for candidate 2 (Al–3.0Mg–7.8Zn–1.3Cu, wt%):

| Quantity | Value | Source |
|---|---|---|
| Point prediction, yield strength (YS) | 625 MPa | `outputs/candidates_final.csv` (row 121: 624.5 MPa) |
| Split-conformal 90% interval | [517, 732] MPa | `outputs/lab_protocols.txt` §7; `outputs/credibility_report.json` |
| Conformal half-width | 107.5 MPa | `credibility_report.json` → `q_halfwidth` |
| Calibration-set size | n = 696 | `credibility_report.json` → `n_cal` |
| Empirical coverage | 90.1% (nominal 90%) | `credibility_report.json` → `coverage_val` |
| Model error, YS | R² 0.79 (CV) / 0.746 (holdout), MAE 53 / 57 MPa, RMSE 70.5 MPa | `REPORT.md` §3.2; `outputs/holdout_report.json` |

The interval [517, 732] is a **distribution-free, finite-sample-valid** statement about
the *conditional distribution of measured YS given the feature vector*, calibrated on
696 held-out records. It is the object the experiment should test.

### 1.2 The hypothesis

> **H1 (primary).** A single commercial-quality cast + homogenised + solution-treated +
> T6-aged heat of nominal composition Al–3.0Mg–7.8Zn–1.3Cu (wt%), tested to ASTM E8
> with n ≥ 3 specimens, yields a **mean 0.2%-offset yield strength inside [517, 732] MPa**.

This is deliberately weaker than "the alloy reaches 625 MPa." The interval is the
honest claim; 625 MPa is only the centre.

Because the model's own MAE (53–57 MPa) is *half* the conformal half-width, a design
that can only resolve ±60 MPa is already adequate to test H1. That is a crucial and
favourable fact: **testing the interval is much cheaper than testing the point
prediction.**

### 1.3 Confirm / disconfirm / uninformative

Let μ be the true mean YS of the *population of heats* produced by the protocol, and
let [L, U] be the 95% CI on μ from this experiment.

| Outcome | Interpretation |
|---|---|
| **Confirms** — L > 517 MPa and U < 732 MPa | The conformal interval is supported. The pipeline's uncertainty quantification is validated on a genuine out-of-sample material. This is the *most valuable* outcome because it validates the method, not just the alloy. |
| **Confirms (weaker)** — point estimate inside [517, 732], CI overlaps one bound | Consistent with H1; report the interval honestly, do not claim the bound was excluded. |
| **Disconfirms (overshoot)** — U < 517 MPa | The model **over-predicted** by more than its own stated uncertainty. This is a *calibration failure*, not merely an accuracy miss, and is the Li et al. failure mode reproduced. Highly publishable as a negative result (§8). |
| **Disconfirms (undershoot)** — L > 732 MPa | The alloy is *stronger* than predicted. Under the project's own framing this is a "success" for the alloy but a **failure for the conformal claim**, because the interval did not cover. It must be reported as a coverage violation, not as a triumph. |
| **Uninformative** — CI spans a bound (e.g. [480, 610]) | **No conclusion about the interval can be drawn.** This is the outcome to design *against*, because it wastes the entire experimental campaign. See §4. |
| **Uninformative** — porosity/defect-dominated scatter, CV > 10% | The measured strength reflects casting quality, not alloy design. Cannot be attributed to composition or to the model. |
| **Uninformative** — unexpected primary phases in XRD | If the alloy is not single-phase fcc + fine precipitates, the surrogate (trained on wrought microstructures) was never applicable and the comparison is void. Report the microstructure finding instead. |

**Design principle: every cell above is a publishable or at least reportable outcome.**
There is no branch that produces "nothing to say."

### 1.4 The confound that must be named in the hypothesis

H1 as written confounds two things: the **composition** and the **processing route**.
Because the candidate composition is not novel (§2), any measured strength difference
is attributable to the route as much as to the composition. Section 4 therefore adds a
**secondary hypothesis** that separates them.

> **H2 (secondary).** For the fixed candidate composition, the *measured* mean YS
> differs from the model's prediction by more than the model's own MAE, and the
> direction of the difference is consistent with the processing-route gap between the
> model's training distribution and this experiment.

H2 is what makes a negative result informative rather than merely disappointing.

---

## 2. Composition strategy — and the novelty problem

### 2.1 Is the composition novel? No — and the honest framing matters

I checked the candidate against the registered composition limits of the two nearest
commercial alloys:

| Element (wt%) | **Candidate 2** | AA7075 limits | AA7055 limits |
|---|---|---|---|
| Zn | **7.80** | 5.1–6.1 | 7.6–8.4 |
| Mg | **3.02** | 2.1–2.9 | 1.8–2.3 |
| Cu | **1.33** | 1.2–2.0 | 2.0–2.6 |
| Zn+Mg+Cu total | **12.2** | 9.7 | 12.4 |

*AA7075/AA7055 registered limits: Aluminium Association "International Alloy
Designations and Chemical Composition Limits for Wrought Aluminum and Wrought Aluminum
Alloys" (2009), as tabulated by Li et al., Commun. Mater. 1:73 (2020),
[10.1038/s43246-020-00074-2](https://doi.org/10.1038/s43246-020-00074-2), Table 3.*

**Verdict.** The candidate's Zn (7.80) sits squarely **inside the AA7055 window**; its
total alloying level (12.2 wt%) is essentially identical to AA7055 (12.4 wt%). It is
**marginally outside AA7075 in Mg** (3.02 vs. max 2.9). It is therefore *not* a novel
composition in any meaningful sense — it is a high-Zn 7xxx alloy in the 7055/7050
neighbourhood with a slightly elevated Mg level.

Two consequences:

1. **Novelty cannot come from the composition.** Any paper that claims "a new alloy"
   on the strength of this composition will be rejected by a competent referee who
   knows the 7xxx family. The defensible novelty is the **transparent pipeline +
   honest uncertainty quantification + the validation result**, whatever that result is.
2. **A known-good reference exists**, which is a gift: it converts an uninterpretable
   measurement into a calibrated one.

### 2.2 Decision: cast **both** the ML candidate **and** a commercial 7075 reference

I recommend casting **both**, and I recommend the reference be **AA7075 wrought
stock** (not a re-cast 7075), for the following reasons:

**Why not candidate-only.** With no reference, a measured 480 MPa has three
indistinguishable explanations: (i) the model over-predicted; (ii) the student's
casting process is poor (porosity, segregation, quench delay); (iii) the heat treatment
was off-spec. The experiment would be uninformative exactly when it matters most —
i.e. when the answer is "low." This is the single largest design risk.

**Why not reference-only.** Pointless — it tests nothing about the model.

**Why both, and why a wrought reference rather than a re-cast one.** The reference has
one job: to prove the **tensile-testing chain** (specimen machining, alignment,
extensometry, machine calibration) is trustworthy. A re-cast 7075 would inherit the
same casting defects as the candidate and would therefore not separate "bad alloy" from
"bad casting." Commercial 7075-T6 wrought bar is a certified material with a documented
minimum YS (ASM/MatWeb lists ≈ 503 MPa typical YS for 7075-T6;
[MatWeb AA7075-T6](https://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA7075T6);
see also [Kaiser Aluminum 7075 rod & bar technical data](https://online.kaiseraluminum.com/depot/PublicProductInformation/Document/1028/Kaiser_Aluminum_7075_Rod_and_Bar.pdf)).
If the reference tests at 503 ± 30 MPa on the same machine, the chain is good, and any
candidate shortfall is real. If the reference itself tests at 440 MPa, **stop and fix
the machine before drawing any conclusion.**

**Trade-off acknowledged.** The reference costs money (buying certified 7075-T6 bar)
and consumes machining and machine time. That cost is small relative to the cost of an
uninterpretable result. The trade-off is worth it.

### 2.3 A third arm, if budget allows: the "same-route 7075" arm

The strongest design adds a **third** arm: a *cast* 7075-composition heat put through
**the identical route** as the candidate. This isolates the composition effect from the
process effect, and is the direct experimental realisation of H2. It is the arm that
would let the student say "the ML candidate outperforms a same-route 7075 by X MPa" —
a genuinely novel and defensible claim. It is optional in §10 (reduced design) because
it costs one more melt.

---

## 3. What varies, what is held fixed — and why the ML should be re-pointed at process

### 3.1 The lesson from the two precedents, applied

**Jiang et al. (2023)** — [10.1038/s41524-023-00979-9](https://doi.org/10.1038/s41524-023-00979-9)
— transferred 1053 process–property records of *commercial AA7xxx* alloys to design a
**three-stage solution + ageing process (T66R)** for an existing alloy. Prediction error
was 3.2% (train) / 3.4% (test) for UTS, and the verified alloy reached **767 ± 6 MPa**
(vs. 715 ± 6 MPa for conventional T6). The reason it worked: **the ML target was a
process, the training data and the experiment shared the same processing regime, and
the composition was held fixed.**

**Li et al. (2020)** — [10.1038/s43246-020-00074-2](https://doi.org/10.1038/s43246-020-00074-2)
— the "952 MPa" case. The ML target was 550 MPa; the **as-cast** alloy reached **562
MPa**. The 952 MPa came from extrusion + double-stage solution treatment + T6. The
authors state plainly that the processing "contributed to the high strength of the
optimized alloy, **beyond the machine-learning-assisted composition optimization**," and
that for isolated compositions the model "**helplessly predicted… values close to the
average**."

**Applied to this project.** The *Aloy* surrogate's inputs are composition + a
coarse **process-route categorical encoding** (`src/aloy/models.py`, `_PROC_ENCODE`:
`as_cast 0.0 … aged_peak 1.0`), plus test temperature. It has **no continuous process
variables** — no solution-treatment temperature, no quench rate, no ageing time or
temperature. It cannot learn a process–property relationship of the kind Jiang used.

Worse, I verified the training distribution directly:

```
Full Al≥50% training set (n = 1150):  processing categories present are
  Solutionised + Artificially peak aged   375
  Solutionised + Artificially over aged   214
  Strain Hardened / hardened               235
  No Processing                            140
  Solutionised + Naturally aged             86
  Solutionised + Cold Worked + Nat. aged    57
  … (solutionised, artificial aged, naturally aged)
Records with "cast" anywhere in the processing label:  0
```

**The training set contains zero as-cast records.** Every record is a wrought,
solution-treated, or aged material. The model has never seen a cast microstructure.

### 3.2 Therefore: the ML should be re-pointed at process, not composition

This is the most important scientific recommendation in this document.

- **Composition is a dead end for novelty.** §2 shows the candidate is inside the 7055
  envelope. Optimising composition further produces either another known alloy or an
  unmanufacturable one.
- **The model's process channel is the weakest and most valuable part.** It is a single
  ordinal scalar. The honest, publishable, and *cheap* upgrade is to **add continuous
  process features** (homogenisation T/t, solution T/t, quench rate, ageing T/t) and
  re-train — exactly Jiang's move, but starting from a weaker position.
- **The student's own lab protocol already contains the process variables.** The
  protocol already fixes homogenisation (465 °C/12 h), solution (465–475 °C/2 h),
  quench (<10 s), and ageing (120 °C/24 h). These are the natural independent variables.

### 3.3 Independent variables, levels, and fixed parameters

For the **process** question (H2, and the highest-value version of the experiment):

| Factor | Symbol | Levels | Rationale |
|---|---|---|---|
| Ageing temperature | T_age | 120 °C, 160 °C | T6 vs. T73 branch already in the protocol (`outputs/lab_protocols.txt` §6) |
| Ageing time | t_age | 24 h, 8 h | pairs with the above to give T6 and T73 |
| Solution temperature | T_sol | 465 °C, 475 °C | the protocol's own window; 475 °C is the stated ceiling |
| Homogenisation | — | 465 °C/12 h **or** none | the protocol calls this "optional"; testing that claim is a cheap, real result |

Full factorial 2⁴ = 16 conditions is **not feasible** for one student (16 casts, 16×
heat-treatment batches, 16×3 tensile bars = 48 bars).

For the **composition** question (H1, the primary hypothesis), the design is much
simpler because composition is fixed: **one composition, one route (the protocol's T6),
replicated across heats.** That is the design I recommend as the primary experiment,
with the process factors relegated to a secondary, reduced comparison (§4.5).

### 3.4 Fixed parameters (must not drift between arms)

Melt 700 °C / pour 690 °C; Al-5Ti-1B grain refiner 0.1 wt%; degas with Ar or C₂Cl₆;
solutionise 465–475 °C/2 h; cold-water quench, transfer < 10 s; T6 age 120 °C/24 h —
all as written in `outputs/lab_protocols.txt`. Crucible and mould material, mould
pre-heat temperature, and quench medium temperature must be **recorded and held
constant across all heats**, because they are uncontrolled confounders otherwise.

---

## 4. Statistical power and replication

### 4.1 The scatter estimate — what I could and could not find

**What I could not find:** a peer-reviewed, material-specific standard deviation for the
**yield strength of 7xxx aluminium tensile specimens** measured to ASTM E8. I searched
and did not find a defensible published σ for *this alloy class*. I am stating this
explicitly rather than inventing a number.

**What I did find, and will use as the method floor:**

> **ASTM Research Report RR:E28-1046**, NIST/ASTM interlaboratory study (Luecke, Splett,
> McColskey, 2016), for tension testing of a structural alloy:
> yield-strength **repeatability s_r = 11 MPa (CV 1.03%)** and **reproducibility
> s_R = 15 MPa (CV 1.41%)** at x̄ = 1067 MPa.
> URL: [https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=920214](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=920214)

This is the **measurement-method** scatter (same specimens, same/different labs). It is
*not* the specimen-to-specimen scatter of a cast alloy. Scaled to a 600 MPa alloy,
CV 1.03% → **σ_method ≈ 6 MPa** (repeatability) and **σ_method ≈ 8.5 MPa**
(reproducibility). So **method noise is negligible** relative to the effects we care
about. The scatter that matters is **material** scatter.

**Supporting material-scatter evidence** (cast Al–Zn–Mg–Cu, 7 compositions, T6):
yield strengths spanned 280–540 MPa across compositions, with Archimedes porosity
measurement used to explain scatter — Ghiaasiaan & Shankar, *Int. J. Metalcasting*
13:300 (2019), [10.1007/s40962-018-0254-z](https://doi.org/10.1007/s40962-018-0254-z).
This establishes that **cast Al–Zn–Mg–Cu T6 yield strengths land in the 280–540 MPa
band**, i.e. *below* the candidate's 625 MPa prediction — direct precedent for the
overshoot branch of §1.3.

**Assumption I am making, stated explicitly:**

> **[ASSUMPTION]** For a single well-executed cast heat, the **specimen-to-specimen**
> σ of YS is **25 MPa**, and the **heat-to-heat** σ is **30 MPa**. These are engineering
> estimates consistent with a material CV of ~4–5%, which is typical for cast
> aluminium, and they are *larger* than the method floor by a factor of ~3–4. They must
> be replaced by measured values after the first campaign.

I deliberately chose σ_heat (30) > σ_spec (25). In casting, the heat-to-heat component
usually dominates because it captures melt chemistry drift, gas content, and quench
variation. This is the assumption that most changes the required N, so §4.4 tests it.

### 4.2 The two-level variance model (this is the point most student work misses)

If a student casts **one heat** and pulls **n** specimens, the standard error of the
mean is

    SE = sqrt( σ_heat²/H + σ_spec²/(H·n) )

With **H = 1**, the first term does **not** shrink as n grows. Adding specimens to a
single heat estimates *that heat's* strength ever more precisely, but tells you nothing
about the alloy. **Testing 3 bars from 1 heat does not measure what the student thinks
it measures.** This is the single most common fatal flaw in undergraduate
alloy-validation work, and it is why the design below fixes **H ≥ 3**.

### 4.3 Power calculation — precision framing

To estimate a mean to a 95% CI half-width of ±h, the required total sample size is

    N = (1.96 · σ / h)²   (for a single-level model)

and in the two-level model, choose (H, n) to satisfy the SE formula in §4.2.

Computed (σ_heat = 30, σ_spec = 25 MPa):

| H (heats) | n (specimens/heat) | total bars | SE (MPa) | 95% CI half-width |
|---|---|---|---|---|
| 1 | 3 | 3 | 33.3 | **±65.3** |
| 1 | 6 | 6 | 31.7 | ±62.1 |
| 2 | 3 | 6 | 23.5 | ±46.1 |
| **3** | **3** | **9** | **19.2** | **±37.7** |
| 3 | 5 | 15 | 18.5 | ±36.2 |
| 5 | 3 | 15 | 14.9 | ±29.2 |
| 5 | 5 | 25 | 14.3 | ±28.1 |

**Reading of the table.** Going from 1 heat to 3 heats (3 bars → 9 bars) cuts the CI
half-width from ±65 MPa to ±38 MPa — a *larger* gain than going from 3 heats to 5
heats. **The marginal return on specimens within a heat is poor; the return on
independent heats is good.** This is the quantitative justification for H = 3.

**Is ±38 MPa enough to test H1?** Yes. The interval [517, 732] is 215 MPa wide; a CI of
±38 MPa around a measured mean can resolve inside/below/above in the great majority of
cases. It is *not* enough to resolve the point prediction 625 MPa to within the model's
MAE, but that is not the claim being tested (§1.2).

### 4.4 Sensitivity — what if scatter is 2× worse?

If the first campaign shows the casting is poor, σ_heat and σ_spec could double
(σ_heat = 60, σ_spec = 50 MPa):

| H | n | total bars | SE (MPa) | 95% CI half-width |
|---|---|---|---|---|
| 3 | 3 | 9 | 38.4 | ±75.3 |
| 3 | 5 | 15 | 37.0 | ±72.5 |
| 5 | 5 | 25 | 28.6 | ±56.1 |
| 8 | 5 | 40 | 22.6 | ±44.2 |

**Conclusion of the sensitivity analysis:** if scatter doubles, **the experiment can no
longer cleanly resolve the interval at student scale** — a ±56 to ±75 MPa CI on a
215 MPa-wide interval will often straddle a bound, producing the "uninformative" branch
of §1.3. The correct response is **not** to add more specimens to the same bad heat; it
is to **fix the casting process** (degassing, mould pre-heat, quench discipline) and
re-measure σ on a pilot heat. If σ cannot be brought down, the honest outcome is that
H1 is only testable as a **crude** check (is the mean above or below 517?) and must be
reported as such.

### 4.5 Power for the process sub-study

For the reduced process comparison (§3.3), a two-level factor (e.g. T6 vs. T73) with
σ = 30 MPa and a realistic effect of ~50 MPa (T73 typically over-ages below T6 peak)
requires, at 80% power, α = 0.05:

    n_per_group = 2·(1.96 + 0.84)²·σ²/Δ² ≈ 2·7.85·900/2500 ≈ 5.7 → 6 per group

So the process comparison needs **~6 bars per condition**, i.e. ~12 bars for a
two-condition test. This is why the full 2⁴ factorial is infeasible (§3.3): 16
conditions × 6 = 96 bars.

---

## 5. Controls

Each control earns its place by closing a specific alternative explanation.

| # | Control | What it rules out | How many |
|---|---|---|---|
| C1 | **Certified AA7075-T6 wrought bar**, tested on the same machine, same operator, same week | Machine mis-calibration, extensometer error, specimen-machining error, operator error. Also gives a direct reference number. | 3 bars |
| C2 | **Same-route cast 7075** (nominal 7075 composition, identical casting + heat treatment) | The "cast vs. wrought" confound. Separates *composition* effect from *processing* effect — the direct test of H2. | 3 bars from ≥1 heat |
| C3 | **As-cast / un-aged blank** of the candidate composition | Confirms the alloy is heat-treatable and that the T6 response is real. A T6 bar that equals the as-cast bar means the ageing did not work. | 2 bars |
| C4 | **Hardness blanks** (one coupon per heat, un-machined) | Non-destructive cross-check of heat-to-heat consistency before committing to machining tensile bars. | 1 coupon/heat |
| C5 | **Composition check** by EDS/optical emission on each heat | Confirms the actual composition, which the whole prediction depends on. Charge overage means nominal ≠ actual. | 1 sample/heat |

**C1 is non-negotiable.** If it fails (reference YS outside ~470–540 MPa), the entire
campaign is void and must be repeated after fixing the test chain.

---

## 6. Measurement plan

For each property: method, standard, sample prep, and the **method's own uncertainty**.
The right-hand column states whether the ML model's inputs actually depend on it — this
prevents collecting data that does not feed the loop.

| Property | Method | Standard | Sample prep | Method uncertainty | Does the ML depend on it? |
|---|---|---|---|---|---|
| **Yield strength (0.2% offset)** | Uniaxial tension, room temp | **ASTM E8/E8M-25** ([astm.org/Standards/E8.htm](https://www.astm.org/Standards/E8.htm)) | Machined round or flat specimens; sub-size permitted for small castings; grip alignment per standard | Method floor s_r ≈ 11 MPa (CV 1.03%), s_R ≈ 15 MPa (RR:E28-1046). Material scatter dominates. | **Yes — `measured.ys_mpa` is the only field `aloy.active` consumes** (`src/aloy/active.py` line 151). This is the primary output. |
| **UTS** | Same test | ASTM E8/E8M-25 | Same specimen | s_r ≈ 11 MPa (CV 0.64%) | Not consumed by the loop, but needed for the paper and for UTS-model validation. |
| **Elongation** | Same test, post-fracture gauge length | ASTM E8/E8M-25 | Same specimen; elongation is gauge-length dependent — report gauge length | s_r ≈ 1.6% (CV 3.3%) | Model predicts it (R² ≈ 0.21 — weak). Report it, but **do not over-interpret** a match or mismatch. |
| **Vickers hardness** | Vickers, HV1 or HV5 | **ASTM E92** ([astm.org/Standards/E92.htm](https://www.astm.org/Standards/E92.htm)); micro-indentation variant ASTM E384 | Mounted, ground, polished to 1 µm; ≥10 indents per condition, report mean ± SD | Typically ±2–3% of reading for a homogeneous specimen **[ASSUMPTION: verify with lab]** | Indirectly — hardness is in the model's target list but is not the design objective. Use as a cheap consistency check. |
| **Phase identification** | XRD, Cu-Kα, 2θ 20–90° | No single ASTM standard for phase ID; report per instrument convention. Rietveld refinement if quantitative. | Flat polished surface; as-cast and T6 conditions both | Peak detection is qualitative for minor phases; **η-MgZn₂ and η′ are nanoscale and generally NOT resolvable by lab XRD** | No — CALPHAD screening used phases, but the surrogate does not take XRD as input. |
| **Microstructure + chemistry** | SEM backscatter + EDS | Instrument convention; EDS quantification accuracy ~1–2 wt% for major elements | Polished + etched (Keller's) for OM; unetched for SEM/EDS | EDS: ±1–2 wt% absolute for major elements | **Indirectly and importantly** — EDS confirms actual composition, which *is* the model's input. |
| **Density** | Archimedes (mass in air / mass in water) | **ASTM B962** ([astm.org/b0962-17.html](https://www.astm.org/b0962-17.html)); ASTM E252 covers foil thickness, not bulk density | Solid, pore-free coupon; weigh to 0.1 mg; use wetting agent | ~0.1–0.5% for a solid specimen; **inflated by open porosity** — porosity *reduces* apparent density | Yes — `rho_rule` is an input feature; a density mismatch flags porosity or composition error. |
| **Chemical composition** | Optical emission spectrometry (preferred) or EDS | Instrument convention | One sample per heat, from the cast billet | OES: ±0.05–0.1 wt% for Zn/Mg/Cu **[ASSUMPTION: verify with lab]** | **Yes — composition is the model's primary input.** |

**Note on porosity.** Because Archimedes density is sensitive to open porosity, it
doubles as a **porosity control**. If measured density is materially below the predicted
2.816 g/cm³, the specimen contains porosity and its strength is not representative.

**Note on what NOT to bother with at this stage.** TEM, APT, DSC, and EBSD are
high-value for a *mechanistic* paper but are not required to test H1, and are unlikely
to be available. Do not design them into the critical path (§10).

---

## 7. The decision rule, fixed in advance

**This rule must be written down and dated before any specimen is tested.** Fixing it
in advance is what prevents post-hoc rationalisation.

Let ȳ be the measured mean YS and [L, U] the 95% CI on the mean (from H = 3 heats ×
n = 3 specimens, SE ≈ 19 MPa → ±38 MPa).

| Condition | Conclusion | Action |
|---|---|---|
| **L > 517 and U < 732** | **H1 confirmed.** The conformal interval is validated out-of-sample. | Write the positive validation paper (§8). Feed ȳ into `experiment_log.json`. |
| **ȳ ∈ [517, 732] but CI crosses a bound** | **H1 consistent, not confirmed.** Report honestly. | Report as "consistent with the model's interval." Do not claim the bound was established. |
| **U < 517** | **H1 disconfirmed — model over-predicted beyond its stated uncertainty.** | Report as a **calibration failure**. This is the Li et al. failure mode and is publishable (§8). Feed ȳ into the log anyway — a large negative residual is *exactly* the informative point the active-learning loop needs. |
| **L > 732** | **H1 disconfirmed — interval failed to cover.** | Report as a coverage violation. Do **not** spin this as a success. Investigate whether the model simply learned the composition mean. |
| **CI spans a bound with SE > 50 MPa** | **Uninformative.** | Do not publish a strength claim. Diagnose the scatter source (porosity? chemistry drift? quench delay?) and re-cast. |

### 7.1 Conditional branches

**If elongation is poor (< 5%) while YS is in the interval.** The model predicts 12.3%
(and its elongation R² is only 0.21–0.27, `holdout_report.json`). A brittle but strong
result means the *strength* claim survives but the *ductility* claim does not. The
conclusion narrows to: "the YS interval is validated; the elongation prediction is not."
This is a legitimate, publishable, and honest split verdict — it is *not* a failure.

**If XRD shows unexpected primary phases** (e.g. coarse Mg(Zn,Cu,Al)₂, S-phase Al₂CuMg,
or Al₇Cu₂Fe constituent particles undissolved). This means the solution treatment did
not fully dissolve the as-cast phases, so the alloy tested is **not** the alloy modelled.
The result is **uninformative about H1** and must be reported as a processing finding.
Do not enter it into the active-learning loop as if it were a composition result.

**If the reference control C1 fails** (7075-T6 outside ~470–540 MPa). **Stop.** No
conclusion from any arm is valid. Fix the test chain and repeat.

### 7.2 Feedback into `experiment_log.json` and the `aloy.active` loop

I read `src/aloy/active.py` to confirm what the loop actually consumes:

```python
# active.py, lines 148–154 (approximate)
log = ExperimentLog().load()
for r in log:
    if r.get("measured", {}).get("ys_mpa") is not None:
        comp = r["composition"]
        extra_x.append(np.clip(xv, 0, 1))
        extra_y.append(r["measured"]["ys_mpa"])
```

**Confirmed: the loop consumes exactly one field — `measured.ys_mpa` — and the
`composition` dict.** Nothing else (no elongation, no UTS, no processing, no
uncertainty) enters the Bayesian update. Consequences:

1. **The record format must match.** `composition` is a dict of **mass fractions**
   (they sum to 1.0 in the existing records, e.g. `{"Al": 0.9069, "Zn": 0.042, …}`).
   The candidate must be written in the **same mass-fraction form**, not wt%.
2. **The headline candidate is NOT currently in the log.** I checked all 15 records in
   `outputs/experiment_log.json`: the closest entries are `{Al 0.8946, Mg 0.0241, Zn
   0.0372, Cu 0.0298, Cr, Ti, Zr}` and similar; **no record matches
   Al–3.0Mg–7.8Zn–1.3Cu.** The log holds *different* candidate proposals from
   `next_experiments.csv`. **A new record must be appended** for candidate 2 before any
   feedback is possible.
3. **A single scalar per composition.** Feeding one heat's mean YS as a single point
   with no uncertainty weight means the GP will treat a noisy measurement as exact.
   The GP does add noise (qLogNEI is a *noisy* EI variant), so this is tolerable, but
   **the honest thing is to feed the mean of ≥3 heats** and to record the per-heat
   values in a separate field for the paper.

**Recommended record** (append to `outputs/experiment_log.json`; do **not** modify
existing records):

```json
{
  "composition": {"Al": 0.8781, "Mg": 0.0302, "Zn": 0.0780, "Cu": 0.0133,
                  "Si": 0.0001, "Fe": 0.0002},
  "measured": {"ys_mpa": <MEAN_OF_HEATS>},
  "predicted": {"ys_mpa": 624.5},
  "meta": {"n_heats": 3, "n_specimens": 9, "sd_ys_mpa": <SD>,
           "processing": "cast+homog465C12h+soln470C2h+WQ+T6_120C24h",
           "reference_7075T6_ys_mpa": <MEASURED_REFERENCE>,
           "date": "YYYY-MM-DD"}
}
```

The `meta` block is ignored by `active.py` but is essential for the manuscript and for
anyone re-running the loop later.

---

## 8. The publication path for BOTH outcomes

A negative result is publishable — but only if it is *designed* to be, which §1.3 and
§7 ensure. Here is the concrete mapping.

### 8.1 If the prediction holds (ȳ ∈ [517, 732])

**Story:** "A transparent, open ML pipeline predicted a 7xxx alloy's yield strength
with a distribution-free interval; the interval was validated out-of-sample on a cast
and heat-treated alloy, including a same-machine commercial reference."

**Novelty:** not the alloy (§2) — the **calibrated uncertainty quantification validated
on real material**, plus the honest domain-discipline finding (the MPEA contamination
result, `REPORT.md` §2).

**Venues, best fit first:**
- ***Materialia*** or ***Journal of Alloys and Compounds*** — short communication /
  full article. JAC is the natural home for a 7xxx processing-and-properties paper.
- ***Materials Science and Engineering: A*** — if the paper carries real microstructure
  work (SEM/EDS + hardness) alongside the tensile validation.
- ***npj Computational Materials*** — only if the paper's *core* is the method
  (conformal calibration validated experimentally), not the alloy. Higher bar.

### 8.2 If the prediction overshoots (U < 517 MPa) — **the most likely outcome**

This is the branch the two precedents predict. Cast Al–Zn–Mg–Cu T6 yield strengths
land at 280–540 MPa (Ghiaasiaan & Shankar 2019,
[10.1007/s40962-018-0254-z](https://doi.org/10.1007/s40962-018-0254-z)); the model's
local training neighbours for this composition measure 602–614 MPa and are **wrought**
(see §9.3); and Li et al. document exactly this failure mode.

**Story:** "An ML inverse-design pipeline predicted 625 MPa [517, 732] for a cast
Al–Zn–Mg–Cu alloy. Experimental validation gave X MPa. The discrepancy is attributable
to the processing-route gap between the model's wrought training distribution and the
cast validation route. We quantify the gap and show that the conformal interval did not
cover."

**Why this is genuinely valuable:** it is a **pre-registered, quantitative demonstration
of the processing-regime failure mode** that the field repeatedly warns about but
rarely measures on a single well-characterised alloy. It is the experiment that Li et
al. *did not run* (they reported the as-cast 562 MPa but published the extruded 952 MPa).

**Venues, best fit first:**
- ***npj Computational Materials*** or ***Materials Science and Engineering: A*** — a
  negative/cautionary validation result with method-level implications is squarely in
  scope. This is the *strongest* version of this paper.
- ***Journal of Alloys and Compounds*** — acceptable, but frame it as a validation
  study, not a discovery.
- ***Materialia*** — good fit for a concise, well-controlled negative result.

**The paper is stronger, not weaker, if the negative result is pre-registered** (i.e.
this document is dated and archived before the experiment). State the pre-registration
in the manuscript.

### 8.3 If the prediction undershoots (L > 732 MPa)

**Story:** "The alloy exceeded its predicted interval." Two sub-cases:
- If a same-route 7075 control (C2) is *also* far above handbook, the likely cause is a
  **test-chain artefact** — recheck C1 before believing it.
- If C2 is normal and the candidate is genuinely >732 MPa, the finding is a real alloy
  result, but the **conformal interval failed to cover** and must be reported as such.

**Venue:** *Materials Science and Engineering: A* or *Journal of Alloys and Compounds*,
as an alloy-development paper — but the UQ failure must be in the abstract, not buried.

### 8.4 The Mg–Ca–Li branch

Out of scope for this design. It carries a mandatory SF₆/CO₂ cover-gas requirement and
a never-use-water safety rule (`outputs/mg_lab_protocols.txt` §7) that make it a
materially higher-risk campaign. **Do not attempt the Mg branch in parallel with the Al
branch.** One student, one campaign.

---

## 9. What he cannot do — stated plainly

Each item is **equipment-dependent and must be confirmed with the lab before
scheduling.** I assume he has none of it.

| Capability | Why it matters | If unavailable |
|---|---|---|
| **Induction melting with controlled atmosphere** | Zn (bp 907 °C) and Mg (bp 1090 °C) volatilise; melt at 700 °C in air loses both, shifting composition. | **Workaround:** resistance furnace + flux/Ar cover + the protocol's charge overage (Zn +7%, Mg +10%). **Weaken the claim:** actual composition must be measured by OES/EDS and reported; the composition is then *whatever was measured*, not nominal. |
| **Quench-rate measurement** | The model has no quench-rate input, but quench rate strongly controls 7xxx strength (vacancy supersaturation). Without it, the route is under-specified and non-reproducible. | **Workaround:** hold the protocol's "<10 s transfer, cold water" and *record* transfer time and water temperature for every specimen. **Weaken the claim:** cannot report a quench rate; the route is described qualitatively. |
| **DSC (incipient melting)** | The protocol asserts a 477 °C incipient-melting ceiling. If the true onset for *this* composition is lower, the 475 °C solution treatment may already be damaging specimens — and the student would not know. | **Workaround:** stay conservatively below 470 °C, or verify the ceiling from published DSC on comparable alloys (e.g. [10.1007/s11665-011-9973-5](https://link.springer.com/article/10.1007/s11665-011-9973-5); [OSTI incipient melting in AA7075](https://www.osti.gov/servlets/purl/1876952)). **Weaken the claim:** the ceiling is inherited, not measured. |
| **Extrusion / rolling mill** | This is *the* reason Li et al. reached 952 MPa. Without deformation, the alloy cannot reach that class. | **Weaken the claim, fundamentally:** the experiment tests the **as-cast + T6** alloy only. The predicted 625 MPa is compared against a cast specimen; §9.3 shows the model was trained on wrought data. **This limitation must be in the abstract.** |
| **TEM / APT** | Needed to prove the η′ precipitate mechanism. | **Workaround:** hardness + XRD + SEM. **Weaken the claim:** the strengthening mechanism is asserted by analogy to 7xxx literature, not demonstrated. Do not claim a mechanism. |
| **NIMS creep data** | The project lists no creep/corrosion data. NIMS databases require registration. | **Out of scope.** Do not claim creep or corrosion performance. |
| **Statistical software / expertise** | The two-level variance decomposition (§4.2) requires a random-effects model, not a t-test. | **Workaround:** compute heat means and specimen SDs by hand; report both components separately. **Weaken the claim:** report the conservative (larger) SD. |
| **Cost of certified 7075-T6 bar** | Control C1 is non-negotiable (§5). | **Workaround:** a scrap aerospace 7075-T6 part with a known pedigree, or a university-owned reference coupon with a certificate. Do **not** substitute an unknown 7xxx offcut. |

### 9.3 The limitation that must be stated in the abstract

I verified this directly from the training data:

> **The Aloy YS model was trained on 1150 wrought/processed Al records containing zero
> as-cast entries. Its ten nearest training neighbours to the candidate composition are
> all "Solutionised + Artificially peak/over aged" wrought records, measuring 602–614
> MPa (peak-aged) or 410–421 MPa (over-aged). The model's 625 MPa prediction for a
> *cast* alloy therefore lies above every local wrought analogue in its own training
> set.**

This is not a reason to abandon the experiment — it is the reason the experiment is
*interesting*. But it means the honest prior is that the model will **overshoot** for a
cast specimen, and the design must be able to say so cleanly. §7 and §8.2 do exactly
that.

---

## 10. The minimal executable version

If the full design is too large (it probably is, for one semester), this reduced version
still produces a defensible result.

### 10.1 Reduced design

| Element | Full | **Reduced (recommended minimum)** |
|---|---|---|
| Compositions | candidate + cast-7075 + wrought-7075 | **candidate + wrought 7075-T6 (C1)** |
| Heats | 3 | **3** (this is the part you must not cut — §4.2) |
| Specimens/heat | 3 | **3** |
| Total tensile bars | 18–24 | **9 (candidate) + 3 (reference) = 12** |
| Process study | T6 vs T73 comparison | **dropped** — record the limitation |
| Homogenisation | tested as a factor | **fixed ON** (465 °C/12 h) |
| Microstructure | SEM/EDS + XRD + hardness | **hardness + Archimedes density + EDS only** |
| Porosity check | quantitative image analysis | **density-based only** |

**What the reduced version gives up:** it cannot separate composition from processing
(no C2), and it cannot say anything about the T6/T73 trade-off. It *can* still test H1
(§1.2) and it *can* still produce the negative-result paper (§8.2), because both depend
only on the candidate measurement plus the reference control.

**What it must NOT give up:** H = 3 heats. A single heat, however many specimens, is
not a measurement of the alloy.

### 10.2 Rough timeline

| Weeks | Activity | Gate |
|---|---|---|
| 0 | **Confirm equipment** (§9 table). Order 7075-T6 reference bar. | If no furnace with cover gas/Ar, redesign around a flux route. |
| 1 | Pilot heat (1 melt). Machine 3 bars. Measure. Compute σ_spec. | If σ_spec > 50 MPa, stop and fix casting. |
| 2–3 | Cast heats 1–3 of the candidate; cast 1 heat of 7075 if C2 included. | Chemistry confirmed by EDS/OES on each heat. |
| 3–4 | Homogenise, solutionise, quench, T6 age all heats on a fixed schedule. | Record transfer times and water temperature. |
| 4–5 | Machine 9 + 3 bars to ASTM E8. Hardness + density coupons. | Specimen dimensions within E8 tolerance. |
| 5 | Tensile testing, all arms interleaved on the same machine. | **C1 must fall in 470–540 MPa.** |
| 6 | XRD/EDS as available. Analyse against the fixed decision rule (§7). | — |
| 7 | Write up. Append the record to `experiment_log.json`. Run `aloy.active`. | — |

### 10.3 Key risk

**The dominant risk is not that the model is wrong — it is that the casting is bad.**
If the student's first heat is porous or chemically off-target, the measured strength
will be low for reasons that have nothing to do with the model, and the experiment
becomes the "uninformative" branch of §1.3. **Mitigation: the pilot heat and the C1
reference control are the two gates that must pass before the main campaign proceeds.**
Do not skip them to save a week.

**The second risk** is that a ±65 MPa CI (H=1, the likely shortcut) straddles a bound
and the student is left with a result that cannot be interpreted either way. The
mitigation is the H = 3 minimum, which is the whole point of §4.

---

## 11. Errors and gaps found in the existing lab protocol

Read against `outputs/lab_protocols.txt` and `outputs/mg_lab_protocols.txt`:

1. **The charge overage dilutes the balance element — the target composition is not
   achieved even if nothing volatilises.** For candidate 2, the protocol charges
   439.03 g Al + 41.75 g Zn + 16.63 g Mg + 6.67 g Cu + 0.10 g Fe + 0.07 g Si =
   **504.25 g total**, which normalises to **Al 87.07, Zn 8.28, Mg 3.30 wt%** — not the
   stated target of Al 87.81, Zn 7.80, Mg 3.02. The overage is applied to Zn and Mg
   *masses* without reducing the Al balance, so the batch is 4.25 g over 500 g and the
   Al is diluted. **Fix:** state the assumed loss fractions explicitly and solve the
   charge so that *post-loss* composition equals target. This is a real bookkeeping
   error, not a rounding artefact.

2. **The 477 °C incipient-melting figure is asserted without a source.** The protocol
   warns "stay BELOW 477 °C" but cites nothing. The phenomenon is real
   ([OSTI report on incipient melting in AA7075](https://www.osti.gov/servlets/purl/1876952);
   [DSC phase-transition study, J. Mater. Eng. Perform. 2011](https://link.springer.com/article/10.1007/s11665-011-9973-5)),
   but the *onset temperature is composition-dependent* and the protocol gives no
   measurement for the candidate's own composition. **This is a safety/quality-critical
   unsourced number** and should either be cited or measured by DSC before the 475 °C
   solution treatment is used.

3. **"Quench air dingin" (cold-water quench) conflicts between languages and lacks a
   rate.** The English text says "cold water (<40 °C), transfer < 10 s"; the Indonesian
   summary says "quench air dingin." Cold water and air are separated by two orders of
   magnitude in quench rate and produce completely different precipitate
   microstructures. **Clarify to "cold water"** and add a required transfer-time log.

4. **No uncertainty is attached to any predicted property in the protocol.** §7 lists
   "Yield strength: 625 MPa [517, 732]" but gives the other predictions (UTS 660,
   elongation 12.3, density 2.816) as bare point values with no interval, even though
   the elongation model has R² ≈ 0.21. **Add the model's MAE or an interval to every
   predicted quantity**, or mark it as a point estimate.

5. **Homogenisation is labelled "optional" without justification or a test.** It is the
   step that dissolves as-cast segregation; calling it optional without evidence risks a
   student skipping the step that most affects the measured result. Either justify the
   optionality or make it mandatory.

6. **The Mg protocol's solution temperature for candidate 3 (525 °C/8 h) is not
   obviously safe.** With 8.94 wt% Al, the Mg₁₇Al₁₂ eutectic (≈437 °C) and Mg–Y phases
   bound the safe solution window; 525 °C exceeds the conventional AZ91 solution
   temperature (~413 °C) by >100 °C. **This needs a DSC or a cited phase diagram before
   it is used** — molten Mg in a lab furnace is a serious hazard. (No Mg work is
   recommended in this campaign regardless, §8.4.)

7. **`outputs/experiment_log.json` contains 15 records, all with `measured: {}`, and
   none matching the headline candidate.** The log holds *other* proposals from
   `next_experiments.csv`. Anyone reading the release would reasonably assume the log
   tracks the headline candidate. **Add the candidate-2 record (§7.2) or document why
   the log tracks a different set.**

---

## 12. References

1. Jiang, L. et al. *A rapid and effective method for alloy materials design via sample
   data transfer machine learning.* npj Comput. Mater. **9**, 26 (2023).
   https://doi.org/10.1038/s41524-023-00979-9
2. Li, J. et al. *Accelerated discovery of high-strength aluminum alloys by machine
   learning.* Commun. Mater. **1**, 73 (2020). https://doi.org/10.1038/s43246-020-00074-2
3. ASTM E8/E8M-25, *Standard Test Methods for Tension Testing of Metallic Materials.*
   https://www.astm.org/Standards/E8.htm
4. ASTM RR:E28-1046 (NIST/ASTM interlaboratory study, Luecke, Splett & McColskey, 2016).
   Yield-strength repeatability CV 1.03%, reproducibility CV 1.41%.
   https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=920214
5. ASTM E92, *Standard Test Methods for Vickers and Knoop Hardness of Metallic
   Materials.* https://www.astm.org/Standards/E92.htm
6. ASTM B962-17, *Standard Test Methods for Density of Compacted or Sintered Powder
   Metallurgy Products Using Archimedes' Principle.* https://www.astm.org/b0962-17.html
7. Ghiaasiaan, R. & Shankar, S. *Effect of Alloy Composition on Microstructure and
   Tensile Properties of Net-Shaped Castings of Al–Zn–Mg–Cu Alloys.* Int. J.
   Metalcasting **13**, 300–310 (2019). https://doi.org/10.1007/s40962-018-0254-z
8. MatWeb / ASM, *Aluminum 7075-T6; 7075-T651.*
   https://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA7075T6
9. Kaiser Aluminum, *Technical Data: Rod & Bar Alloy 7075.*
   https://online.kaiseraluminum.com/depot/PublicProductInformation/Document/1028/Kaiser_Aluminum_7075_Rod_and_Bar.pdf
10. OSTI, *Incipient Melting in AA7075.* https://www.osti.gov/servlets/purl/1876952
11. *DSC Study on Phase Transitions… of 7xxx Series Alloys*, J. Mater. Eng. Perform.
    (2011). https://link.springer.com/article/10.1007/s11665-011-9973-5
12. Aloy project release, DOI 10.5281/zenodo.22844739 — `REPORT.md`,
    `outputs/lab_protocols.txt`, `outputs/experiment_log.json`,
    `outputs/credibility_report.json`, `outputs/holdout_report.json`,
    `src/aloy/active.py`, `src/aloy/models.py`, `src/aloy/data.py`.

---

## Appendix A — Derivation of the power numbers in §4

Two-level model: `SE = sqrt(σ_heat²/H + σ_spec²/(H·n))`, with σ_heat = 30, σ_spec = 25.

- H=3, n=3: sqrt(900/3 + 625/9) = sqrt(300 + 69.4) = sqrt(369.4) = **19.2 MPa** → ±37.7
- H=5, n=5: sqrt(900/5 + 625/25) = sqrt(180 + 25) = sqrt(205) = **14.3 MPa** → ±28.1
- H=1, n=3: sqrt(900 + 208.3) = sqrt(1108.3) = **33.3 MPa** → ±65.3

Sensitivity (σ_heat = 60, σ_spec = 50): H=5, n=5 → sqrt(720 + 100) = **28.6 MPa** → ±56.1.

Single-level precision formula used for the table header:
`N = (1.96·σ/h)²`.

Two-sample power (80%, α=0.05, two-sided): `n = 2·(1.96+0.84)²·σ²/Δ²`.

## Appendix B — Pre-registration statement

This design document should be **dated and archived (e.g. as a Zenodo version) before
the first tensile test**. The decision rule in §7 is fixed at that point. Any deviation
during execution must be recorded with its reason. This is what makes a negative result
publishable (§8.2) rather than merely disappointing.

---

## Erratum (added 2026-10-06)

**Two items in this document were refuted by a later, more careful review.** They were
wrong, and they are retracted here. The body of §11 is left unedited so the original
reasoning stays visible.

**`docs/PROTOCOL_CORRECTED.md` is now the governing document for all protocol
questions.** Where this document and that one disagree on a protocol matter, that one
wins.

### Item 1 — §11.1, the charge arithmetic: **RETRACTED**

§11.1 claimed "the charge overage dilutes the balance element — the target composition
is not achieved **even if nothing volatilises**." That is arithmetically true **only in
the no-volatilisation case, which is not the protocol's stated assumption.**

The protocol applies the overage *because it assumes Zn and Mg will be lost*. Under the
protocol's own stated loss fractions, both normalisations are correct:

| Scenario | Normalised composition |
|---|---|
| **No loss** (what §11.1 assumed) | Al 87.07 / Zn 8.28 / Mg 3.30 wt% |
| **With the stated 7 % Zn / 10 % Mg loss** | Al 87.81 / Zn 7.80 / Mg 3.02 wt% — **the target** |

So: **the old numbers were not wrong. The old protocol was silent about its
assumption.** The defect was the missing stated philosophy, not the arithmetic. §11.1's
characterisation of this as "a real bookkeeping error" is withdrawn.

The criticism that *does* survive: the **7 % / 10 % loss fractions are themselves
unsourced assumptions.** They are not measured for this furnace or this alloy, and they
must be replaced by a pilot-heat result (pre- and post-melt weighing plus OES
chemistry). The correction, the explicit philosophy and the corrected charge tables are
in `PROTOCOL_CORRECTED.md` §0 and §2.

### Item 2 — §11.3, the quench medium: **RETRACTED**

§11.3 claimed a "two-orders-of-magnitude conflict" between "cold water" and "quench air
dingin." **This was a language misreading. *Air dingin* is Indonesian for "cold water."**
There was never a medium conflict, and no such claim should be repeated.

The valid part survives: the quench **medium, its temperature range, agitation and
transfer time were never specified as numbered procedure steps**, and the English and
Indonesian text were mixed across files. `PROTOCOL_CORRECTED.md` §4.5 now fixes these as
**agitated cold water at 20–30 °C (maximum 40 °C), transfer ≤ 10 s (target ≤ 5 s)**,
recorded per specimen.

### Other statements in this document now superseded

Listed for the record only. Sections are not rewritten.

| Location | Statement as written | Correction |
|---|---|---|
| §3.3, §3.4, §10.1 | Homogenisation "465 °C/12 h" | Now **475 °C/12 h** (Wang et al. 2022: 465 °C leaves M + S phases; 475 °C dissolves them). `PROTOCOL_CORRECTED.md` §4.3. |
| §3.3, §3.4 | Solution treatment "465–475 °C/2 h" | Setpoint now **470 °C/2 h**, hard ceiling 477 °C, >480 °C invalidates the heat. `PROTOCOL_CORRECTED.md` §3, §4.4. |
| §11.2 | The 477 °C ceiling is "asserted without a source" and should "either be cited or measured by DSC" | Now **cited**: it is the wrought-AA7075 solidus (Alcoa/ASM); Sandia SAND2022-9908 puts the theoretical onset at 905–910 °F; Wang et al. 2022 give as-cast DSC peaks of 479.8–491.3 °C. It is still **not measured on this alloy** — DSC remains required. |
| §9 table (DSC row) | "stay conservatively below 470 °C" | Consistent with the correction; the 470 °C setpoint was adopted from it. The suggested source `10.1007/s11665-011-9973-5` is a weaker citation than Wang et al. 2022. |
| §11.5 | Homogenisation "optional" | Now **mandatory**. A "no homogenisation" arm may be run as an experiment but must be reported as out-of-spec. |
| §11.6 | Mg candidate 3 at 525 °C is "not obviously safe" | **Confirmed unsafe.** 8.94 wt% Al puts the alloy on the Mg₁₇Al₁₂ eutectic (~437 °C); 525 °C exceeds it by ~88 °C. **Do not run.** Mg–Al branch capped at ≤ 415 °C and only with a DSC. |
| §9 table (melting row) | The "Zn +7 %, Mg +10 %" overage presented as a validated workaround | Valid in principle, but the loss fractions are **assumptions**, not measurements (see Item 1). |

### Not contradicted

§11.4 (no uncertainty on predicted properties other than YS) **remains open and valid** —
it concerns intervals on *predicted* properties, which is a different matter from the
tolerances on *controlled parameters* added in `PROTOCOL_CORRECTED.md` §4.2. §2
(composition novelty), §4 (power), §9.3 (wrought-only training set) and §11.7
(experiment log) were re-checked and stand.
