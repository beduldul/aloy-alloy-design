# Release Guide — how to publish this work with a citable DOI

This walks through releasing the package on **Zenodo** so it gets a permanent
DOI. No journal, no experiments and no supervisor approval are required — this
is a legitimate, citable scientific artefact. Estimated time: under an hour.

---

## Step 0 — Understand what you are and are not publishing

You ARE publishing:
- a reproducible software package,
- derived, machine-readable candidate compositions,
- full documentation of method, data provenance, uncertainty and limitations.

You are NOT (yet) publishing:
- new experimental measurements,
- a validated new alloy,
- a claim that the predictions are correct.

State this plainly in the abstract. Reviewers and readers reward honesty;
overclaiming is the fastest way to have a release ignored or criticised.

---

## Step 1 — Clean the tree before uploading

Remove generated caches and the (large) trained model binaries if you prefer a
lighter archive — but **keep the predictions and figures**, they are the result.

```bash
cd "<project root>"
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name ".DS_Store" -delete
rm -rf .ipynb_checkpoints
```

Decide on models: `outputs/models*/` (~40 MB compressed) may be included for
full reproducibility, or omitted with a note that `load_or_train()` regenerates
them in ~35 s. Including them is friendlier; the archive stays small.

## Step 2 — Record a manifest (integrity)

```bash
cd "<project root>"
find . -type f -not -path "./.git/*" -not -name "MANIFEST.sha256" \
  -exec shasum -a 256 {} \; | sort -k2 > MANIFEST.sha256
wc -l MANIFEST.sha256
```

This lets anyone verify they received the package intact, and lets you prove
which exact files produced the published numbers.

## Step 3 — Put it on GitHub (recommended, not required)

```bash
cd "<project root>"
git init
git add .
git commit -m "Aloy v1.0.0: Al/Mg alloy inverse-design pipeline + candidate data"
git branch -M main
# create an empty repo named aloy-alloy-design on github.com, then:
git remote add origin https://github.com/<your-username>/aloy-alloy-design.git
git push -u origin main
```

Why GitHub first: Zenodo can mint the DOI automatically from a GitHub release
and archive the exact commit. It also gives you issue tracking and a public
history, which reviewers like.

## Step 4 — Create the Zenodo deposit

1. Go to https://zenodo.org and sign in with GitHub (or ORCID).
2. Click **New upload**.
3. Fill in:
   - **Upload type:** Software (or Dataset — either is fine).
   - **Title:** copy the title from `CITATION.cff`.
   - **Authors:** your full name, affiliation "Institut Teknologi Bandung".
   - **Description:** paste the "Release abstract" from Step 6 below.
   - **Version:** 1.0.0
   - **Language:** English
   - **Keywords:** materials informatics; aluminium alloys; magnesium alloys;
     multi-objective optimisation; Bayesian optimisation; CALPHAD; alloy design.
   - **Licence:** MIT (for the code). Add, in the description, that the bundled
     raw datasets remain CC BY 4.0 with attribution to Bhat et al. (2023) and
     Ghorbani & Birbilis (2025).
   - **Related identifiers:** add the two source DOIs
     (`10.17632/b6br4yk6r3.1`, `10.17632/2fjhmdg5nt.2`) as "is derived from".
4. **Upload** either the zip you create in Step 5, or connect the GitHub repo.

## Step 5 — Create the upload archive

```bash
cd "<parent of project dir>"
zip -r aloy-v1.0.0.zip "aloy-alloy-design" \
  -x "*/__pycache__/*" "*/.git/*" "*/.DS_Store"
ls -lh aloy-v1.0.0.zip
```

Upload that file in Zenodo, then click **Publish**. Zenodo immediately assigns a
DOI of the form `10.5281/zenodo.NNNNNNN`.

## Step 6 — Replace the DOI placeholders (automated)

Once Zenodo shows your DOI (it appears at the top of the deposit page after you
click **Publish**, in the form `10.5281/zenodo.1234567`), run ONE command:

```bash
cd "<project root>"
PYTHONPATH=src python3 -m aloy.doi --set 10.5281/zenodo.1234567
```

