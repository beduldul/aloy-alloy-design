# CARA MENDAPATKAN DOI — Panduan Klik-demi-Klik (Zenodo)

Panduan ini menjawab: **"gimana mendapatkan DOI-nya?"**
Waktu: ~20 menit. Biaya: **gratis**. Tidak perlu eksperimen.

> **Kenapa saya (AI) tidak bisa dapatkan DOI untukmu?**
> DOI diterbitkan Zenodo ke akun atas nama pemilik karya. Hanya kamu yang bisa
> login, klik Publish, dan menyetujui lisensi — itu pernyataan kepengarangan yang
> sah dan tidak bisa didelegasikan. Yang sudah saya siapkan: semua file, metadata,
> dan skrip pengganti DOI, sehingga kamu tinggal klik.

---

## Ringkasan alur (5 tahap)

```
1. Buat akun Zenodo        → login pakai GitHub atau ORCID (2 menit)
2. Buat deposit "New upload" → isi judul, penulis, lisensi (5 menit)
3. Upload aloy-v1.0.0.zip   → file yang sudah saya siapkan (2 menit)
4. Klik "Publish"           → DOI langsung terbit (1 menit)
5. Jalankan 1 perintah      → tulis DOI ke semua file (1 menit)
```

---

## TAHAP 1 — Buat akun Zenodo

1. Buka **https://zenodo.org**
2. Klik **Sign up** (kanan atas).
3. Pilih **Sign up with GitHub** (paling praktis) atau **Sign in with ORCID**
   (lebih dihargai di dunia akademik — kalau kamu punya ORCID, pakai ini).
4. Selesaikan verifikasi email.

> Zenodo dikelola CERN. DOI-nya diakui secara internasional dan bisa disitasi
> resmi di CV, skripsi, dan publikasi.

---

## TAHAP 2 — Buat deposit baru

1. Klik **New upload** (tombol biru di kanan atas).
2. Isi kolom berikut **persis** (sudah saya siapkan agar tinggal salin):

| Kolom Zenodo | Isi |
|---|---|
| **Upload type** | `Software` |
| **Title** | `Aloy: A transparent machine-learning pipeline for inverse design of low-cost, high-strength aluminium and magnesium alloys` |
| **Creators** | `Al-Kaysan, Abdul Afif` — affiliation: `Institut Teknologi Bandung` |
| **Description** | Salin **abstrak lengkap** dari `release/PUBLICATION_PACKAGE.md` bagian "Abstract for the Zenodo deposit" |
| **Version** | `1.0.0` |
| **Language** | `English` |
| **License** | `MIT License` |
| **Keywords** | `materials informatics; aluminium alloys; magnesium alloys; multi-objective optimisation; Bayesian optimisation; CALPHAD; alloy design` |

3. Di bagian **Related works**, tambahkan dua entri ini (klik "Add related work"):

| Relation | Identifier | Resource type |
|---|---|---|
| `is derived from` | `10.17632/b6br4yk6r3.1` | Dataset |
| `is derived from` | `10.17632/2fjhmdg5nt.2` | Dataset |

> ⚠️ **Penting:** Karena kita memakai dan mendistribusikan ulang data mereka,
> kredit dua dataset sumber itu **wajib** (lisensi CC BY 4.0). Ini juga yang
> membuktikan karyamu jujur secara ilmiah.

---

## TAHAP 3 — Upload file

1. Di bagian **Files**, klik **Choose files**.
2. Pilih file: **`aloy-v1.0.0.zip`**
   (lokasi: satu folder di atas proyek — `/Users/abdulafifalkaysan/Documents/aloy-v1.0.0.zip`)
3. Tunggu sampai unggahan selesai (60 MB, ~1 menit).

> **Bagaimana kalau mau versi lebih ringan?** Hapus `outputs/models*/` dari zip
> sebelum upload — model bisa di-generate ulang dengan
> `python3 -m aloy.mg_models`. Tapi menyertakannya lebih ramah untuk pembaca.

---

## TAHAP 4 — Terbitkan (ini yang menghasilkan DOI)

