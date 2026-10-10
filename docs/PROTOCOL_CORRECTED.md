# PROTOCOL_CORRECTED — Al–Zn–Mg–Cu (and Mg branch) casting & heat-treatment protocol

**Supersedes:** `outputs/lab_protocols.txt`, `outputs/lab_protocols.json`,
`outputs/mg_lab_protocols.txt`, `outputs/mg_lab_protocols.json`, and the protocol
summary in `README.md` / `REPORT.md`.

**Why it supersedes them:** those files are the *published* release artefacts
(Zenodo DOI [10.5281/zenodo.22844739](https://doi.org/10.5281/zenodo.22844739)) and are
frozen by `MANIFEST.sha256`. They are **not edited here**. This document is the
controlled, citable correction. Where this document and the frozen files disagree,
**this document governs any actual laboratory work.**

**Author of the correction:** experimental design review, 2026-10-06.
**Status:** requires supervisor sign-off and the "must be confirmed with the lab" items
(§7) before any melt is scheduled.

---

## 0. The one principle that fixes most of this document

> **Charge principle — philosophy (a): "charge to hit the post-melt composition".**
>
> The stated target composition (e.g. Al–3.0Mg–7.8Zn–1.3Cu) is the **composition of the
> solidified ingot after melting losses**, not the mass of metal put into the crucible.
> The charge is therefore the nominal ingot mass *divided by* (1 − assumed loss
> fraction) for the volatile elements, with **Al as the balance element reduced to
> absorb the difference**.
>
> Assumed loss fractions of the **charged mass**: **Zn 7.0 wt%, Mg 10.0 wt%**, all other
> elements 0. These are *assumptions*, not measurements, and must be replaced by the
> pilot-heat result (§9).

The old protocol applied the same arithmetic but **never said which philosophy it used,
never printed the total charge, and presented the target wt% as if it were achieved**.
That omission — not the arithmetic — was the defect. It caused a downstream reviewer
(`EXPERIMENTAL_DESIGN.md` §11.1) to normalise the 504.25 g charge and conclude the
alloy would be Al 87.07 / Zn 8.28 / Mg 3.30. **That conclusion is only correct if no
volatilisation occurs at all** (see §2.3). A protocol that does not state its
assumption cannot be checked; this one does.

> **Cross-reference.** `docs/EXPERIMENTAL_DESIGN.md` now carries an **Erratum
> (added 2026-10-06)** that formally retracts its §11.1 charge-arithmetic claim and its
> §11.3 "air dingin" medium-conflict claim, and records the other statements in that
> document superseded by this one. This document remains the governing reference for
> all protocol questions.

---

## 1. Change log

| # | Defect (old) | What was wrong | What it is now | Source that justifies it |
|---|---|---|---|---|
| 1 | Charge overage | Zn +7 % / Mg +10 % applied with no stated philosophy; target wt% printed as achieved; total charge (504.25 g) never shown; "balance = Al" printed under a table where Al is *not* the balance | §2: philosophy stated; loss fractions explicit; per-element charge **and** resulting ingot mass printed; a "if no loss occurs" column exposes the risk; total charge shown for every candidate | Arithmetic below; assumption is explicitly an engineering estimate (no source claims 7 %/10 % for this furnace) |
| 2 | 477 °C incipient-melting ceiling | Unsourced; it is the **wrought AA7075 solidus**, not a measured onset for a *cast* high-Zn alloy; leaves only 2 °C margin under the 475 °C setpoint | §4.4: ceiling retained as the *wrought* limit, **solution setpoint lowered to 470 °C**, hard limit 477 °C, invalidate the heat above 480 °C; DSC required | ASM/Alcoa 7075 datasheet (solidus 477 °C, liquidus 635 °C); Sandia SAND2022-9908 (theoretical incipient melting 905–910 °F ≈ 485–488 °C); Wang et al. 2022 (as-cast DSC: eutectic dissolution peak 479.8–482.0 °C, S-phase 484.4–491.3 °C; overburn risk at 480 °C for Cu+Mg > 4.24 wt%) |
| 3 | "Quench air dingin" vs "cold water" | **Not actually a two-orders-of-magnitude conflict** — *air dingin* is Indonesian for "cold water". The real defect is that no medium temperature, agitation or transfer time appears as a numbered step, and the two languages are mixed across files | §4.5: medium fixed as **agitated cold water, 20–30 °C (max 40 °C), transfer ≤10 s (target ≤5 s)**, recorded per specimen | Starink et al. 2015 (quench-sensitivity model); Milkereit et al. 2019 (UCCR concept); Quench Rate Study on AA7075 (S-Al₂CuMg suppressed only above ≈10 K/s; η needs far faster) |
| 4 | No tolerances on any controlled parameter | Only YS had an interval; every furnace step was a bare number, so nothing could be declared out-of-spec | §4 tolerance table (± °C, ± min, ± s) with explicit **heat-invalidation rules** | AMS 2750 (pyrometry/furnace class); ASTM E220 (thermocouple calibration); ASTM E8/E8M |
| 5 | Homogenisation "optional" | No justification either way; it is the step that dissolves the as-cast eutectic network and raises the incipient-melting onset | §4.3: **mandatory**, and raised from 465 °C/12 h to **475 °C/12 h** (one-step) | Wang et al. 2022: 465 °C/24 h leaves M + S phases; 470 °C/24 h dissolves most; 475 °C/24 h gives complete dissolution for low-Cu+Mg alloys; interdendritic dissolution ≈4.5 h, solute homogenisation 4.4–5.6 h at 475 °C |
| 6 | Mg candidate 3 solution treatment 525 °C/8 h | Unsafe: 8.94 wt% Al puts this alloy on the Mg–Mg₁₇Al₁₂ eutectic (≈437 °C); 525 °C exceeds it by ~90 °C | §5: **525 °C is unsafe — do not run.** Mg–Al-bearing branch capped at **≤415 °C**, and the Mg branch must not be run at all without a DSC | Gao, Zhu & Chen 2010 (β-Mg₁₇Al₁₂ dissolution near the 437 °C eutectic); ASM Handbook Vol. 4 (AZ91 solution treatment ≈413 °C) |
| 7 | `experiment_log.json` does not track the headline candidate | All 15 records are other proposals with `measured: {}`; the candidate to be cast has no record | Documented here (§8). Tooling fix is owned by a separate worker | `outputs/experiment_log.json`; `outputs/candidates_final.csv` row 121 |
| +1 | Degassing was a note, not a step | "Degas with Ar **or** C₂Cl₆" appears only in §9 notes; two methods with very different effectiveness and hazard; porosity is the dominant scatter source for tensile results | §4.2: **mandatory numbered step**; Ar (rotary or lance) 10–20 min preferred; C₂Cl₆ only with fume extraction and PPE; verify by Archimedes density | Degassing-parameter studies on Al castings (PMC9740475); ATSDR / ILO ICSC 0051 (hexachloroethane toxicity) |
| +2 | No mould pre-heat, no crucible material | Design doc flags both as uncontrolled confounders; protocol says only "a steel mould" | §4.1: mould **200–300 °C**, crucible **graphite-clay or SiC** (not mild steel), both recorded per heat | Design doc §3.4 / §9; standard Al foundry practice |
| +3 | No specimen-extraction plan | "3 specimens, ASTM E8" with no position; centre/edge, top/bottom scatter dominates cast scatter | §4.7: dedicated test-bar mould; specimens from the **lower-centre**, away from riser and chill skin; positions recorded; H ≥ 3 heats | Design doc §4.2 (two-level variance model); ASTM E8/E8M |
| +4 | Grain refiner dose never justified | 0.1 wt% Al-5Ti-1B asserted with no basis and no note on poisoning | §4.2: 0.1 wt% master alloy = 0.005 wt% Ti + 0.001 wt% B, which is the standard 1 kg/t dose — **correct for this alloy** (no Zr, no Cr); flagged as a confounder if a 7075 arm is cast on the same line | Samuel et al. 2023 (1 kg/1000 kg → 0.005 % Ti, 0.001 % B, 100–150 µm grains); Zr-poisoning literature |

---

## 2. Corrected charge tables

### 2.1 Method, shown so it can be checked

For each element *e* with target ingot fraction *wₑ* and assumed loss fraction *Lₑ*:

```
charge_e   = (w_e × 500 g) / (1 − L_e)          [g to weigh out]
ingot_e    = charge_e × (1 − L_e) = w_e × 500 g [g in the solidified ingot]
```

with `L(Zn) = 0.07`, `L(Mg) = 0.10`, `L(all others) = 0`.

### 2.2 Candidate 2 (the headline alloy) — worked in full

Target: **Al 87.805 / Zn 7.803 / Mg 3.024 / Cu 1.335 / Si 0.013 / Fe 0.020 wt%.**

| Element | Target wt% | Target ingot mass (g) | **Charge to weigh (g)** | Ingot mass after assumed loss (g) | Old protocol charge (g) |
|---|---|---|---|---|---|
| Al | 87.805 | 439.026 | **439.026** | 439.026 | 439.03 |
| Zn | 7.803 | 39.017 | **41.953** | 39.017 | 41.75 |
| Mg | 3.024 | 15.120 | **16.800** | 15.120 | 16.63 |
| Cu | 1.335 | 6.673 | **6.673** | 6.673 | 6.67 |
| Fe | 0.020 | 0.098 | **0.098** | 0.098 | 0.10 |
| Si | 0.013 | 0.065 | **0.065** | 0.065 | 0.07 |
| **Total** | 100.000 | **500.000** | **504.615** | **499.999** | 504.25 |

Arithmetic, one line per volatile element:

- Zn: `39.017 / (1 − 0.07) = 39.017 / 0.93 = 41.953 g`
- Mg: `15.120 / (1 − 0.10) = 15.120 / 0.90 = 16.800 g`
- Al: `439.026 / (1 − 0) = 439.026 g` (balance element — **not** overcharged)

**Verification of the previous reviewer's check.** Normalising the 504.25 g charge
*without* applying any loss gives Al 87.07 / Zn 8.28 / Mg 3.30 / Cu 1.32 — exactly the
figure in `EXPERIMENTAL_DESIGN.md` §11.1. That figure is therefore a **no-loss
scenario**, not the expected outcome. Under the stated 7 %/10 % losses the charge yields
Al 87.81 / Zn 7.80 / Mg 3.02 — the target. **The old numbers were not wrong; the old
document was silent about why they were those numbers.** Both are now stated.

**If no loss occurs** (e.g. the melt is covered with Ar and Mg loss is ~2 %), the
corrected charge yields Al 87.00 / Zn 8.31 / Mg 3.33 — a ~10 % relative overshoot on
Mg. This is the residual risk of philosophy (a) and is why §4.2 mandates a post-cast
OES/EDS chemistry check on every heat.

### 2.3 All three candidates

| Element | C1 target wt% | C1 charge (g) | C2 target wt% | C2 charge (g) | C3 target wt% | C3 charge (g) |
|---|---|---|---|---|---|---|
| Al | 87.100 | 435.501 | 87.805 | 439.026 | 87.970 | 439.848 |
| Zn | 7.068 | 38.001 | 7.803 | 41.953 | 7.968 | 42.836 |
| Mg | 4.656 | 25.868 | 3.024 | 16.800 | 3.067 | 17.038 |
| Cu | 1.152 | 5.762 | 1.335 | 6.673 | 0.962 | 4.812 |
| Si | 0.011 | 0.057 | 0.013 | 0.065 | 0.013 | 0.067 |
| Fe | 0.011 | 0.055 | 0.020 | 0.098 | 0.020 | 0.100 |
| **Total charge (g)** | — | **505.245** | — | **504.615** | — | **504.701** |
| **Ingot after loss (g)** | — | **499.998** | — | **499.999** | — | **499.999** |

**Weighing order:** Al first (largest, lowest vapour pressure), then Cu, then the minor
elements, then **Zn and Mg last, immediately before the refiner and the pour**, to
minimise hold-time volatilisation. Pre-heat all charge to >150 °C before adding (moisture).

---

## 3. What the literature actually says about incipient melting (defect 2)

This is the number that can scrap a campaign, so it is stated carefully.

1. **Wrought AA7075 datasheet (Alcoa, via ASM MatWeb / distributor datasheets):**
   *solidus* **477 °C (890 °F)**, *liquidus* 635 °C (1175 °F), with the explicit note
   that "homogenization may raise the eutectic melting temperature 20–40 °F but usually
   does not eliminate eutectic melting." → **The old 477 °C figure is real, but it is
   the wrought-7075 solidus, not a measurement on the student's cast alloy.**
   <https://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA7075T6>

2. **Sandia SAND2022-9908, "Incipient Melting in AA7075" (Brehm et al., 2022, DOI
   [10.2172/1876952](https://doi.org/10.2172/1876952)):** the *theoretical* incipient-melting
   temperature for AA7075 is **905–910 °F ≈ 485–488 °C**; the first *optical* signs of
   incipient melting (Al₂CuMg agglomeration) appeared at 925 °F ≈ 496 °C in unstrained
   material; obvious eutectic networking only at 1035 °F. Crucially, the authors state
   that **because forging strain was not applied, the onset in this study is higher than
   in practice**. A cast alloy carries its own residual stress and far coarser
   segregation, so its onset will be **lower**, not higher, than the wrought figure.

3. **Wang et al., *Materials & Design* 221 (2022) 110975, DOI
   [10.1016/j.matdes.2022.110975](https://doi.org/10.1016/j.matdes.2022.110975)** —
   the most directly relevant source, because it measures **as-cast** Al–Zn–Mg–Cu by DSC:
   - the α-Al + M (Mg(ZnAlCu)₂) eutectic dissolves with a peak at **479.8–482.0 °C**;
   - the S (Al₂CuMg) / Cu-enriched phase at **484.4–491.3 °C**;
   - the S phase *precipitates* at **462–472 °C during solidification**;
   - alloys with **(Cu + Mg) > 4.24 wt%** — which includes the candidate (Cu+Mg = 4.36)
     — "may be overburnt at 480 °C", and retain residual S even after 475 °C/24 h.

4. **Wen et al., *Rare Metals* 37 (2018) 376, DOI
   [10.1007/s12598-016-0768-6](https://doi.org/10.1007/s12598-016-0768-6):**
   Mg(Zn,Cu,Al)₂ dissolves *directly* into the matrix only at **470–475 °C**; at
   450–465 °C it instead **transforms into S(Al₂CuMg)**, which is then much harder to
   dissolve. → **The solution temperature must be at the top of the window, not the
   bottom** — the opposite of what a safety-first instinct suggests, which is exactly
   why the ceiling must be established by DSC rather than guessed.

**Composition dependence, stated plainly:** the eutectic-melting onset falls as
**Zn + Mg + Cu** rises and as the **Zn:Mg ratio falls** (more S/T-phase formers). The
candidate sits at Zn+Mg+Cu = 12.2 wt%, Zn:Mg = 2.58, Cu+Mg = 4.36 wt% — i.e. in the
**highest-risk corner** of the family. Its onset is therefore plausibly in the
**470–480 °C** band, and the protocol's old "stay below 477 °C, setpoint 475 °C" left a
2 °C margin. **That is not a safe process window.**

**Corrected rule:** solution setpoint **470 °C**, hard ceiling **477 °C**, and any
recorded excursion above **480 °C invalidates the heat** pending metallographic
inspection. If a DSC is available, measure the onset on the *actual cast alloy* and set
the ceiling 10 °C below it. If no DSC is available, the 470 °C setpoint is the
conservative fallback — but it is a fallback, and this must be said in any write-up.

---

## 4. Corrected procedure — aluminium branch

### 4.1 Casting

1. **Charge** per §2. Pre-heat all charge and all tools to **>150 °C** (moisture).
2. **Crucible:** graphite-clay or SiC, coated with refractory wash. **Not mild steel**
   (Fe pickup; this alloy is Fe-sensitive and Fe is a model input). Record the crucible
   type for every heat.
3. **Melt** at **700 ± 15 °C**. Do not exceed 730 °C (accelerates Zn/Mg loss and oxide
   formation). Cover with Ar or a proprietary flux if available.
4. **Mould pre-heat:** steel mould to **250 ± 50 °C** (200–300 °C). Record. An unheated
   mould causes cold shuts and columnar grains and is a recorded confounder.
5. **Grain refiner:** Al-5Ti-1B master alloy at **0.1 wt% of the charge**
   (= 0.005 wt% Ti, 0.001 wt% B — the standard 1 kg/t dose). Add at 700–720 °C, stir,
   and **hold no longer than 30 min** before pouring (fading). Note: if a 7075 arm is
   cast on the same line, its Cr (~0.2 wt%) and any Zr **poison** the refiner; dose
   separately and do not reuse the crucible without cleaning.
6. **Degas — mandatory step, not a note.** Argon via rotary degasser or lance,
   **10–20 min** at 700–720 °C, then skim. C₂Cl₆ tablets are a *fallback only*: they
   generate HCl/Cl₂ and must be used under fume extraction with a respirator (see §6).
   **Record the method and duration.** Porosity is the dominant scatter source for a
   tensile result and is the difference between an interpretable and an uninterpretable
   campaign.
7. **Pour** at **690 ± 10 °C** into the pre-heated mould. Record actual pour temperature
   from an immersed thermocouple, not the furnace setpoint.

### 4.2 Tolerances and invalidation rules

| Step | Target | Tolerance | If exceeded |
|---|---|---|---|
| Melt temperature | 700 °C | ± 15 °C | >730 °C: discard, re-melt (composition drift) |
| Pour temperature | 690 °C | ± 10 °C | >720 °C or <660 °C: record, flag heat |
| Mould pre-heat | 250 °C | ± 50 °C | outside 150–350 °C: record, flag heat |
| Refiner addition | 0.1 wt% | ± 0.02 wt% | record actual mass added |
| Degassing | Ar, 10–20 min | ≥10 min | <10 min: record, expect higher porosity |
| Homogenisation | 475 °C / 12 h | ± 5 °C, ± 0.5 h | see §4.3 |
| **Solution treatment** | **470 °C / 2 h** | **± 3 °C, ± 10 min** | **any reading >480 °C invalidates the heat**; 477–480 °C: metallography before use |
| Quench medium | water 20–30 °C | ≤ 40 °C | >40 °C: re-quench not possible; flag specimen |
| Quench transfer | ≤ 5 s (target) | hard limit 10 s | >10 s: mark specimen; do not pool with fast-quenched bars |
| Ageing | 120 °C / 24 h | ± 3 °C, ± 15 min | outside: re-age from solution treatment if quench delay was short |

*Tolerance basis:* AMS 2750 furnace-class uniformity (± 5.6 °C / ± 10 °F in this range)
and ASTM E220 thermocouple calibration (± 2.2 °C or 0.75 % for type K). A furnace that
cannot hold ± 5 °C uniformity cannot execute this protocol; confirm before scheduling.

### 4.3 Homogenisation — **mandatory**

**475 °C / 12 h**, then air cool. (Raised from the old 465 °C/12 h.)

Justification: Wang et al. (2022) show that at **465 °C** the as-cast M and S phases
largely *survive* (and M partly *transforms to* S), whereas at **470 °C** most dissolve
and at **475 °C** dissolution is essentially complete for comparable alloys. Interdendritic
dissolution takes ≈4.5 h and solute homogenisation 4.4–5.6 h at 475 °C, so 12 h is
sufficient. Homogenisation also **raises the incipient-melting onset** (the Alcoa note
says 20–40 °F), which widens the very thin solution-treatment window of §3. Dropping it
is not defensible for a cast alloy; the design document's plan to use it as an
experimental factor is fine, but the **"no homogenisation" arm must be reported as
out-of-spec**, not as an equivalent route.

### 4.4 Solution treatment and quench

8. **Solutionise at 470 ± 3 °C for 2 h**, load into a furnace already at temperature.
9. **Quench: agitated cold water at 20–30 °C (never above 40 °C); transfer ≤10 s,
   target ≤5 s.** Record the transfer time and the water temperature for every
   specimen. Do not use air, polymer, or boiling water.
10. **Why the quench dominates the result:** quenching controls whether the T6 ageing
    response exists at all. Starink et al. (2015) show the quench-sensitivity reactions
    are a high-temperature reaction (≈450→350 °C, mostly S-Al₂CuMg), a medium-temperature
    reaction (≈350→250 °C, η-Mg(Al,Cu,Zn)₂) and a low-temperature reaction (≈250→150 °C).
    The high-temperature reaction is suppressed only above roughly **10 K/s**, and the
    η reaction needs substantially faster cooling. An air cool (≈1–5 K/s) loses solute to
    coarse quench-induced precipitates and **can cost tens of MPa of age-hardening
    response**; that is why "cold water" is not optional and why the medium temperature
    must be controlled. Agitated water on a small section gives the required rate; still
    water in a thick section may not.
11. **Record** (mandatory log per specimen): transfer time, water temperature, water
    agitation on/off, time from quench to start of ageing.

### 4.5 Artificial ageing

12. **T6: 120 ± 3 °C for 24 h (± 15 min)**, then air cool. The T73 branch (160 °C/8 h)
    may be run as a *secondary* comparison only.

### 4.6 Characterisation

13. Post-cast chemistry by **OES/EDS on every heat** (mandatory — §2.2). The composition
    that goes into the model is the **measured** composition, not the nominal one.
14. Optical/SEM + EDS; XRD; Vickers HV (10 indents, before and after ageing);
    Archimedes density (ASTM B962) as a porosity proxy; tensile per §4.7.

### 4.7 Specimen extraction (missing from the old protocol)

15. Cast a **dedicated test-bar mould** (a bar or plate with a riser), not a simple
    ingot, so that a sound, riser-free region exists for machining.
16. Extract all tensile specimens from the **lower-centre** of the casting: below the
    riser (shrinkage porosity) and inside the chill skin (fine-grain, different
    composition). Keep every specimen at the **same height and orientation**; the
    specimen axis parallel to the casting's thermal axis.
17. **Record the position of every specimen** (height, radial offset). n ≥ 3 specimens
    per heat, H ≥ 3 heats (the design document's two-level variance requirement).
18. Machine to ASTM E8/E8M subsize geometry; verify dimensions before testing. Run the
    certified AA7075-T6 reference bar on the same machine, same week (§2.2 of the design
    document) before trusting any candidate number.

---

## 5. Magnesium branch — corrected windows

**Verdict on the old Mg protocol: candidate 3's 525 °C/8 h is unsafe and must not be run.**

- The Mg–Al system has a **Mg₁₇Al₁₂ eutectic at ≈437 °C**. Candidate 3 contains
  **8.94 wt% Al**, so that eutectic is present in its as-cast microstructure.
- Heating it to **525 °C** — 88 °C above the eutectic — will locally melt the
  grain-boundary eutectic. In magnesium this is not a "quality" defect: locally molten
  Mg in a furnace is a **fire and burn hazard**, and the ingot is scrap.
- 525 °C/8 h is a **Mg–RE (WE43-class)** schedule. It is valid only for alloys with
  essentially no aluminium (WE43 contains < 0.01 wt% Al). It was applied here because
  the generator's `_classify()` routes any alloy with > 2 wt% total rare earth to the
  `mg_re` family — **ignoring the 8.94 wt% Al that actually controls the melting onset.**
  That is a genuine logic defect in `mg_protocol.py`, not a typo.
- **Corrected window for candidate 3: ≤ 415 °C, ≤ 8 h**, and it must **not be run at all
  without a DSC on the actual cast alloy**, because Ca (1.64 wt%) and Y (4.55 wt%) form
  additional low-melting phases that can shift the onset below 415 °C.

| Mg candidate | Old schedule | Verdict | Corrected |
|---|---|---|---|
| Mg-1 (Mg-4.55Li-1.82Ca-0.52Zn) | 340 °C/2 h, no age | Acceptable in principle (Mg–Li is low-melting by design) | 340 ± 5 °C / 2 h; DSC still advised |
| Mg-2 (Mg-8.41Al-1.85Ca-0.92Sr) | 415 °C/18 h | Borderline: 415 °C is the AZ91 T4 temperature, but 8.41 Al + Ca/Sr may lower the eutectic | ≤ 410 °C; DSC required |
| Mg-3 (Mg-8.94Al-4.55Y-1.64Ca) | **525 °C/8 h** | **UNSAFE — do not run** | **≤ 415 °C, and only with a DSC** |

The design document (§8.4) already recommends dropping the Mg branch for this campaign.
**This correction reinforces that: do not melt magnesium in this campaign.** One
student, one aluminium campaign.

---

## 6. Safety

### Aluminium branch

- **Molten Al + moisture = steam explosion.** Pre-heat charge, mould, tools and any
  scrap to >150 °C. Never add wet, damp or rusty charge. Never pour into a damp mould.
- **Zinc fume.** Zn has appreciable vapour pressure at 700 °C (bp 907 °C). Metal-fume
  fever is a real hazard: local extraction, and do not lean over the crucible.
- **Quench burns and steam.** A 470 °C ingot into water produces violent steam. Use long
  tongs and a face shield, quench in a **deep, open** bucket behind a shield, never in a
  sealed container, and keep water off the floor. Transfer times are short — rehearse the
  motion before the heat.
- **C₂Cl₆ (hexachloroethane) is toxic.** It decomposes to HCl, Cl₂ and chlorinated
  organics; exposure is associated with liver effects. Use **only** under fume extraction
  with a respirator; prefer argon. (ATSDR Toxicological Profile; ILO ICSC 0051.)
- **Dross and furnace:** never disturb a crust with a wet tool; keep a dry sand/vermiculite
  bucket and a Class D extinguisher at the furnace.
- **Al-5Ti-1B** master alloy is safe to handle, but avoid breathing fines.

### Magnesium branch (if it is ever run — it should not be, this campaign)

- **Never melt Mg without SF₆/CO₂ cover gas (0.5–1 % SF₆) or a protective flux.** Molten
  Mg burns in air with a white flame near 3000 °C.
- **Never use water on a Mg fire.** Dry sand, dry graphite or a Class D extinguisher only.
- **Pre-heat everything to >150 °C** — molten Mg + water is explosive.
- **No rust, iron oxide or silica refractory in contact with the melt** (thermite-type
  reduction / violent reaction).
- **SF₆ is a potent greenhouse gas** (~23 500 GWP): use the minimum flow and ventilate.
- Work in a fume hood; MgO fume and SF₆ decomposition products are respiratory hazards.
- The 525 °C schedule of §5 is itself a safety hazard, not merely a quality defect.

---

## 7. Must be confirmed with the laboratory before scheduling

Do **not** assume any of these exist. Each is a gate.

1. **DSC** — to measure the incipient-melting onset of the *cast* alloy. Without it, the
   §3 ceiling is inherited, not measured, and the 470 °C setpoint is a fallback.
2. **OES or EDS** for post-cast chemistry on every heat — without it the charge
   philosophy of §0 cannot be verified and the composition is unknown.
3. **Furnace with ± 5 °C uniformity and a calibrated thermocouple/recorder** (AMS 2750
   class). If the furnace cannot hold ± 5 °C, the solution-treatment window is unachievable.
4. **Argon degassing equipment** (rotary degasser or lance + Ar supply). Without it,
   expect porosity-dominated scatter and an uninformative tensile result.
5. **Agitated quench tank with temperature control** and a stopwatch. Without controlled
   transfer time, the T6 response is not reproducible.
6. **Mould-preheat oven** capable of 200–300 °C.
7. **Crucible**: graphite-clay or SiC. If only mild steel is available, expect Fe pickup
   and say so in the write-up.
8. **Tensile machine + certified AA7075-T6 reference bar** (design document control C1).
   If the reference does not land in 470–540 MPa, stop and fix the machine.
9. **Specimen machining to ASTM E8/E8M subsize** dimensions.
10. **Vickers hardness tester** and an Archimedes density kit (0.1 mg balance).
11. **Fume extraction** if C₂Cl₆ is to be used at all.

---

## 8. Defect 7 — the experiment log (documentation only)

`outputs/experiment_log.json` holds **15 records, all with `measured: {}`**, none of
which is the headline Al–3.0Mg–7.8Zn–1.3Cu candidate (the log tracks other proposals
from `next_experiments.csv`). Anyone reading the published release would reasonably
assume the log tracks the alloy the project is about. **The candidate has no record.**

This is a **documentation defect, not a laboratory defect.** A separate worker owns the
tooling fix. The requirement is: before the first tensile test, a record for the
candidate (composition, route, predicted YS 624.5 MPa with the [517, 732] MPa conformal
interval) must exist in the log, and every measured value must be written back to it.
Nothing in this document changes that file.

---

## 9. What remains uncertain, and why

1. **The true incipient-melting onset for this cast alloy is unknown.** The 470 °C
   setpoint is a conservative inference from wrought-7075 solidus data (477 °C) and
   as-cast DSC literature (479–491 °C peaks). It is **not** a measurement on this alloy.
   A DSC is the only way to close this.
2. **The loss fractions (Zn 7 %, Mg 10 %) are assumptions with no source for this
   furnace.** They come from the original protocol. A single pilot heat with pre- and
   post-melt weighing plus OES chemistry would replace them with measured values. Until
   then, philosophy (a) is correct in principle but its *inputs* are estimated.
3. **Two hours at 470 °C may be insufficient** to dissolve the S phase in a high-(Cu+Mg)
   cast alloy; Wang et al. used 24 h at 475 °C. The 2 h figure is inherited from wrought
   practice. If the microstructure after solution treatment shows residual S, the hold
   time is the variable to change — but only with a DSC-confirmed ceiling.
4. **The achieved quench rate is not measured.** The protocol specifies the medium and
   the transfer time, not the K/s. Without a thermocouple in the specimen, the quench
   rate is described qualitatively, exactly as the design document warns.
5. **The model was trained on wrought data with zero as-cast records** (design document
   §9.3). The honest prior is that 625 MPa **overshoots** for a cast + T6 specimen, and
   the literature band for cast Al–Zn–Mg–Cu T6 (280–540 MPa, Ghiaasiaan & Shankar 2019)
   lies below the prediction. This is a limitation of the *experiment's* interpretation,
   not something this protocol can fix.
6. **The Mg branch cannot be made safe** without a DSC and cover-gas capability. The
   corrected windows in §5 are upper bounds, not validated schedules.
7. **Grain refiner interaction** is only benign for the candidate itself; if a
   7075-composition arm is added, Cr/Zr poisoning must be handled separately.
8. **The furnace and thermocouple tolerances assumed here (AMS 2750-class) may not match
   ITB equipment.** Confirm item 3 in §7 before trusting any ± °C figure in §4.2.

---

## 10. References

1. ASM MatWeb / Alcoa, *Aluminum 7075-T6; 7075-T651* — solidus 477 °C, liquidus 635 °C,
   eutectic-melting note. <https://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA7075T6>
2. Brehm, J., Buckner, J., Profazi, C., Hickman, A. *Incipient Melting in AA7075*,
   Sandia National Laboratories, SAND2022-9908 (2022). DOI
   [10.2172/1876952](https://doi.org/10.2172/1876952).
3. Wang, Y., Hou, L. et al. *Tuning homogenization of high-strength aluminum alloys
   through thermodynamic alloying approach.* Materials & Design **221**, 110975 (2022).
   DOI [10.1016/j.matdes.2022.110975](https://doi.org/10.1016/j.matdes.2022.110975).
4. Wen, K., Xiong, B.-Q. et al. *Transformation and dissolution of second phases during
   solution treatment of an Al–Zn–Mg–Cu alloy containing high zinc.* Rare Metals **37**,
   376–380 (2018). DOI [10.1007/s12598-016-0768-6](https://doi.org/10.1007/s12598-016-0768-6).
5. Starink, M. J., Milkereit, B., Zhang, Y., Rometsch, P. A. *Predicting the quench
   sensitivity of Al–Zn–Mg–Cu alloys.* Materials & Design **88**, 958–971 (2015). DOI
   [10.1016/j.matdes.2015.09.058](https://doi.org/10.1016/j.matdes.2015.09.058).
6. Milkereit, B., Starink, M. J., Rometsch, P. A., Schick, C., Kessler, O. *Review of the
   Quench Sensitivity of Aluminium Alloys.* Materials **12**, 4083 (2019). DOI
   [10.3390/ma12244083](https://doi.org/10.3390/ma12244083).
7. Graf, G. et al. *Quench rate sensitivity of age-hardenable Al-Zn-Mg-Cu alloys with
   respect to the Zn/Mg ratio.* Acta Materialia **227**, 117727 (2022). DOI
   [10.1016/j.actamat.2022.117727](https://doi.org/10.1016/j.actamat.2022.117727).
8. Gao, W., Zhu, T., Chen, Z. W. *Dissolution of Eutectic β-Mg₁₇Al₁₂ Phase in Magnesium
   AZ91 Cast Alloy at Temperatures Close to Eutectic Temperature.* J. Mater. Eng.
   Perform. **19**, 860–867 (2010). DOI
   [10.1007/s11665-009-9539-y](https://doi.org/10.1007/s11665-009-9539-y).
9. Samuel, E. et al. *A Review on Fundamentals of Grain Refining of Al-Si Cast Alloys.*
   IntechOpen (2023). DOI [10.5772/intechopen.112987](https://doi.org/10.5772/intechopen.112987)
   — Al-5Ti-1B at 1 kg/t gives 0.005 % Ti + 0.001 % B, grains 100–150 µm.
10. *A Novel Insight Toward Zr Poisoning on Grain Refinement of Al-5Ti-1B.* Metall.
    Mater. Trans. B (2024). DOI
    [10.1007/s11663-024-03140-z](https://doi.org/10.1007/s11663-024-03140-z).
11. ASTM E8/E8M, *Standard Test Methods for Tension Testing of Metallic Materials.*
    <https://www.astm.org/Standards/E8.htm>
12. AMS 2750, *Pyrometry* (furnace-class temperature uniformity); ASTM E220,
    *Calibration of Thermocouples by Comparison Techniques.*
13. *Effect of Degassing Parameters on Mechanical Properties of EN AC-46000 Gravity Die
    Castings.* PMC9740475. <https://pmc.ncbi.nlm.nih.gov/articles/PMC9740475/>
14. ATSDR, *Toxicological Profile for Hexachloroethane*; ILO ICSC 0051,
    *Hexachloroethane.*
15. Ghiaasiaan, R. & Shankar, S. *Effect of Alloy Composition on Microstructure and
    Tensile Properties of Net-Shaped Castings of Al–Zn–Mg–Cu Alloys.* Int. J.
    Metalcasting **13**, 300–310 (2019). DOI
    [10.1007/s40962-018-0254-z](https://doi.org/10.1007/s40962-018-0254-z).
16. Aloy project release, DOI [10.5281/zenodo.22844739](https://doi.org/10.5281/zenodo.22844739)
    — `docs/EXPERIMENTAL_DESIGN.md`, `outputs/lab_protocols.*`, `outputs/candidates_final.csv`,
    `outputs/experiment_log.json`.

---

## Appendix — status of the generator (`src/aloy/protocol.py`, `src/aloy/mg_protocol.py`)

**The generator was NOT modified.** Reason: editing it would create a fork between the
code and the published release, and re-running it would overwrite
`outputs/lab_protocols.txt` / `.json`, which are frozen by `MANIFEST.sha256` and
referenced by the Zenodo DOI. I was instructed not to modify those files in place, and
editing the generator alone would leave the repository in a state where running
`python -m aloy.protocol` silently destroys the frozen artefacts.

**Therefore the generated files and this document now differ.** Specifically, the
generator still:

- applies the overage without printing the total charge, the loss fractions, or the
  "if no loss occurs" case (defect 1);
- prints "477 C" with no citation and keeps the 475 °C setpoint (defect 2);
- states "cold water" in English but leaves `air dingin` in `README.md` (defect 3);
- emits no tolerances (defect 4);
- labels homogenisation "optional" (defect 5);
- emits the unsafe 525 °C/8 h for Mg candidate 3, because `_classify()` routes on rare
  earths and ignores the 8.94 wt% Al (defect 6);
- prints "(balance = Al, add last to minimise oxidation)", which is misleading — Al is
  the balance element and is charged *first*, and Cu/Fe/Si are the minor additions.

**A separate fix is required, and it should be done as a new release version** (edit the
generator, re-run it, re-issue the release with a new DOI and a refreshed manifest), not
as a silent edit to a published artefact.
