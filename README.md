# FitMate: Web Personal Trainer Assistant

Aplikasi web (Python + Flask) yang menyusun program latihan mingguan sesuai profil pengguna,
mencatat sesi latihan dan berat badan, lalu menampilkan grafik progres. Antarmuka tersedia dalam
Bahasa Indonesia dan Inggris. Data disimpan dalam file JSON. Rekomendasi dibuat dengan aturan
(rule-based), bukan AI.

> FitMate memberi saran umum, bukan nasihat medis.

## Menjalankan di komputer sendiri

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                      # buka http://127.0.0.1:5000
```

Menjalankan tes:

```bash
pip install pytest
python -m pytest
```

## Struktur proyek

| Berkas | Fungsi |
| --- | --- |
| `app.py` | Aplikasi Flask: semua rute (halaman), CSRF, sesi login |
| `recommender.py` | Logika rekomendasi program (split, pemilihan latihan, set/repetisi) |
| `repository.py` | Fungsi data: pengguna, profil, catatan latihan, catatan berat |
| `storage.py` | Baca/tulis file JSON secara atomik |
| `validators.py` | Validasi semua input formulir |
| `i18n.py` | Terjemahan Indonesia dan Inggris (satu tabel, pasangan berdampingan) |
| `charts.py` | Grafik SVG dibuat dengan Python |
| `data/exercises.json` | Pustaka 55 latihan (dua bahasa) |
| `templates/` | Halaman HTML (Jinja2) |
| `public/style.css` | Gaya tampilan (juga `favicon.svg`) |
| `tests/` | Tes otomatis (pytest) |

Data pengguna lokal ada di `data/runtime/` (tidak ikut Git).

## Version control dengan Git

```bash
git init
git add .
git commit -m "FitMate: versi awal"
git branch -M main
git remote add origin https://github.com/USERNAME/fitmate.git
git push -u origin main
```

## Deploy ke Vercel

Vercel mengenali Flask otomatis dari file `app.py` yang memuat variabel `app`
([dokumentasi](https://vercel.com/docs/frameworks/backend/flask)). Tidak perlu `vercel.json`.
File statis harus ada di folder `public/` (sudah begitu).

1. Push proyek ke GitHub (langkah di atas).
2. Di vercel.com: **Add New, Project**, pilih repositori `fitmate`, lalu **Deploy**.
3. Di **Settings, Environment Variables**, tambahkan `SECRET_KEY` berisi teks acak panjang, lalu deploy ulang.
   Buat dengan: `python -c "import secrets; print(secrets.token_hex(32))"`.
   Tanpa ini, sesi login hilang setiap server restart.
4. Opsional: `FITMATE_UTC_OFFSET` (default `7`, WIB) untuk menentukan "hari ini" pada penanda jadwal.

Alternatif lewat CLI: `npm i -g vercel`, lalu `vercel` di folder proyek.

## Keterbatasan penyimpanan (baca sebelum presentasi)

Filesystem Vercel hanya bisa ditulis di `/tmp` dan **sifatnya sementara**. Di Vercel, FitMate
menulis data ke `/tmp/fitmate_data`, sehingga:

- akun dan catatan **bisa hilang** saat instance berganti atau restart;
- dua instance berbeda **tidak berbagi** data, jadi pengguna bisa tiba-tiba "tidak terdaftar";
- aplikasi menampilkan catatan "Mode demo" di footer dan memaksa login ulang bila akun tidak ditemukan.

Untuk demo tugas ini cukup, untuk pemakaian nyata tidak. Jalan keluar bila nanti diperlukan:
ganti isi `storage.py` (hanya fungsi `load`/`save`) agar membaca/menulis ke layanan penyimpanan
eksternal (mis. Redis/KV atau database dari Vercel Marketplace), tanpa mengubah bagian lain.
Detail layanan dan harga perlu diverifikasi langsung di dokumentasi Vercel.

Selain itu, penguncian file hanya berlaku dalam satu proses. JSON tidak aman untuk banyak
pengguna menulis bersamaan.

## Keamanan yang sudah ada, dan yang belum

Sudah: kata sandi di-hash (PBKDF2-SHA256), token CSRF di semua formulir POST, cookie sesi
HttpOnly/SameSite (Secure di Vercel), validasi input, setiap pengguna hanya bisa mengakses
datanya sendiri, redirect login dibatasi ke path internal, hapus akun beserta data.

Belum: pembatasan percobaan login (rate limiting), pemulihan kata sandi, verifikasi email.

## Catatan konten latihan

Angka set, repetisi, dan istirahat ada di konstanta `recommender.py` dan mengikuti praktik umum.
**Belum diverifikasi** oleh pelatih atau sumber kepelatihan. Minta peninjauan sebelum dipakai nyata.