1. Periksa sekali lagi semua kolom.
2. Klik tombol **Publish** (biru, kanan bawah).
3. **Selesai** — Zenodo langsung menampilkan DOI-mu, bentuknya:

```
10.5281/zenodo.1234567
```

Itu DOI-mu. Bisa langsung dipakai di CV, atau dibuka sebagai
`https://doi.org/10.5281/zenodo.1234567`.

> DOI ini **permanen**. Kalau nanti kamu update karyanya, Zenodo memberi DOI versi
> baru (mis. `...1234568`) sambil DOI lama tetap menunjuk ke v1.0.0.

---

## TAHAP 5 — Tulis DOI ke dalam file (1 perintah)

Setelah dapat DOI, jalankan:

```bash
cd "/Users/abdulafifalkaysan/Documents/aloy-alloy-design"
PYTHONPATH=src python3 -m aloy.doi --set 10.5281/zenodo.1234567
```

Ini otomatis mengganti placeholder di **semua** file (README badge, `CITATION.md`,
`CITATION.cff`, template naskah). Lalu bangun ulang arsipnya:

```bash
PYTHONPATH=src python3 -m aloy.release --build
```

Cek kapan saja dengan:
```bash
PYTHONPATH=src python3 -m aloy.doi --check
```

---

## CARA LEBIH CEPAT (opsional): lewat GitHub

Kalau kamu taruh kode di GitHub, Zenodo bisa menerbitkan DOI **otomatis** setiap
kamu bikin "Release":

1. Buat repo di GitHub, push kodenya:
   ```bash
   cd "/Users/abdulafifalkaysan/Documents/aloy-alloy-design"
   git init && git add . && git commit -m "Aloy v1.0.0"
   git remote add origin https://github.com/<username>/aloy-alloy-design.git
   git push -u origin main
   ```
2. Di Zenodo: **Settings → GitHub →** aktifkan repo `aloy-alloy-design`.
3. Di GitHub: **Releases → Create a new release →** tag `v1.0.0` → **Publish release**.
4. Zenodo otomatis mengarsipkan commit itu dan menerbitkan DOI.

Kelebihannya: DOI terikat ke commit persis (reproducibility lebih kuat), dan
kamu dapat badge otomatis. Kekurangannya: harus setup git dulu.

---

## Pertanyaan yang sering muncul

**"Saya mahasiswa S1, boleh punya DOI?"**
Boleh. Zenodo tidak mensyaratkan gelar atau institusi. Banyak mahasiswa
menerbitkan dataset/kode di sana.

**"Apakah ini dianggap publikasi?"**
Ya — software/data DOI adalah artefak yang bisa disitasi dan dihitung di CV.
Tapi **bukan** pengganti publikasi jurnal; lihat `docs/RELEASE_GUIDE.md` Step 7.

**"Harus punya pembimbing?"**
Untuk rilis dataset/kode: tidak. Untuk naskah jurnal: sebaiknya ya.

**"Kalau data sumbernya bukan punyaku?"**
Kamu tidak mengklaim data itu milikmu — kamu mendistribusikan ulang di bawah
CC BY 4.0 dengan atribusi (sudah dicantumkan). Yang kamu klaim adalah *kode dan
hasil turunan*-nya, di bawah MIT.

**"Bisa dihapus?"**
DOI Zenodo bisa dibuat "closed"/restricted, tapi idealnya jangan dihapus —
tujuan DOI justru agar permanen. Pastikan sudah benar sebelum Publish.

---

## Checklist sebelum klik Publish

- [ ] Sudah jalankan `PYTHONPATH=src python3 -m aloy.release --check` → PASS
- [ ] `aloy-v1.0.0.zip` ter-upload
- [ ] Judul, penulis (nama + afiliasi ITB) benar
- [ ] Abstrak tercantum, dan **menyatakan ini prediksi, bukan pengukuran**
- [ ] Lisensi: MIT
- [ ] Dua "is derived from" (DOI dataset sumber) tercantum
- [ ] Version: 1.0.0

Setelah Publish → **TAHAP 5**: jalankan `aloy.doi --set <DOI-mu>`.
