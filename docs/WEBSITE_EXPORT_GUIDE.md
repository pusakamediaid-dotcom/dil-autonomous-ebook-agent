# Website Export Layer — Panduan Export Website & PDF

Dokumentasi ini menjelaskan fitur Website Export Layer pada DIL Autonomous Ebook Agent, cara menjalankan test export, build site lokal, deploy ke GitHub Pages, membaca laporan validasi, dan troubleshooting umum.

---

## 0. Jalur Produksi Stabil (UPDATE)

Saat ini ada **dua folder website** dengan peran berbeda:

| Folder | Peran | Sumber |
|---|---|---|
| `/site` | **Output generator / staging** | Dihasilkan oleh `src/exporters/site_builder.py` dari `output/ebook.md` (atau `samples/ebook.md` sebagai fallback). |
| `/docs` | **Website publik produksi (stabil)** | Sumber resmi yang dibaca GitHub Pages. |

**GitHub Pages aktif membaca `/docs`** dengan konfigurasi:

- Source: **Deploy from a branch**
- Branch: **`main`**
- Folder: **`/docs`**
- Custom domain: **`agent.pusakamedia.id`** (via `docs/CNAME`)

### Cara Menyalin Hasil Terbaru dari `/site` ke `/docs`

Setelah `site_builder.py` menghasilkan `site/ebook.html` baru:

```bash
# Dari root repository
cp site/ebook.html docs/ebook.html
# (Opsional) salin CSS / asset lain jika perlu:
# cp site/style.css docs/style.css
```

> **Jangan menimpa `docs/index.html`** dengan hasil generator. `docs/index.html`
> adalah landing page produksi yang dirancang khusus (dengan branding, status,
> dan link). Hanya salin konten preview ebook (`ebook.html`).

### Custom Domain `agent.pusakamedia.id`

- File `docs/CNAME` sudah berisi `agent.pusakamedia.id`.
- DNS harus diatur DIL: CNAME `agent` → `pusakamediaid-dotcom.github.io`.
- Panduan lengkap: lihat [`CUSTOM_DOMAIN_SETUP.md`](CUSTOM_DOMAIN_SETUP.md).

### Workflow Validasi Produksi

- Validator: `src/validators/production_website_validator.py`
- Workflow: `.github/workflows/production_website_check.yml`
- Output: `output/production_website_validation_report.json`
- Workflow ini **hanya memvalidasi** isi `/docs` — tidak melakukan deploy.
  Deploy ditangani langsung oleh GitHub Pages dari branch `main` folder `/docs`.

> Workflow lama `deploy_site.yml` (yang mem-publish folder `/site` lewat
> `actions/deploy-pages`) **tidak lagi menjadi sumber kebenaran** untuk
> website publik. Workflow tersebut dibiarkan untuk kompatibilitas, tetapi
> tidak perlu dijalankan saat menggunakan jalur `/docs`. Jika ingin
> menonaktifkan, hapus workflow_dispatch atau ganti `on:` menjadi nonaktif
> — **jangan dihapus** file historisnya.

---

## 1. Tujuan Website Export Layer

Website Export Layer bertujuan mengubah output utama `output/ebook.md` menjadi tiga bentuk:

1. **Website statis** (`site/index.html`) untuk preview dan publikasi via GitHub Pages.
2. **Export PDF** (`output/ebook.pdf`) jika dependency `pandoc` tersedia; jika tidak, tersedia file fallback dengan instruksi manual.
3. **Laporan validasi** (`website_validation_report.json` dan `pdf_validation_report.json`) untuk memastikan output tidak kosong dan aman.

Setelah layer ini aktif, repository dapat menjalankan mode test tanpa API, membangun artifact, dan menerbitkan website statis.

---

## 2. Struktur File Baru

File dan folder yang ditambahkan pada tahap ini:

| File / Folder | Fungsi |
|---|---|
| `src/exporters/markdown_to_html.py` | Konverter Markdown sederhana ke HTML (standard library, tanpa dependency berat) |
| `src/exporters/site_builder.py` | Membangun `site/index.html`, `site/style.css`, dan `site/metadata.json` |
| `src/exporters/pdf_exporter.py` | Export PDF via `pandoc` atau fallback note |
| `src/validators/pdf_validator.py` | Memeriksa keberadaan dan ukuran PDF / fallback |
| `src/validators/website_validator.py` | Memeriksa struktur HTML, CSS, dan placeholder fatal |
| `.github/workflows/deploy_site.yml` | Workflow deploy otomatis ke GitHub Pages |
| `.github/workflows/test_export.yml` | Workflow test export tanpa API |
| `site/index.html` | Landing page awal preview |
| `site/style.css` | Gaya murni tanpa CDN atau font eksternal |
| `site/README.md` | Penjelasan folder `site` untuk GitHub Pages |
| `samples/ebook.md` | Contoh ebook pendek (Dasar Tegangan, Arus, dan Hambatan) |
| `samples/site-preview.html` | Preview statis dari sample ebook |
| `docs/WEBSITE_EXPORT_GUIDE.md` | Dokumentasi ini |

