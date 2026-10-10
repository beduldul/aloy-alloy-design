# Laporan Riset: Penemuan Paduan Al Berbasis Pembelajaran Mesin
## Machine-Learning-Guided Discovery of Low-Cost, High-Strength Aluminium Alloys

**Periode:** 2026 · **Bidang:** Metalurgi Fisik / Materials Informatics
**Lingkungan:** MacBook M4 Pro (10 core CPU, GPU MPS), Python 3.12

---

## Abstrak

Kami mengembangkan pipeline terbuka untuk menemukan paduan aluminium berkekuatan
tinggi dengan biaya rendah, menggunakan pembelajaran mesin pada data eksperimen
publik. Pipeline mencakup (i) kurasi data dengan disiplin domain, (ii) model
surrogate ensemble dengan validasi bebas kebocoran, (iii) desain invers
multi-objektif NSGA-II, (iv) penyaringan fasa fisik (Hume-Rothery + CALPHAD),
(v) loop *active learning* Bayesian, dan (vi) kuantifikasi ketidakpastian
*conformal prediction*.

**Hasil utama:** kandidat berbasis Al–Zn–Mg–Cu (kelas 7xxx) diprediksi mencapai
**~620–625 MPa yield strength** pada **~2.65 USD/kg**, yaitu **+24% kekuatan**
dibanding AA7075-T6 komersial dengan **~24% biaya lebih rendah**. Analisis
*harga-sensitivitas* menunjukkan kurva nilai jenuh di bawah 3 USD/kg: elemen
eksotis (Li, Sc) **tidak** memberikan keunggulan yang sebanding biayanya.

---

## 1. Pendahuluan & motivasi

Kebutuhan struktur ringan-kokoh (otomotif, kedirgantaraan) mendorong pencarian
paduan Al berkekuatan tinggi. Pendekatan tradisional (coba-coba) memakan waktu
dekade. *Materials informatics* mempercepat ini, tetapi rentan terhadap dua
kesalahan: **(a) kontaminasi domain** (mencampur kelas material berbeda) dan
**(b) pelaporan berlebihan** (prediksi tanpa error bar).

Kontribusi kami adalah pipeline yang secara eksplisit menangani keduanya.

## 2. Data

| Sumber | DOI | n mentah | n dipakai |
|---|---|---|---|
| Mendeley (Bhat/Barnard/Birbilis 2023) | 10.17632/b6br4yk6r3.1 | 1151 | 1151 |
| Citrine MPEA (Borg et al. 2020) | 10.6084/m9.figshare.12642953 | 1545 | 7 |

**Penemuan kritis:** korpus MPEA didominasi alloy refraktori berat (median fraksi
Al **0,08**; YS hingga 3416 MPa). Mencampurkannya membuat model memprediksi
kekuatan mustahil untuk paduan Al. **Kami membatasi ke Al ≥ 50%.** Dampak:

| Metrik | Sebelum filter | Setelah filter |
|---|---|---|
| Max YS di data | 3416 MPa | **790 MPa** |
| MAE YS (CV) | 160 MPa | **53 MPa** |
| R² YS (CV) | 0.74 | **0.79** |

## 3. Metode

### 3.1 Fitur fisik
δr (Hume–Rothery), Δχ, VEC, Ω = T_m·ΔS/|ΔH_mix|, ΔS_mix, ρ (rule-of-mixtures),
biaya/kg, T_lebur & modulus bulk rata-rata, encoding rute proses.

### 3.2 Model surrogate
Ensemble {HistGradientBoosting, RandomForest, ExtraTrees}. Validasi **GroupKFold
per komposisi** (bebas kebocoran antar-varian serupa). Sebaran antar-anggota =
estimasi ketidakpastian epistemik.

| Target | n | R² CV | MAE CV | R² holdout |
|---|---|---|---|---|
| Yield strength | 1050 | 0.79 | 53 MPa | 0.75 |
| UTS | 1120 | 0.84 | 45 MPa | 0.82 |
| Elongasi | 1050 | 0.27 | 4.6 % | 0.21 |

### 3.3 Desain invers
NSGA-II, 4 objektif (maks YS, maks elongasi, maks specific strength, min biaya),
kendala δr ≤ 0.075 & jendela stabilitas Ω. 160 solusi Pareto per skenario.

### 3.4 Penyaringan fasa
Kesetimbangan CALPHAD (pycalphad, db `alzn_mey.tdb`) + kriteria presipitasi
terkalibrasi. **Validasi:** AA7075 & AA2024 nyata terklasifikasi "medium" (benar);
hanya fraksi fasa-berlebih besar (>8%) dihukum.

