# /docs — Website Publik DIL Autonomous Ebook Agent

Folder ini adalah **sumber resmi website publik produksi** yang di-host oleh GitHub Pages.

## Konfigurasi GitHub Pages

- **Source**: Deploy from a branch
- **Branch**: `main`
- **Folder**: `/docs`
- **Custom domain**: `agent.pusakamedia.id` (via `docs/CNAME`)

## File Penting

| File | Fungsi |
|---|---|
| `index.html` | Landing page utama (tampilan publik) |
| `index.md` | Fallback Markdown |
| `ebook.html` | Preview ebook contoh |
| `CNAME` | Custom domain GitHub Pages |
| `CUSTOM_DOMAIN_SETUP.md` | Panduan DNS untuk DIL |
| `PRODUCTION_FIX_REPORT.md` | Laporan audit & perbaikan terbaru |
| `WEBSITE_EXPORT_GUIDE.md` | Panduan export website & PDF |

## URL

- Default: <https://pusakamediaid-dotcom.github.io/dil-autonomous-ebook-agent/>
- Custom domain (setelah DNS aktif): <http://agent.pusakamedia.id/>

## Hubungan dengan `/site`

- `/site` = output generator / staging (dihasilkan oleh `src/exporters/site_builder.py`).
- `/docs` = website publik stabil (yang Anda lihat sekarang).

Untuk menyalin hasil terbaru dari `/site` ke `/docs`, lihat `WEBSITE_EXPORT_GUIDE.md`.

## Larangan

- Jangan menaruh secret, API key, token, atau data rahasia di folder ini.
- Jangan menambahkan klaim "gratis tanpa limit" atau "penghasilan pasti".
- Jangan mengaktifkan auto-posting tanpa approval manusia.
