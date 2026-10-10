# Data Sources, Provenance and Licence Compliance

This document records exactly where every input came from, how it was processed,
and the licence terms under which it is redistributed. Reviewers and users need
this to trust the results; it is also what CC BY 4.0 requires.

## 1. Primary experimental datasets (ground truth)

### 1.1 Aluminium alloys
- **Title:** Aluminium alloy dataset for supervised learning
- **Authors:** Ninad Bhat, Amanda Barnard, Nick Birbilis
- **Publisher:** Mendeley Data, Version 1 (14 Feb 2023)
- **DOI:** https://doi.org/10.17632/b6br4yk6r3.1
- **Licence:** CC BY 4.0
- **Retrieved:** 2026-09-19
- **Local file:** `data/raw/mendeley_al_alloys.csv` (sha256 recorded in `MANIFEST.sha256`)
- **Content:** ~1150 Al alloys; 25 element columns (mass fractions), processing
  route text, Yield Strength (MPa), Tensile Strength (MPa), Elongation (%),
  alloy class label.
- **Processing applied:** dropped rows labelled `outlier`; kept rows whose
  element mass fractions sum to [0.95, 1.05]; mapped free-text processing into a
  12-class categorical + binary "aged" flag. No property values were altered.

### 1.2 Magnesium alloys
- **Title:** Magnesium alloy mechanical property database
- **Authors:** Marzie Ghorbani, Nick Birbilis
- **Publisher:** Mendeley Data, Version 2 (12 Jun 2025)
- **DOI:** https://doi.org/10.17632/2fjhmdg5nt.2
- **Licence:** CC BY 4.0
- **Retrieved:** 2026-09-19
- **Local file:** `data/raw/mendeley_mg_alloys.xlsx`
- **Content:** 916 Mg alloys; 31 element columns in wt% (sum exactly 100),
  processing/heat-treatment text, YS (MPa), UTS (MPa), Ductility.
- **Processing applied:** converted wt% to mass fractions; kept rows with
  Mg > 50 wt% and at least one mechanical property. No property values altered.

## 2. Secondary dataset (used, then excluded — documented for transparency)

### 2.1 Citrine MPEA corpus
- **Title:** Expanded dataset of mechanical properties and observed phases of
  multi-principal element alloys
- **Authors:** Borg et al. (2020), DOI https://doi.org/10.6084/m9.figshare.12642953
- **Licence:** Apache-2.0 (repository); dataset on Figshare
- **Content:** 1545 multi-principal-element alloys.

**Why only 7 rows are used:** this pipeline designs *aluminium-based* alloys.
The MPEA corpus is dominated by heavy refractory alloys — the median aluminium
mass fraction is **0.08**, and it contains yield strengths of 1500–3416 MPa
belonging to an entirely different material class. Training on them caused the
surrogate to predict physically impossible strengths for Al alloys (up to
~1700 MPa) and inflated the cross-validated error by ~3×.

We therefore filter to **Al >= 50 wt%**, which retains 7 MPEA rows. This is
reported here rather than silently, because it changes the dataset size from
2696 to 1158 records and explains the model's accuracy improvement
(MAE 160 → 53 MPa).

## 3. Elemental property tables

Values in `src/aloy/elements.py` are standard handbook data (atomic mass,
density, atomic radius, electronegativity, melting point, bulk modulus) drawn
from IUPAC/CRC compilations. Costs are **indicative 2024 market order-of-magnitude
estimates** for design ranking only — they are explicitly NOT procurement quotes
and must not be used for budgeting.

## 4. Redistribution statement

The raw files in `data/raw/` are redistributed under CC BY 4.0, with attribution
to the original authors as given above. The software in `src/` is MIT-licensed.
If you redistribute this package you must preserve both attributions.

## 5. Reproduction

Deterministic seeds are fixed throughout (`seed=0/1/42/99` as documented in each
module). To regenerate every artefact from the raw files:

```bash
PYTHONPATH=src python3 -m aloy.pipeline
PYTHONPATH=src python3 -m aloy.scenarios
PYTHONPATH=src python3 -m aloy.calphad_check
PYTHONPATH=src python3 -m aloy.active
PYTHONPATH=src python3 -m aloy.credibility
PYTHONPATH=src python3 -m aloy.protocol
PYTHONPATH=src python3 -m aloy.loop_sim
PYTHONPATH=src python3 -m aloy.mg_models
PYTHONPATH=src python3 -m aloy.mg_design
PYTHONPATH=src python3 -m aloy.mg_protocol
PYTHONPATH=src python3 -m aloy.plots_mg
```

Small numerical differences (typically <1%) may appear across operating systems
or library versions because of floating-point and multithreaded reduction order.
