# Monetization Workflow - DIL Content & Income Agent

## ⚠️ Penting: Bukan Mesin Uang Otomatis

Agent ini **BUKAN** mesin uang instan atau sistem penghasil uang otomatis. Agent ini adalah **alat bantu** untuk:

1. **Riset** — Mencari peluang produk affiliate dan berita dari sumber resmi
2. **Draft** — Membuat draf konten yang perlu review manusia
3. **Perencanaan** — Membuat jadwal posting yang perlu approval manusia
4. **Laporan** — Membuat laporan potensi dan rekomendasi

**Semua publikasi memerlukan review dan approval manusia.**

## Arsitektur Agent

```
DIL Content & Income Agent
├── Ebook Production Agent (sudah ada)
│   └── Produksi ebook melalui GitHub Actions
│
├── Affiliate Commerce Agent (baru)
│   ├── AffiliateProductResearchAgent → Riset produk
│   ├── AffiliateContentAgent → Draft konten promosi
│   ├── ComplianceAgent → Cek kepatuhan
│   └── PublishingPlannerAgent → Jadwal posting
│
└── News Content Publishing Agent (baru)
    ├── NewsResearchAgent → Riset berita
    ├── NewsContentAgent → Draft konten berita
    ├── ComplianceAgent → Cek kepatuhan
    └── PublishingPlannerAgent → Jadwal posting
```

## Mode Kerja

| Mode | Deskripsi | Output | Approval |
|------|-----------|--------|----------|
| `affiliate_research` | Riset produk affiliate | Laporan + kandidat produk | Tidak |
| `affiliate_content` | Buat draft konten affiliate | Draft konten MD | Tidak |
| `affiliate_publish_plan` | Buat jadwal posting affiliate | Jadwal JSON | Tidak |
| `news_research` | Riset berita dari sumber resmi | Laporan berita JSON | Tidak |
| `news_content` | Buat draft konten berita | Draft konten MD | Tidak |
| `news_publish_plan` | Buat jadwal posting berita | Jadwal JSON | Tidak |
| `income_report` | Buat laporan potensi penghasilan | Laporan JSON | Tidak |

## Alur Kerja Affiliate

```
1. User membuat Issue dengan label "income-agent-run"
   ↓
2. GitHub Actions memicu income_agent_run.yml
   ↓
3. IncomeGenerator membaca input dari Issue
   ↓
4. AffiliateCommerceAgent dijalankan:
   a. ProductResearchAgent → riset produk
   b. ContentAgent → buat draft konten
   c. ComplianceAgent → cek kepatuhan
   d. PlannerAgent → buat jadwal
   ↓
5. Output disimpan di output/affiliate/
   ↓
6. User mereview output
   ↓
7. User mempublikasikan secara manual
```

## Alur Kerja Berita

```
1. User membuat Issue dengan label "income-agent-run"
   ↓
2. GitHub Actions memicu income_agent_run.yml
   ↓
3. IncomeGenerator membaca input dari Issue
   ↓
4. NewsAgent dijalankan:
   a. NewsResearchAgent → riset berita
   b. NewsContentAgent → buat draft konten
   c. ComplianceAgent → cek kepatuhan
   d. PlannerAgent → buat jadwal
   ↓
5. Output disimpan di output/news/
   ↓
6. User mereview output
   ↓
7. User mempublikasikan secara manual
```

## Sumber Data yang Diizinkan

### Affiliate
- ✅ API resmi marketplace (jika tersedia)
- ✅ Halaman publik produk (tanpa login)
- ✅ Input manual dari user
- ✅ CSV yang diupload user
- ❌ Scraping halaman login
- ❌ Cookie akun user
- ❌ Bot otomatis

### Berita
- ✅ RSS resmi media
- ✅ API berita resmi
- ✅ Google Custom Search API
- ✅ Input manual dari user
- ✅ Situs resmi lembaga
- ❌ Menyalin artikel penuh
- ❌ Berita tanpa sumber
- ❌ Berita palsu

## Sumber Data yang Dilarang

1. **Login scraping** — Jangan mengambil data dari halaman yang butuh login
2. **Cookie stealing** — Jangan menggunakan cookie akun user
3. **Automated browsing** — Jangan membuka banyak halaman secara otomatis
4. **Rate limit abuse** — Jangan melanggar batas request
5. **Full article copy** — Jangan menyalin artikel penuh
6. **Fake news** — Jangan membuat berita palsu

## Keamanan

### API Key
- Semua API key disimpan di GitHub Secrets
- Tidak ada API key di file kode
- Tidak ada API key di log

### Approval Gate
- Semua publikasi memerlukan approval
- Semua konten default DRAFT
- Tidak ada auto-post tanpa approval

### Cost Guard
- Semua agent punya cost guard
- Batas token per run
- Batas biaya per run

### Compliance Agent
- Cek disclosure affiliate
- Cek sumber berita
- Cek klaim palsu
- Cek spam
- Cek ujaran kebencian

## Output

### Affiliate
- `output/affiliate/affiliate_research_report.json` — Laporan riset
- `output/affiliate/product_candidates.json` — Kandidat produk
- `output/affiliate/content_drafts.md` — Draft konten
- `output/affiliate/affiliate_publish_plan.json` — Jadwal posting
- `output/affiliate/compliance_report.json` — Laporan kepatuhan

### Berita
- `output/news/news_research_report.json` — Laporan riset
- `output/news/news_content_drafts.md` — Draft konten
- `output/news/compliance_report.json` — Laporan kepatuhan

### Publishing
- `output/publishing/publishing_plan.json` — Jadwal posting

### Reports
- `output/run_report.json` — Laporan eksekusi
- `output/cost_report.json` — Laporan biaya
- `output/error_log.txt` — Log error
