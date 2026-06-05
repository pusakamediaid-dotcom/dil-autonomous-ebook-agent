# Affiliate Agent Guide - DIL Content & Income Agent

## Apa itu Affiliate Agent?

Affiliate Agent adalah sistem AI yang membantu Anda:

1. **Riset produk** — Mencari produk yang cocok untuk promosi affiliate
2. **Buat draft konten** — Membuat draf promosi yang informatif dan tidak spam
3. **Cek kepatuhan** — Memastikan konten memenuhi standar etika dan legal
4. **Buat jadwal** — Membuat rencana posting yang terstruktur

**⚠️ Penting:**
- Agent ini BUKAN mesin uang otomatis
- Semua output adalah DRAFT yang perlu review Anda
- Affiliate disclosure WAJIB disertakan
- Tidak ada auto-post tanpa approval

## Cara Menjalankan

### 1. Buat GitHub Issue

Buka tab Issues → New Issue → pilih template "Income Agent"

### 2. Isi Formulir

| Field | Contoh |
|-------|--------|
| Mode Agent | `affiliate_research` |
| Target Niche | Produk digital, perlengkapan belajar |
| Target Audiens | Pelajar, mahasiswa, kreator pemula |
| Platform | `tokopedia` atau `manual` |
| Brief Tugas | Cari produk edukatif untuk audiens DIL |
| Approval | ✅ Centang |

### 3. Tunggu Eksekusi

GitHub Actions akan menjalankan agent. Proses ini memakan waktu 1-3 menit.

### 4. Review Output

Setelah selesai, buka tab Actions → klik run terbaru → download artifact.

## Mode yang Tersedia

### affiliate_research

**Tujuan:** Mencari produk yang cocok untuk promosi affiliate.

**Input:**
- Target niche
- Target audiens
- Platform (tokopedia, shopee, manual)
- Produk manual (opsional)

**Output:**
- `affiliate_research_report.json` — Laporan riset lengkap
- `product_candidates.json` — Daftar produk kandidat
- `compliance_report.json` — Laporan kepatuhan

**Tips:**
- Jika API marketplace tidak tersedia, gunakan input manual
- Isi template CSV dengan produk yang Anda riset sendiri
- Verifikasi setiap produk sebelum dipromosikan

### affiliate_content

**Tujuan:** Membuat draft konten promosi affiliate.

**Input:**
- Produk dari `product_candidates.json` (hasil affiliate_research)
- Atau produk manual

**Output:**
- `content_drafts.md` — Draft konten lengkap
- `compliance_report.json` — Laporan kepatuhan

**Format Output:**
```markdown
# Draft Konten Affiliate

## Produk 1 — Nama Produk

### Angle Edukasi
...

### Draft Threads
...

### Draft Caption Pendek
...

### CTA
...

### Disclosure
...

### Risiko Klaim
...
```

### affiliate_publish_plan

**Tujuan:** Membuat jadwal posting affiliate.

**Output:**
- `publishing_plan.json` — Jadwal posting

**Aturan:**
- Semua status = DRAFT
- Maksimal 3 posting per hari
- Tidak ada auto-post

## Sumber Data yang Diizinkan

### ✅ Diizinkan
- API resmi marketplace (jika tersedia)
- Halaman publik produk (tanpa login)
- Input manual dari Anda
- CSV yang Anda upload

### ❌ Dilarang
- Scraping halaman login
- Cookie akun Anda
- Bot otomatis yang membuka banyak halaman
- Mengambil data yang dilarang platform

## Affiliate Disclosure

**WAJIB** menyertakan disclosure di setiap konten affiliate:

> Catatan: tautan ini bisa berupa link affiliate. Jika Anda membeli melalui link ini, saya bisa mendapat komisi tanpa biaya tambahan untuk Anda.

## Aturan Konten

### ✅ Boleh
- Konten edukatif tentang produk
- Review jujur berdasarkan riset
- Rekomendasi berdasarkan manfaat praktis
- CTA yang informatif dan tidak agresif

### ❌ Dilarang
- Klaim produk pasti menghasilkan uang
- Testimoni palsu
- Janji penghasilan pasti
- CTA agresif (beli sekarang!!!)
- Spam
- Clickbait berlebihan
- Produk ilegal atau berbahaya

## Produk yang Dilarang

- Produk ilegal
- Produk berbahaya
- Produk dewasa
- Judi
- Senjata
- Barang palsu/replica
- Skema cepat kaya

## Cara Membaca Artifact

1. Buka tab Actions di repository
2. Klik run terbaru (hijau = sukses, merah = gagal)
3. Scroll ke bawah ke bagian "Artifacts"
4. Download `affiliate-output`
5. Buka file JSON dan MD di text editor

## Troubleshooting

### "Tidak ada produk"
- Isi field "Link Produk atau Sumber Manual" dengan produk
- Atau jalankan `affiliate_research` terlebih dahulu

### "Compliance REJECT"
- Baca `compliance_report.json` untuk tahu masalahnya
- Perbaiki konten sesuai rekomendasi
- Jalankan ulang

### "Mode tidak dikenal"
- Pastikan mode salah satu dari: affiliate_research, affiliate_content, affiliate_publish_plan

## Tips Optimasi

1. **Riset dulu** — Jalankan `affiliate_research` sebelum `affiliate_content`
2. **Verifikasi manual** — Selalu verifikasi produk sebelum promosi
3. **Variasi konten** — Jangan posting konten yang sama berulang
4. **Jangan spam** — Maksimal 3 posting per hari
5. **Review semua** — Selalu review draft sebelum posting
6. **Pantau performa** — Buat `income_report` secara berkala
