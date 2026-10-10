# ROADMAP — *Aloy*, re-scoped for a semester-3 student

**Author:** Abdul Afif Al-Kaysan, Metallurgical Engineering, Institut Teknologi Bandung
**Date:** 2026-10-06 · **Status of the project:** software published (Zenodo DOI
[10.5281/zenodo.22844739](https://doi.org/10.5281/zenodo.22844739)), **never experimentally
validated**
**Position:** semester 3 · no lab access · no supervisor relationship · coursework in progress
**Supersedes:** the scheduling assumptions implicit in `docs/EXPERIMENTAL_DESIGN.md` §10 and
`proposal/PKM-RE-2027-proposal.md`. Those documents are **not edited**. This one governs *when*
things happen; `PROTOCOL_CORRECTED.md` still governs *how* the experiment is done once it happens.

---

## 0. What changed, stated plainly

The previous plan — casting heats, DSC, OES chemistry, an AMS-2750-class furnace, argon
degassing, a certified AA7075-T6 reference bar, 3 heats × 3 specimens, and a PKM-RE proposal to
fund it — was **written for a student who has a laboratory**. He does not. He is in semester 3,
has no supervisor, no equipment, and coursework still in progress. That plan was pitched two to
three years too early. It is **deferred, not cancelled**.

The important thing to say clearly:

> **The computational work is not the consolation prize. It is the part he can actually do now,
> and it is the reason he will be able to do the experiment later.**

Three reasons that is not a platitude:

1. **The pipeline is pure computation.** It needs a laptop, not a lab. Everything in `src/aloy/`
   runs on the machine it already runs on.
2. **The highest-value scientific upgrade is computational and is doable this semester.** The
   design document itself identifies it: the model's process channel is a single ordinal scalar,
   and the honest upgrade is to add continuous process features and re-train (§2 below).
3. **A student who walks into a lab with a DOI'd, reproducible pipeline, a pre-registered
   decision rule, and a corrected protocol is a different proposition from a student who walks in
   with an idea.** The existing artefacts *are* the calling card. The computational work this
   semester is what converts "I want to join your lab" into "I have something to run in your lab,
   and here is the document that says exactly what I need."

What follows is a plan that respects his actual position.

---

## 1. Capability audit — what the experimental design requires, honestly marked

Every row below is a requirement pulled from `EXPERIMENTAL_DESIGN.md` §9, §10 and
`PROTOCOL_CORRECTED.md` §7. The verdict column is blunt.

| Requirement | Source | Verdict |
|---|---|---|
| **A supervisor with NUPTK** | PKM rule; protocol sign-off | **Requires a supervisor** — he has none. This is the single largest gate. |
| **Team of 3–5 active ITB undergraduates, ideally ≥2 cohorts** | PKM rule | **Requires a supervisor + people** — he has one name (his own). |
| **Melting furnace (induction w/ atmosphere, or resistance + flux/Ar cover)** | Design §9; Protocol §4.1 | **Requires a lab placement** |
| **DSC for the incipient-melting onset of the *cast* alloy** | Protocol §7.1, §3 | **Requires a lab placement + supervisor.** Without it the 470 °C setpoint is inherited, not measured. |
| **OES or EDS for post-cast chemistry on every heat** | Protocol §7.2 | **Requires a lab placement** |
| **Furnace with ±5 °C uniformity + calibrated thermocouple (AMS 2750 class)** | Protocol §7.3 | **Requires a lab placement.** If ITB's furnaces cannot hold ±5 °C, the solution-treatment window is unachievable and the design must be redrawn. |
| **Argon degassing (rotary degasser or lance + Ar supply)** | Protocol §7.4 | **Requires a lab placement** |
| **Agitated quench tank with temperature control + stopwatch** | Protocol §7.5 | **Requires a lab placement** |
| **Mould-preheat oven, 200–300 °C** | Protocol §7.6 | **Requires a lab placement** |
| **Graphite-clay or SiC crucible + refractory wash** | Protocol §7.7 | **Requires funding** (consumable) + a lab placement |
| **Tensile machine** | Protocol §7.8 | **Requires a lab placement** |
| **Certified AA7075-T6 reference bar (control C1)** | Design §2.2, §5 | **Requires funding.** Non-negotiable; an unknown 7xxx offcut is not a substitute. |
| **Specimen machining to ASTM E8/E8M subsize** | Protocol §7.9 | **Requires a lab placement** |
| **Vickers hardness tester + Archimedes density kit (0.1 mg balance)** | Protocol §7.10 | **Requires a lab placement** |
| **SEM/EDS + XRD** | Protocol §4.6 | **Requires a lab placement** |
| **Fume extraction (if C₂Cl₆ is used at all)** | Protocol §7.11 | **Requires a lab placement** |
| **Charge metal: Al, Zn, Mg, Cu (~505 g per heat) + Al-5Ti-1B refiner** | Protocol §2, §4.2 | **Requires funding** |
| **3 heats × 3 tensile specimens + 3 reference bars** | Design §4, §10.1 | **Requires funding + a lab placement.** The H = 3 minimum must not be cut. |
| **Extrusion / rolling mill** | Design §9 | **Not realistic before semester 5–6**, and arguably out of scope entirely — it needs a mill the project has no path to. |
| **TEM / APT (to prove the η′ mechanism)** | Design §9 | **Not realistic before semester 5–6** |
| **NIMS creep / corrosion data** | Design §9 | **Not realistic before semester 5–6** (registration-gated) |
| **The *whole campaign* as designed** | Design §10 | **Not realistic before semester 5–6.** Realistically: semester 6 or later, and only after a lab placement has actually happened. |

**Summary verdict.** Of the ~20 requirements, **zero are available today**. Roughly half become
available *with a lab placement* (which he does not yet have and must earn), several need *a
supervisor*, several need *funding*, and three are genuinely out of reach before semester 5–6.
**Nothing in the experimental design is executable this semester, and no amount of planning will
change that.** The plan below therefore spends this semester on the one thing that *is*
executable.

---

## 2. What he can do NOW (semester 3), with zero lab access

### 2.1 The decisive question: can he add continuous process features and re-train?

The design document calls this "the most important scientific recommendation in this document"
(§3.2), because the model's process channel is a single ordinal scalar
(`_PROC_ENCODE` in `src/aloy/models.py`: `as_cast 0.0 … aged_peak 1.0`) with **no continuous
process variables**. I checked the code and the data directly.

**What the current training data actually contains.** `src/aloy/data.py::load_mendeley_al()` reads
`data/raw/mendeley_al_alloys.csv` (Bhat/Barnard/Birbilis 2023, DOI `10.17632/b6br4yk6r3.1`). I
inspected it:

```
shape: (1154, 31)
columns: Processing, Ag, Al, B, Be, Bi, Cd, Co, Cr, Cu, Er, Eu, Fe, Ga, Li, Mg, Mn,
         Ni, Pb, Sc, Si, Sn, Ti, V, Zn, Zr, Elongation (%), Tensile Strength (MPa),
         Yield Strength (MPa), class
columns containing 'temp'/'time'/'hour'/'quench'/'solut'/'age':  []   ← none
rows with 'cast' in the Processing label:                        0
```

So: **the training set has no continuous process columns at all.** There is no solution
temperature, no ageing temperature, no ageing time, no quench rate anywhere in the source file.
The `_PROC_ENCODE` map is derived from a free-text `Processing` string, and it is the *only*
process information the model ever sees. Retraining with continuous process features is therefore
**impossible on the current data** — the columns do not exist. `assemble_matrix()` has nothing to
assemble. This is not a code problem; it is a data problem.

**So the question becomes: does such a dataset exist publicly?** It does. I found it and verified
it by downloading and parsing it.

> **`Wrought Aluminum Alloys_01` — Mendeley Data, DOI
> [10.17632/gw8fvv7wth.2](https://doi.org/10.17632/gw8fvv7wth.2) (v2, published 15 July 2026),
> contributor Xin Chang, licence CC BY 4.0.**
> File: `Aged forged Al alloy.xlsx` (76 kB). Companion GitHub repository:
> <https://github.com/UQ43815685/ageing_behaviour_Al_alloys_with_feature_screening>
> (contains `dataset.xlsx`, the 430-row subset).
> Rows 1–430 are sourced from Hu, Tan, Knibbe, Jiang, Li & Zhang, *Mater. Sci. Eng. A* **917**,
> 147381 (2024), DOI [10.1016/j.msea.2024.147381](https://doi.org/10.1016/j.msea.2024.147381);
> the remainder are from literature and the authors' own measurements.

**Verified contents** (I downloaded and parsed the file; these are measured, not claimed):

| Column | Meaning | Observed range (n = 524) |
|---|---|---|
| `Si, Fe, Cu, Mn, Mg, Cr, Zn, V, Ti, Zr, Li, Ni, Be, Sc` | composition, wt% | Al balance 82.4–99.1 wt% (all rows Al ≥ 82 wt%) |
| **`Tsol`** | **solution-treatment temperature (°C)** | **450 – 560** |
| **`Tage`** | **ageing temperature (°C)** | **25 – 290** |
| **`tage`** | **ageing time (h)** | **0 – 1440** |
| `YS`, `UTS`, `El` | yield strength, UTS, elongation | YS 62–684 MPa (475 rows non-null) |
| `Reference (APA)` | provenance string | — |

**Critically: 192 rows are 7xxx-like (Zn ≥ 4 wt%) and have `Tsol`, `Tage`, `tage` and `YS` all
present.** 25 rows sit at Zn ≥ 6, Mg ≥ 2, Cu ≥ 1 — i.e. the model's own candidate neighbourhood
(candidate 2 is Al–3.0Mg–7.8Zn–1.3Cu). The Zn maximum in the dataset is 8.6 wt%, so the
candidate's 7.8 wt% Zn is inside the covered range.

**Verdict: the "add continuous process features and re-train" upgrade is FEASIBLE NOW.** The data
exists, is openly licensed (CC BY 4.0), is small enough to download in seconds, and contains
exactly the three continuous columns the design document asked for.

**Two honest caveats that must be stated, because they change what the upgrade can claim:**

1. **It does not fix the as-cast gap.** The dataset has no "processing route" column and no cast
   records in any usable sense — a handful of provenance strings mention casting, but the file
   has no field that distinguishes cast from wrought. It is, as its title says, *wrought* alloys.
   So after this upgrade the model will have **continuous process features but still zero as-cast
   records.** It will learn *process–property relationships within wrought material* — which is
   Jiang's actual achievement — and it will **still not be able to predict a cast specimen
   honestly.** That limitation stays in the abstract. Do not let the upgrade hide it.
2. **It is a different source from the current training set**, so combining them is a
   domain-shift problem, not a concatenation. The honest approach is to train on the new dataset
   *alone* first (it is self-consistent: one process family, complete process columns), measure
   its CV metrics, and only then attempt a combined model with a source indicator. Report both.

**What the upgrade produces, concretely:**

- A v0.2 surrogate whose feature matrix includes `Tsol`, `Tage`, `tage` (and `log10(tage)`, since
  0–1440 h spans four decades) as continuous inputs.
- An honest CV comparison against the current model (the current YS model: R² 0.79 CV / 0.746
  holdout, MAE 53 / 57 MPa). If the new features do not improve it, **that is a result and it
  gets reported** — the design document's whole ethic is that negative results are results.
- **A predicted process-response surface**: YS as a function of `Tage` and `tage` at fixed
  candidate composition, with a conformal band. This is a genuinely new object the project has
  never had, and — this is the strategic point — **it is testable with a far cheaper experiment
  than casting.** Validating a process-response surface needs a *furnace and a hardness/tensile
  tester*, not a melting line, not a DSC, not a certified reference bar. A supervised
  solution-treat-and-age campaign on **existing wrought 7075 bar** is a realistic semester-5
  experiment. This is the path from computation to experiment that does not require the full
  casting campaign first.

**Honest effort estimate.** Loading, harmonising the composition columns to `ELEMENT_COLS` mass
fractions, adding the features to `assemble_matrix()`, retraining, running the leak-free GroupKFold
comparison, and producing the response-surface figure: **40–80 hours of careful work, i.e. roughly
3–5 weeks part-time alongside coursework.** It is a semester-sized project, not a weekend. It
requires no money, no supervisor and no lab. It is the highest-value thing available to him.

**I also checked whether Jiang et al.'s own 1053-record dataset could be obtained.** It cannot:
the paper's Data Availability statement reads *"The data that support the findings of this study
are available from the corresponding author upon reasonable request."* It is not an open dataset.
Do not plan around it. (The Mendeley dataset above is the closest open equivalent.)

### 2.2 The other doable-now candidates, ranked

| Rank | Option | Value | Effort | Verdict |
|---|---|---|---|---|
| **1** | **Add continuous process features + re-train (§2.1)** | **High** — it is the design document's own top recommendation, it produces a new testable object (the process-response surface), and it moves the project from "composition prediction" to "process prediction", which is where the field's validated successes are (Jiang 2023). | 40–80 h | **Recommended.** Do this. |
| **2** | **Conformal calibration audit on a genuinely held-out slice** | **Medium–high** — the current interval (±107.5 MPa, 90.1 % empirical coverage on n_cal = 696) is the project's headline honest claim and its least-audited one. `credibility.py` calibrates on a 40 % split of a 1150-record set; a stricter audit (nested splits, coverage vs. composition distance, coverage in the 7xxx sub-domain specifically) would either strengthen the claim or find it is optimistic. Either outcome is publishable and cheap. | 10–20 h | **Do this second.** It is small, it directly defends the claim the experiment will test, and it can run alongside rank 1. |
| **3** | **Reproduce a published ML-alloy result as an external benchmark** | **Medium** — e.g. reproduce Jiang's TrAdaBoost or Li's Kriging pipeline on open data and report whether the published accuracy is reproducible. Genuine scientific value (reproducibility), but it needs the published data, and Jiang's is not open. | 30–60 h | **Defer.** The data availability is the blocker. |
| **4** | **Write the methods paper from existing work** | **Low–medium now, higher later** | 40–80 h | **Defer.** With no experimental validation and a non-novel composition, a standalone methods paper has a weak novelty case and `README.md` already says: fill `MANUSCRIPT_TEMPLATE.md` **"only after there is experimental data."** Keep that discipline. |
| **5** | **Build a small open-source tool** | **Low** | 20–40 h | **Skip for now.** The pipeline is already published and DOI'd. Packaging it further adds no science. |

**Recommendation: do rank 1, with rank 2 as a parallel small task.** They share the same code
paths (`assemble_matrix`, `train`, `conformal_intervals`) and rank 2 makes rank 1's new metrics
trustworthy.

---

## 3. The path to the experiment — a staged timeline

Assumed calendar (Indonesian academic year): **semester 3** = Sep 2026 – Jan 2027;
**semester 4** = Feb – Jun 2027; **semester 5** = Sep 2027 – Jan 2028; **semester 6** =
Feb – Jun 2028. Confirm against the current ITB academic calendar; the staging does not depend on
the exact dates.

### Stage 1 — Semester 3–4 (now → mid-2027): compute, and get *into* a lab

**Computational (the main effort).**
- Semester 3 (now → Jan 2027): complete the continuous-process upgrade (§2.1). Deliverable: a
  tagged v0.2 of the pipeline with the new dataset, the honest CV comparison, and the
  process-response surface.
- Semester 3–4: the conformal calibration audit (§2.2 rank 2). Deliverable: a short technical note.
- Keep the existing DOI'd release untouched. **Release v0.2 as a new version with its own DOI**,
  per `PROTOCOL_CORRECTED.md`'s own rule (a published artefact is never silently edited).

**Coursework.** It is semester 3. Coursework is not optional and it is not a distraction — the
metallurgy he learns now (phase transformations, heat treatment, thermodynamics) is exactly what
the process-feature work requires him to reason about. Protect the GPA.

**How to get into a lab — concretely.**
- **Whom to approach.** Not the head of department. Approach a *lecturer whose research is
  already in physical metallurgy, alloy design, or materials characterisation*, and who supervises
  undergraduates. ITB's Metallurgical Engineering faculty pages list research interests; find the
  two or three whose work touches Al alloys, heat treatment, or computational materials. Approach
  them individually.
- **What to say.** One paragraph, in Indonesian or English as appropriate:
  *"I am in semester 3. I built and published a machine-learning alloy-design pipeline
  (DOI 10.5281/zenodo.22844739). It predicts an Al–Zn–Mg–Cu composition at 625 MPa with an honest
  conformal interval of [517, 732] MPa, and it has never been validated experimentally. I have
  written the full experimental design and a corrected casting protocol — the documents are here.
  I am not asking for equipment yet. I am asking whether I can join your group, learn your
  equipment, and help with whatever work is running, so that in a year I can run a small
  supervised experiment of my own."*
- **What a semester-3 student can usefully offer a lab.** Honest list: literature review and
  data extraction; sample preparation and metallography; hardness testing; Archimedes density;
  specimen logging; **and, unusually for semester 3, a working computational pipeline, Python
  competence, and a habit of documenting to a reproducible standard.** The last one is the real
  offer. Most labs have more samples than hands and more data than analysis capacity. Offer to
  analyse *their* existing data with the pipeline. That is a genuine trade, not a favour.
- **The calling card.** The DOI is the differentiator. Show it. Show `EXPERIMENTAL_DESIGN.md`
  (including its Erratum) and `PROTOCOL_CORRECTED.md` — they demonstrate that he already thinks
  about controls, power, pre-registration and failure modes, which is not typical for his year.
  Showing a document that *retracts two of its own claims* is a stronger signal than showing one
  that does not.

**Gate for Stage 1 → 2:** a lecturer has agreed, in some form, to let him into the group.

### Stage 2 — Semester 4–5 (mid-2027 → Jan 2028): learn equipment, do a small supervised experiment

- Join the lab. Do not lead with the casting campaign. Lead with **learning**: furnace operation,
  thermocouple practice, quench handling, tensile specimen preparation, hardness testing.
- Run a **small supervised experiment** — the natural one is the *process* experiment, not the
  casting one: solution-treat and age **existing wrought 7075 (or 7055) bar** at a few
  temperature/time combinations, measure hardness and (if the machine is available) yield
  strength, and compare against the v0.2 process-response surface from Stage 1. This needs a
  furnace and a hardness tester — no melting, no DSC, no certified reference bar, no casting line.
  It is the cheapest experiment that tests a *new* model claim.
- This is also where the process-response prediction gets its first real test, and where he learns
  whether the lab's equipment can hold ±5 °C at all.
- Run the **C1 reference control** (tensile a certified AA7075-T6 bar) the moment tensile access
  exists, before trusting any other number.

**Gate for Stage 2 → 3:** the lab has confirmed, in writing, that the eleven items in
`PROTOCOL_CORRECTED.md` §7 either exist or do not. The casting campaign cannot be scheduled until
this is answered.

### Stage 3 — Semester 5–6 (2027–2028): the casting campaign, PKM, and the paper

- The casting campaign per `EXPERIMENTAL_DESIGN.md` §10.1 reduced design and
  `PROTOCOL_CORRECTED.md` §4: **3 heats × 3 specimens** of Al–3.0Mg–7.8Zn–1.3Cu plus the
  certified 7075-T6 reference. H = 3 is not negotiable.
- Pre-register the decision rule (design §7) *before* the first melt.
- Feed results into `outputs/experiment_log.json` via
  `python3 -m aloy.experiment_log` (see `docs/EXPERIMENT_LOG_HOWTO.md`) and run `aloy.active`.
- Write the paper. Both outcomes are publishable (design §8).

**The PKM windows — be concrete.**

| Cycle | Expected proposal window | His semester then | What is realistically deliverable |
|---|---|---|---|
| **PKM 2026** | Closed **9 April 2026** | — | Already missed. Not a loss. |
| **PKM 2027** | ~**March–April 2027** (the 2026 cycle ran Mar–Apr 2026) | End of semester 4 / start of 5 | **Only** a reframed proposal (§4): computational + a minimal supervised experiment. Requires a **team and a NUPTK supervisor secured by ~February 2027.** |
| **PKM 2028** | ~**March–April 2028** | Semester 6 | **The full casting campaign.** This is the natural target for the experiment as designed. |

**What must be in place before submitting any PKM proposal** (all verified against the PKM rules
as recorded in `proposal/PKM-RE-2027-proposal.md` §A.3 and §C.1):
1. A team of **3–5 active ITB undergraduates**, one chair + 2–4 members, ideally spanning ≥ 2
   cohorts. He has one name. This is the hardest item.
2. A **supervising lecturer with an NUPTK** (one lecturer may supervise at most 10 teams).
3. Each member confirmed **not already registered on another PKM proposal in any scheme**.
4. For a laboratory-based proposal: **lab confirmation and a signed safety/ethics approval**,
   not a verbal agreement.
5. Confirmation of whether the already-DOI'd work counts as prior publication (proposal §C.3 —
   currently unresolved and must be asked in writing to Belmawa).

**Decision point, February 2027:** if a team and supervisor are not in place by then, **do not
submit to PKM 2027.** Aim at PKM 2028 with the casting campaign. Missing a cycle costs a year;
submitting an incomplete proposal costs credibility with the supervisor he will need for years.

---

## 4. What to do with the existing artefacts

| Artefact | Decision | Why |
|---|---|---|
| `docs/EXPERIMENTAL_DESIGN.md` (+ Erratum) | **Keep as-is for later.** | It is a correct design for a campaign he will run in semester 6. Its power calculations, decision rule and erratum are still valid. Do not rewrite it for a smaller experiment — that would destroy a good document to solve a scheduling problem. |
| `docs/PROTOCOL_CORRECTED.md` | **Keep as-is for later.** | Governing protocol for the real campaign. Unchanged. |
| `docs/EXPERIMENT_LOG_HOWTO.md` + `aloy.experiment_log` | **Keep and use now.** | It is the ingest path for results *whenever* they arrive, including the small Stage-2 process experiment on wrought bar. It works today. |
| `proposal/PKM-RE-2027-proposal.md` | **Reframe — do not submit as written.** | It currently requires a 3–5 person team, a NUPTK supervisor, lab confirmation and a casting campaign, none of which exist. Submitting it in this state is impossible. |

**The PKM reframing, specifically.** The existing proposal is a **casting-campaign** proposal. It
cannot be delivered by a semester-3 team with no lab. Two options:

- **Option A (recommended for PKM 2027, if a team and supervisor exist by Feb 2027):** reframe to
  a **computational + minimal supervised experiment** proposal. The novelty claim survives almost
  intact — the pre-registered falsification of a conformal interval is still the core idea — but
  the experiment arm shrinks from "cast 3 heats" to "solution-treat and age existing wrought 7075
  bar at N conditions, measure hardness/YS, compare against the v0.2 process-response surface."
  This needs a furnace and a hardness tester, not a foundry. It is deliverable. It also produces
  the first genuine out-of-sample test the project will have had.
- **Option B (for PKM 2028):** keep the casting proposal essentially as written, updated with the
  v0.2 model's new predictions and the measured equipment confirmations. This is what the document
  was built for.

**Do not** attempt to submit the current proposal unchanged to PKM 2027. It would be rejected at
the institutional stage for missing team/supervisor, and the effort would be wasted.

---

## 5. The honest risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| **He loses interest / the project stalls.** A semester-3 student with a finished project and a plan that says "wait two years" is at real risk of drifting away. | **High** | This is the most serious risk, and it is why §2 exists. Give him something with a *result* this semester: the continuous-process upgrade produces new numbers, a new figure and a new claim within weeks. Momentum is the mitigation. Also: the Stage-1 goal (get into a lab) is a *social* goal, not a technical one — it needs a deadline, not motivation. |
| **The lab placement never materialises.** Lecturers are busy; semester-3 students are low priority; the one who says yes may be on leave. | **High** | Approach **three** lecturers, not one. Lead with the offer to analyse their data. If by the end of semester 4 no placement exists, treat it as information: either approach a different group (computational materials, or a lab that does characterisation rather than casting), or pivot the project's centre of gravity toward computation and publish the methods work instead. Do not let the project's entire value hinge on one conversation. |
| **The computational upgrade needs data that does not exist.** | **Low — verified resolved.** | I downloaded and parsed the dataset. The continuous columns exist (§2.1). The residual risk is different and real: the dataset is **wrought only**, so it cannot fix the as-cast gap. **Mitigation: state the limitation explicitly and never let the v0.2 model be presented as validating a cast alloy.** |
| **The upgrade does not improve the model.** Adding `Tsol`/`Tage`/`tage` may not raise R², because composition may dominate, or because the 524-row set is smaller than the 1150-row set. | **Medium** | **This is a legitimate result and must be reported as one.** The design document's own ethic (and `README.md` §10's honest reporting of the *small* active-learning advantage) is that negative results get published. A documented failure to improve on process features is a real contribution about what drives 7xxx strength. |
| **The composition is not novel enough to publish on its own.** It sits inside the AA7055 envelope (design §2.1). | **Certain** | **Already accepted and designed around.** Novelty never came from the composition. It comes from (i) pre-registered falsification of a conformal interval, (ii) the quantified process-regime failure mode, and (iii) the reference-control chain. If the v0.2 process-response surface works, it adds a fourth, stronger claim. |
| **PKM 2027 is missed and PKM 2028 is the target.** | **Medium–high** | Not a failure — it is the realistic path. Aim at PKM 2028 with the casting campaign and treat PKM 2027 as optional upside. |
| **The lab's furnace cannot hold ±5 °C.** | **Medium** | Discover this in Stage 2, on the cheap process experiment, *before* committing a casting campaign. That is precisely what Stage 2 is for. If it cannot, the solution-treatment window is unachievable and the design must be redrawn — better to learn that with wrought bar than with three heats of cast alloy. |

---

## 6. The single next action

> **This week: download the `Wrought Aluminum Alloys_01` dataset
> ([10.17632/gw8fvv7wth.2](https://data.mendeley.com/datasets/gw8fvv7wth/2), CC BY 4.0, file
> `Aged forged Al alloy.xlsx`) and spend two hours answering one question in a scratch notebook:
> *if `Tsol`, `Tage` and `tage` were added to `assemble_matrix()`, would the YS model's
> cross-validated MAE improve on 53 MPa?***
>
> Then, in the same week, send **one** email to **one** lecturer in physical metallurgy asking to
> join their group — the email in §3, with the DOI in it.

**Why these two, and why this week.**

The first is the highest-leverage technical move available to him because it is the **only** path
in this entire roadmap that converts a *deferred* experiment into a *scheduled* one. The casting
campaign needs a foundry he does not have. The process-response surface needs a furnace he might
have in a year — and it needs the model built *first*, this semester, while he has the time and no
other project. Two hours of scratch work tells him whether the 40–80-hour build is worth starting.
If the columns load and the correlation is there, he starts the build and has a result by January.
If it is not, he has learned that in an afternoon instead of a month, and moves to rank 2.

The second is the highest-leverage *social* move, because every experimental path in this document
runs through a lab placement, and the placement runs through a conversation he has not yet had.
It costs one email.

Neither action requires money, a supervisor, lab access, or anyone's permission. Both are
available to him today. That is what makes them the right next actions — and it is the whole
thesis of this roadmap: **the work he can do now is not a placeholder for the real project. It is
the part of the project that is actually his to do.**

---

## Appendix — sources verified in preparing this roadmap

| Claim | How verified | Result |
|---|---|---|
| Mendeley Al dataset has no continuous process columns | Parsed `data/raw/mendeley_al_alloys.csv` locally | Confirmed: 31 columns, none containing temp/time/quench/solution/age; 0 'cast' rows |
| Continuous-process Al dataset exists and is open | Downloaded and parsed `Aged forged Al alloy.xlsx` from Mendeley `10.17632/gw8fvv7wth.2` (CC BY 4.0) | Confirmed: 524 rows; `Tsol` 450–560 °C, `Tage` 25–290 °C, `tage` 0–1440 h; 192 rows 7xxx-like with all fields |
| Companion GitHub dataset | Fetched `github.com/UQ43815685/ageing_behaviour_Al_alloys_with_feature_screening` | Confirmed: `dataset.xlsx`, 430 rows, columns `SS Temp`, `Ageing Temp`, `Ageing Time`, `YTS`, `UTS`, `EL` |
| Jiang et al. (2023) 1053-record dataset is not open | Read the Data Availability statement in the published article | Confirmed: "available from the corresponding author upon reasonable request" |
| Candidate prediction and interval | `outputs/candidates_final.csv` row 121; `outputs/credibility_report.json` | Confirmed: 624.5 MPa, q_halfwidth 107.52, coverage_val 0.9011, n_cal 696 |
| Process channel is a single ordinal scalar | Read `_PROC_ENCODE` and `assemble_matrix()` in `src/aloy/models.py` | Confirmed |
| PKM structure and requirements | `proposal/PKM-RE-2027-proposal.md` §A.3, §C.1 | Confirmed as recorded there; the 2027 deadline itself is an **estimate** based on the 2026 cycle and should be re-checked against the official announcement when it is published |
