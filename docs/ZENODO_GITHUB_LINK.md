# Owner action: link this GitHub repo in the Zenodo record

The Zenodo record (10.5281/zenodo.22844739) was created before this GitHub
repository existed. Linking them improves findability and lets Zenodo build
a record for each GitHub release. Requires the owner's Zenodo login.

## Option A — recommended: enable the GitHub–Zenodo integration

1. Log in at https://zenodo.org with the account that owns record 22844739.
2. Go to **Account → GitHub** (https://zenodo.org/account/settings/github/).
3. Click **Connect**, authorize the `beduldul` GitHub account, then toggle
   the `aloy-alloy-design` repository **ON**.
4. On GitHub, create a release tagged `v1.0.0` (matching the Zenodo version):
   `gh release create v1.0.0 --title "Aloy v1.0.0" --notes "Initial public release. Software DOI: 10.5281/zenodo.22844739"`.
   Zenodo will automatically create a versioned record linked to the repo.

## Option B — manual metadata edit (no new version)

1. Open https://zenodo.org/records/22844739, log in, click **Edit**.
2. In **Related works**, add:
   - Identifier: `https://github.com/beduldul/aloy-alloy-design`
   - Relation: **is supplemented by** (or *is identified by* per local convention)
3. Save.

Zenodo may ask for a new version to apply metadata changes; either way, the
concept DOI (10.5281/zenodo.22844738) keeps pointing at the latest version.