---

## 3. Cara Menjalankan Test Export

Test export dirancang untuk **berjalan tanpa API key**, menggunakan sample ebook sebagai input.

### Via GitHub Actions (Direkomendasikan)

1. Buka tab **Actions** di repository.
2. Pilih workflow **Test Export**.
3. Klik **Run workflow** → **Run workflow**.
4. Tunggu hingga selesai.
5. Unduh artifact bernama `test-export-artifacts` dari halaman run.

### Lokal (Opsional)

```bash
# Pastikan berada di root repository
cd src/exporters
python site_builder.py

cd ../validators
python website_validator.py
python pdf_validator.py

cd ../exporters
python pdf_exporter.py
```

Hasil:
- `site/index.html` dan `site/style.css` dibuat dari `samples/ebook.md` (fallback jika `output/ebook.md` tidak ada).
- `output/pdf_validation_report.json` dan `output/website_validation_report.json` dihasilkan.
- `output/ebook_pdf_fallback.txt` muncul jika `pandoc` tidak tersedia.

---

## 4. Cara Menjalankan Site Builder Lokal

Site builder mengambil input dari `output/ebook.md` jika ada; jika tidak ada, beralih ke `samples/ebook.md`.

```bash
cd src/exporters
python site_builder.py
```

Output:
- `site/index.html` — Konten ebook dalam bentuk HTML.
- `site/style.css` — Gaya yang konsisten dan mobile-friendly.
- `site/metadata.json` — Berisi `title`, `build_time`, `source`, `status`, dan `message`.

Untuk melihat preview, buka `site/index.html` di browser.

---

## 5. Cara Deploy GitHub Pages

### Persyaratan

- Repository harus mengaktifkan **GitHub Pages** dengan source **GitHub Actions** (bukan branch).
- Workflow `deploy_site.yml` memerlukan permission `pages: write` dan `id-token: write`.

### Langkah Deploy

1. Buka **Settings** > **Pages** di repository GitHub.
2. Di bagian **Build and deployment**, pilih **Source: GitHub Actions**.
3. Buka tab **Actions** di repository.
4. Pilih workflow **Deploy Site to GitHub Pages**.
5. Klik **Run workflow** → **Run workflow**.
6. Tunggu hingga job `deploy` selesai.
7. Website dapat diakses di URL GitHub Pages repository (misalnya `https://pusakamediaid-dotcom.github.io/dil-autonomous-ebook-agent/`).

### Catatan

- Jika GitHub Pages belum diaktifkan, workflow `deploy` akan gagal dengan pesan yang jelas.
- Workflow ini tidak memaksa perubahan settings repository; admin harus mengaktifkan Pages secara manual.

---

## 6. Cara Membaca `website_validation_report.json`

File ini dihasilkan oleh `src/validators/website_validator.py` di folder `output/`.

Contoh isi:

```json
{
  "index_exists": true,
  "style_exists": true,
  "index_size_bytes": 4520,
  "basic_html_valid": true,
  "placeholder_detected": false,
  "status": "PASS",
  "message": "Website valid. HTML lengkap, tidak ada placeholder fatal."
}
```

Interpretasi status:

| Status | Arti | Tindakan |
|---|---|---|
| `PASS` | Website valid dan siap | Deploy ke GitHub Pages aman dilakukan |
| `WARNING` | Website ada tetapi ada masalah minor | Periksa `message` dan perbaiki jika perlu sebelum deploy |
| `FAIL` | Website tidak valid atau tidak ditemukan | Jalankan ulang `site_builder.py` atau periksa sumber Markdown |

Field penting:
- `index_exists`: apakah `site/index.html` ada.
- `style_exists`: apakah `site/style.css` ada.
- `basic_html_valid`: apakah terdapat tag `<html>`, `<head>`, `<body>`.
- `placeholder_detected`: apakah ada `TODO`, `FIXME`, `lorem ipsum`, atau placeholder fatal.

---

## 7. Cara Membaca `pdf_validation_report.json`

File ini dihasilkan oleh `src/validators/pdf_validator.py` di folder `output/`.

Contoh isi:

```json
{
  "pdf_exists": true,
  "pdf_size_bytes": 24580,
  "fallback_exists": false,
  "status": "PASS",
  "message": "PDF ditemukan (24580 bytes)."
}
```

Atau jika pandoc tidak tersedia:

