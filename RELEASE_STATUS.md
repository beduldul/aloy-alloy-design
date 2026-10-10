# Status Rilis — TERBIT ✅

**DOI:** `10.5281/zenodo.22844739`
**URL:** https://doi.org/10.5281/zenodo.22844739
**Tanggal:** 19 September 2026
**Versi:** 1.0.0
**DOI semua-versi:** `10.5281/zenodo.22844738` (selalu menunjuk versi terbaru)

## Verifikasi (dilakukan otomatis terhadap Zenodo)

| Pemeriksaan | Hasil |
|---|---|
| Status record | `published` |
| Resolusi DOI | HTTP 200 → zenodo.org/records/22844739 |
| Lisensi | MIT License |
| File | aloy-v1.0.0.zip (62.7 MB) |
| Related works | 10.17632/b6br4yk6r3.1, 10.17632/2fjhmdg5nt.2 |
| Bahasa | Python |
| Indexed | OpenAIRE |

## Terbitan resmi (untuk CV / sitasi)

> Al Kaysan, A. A. (2026). *Aloy: A transparent machine-learning pipeline for
> inverse design of low-cost, high-strength aluminium and magnesium alloys*
> (Version 1.0.0) [Computer software]. Zenodo.
> https://doi.org/10.5281/zenodo.22844739

## Badge untuk ditampilkan

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22844739.svg)](https://doi.org/10.5281/zenodo.22844739)
```

## Langkah berikutnya (jujur)

Karya ini adalah **rilis software/data** — sah dan dapat disitasi, tetapi
**bukan** bukti ilmiah bahwa paduannya benar-benar sekuat prediksi.

Untuk naik ke publikasi jurnal:

1. Lebur 1 kandidat Al (Al–3.0Mg–7.8Zn–1.3Cu) dan 1 kandidat Mg.
2. Ukur yield strength (uji tarik ASTM E8).
3. Masukkan hasil ke `outputs/experiment_log.json`, jalankan `aloy.active`.
4. Tulis *short communication*: prediksi → eksperimen → selisih.
   (Hasil negatif pun layak terbit dan berharga.)

Venue yang masuk akal setelah ada data validasi: *Journal of Alloys and
Compounds*, *Materials Science and Engineering: A*, *Materialia*,
*npj Computational Materials*.

## Kalau ingin memperbarui rilis

Jangan menimpa. Di Zenodo klik **New version**, unggah arsip baru, terbitkan →
kamu dapat DOI versi baru (mis. `...22844740`) sementara versi 1.0.0 tetap
permanen. Setelah itu jalankan:

```bash
PYTHONPATH=src python3 -m aloy.doi --set 10.5281/zenodo.<doi-baru>
PYTHONPATH=src python3 -m aloy.release --build
```