### 3.5 Active learning
GP `qLogNoisyExpectedImprovement` (BoTorch) + *trust region* untuk mencegah
ekstrapolasi. Surrogate di GPU MPS; akuisisi di CPU/float64 (MPS tak dukung f64).

### 3.6 Ketidakpastian
*Split-conformal prediction*: interval 90% = **±108 MPa**, coverage empiris
**90.1%** (nominal 90%) — terkalibrasi.

## 4. Hasil

### 4.1 Kandidat rekomendasi

| Kandidat | Komposisi (wt%) | YS (MPa) | Elong (%) | ρ | Specific | Biaya |
|---|---|---|---|---|---|---|
| 1 | Al–4.7Mg–7.1Zn–1.2Cu | 625 | 8.9 | 2.77 | 225 | $2.65/kg |
| **2** | **Al–3.0Mg–7.8Zn–1.3Cu** | **625** | **12.3** | 2.82 | 222 | $2.66/kg |
| 3 | Al–3.1Mg–8.0Zn–1.0Cu | 618 | 11.8 | 2.81 | 220 | $2.64/kg |

### 4.2 Perbandingan dengan paduan komersial

| Paduan | YS | Elong | Specific | vs 7075 (YS) | vs 7075 (biaya) |
|---|---|---|---|---|---|
| **Kandidat 2 (model)** | **625** | **12.3** | 222 | **1.24×** | **0.76×** |
| AA7075-T6 (handbook) | 503 | 11.0 | 179 | 1.00 | 1.00 |
| AA2024-T4 | 324 | 20.0 | 117 | 0.64 | 0.94 |
| AA6061-T6 | 276 | 12.0 | 102 | 0.55 | 0.83 |
| AA8090-T6 (Al-Li) | 400 | 6.0 | 157 | 0.80 | 3.43 |

**Validasi densitas:** model memberi 2.798 g/cm³ untuk komposisi 7075;
handbook = **2.81** ✓ (error 0.4%).

### 4.3 Elemen eksotis tidak sepadan

Ketika diberi kebebasan penuh memakai Li/Sc/Zr, optimizer **tetap memilih
komposisi murah** (Li ≈ 0). Sweep harga: plafon $3 → YS 611 MPa; plafon $12 →
618 MPa (**+1%** untuk 4× biaya).

## 5. Protokol eksperimen

Lihat `lab_protocols.txt`. Ringkas untuk kandidat 2 (batch 500 g):

- **Charge:** Al 439 g, Zn 41.8 g (+7%), Mg 16.6 g (+10%), Cu 6.7 g
- **Lebur** 700 °C, tuang 690 °C, grain refiner Al-5Ti-1B 0.1 wt%
- **Homogenisasi** 465 °C / 12 h (opsional)
- **Solution treatment** 465–475 °C / 2 h, quench air dingin
  ⚠️ jangan > 475 °C (incipient melting eutektik ≈ 477 °C)
- **Aging T6** 120 °C / 24 h (atau T73: 160 °C / 8 h untuk tahan SCC)
- **Karakterisasi:** SEM/EDS, XRD, HV, tarik ASTM E8 (3 spesimen), densitas Archimedes

## 6. Batasan

1. **Elongasi lemah** (R²≈0.21–0.27) — defek/mikrostruktur tak terekam.
2. Prediksi kandidat (625 MPa) **di atas** AA7075 nyata → **wajib divalidasi
   eksperimen**; kemungkinan optimistis.
3. Biaya = estimasi pasar indikatif, bukan kuotasi.
4. CALPHAD = penyaringan, bukan full assessment termodinamika.
5. Belum ada data creep/korosi.
6. **Alat prioritisasi, bukan pengganti eksperimen.**

## 7. Kesimpulan & saran

Pipeline menghasilkan kandidat kelas 7xxx yang **secara fisik masuk akal**
(Al–Zn–Mg–Cu, densitas cocok dengan 7075) dan **ekonomis**. Langkah berikutnya:

1. Lebur kandidat 2 & 3, uji tarik, bandingkan dengan interval conformal [517, 732].
2. Masukkan hasil ke `experiment_log.json` → jalankan `aloy.active` (loop tertutup).
3. Plug database CALPHAD lengkap untuk prediksi fraksi presipitat kuantitatif.
4. Perluas ke sistem Mg-base.

## Referensi
- Bhat, Barnard, Birbilis (2023). *Aluminium alloy dataset for supervised learning.* Mendeley Data. DOI 10.17632/b6br4yk6r3.1
- Borg et al. (2020). *Expanded dataset of mechanical properties and observed phases of multi-principal element alloys.* Sci. Data. DOI 10.6084/m9.figshare.12642953
- ASM Handbook Vol. 2 — Properties and Selection: Nonferrous Alloys.
- Otani et al. — Hume-Rothery / Ω parameter criteria.