```json
{
  "pdf_exists": false,
  "pdf_size_bytes": 0,
  "fallback_exists": true,
  "status": "WARNING",
  "message": "PDF tidak ditemukan, tetapi fallback note tersedia. Pandoc mungkin belum tersedia di environment. Lihat output/ebook_pdf_fallback.txt untuk instruksi manual."
}
```

Interpretasi status:

| Status | Arti | Tindakan |
|---|---|---|
| `PASS` | PDF valid dan berukuran > 1 KB | PDF siap digunakan |
| `WARNING` | PDF tidak ada, tetapi tersedia fallback note | Instal `pandoc` di environment lokal atau gunakan instruksi di fallback note untuk membuat PDF manual |
| `FAIL` | PDF tidak ada dan fallback note juga tidak ada | Periksa log runner; pastikan `pdf_exporter.py` berjalan tanpa error |

---

## 8. Batasan PDF Export

- **Best-effort**: PDF export pada tahap ini bersifat best-effort.
- **Dependency eksternal**: Memerlukan `pandoc` dan engine LaTeX (misalnya `xelatex` atau `lualatex`) di environment runner.
- **GitHub Actions default**: Runner `ubuntu-latest` umumnya tidak memiliki `pandoc`+LaTeX terinstal secara default, sehingga fallback note akan dihasilkan.
- **Alternatif**: Jika ingin otomatis tanpa LaTeX, dapat menambahkan `weasyprint` atau `markdown` + `pdfkit` sebagai dependency ringan. Namun, pada tahap ini kami memilih pendekatan pandoc untuk hasil typografi yang lebih baik.
- **Tidak membuat workflow gagal**: Kegagalan PDF export tidak menyebabkan workflow utama gagal.

---

## 9. Troubleshooting Umum

### `site/index.html` tidak dibuat

- Periksa apakah `output/ebook.md` atau `samples/ebook.md` ada.
- Jalankan `python src/exporters/site_builder.py` dari root repository.
- Cek log apakah ada exception di `markdown_to_html.py`.

### `site/style.css` tidak ditemukan

- `site_builder.py` akan membuat `style.css` minimal jika tidak ada.
- Jika masih hilang, salin manual dari `site/style.css` ke folder `site/`.

### Website terlihat tidak berformat

- Pastikan `style.css` berada di folder yang sama dengan `index.html` (yaitu `site/`).
- Pastikan tag `<link rel="stylesheet" href="style.css">` atau style internal ada di HTML.

### Deploy GitHub Pages gagal

- Pastikan GitHub Pages diaktifkan di **Settings > Pages** dengan source **GitHub Actions**.
- Pastikan workflow memiliki permission:
  ```yaml
  permissions:
    contents: read
    pages: write
    id-token: write
  ```
- Periksa log job `build` dan `deploy` di tab Actions.

### PDF tidak terbuat di GitHub Actions

- Ini normal jika runner tidak memiliki `pandoc`. Status akan menjadi `WARNING`.
- Untuk membuat PDF, unduh `ebook.md` dari artifact dan jalankan pandoc secara lokal:
  ```bash
  pandoc output/ebook.md -o output/ebook.pdf --pdf-engine=xelatex -V geometry:margin=2.5cm --toc
  ```

---

## 10. Checklist Sebelum Dianggap Siap Produksi

Sebelum membuka mode produksi penuh, pastikan semua poin berikut terpenuhi:

- [ ] `test_export.yml` berhasil dijalankan (status hijau / passed).
- [ ] `site/index.html` berhasil dibuat dan tidak kosong.
- [ ] `website_validation_report.json` status **`PASS`** (minimal `WARNING` dengan alasan yang jelas).
- [ ] `output/ebook.pdf` ada **atau** `output/ebook_pdf_fallback.txt` tersedia (status `PASS` atau `WARNING`).
- [ ] Tidak ada secret, API key, token, atau password di file output maupun `site/`.
- [ ] Tidak ada placeholder fatal (`TODO`, `FIXME`, `lorem ipsum`) di `site/index.html`.
- [ ] `README.md` sudah diperbarui dengan bagian **Website Export Layer** dan menjelaskan cara pakai.
- [ ] GitHub Pages berhasil menampilkan `site/` (URL bisa diakses dan konten muncul).
- [ ] Mode test menghasilkan konten yang bisa dibaca manusia (bukan placeholder generik).
- [ ] Pipeline agent utama tidak rusak: `memory_agent` → `task_planner_agent` → `router_agent` → `outline_agent` → `writer_agent` → `reviewer_agent` → `repair_agent` → `finalize` tetap berjalan.

---

*Dokumen ini merupakan bagian dari Website Export Layer pada DIL Autonomous Ebook Agent. Terakhir diperbarui: 2025-06-07.*
