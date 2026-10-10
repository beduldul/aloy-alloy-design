# Citation

If you use this software or the derived candidate lists, please cite it as below.
A machine-readable version is provided in `CITATION.cff` (recognised by GitHub,
Zenodo, and most reference managers).

---

## Preferred citation (software + derived data)

> Al-Kaysan, A. A. (2026). *Aloy: A transparent machine-learning pipeline for
> inverse design of low-cost, high-strength aluminium and magnesium alloys*
> (Version 1.0.0) [Computer software].
> https://doi.org/10.5281/zenodo.22844739

The DOI above is a placeholder. It is replaced with the real DOI assigned by
Zenodo after the first deposit (see `docs/RELEASE_GUIDE.md`, step 5).

---

## If you use only the derived candidate data

> Al-Kaysan, A. A. (2026). *Predicted Pareto-optimal Al- and Mg-based alloy
> compositions with phase-risk screening* [Data set].
> https://doi.org/10.5281/zenodo.22844739

---

## You MUST also cite the underlying experimental data

This work would not exist without the two open experimental compilations that
supply the ground truth. Citing them is not optional — it is a condition of the
CC BY 4.0 licences under which they were released.

> Bhat, N., Barnard, A., & Birbilis, N. (2023). *Aluminium alloy dataset for
> supervised learning* [Data set]. Mendeley Data, V1.
> https://doi.org/10.17632/b6br4yk6r3.1

> Ghorbani, M., & Birbilis, N. (2025). *Magnesium alloy mechanical property
> database* [Data set]. Mendeley Data, V2.
> https://doi.org/10.17632/2fjhmdg5nt.2

---

## Third-party software

The pipeline builds on: NumPy, pandas, scikit-learn, SciPy, matplotlib, joblib,
pymoo (NSGA-II), PyCalphad, BoTorch, and PyTorch. Please cite those as well when
their methods are central to your use (see `docs/RELEASE_GUIDE.md`).

---

## How to cite a *future* version with experimental validation

The current release contains **model predictions only**. If you add measured
tensile data, cite it as a new version (Zenodo assigns version-specific DOIs) and
state explicitly in the abstract that validation is included.
