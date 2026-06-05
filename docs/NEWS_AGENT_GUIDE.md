# News Agent Guide - DIL Content & Income Agent

## Apa itu News Agent?

News Agent adalah sistem AI yang membantu Anda:

1. **Riset berita** — Mencari dan meringkas berita dari sumber resmi
2. **Buat draft konten** — Membuat draf konten berita untuk media sosial dan blog
3. **Cek kepatuhan** — Memastikan konten berita memenuhi standar jurnalistik
4. **Buat jadwal** — Membuat rencana posting berita yang terstruktur

**⚠️ Penting:**
- Agent ini BUKAN mesin berita otomatis
- Semua output adalah DRAFT yang perlu review Anda
- Berita WAJIB punya sumber
- Jangan menyalin artikel penuh
- Jangan membuat berita palsu

## Cara Menjalankan

### 1. Buat GitHub Issue

Buka tab Issues → New Issue → pilih template "Income Agent"

### 2. Isi Formulir

| Field | Contoh |
|-------|--------|
| Mode Agent | `news_research` |
| Topik Berita | Berita teknologi, AI, pendidikan digital |
| Brief Tugas | Riset berita terbaru tentang AI untuk konten edukatif |
| Approval | ✅ Centang |

### 3. Tunggu Eksekusi

GitHub Actions akan menjalankan agent. Proses ini memakan waktu 1-3 menit.

### 4. Review Output

Setelah selesai, buka tab Actions → klik run terbaru → download artifact.

## Mode yang Tersedia

### news_research

**Tujuan:** Mencari dan meringkas berita dari sumber resmi.

**Input:**
- Topik berita
- Link berita manual (opsional)
- Item berita manual (opsional)

**Output:**
- `news_research_report.json` — Laporan riset berita

**Tips:**
- Gunakan RSS resmi media jika tersedia
- Masukkan link berita manual jika API tidak tersedia
- Verifikasi setiap sumber

### news_content

**Tujuan:** Membuat draft konten berita.

**Input:**
- Data dari `news_research_report.json` (hasil news_research)

**Output:**
- `news_content_drafts.md` — Draft konten berita
- `compliance_report.json` — Laporan kepatuhan

**Format Output:**
```markdown
# Draft Konten Berita

## Topik: [Judul Berita]

### Ringkasan Utama
...

### Fakta Penting
...

### Konteks
...

### Draft Post Media Sosial
...

### Draft Artikel Pendek
...

### Sumber
...
```

### news_publish_plan

**Tujuan:** Membuat jadwal posting berita.

**Output:**
- `publishing_plan.json` — Jadwal posting

**Aturan:**
- Semua status = DRAFT
- Maksimal 3 posting per hari
- Tidak ada auto-post

## Sumber Berita yang Diizinkan

### ✅ Diizinkan
- RSS resmi media (BBC, TechCrunch, dll.)
- API berita resmi (NewsAPI, dll.)
- Google Custom Search API
- Input manual dari Anda
- Situs resmi lembaga dan organisasi

### ❌ Dilarang
- Menyalin artikel penuh
- Menghilangkan atribusi sumber
- Berita tanpa sumber
- Berita palsu/hoaks
- Opini seolah-olah fakta
- Sumber tidak jelas tanpa label

## Aturan Konten Berita

### ✅ Boleh
- Ringkasan berita dengan sumber
- Analisis singkat dengan label jelas
- Kutipan pendek (maksimal 50 kata)
- Tautan ke sumber asli
- Fakta dan opini dipisah

### ❌ Dilarang
- Menyalin artikel penuh
- Berita tanpa sumber
- Berita palsu/hoaks
- Judul menyesatkan
- Konten politik provokatif
- Ujaran kebencian
- Klaim tanpa sumber

## Label yang Wajib

Setiap konten berita harus memiliki label:

- **Ringkasan** — Jika konten berupa ringkasan
- **Analisis singkat** — Jika konten berupa analisis
- **Opini** — Jika konten berupa pendapat
- **Sumber:** — Selalu cantumkan sumber

## Cara Membaca Artifact

1. Buka tab Actions di repository
2. Klik run terbaru
3. Scroll ke bawah ke bagian "Artifacts"
4. Download `news-output`
5. Buka file JSON dan MD di text editor

## Contoh Penggunaan

### Riset Berita Teknologi

```
Mode: news_research
Topik: Berita teknologi dunia, AI, pendidikan digital
```

### Buat Konten dari Riset

```
Mode: news_content
(Tanpa input lain - akan menggunakan hasil news_research)
```

### Buat Jadwal Posting

```
Mode: news_publish_plan
```

## Troubleshooting

### "Tidak ada sumber berita"
- Isi field "Link Produk atau Sumber Manual" dengan URL berita
- Atau jalankan `news_research` dengan input manual

### "Compliance REJECT"
- Baca `compliance_report.json` untuk tahu masalahnya
- Pastikan ada sumber
- Jangan menyalin artikel penuh
- Perbaiki konten sesuai rekomendasi

### "Konten terlalu pendek"
- Tambahkan lebih banyak sumber berita
- Berikan analisis yang lebih mendalam
- Tambahkan konteks dan fakta pendukung

## Tips Optimasi

1. **Riset dulu** — Jalankan `news_research` sebelum `news_content`
2. **Verifikasi sumber** — Selalu verifikasi sumber berita
3. **Variasi topik** — Jangan posting topik yang sama berulang
4. **Jangan spam** — Maksimal 3 posting per hari
5. **Review semua** — Selalu review draft sebelum posting
6. **Pisahkan fakta dan opini** — Gunakan label yang jelas
7. **Cantumkan sumber** — Selalu tautkan ke sumber asli

## RSS Feed Populer

Berikut beberapa RSS feed yang bisa digunakan:

| Media | RSS Feed |
|-------|----------|
| BBC Technology | https://feeds.bbci.co.uk/news/technology/rss.xml |
| TechCrunch | https://techcrunch.com/feed/ |
| The Verge | https://www.theverge.com/rss/index.xml |
| NYT Technology | https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml |

**Catatan:** RSS feed adalah sumber publik yang diizinkan. Pastikan untuk selalu mencantumkan sumber.

## Etika Jurnalistik

1. **Akurat** — Pastikan fakta benar
2. **Berimbang** — Sajikan berbagai sudut pandang
3. **Jelas sumber** — Cantumkan sumber yang kredibel
4. **Pisahkan fakta dan opini** — Gunakan label yang jelas
5. **Tidak menyesatkan** — Hindari judul clickbait
6. **Hormati privasi** — Jangan sebar data pribadi
7. **Tidak ujaran kebencian** — Hindari konten yang memecah belah
