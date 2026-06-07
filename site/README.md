# Folder Site

Folder `site/` digunakan untuk menyimpan output website statis yang diterbitkan melalui **GitHub Pages**.

## Isi Folder

- `index.html` — Halaman utama yang dibuat atau diperbarui oleh `src/exporters/site_builder.py`.
- `style.css` — Gaya CSS murni tanpa CDN atau font eksternal.
- `metadata.json` — Metadata build yang mencatat judul, waktu build, sumber input, dan status.

## Cara Kerja

1. `src/exporters/site_builder.py` membaca `output/ebook.md` (atau `samples/ebook.md` sebagai fallback).
2. File Markdown dikonversi menjadi HTML menggunakan `src/exporters/markdown_to_html.py`.
3. Hasil ditulis ke `site/index.html`.
4. `site/style.css` dipastikan tersedia untuk menyediakan gaya yang konsisten.
5. `site/metadata.json` dibuat untuk pelacakan build.

## GitHub Pages

Untuk menerbitkan folder ini ke GitHub Pages:

1. Buka **Settings** > **Pages** di repository.
2. Pilih **Source: GitHub Actions**.
3. Jalankan workflow `.github/workflows/deploy_site.yml`.
4. Website akan tersedia di URL GitHub Pages repository.

## Keamanan

- **Jangan** menaruh API key, token, password, atau secret di folder `site/`.
- Semua file di folder ini bersifat **public** setelah diterbitkan ke GitHub Pages.
- Pastikan tidak ada informasi sensitif di `output/ebook.md` sebelum site dibangun.