This replaces the placeholder in every file at once (README badge, `CITATION.md`,
`CITATION.cff`, the manuscript template) and reports if any is left. Then rebuild
the archive so the published package carries the real DOI:

```bash
PYTHONPATH=src python3 -m aloy.release --build
```

You can verify at any time with:

```bash
PYTHONPATH=src python3 -m aloy.doi --check
```

### Faster option: let Zenodo do it for you

If you connected your GitHub repository to Zenodo (Settings → GitHub → flip the
switch for `aloy-alloy-design`), then simply **publishing a GitHub Release** makes
Zenodo archive it and mint the DOI automatically. You still must run the
`--set` command afterwards to write the DOI back into the files.

### Release abstract (paste into Zenodo)

> Aloy is a reproducible, open-source pipeline for the inverse design of
> low-cost, high-strength aluminium- and magnesium-based alloys from published
> experimental data. It combines (i) domain-disciplined data curation,
> (ii) leakage-free ensemble surrogates, (iii) NSGA-II multi-objective design,
> (iv) Hume-Rothery and CALPHAD phase screening, (v) Bayesian active learning
> with trust regions, and (vi) split-conformal prediction intervals.
>
> For aluminium, it predicts Pareto-optimal Al-Zn-Mg-Cu candidates reaching
> ~620 MPa yield strength at ~2.65 USD/kg, and benchmarks them against commercial
> AA7075, AA2024 and AA6061 with due uncertainty. For magnesium, it predicts
> Mg-Ca-Li candidates reaching ~285 MPa at ~1.45 g/cm3, benchmarked against
> AZ91D, ZK60 and WE43. A price-sensitivity analysis shows the value curve
> saturates below 3 USD/kg, i.e. exotic additions (Li, Sc) are not
> cost-effective for strength.
>
> Every prediction is reported with an honest error bar (90% conformal interval
> of ±108 MPa for Al yield strength, with 90.1% empirical coverage), and all
> limitations are documented: yield-strength models are reliable
> (R2 ≈ 0.79 cross-validated), elongation models are weak (R2 ≈ 0.27), and
> **no experimental validation is included**. The package is explicitly an
> experiment-prioritisation tool, not a substitute for experiment. It ships
> ready-to-execute laboratory protocols (including magnesium fire-safety
> procedures) and machine-readable candidate lists.
>
> Source experimental data: Bhat, Barnard & Birbilis (2023), DOI
> 10.17632/b6br4yk6r3.1, and Ghorbani & Birbilis (2025), DOI
> 10.17632/2fjhmdg5nt.2, both CC BY 4.0.

## Step 7 — After release: the honest next step

A software/data DOI is a real publication and is citable in a CV. But it will not
by itself impress a metallurgy committee. The credible path from here:

1. Take **one** Al and **one** Mg candidate to a lab; measure yield strength.
2. Add the measured points to `outputs/experiment_log.json` and re-run
   `aloy.active`.
3. Write a **short communication** (this is a real, achievable genre) reporting:
   prediction → experiment → error. Even a *negative* result ("the model
   overpredicted by 15%") is publishable and scientifically valuable.
4. Only after that is a full research paper realistic.

Plausible venues once you have experimental validation:
- *Journal of Alloys and Compounds* (broad, accepts ML+materials)
- *Materials Science and Engineering: A* (mechanical behaviour focus)
- *Computational Materials Science* / *npj Computational Materials* (method focus)
- *Materialia* / *Results in Materials* (shorter, faster, open access)

## Step 8 — Checklist before you click Publish

- [ ] README states clearly that results are predictions, not measurements
- [ ] Limitations section present and specific
- [ ] CITATION.md credits both source datasets
- [ ] LICENCE distinguishes MIT (code) from CC BY 4.0 (data)
- [ ] `MANIFEST.sha256` generated
- [ ] No personal data, API keys, or large junk files included
- [ ] All placeholder DOIs replaced after publishing
- [ ] Every figure in the release is reproducible by the documented commands
