CATATAN RILIS — file ini menjelaskan isi arsip
================================================

Versi arsip ini TIDAK menyertakan model machine-learning yang sudah dilatih
(folder outputs/models/ dan outputs/models_mg/) karena ukurannya besar (~40 MB).

Model dapat dibuat ulang dengan 2 perintah (butuh ~35 detik):

    PYTHONPATH=src python3 -m aloy.models     # model paduan Aluminium
    PYTHONPATH=src python3 -m aloy.mg_models  # model paduan Magnesium

Semua hasil (daftar kandidat, figur, laporan) SUDAH disertakan, jadi tidak perlu
melatih ulang model hanya untuk membaca hasilnya.

Cek lingkungan:
    python3 -c "import numpy, pandas, sklearn, pymoo, pycalphad, botorch"

Pre-flight check (memastikan paket jujur & lengkap):
    PYTHONPATH=src python3 -m aloy.release --check
