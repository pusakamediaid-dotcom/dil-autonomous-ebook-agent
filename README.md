# DIL Autonomous Content & Income Agent

Agent AI berbasis GitHub Actions untuk produksi ebook teknis premium dan penghasilan konten.

## Production Website Status

| Item | Nilai |
|---|---|
| Website default | <https://pusakamediaid-dotcom.github.io/dil-autonomous-ebook-agent/> |
| Domain khusus | <http://agent.pusakamedia.id/> *(aktif setelah DNS dikonfigurasi)* |
| Source GitHub Pages | `main` / `docs` |
| Preview ebook | [`/ebook.html`](https://pusakamediaid-dotcom.github.io/dil-autonomous-ebook-agent/ebook.html) |
| Validator produksi | `src/validators/production_website_validator.py` |
| Workflow validasi | `.github/workflows/production_website_check.yml` |
| Panduan DNS | [`docs/CUSTOM_DOMAIN_SETUP.md`](docs/CUSTOM_DOMAIN_SETUP.md) |
| Laporan perbaikan terbaru | [`docs/PRODUCTION_FIX_REPORT.md`](docs/PRODUCTION_FIX_REPORT.md) |

**Catatan:** Domain khusus `agent.pusakamedia.id` memerlukan DNS CNAME
`agent` → `pusakamediaid-dotcom.github.io` yang harus diatur oleh DIL pada
panel DNS domain `pusakamedia.id`. Tanpa langkah ini, GitHub Pages akan
menampilkan 404 untuk domain custom. Lihat
[`docs/CUSTOM_DOMAIN_SETUP.md`](docs/CUSTOM_DOMAIN_SETUP.md).

---


## Deskripsi

DIL Autonomous Content & Income Agent adalah sistem yang terdiri dari 3 kelompok agent:

1. **Ebook Production Agent** — Produksi ebook teknis premium
2. **Affiliate Commerce Agent** — Riset produk affiliate dan draft konten promosi
3. **News Content Publishing Agent** — Riset berita dan draft konten untuk media sosial

**⚠️ Penting:** Semua agent ini adalah **alat bantu**, bukan mesin uang otomatis. Semua publikasi memerlukan review dan approval manusia.

## Mode Produksi

| Mode | Deskripsi | Kebutuhan |
|------|-----------|-----------|
| planning | Hanya membuat task_plan.json dan estimasi biaya | - |
| test | Membuat 1 bab pendek untuk validasi | - |
| session | Membuat 3-4 bab untuk satu sesi produksi | Approval jika > 4 bab |
| review | Mengecek output yang sudah ada | - |
| repair | Memperbaiki output yang gagal | - |

**Mode full belum dibuka untuk umum.**

## Mode Income Agent

| Mode | Deskripsi | Output | Auto-Post |
|------|-----------|--------|-----------|
| affiliate_research | Riset produk affiliate | Laporan + kandidat produk | ❌ |
| affiliate_content | Draft konten affiliate | Draft MD + compliance | ❌ |
| affiliate_publish_plan | Jadwal posting affiliate | Jadwal JSON (draft) | ❌ |
| news_research | Riset berita dari sumber resmi | Laporan berita JSON | ❌ |
| news_content | Draft konten berita | Draft MD + compliance | ❌ |
| news_publish_plan | Jadwal posting berita | Jadwal JSON (draft) | ❌ |
| income_report | Laporan potensi penghasilan | Laporan JSON | ❌ |

**Semua posting default DRAFT. Tidak ada auto-post tanpa approval.**

Lihat dokumentasi lengkap:
- [docs/MONETIZATION_WORKFLOW.md](docs/MONETIZATION_WORKFLOW.md)
- [docs/AFFILIATE_AGENT_GUIDE.md](docs/AFFILIATE_AGENT_GUIDE.md)
- [docs/NEWS_AGENT_GUIDE.md](docs/NEWS_AGENT_GUIDE.md)
- [docs/PLATFORM_SAFETY_RULES.md](docs/PLATFORM_SAFETY_RULES.md)

## API Providers

Sistem mendukung 5 provider API:

| ID | Provider | SDK Type | Model Fast | Model Strong |
|----|----------|----------|------------|--------------|
| provider_1 | OpenAI (GPT) | openai | gpt-4o-mini | gpt-4o |
| provider_2 | Gemini 1 | google-genai | gemini-1.5-flash | gemini-1.5-pro |
| provider_3 | Gemini 2 | google-genai | gemini-1.5-flash | gemini-1.5-pro |
| provider_4 | Gemini 3 | google-genai | gemini-1.5-flash | gemini-1.5-pro |
| provider_5 | OpenRouter | openai-compatible | openrouter/auto | openrouter/auto |

**Catatan:** Semua API memiliki kuota dan biaya masing-masing. Tidak ada klaim gratis tanpa limit.

## Setup GitHub Secrets

1. Buka repository Settings
2. Pilih Secrets and variables > Actions
3. Tambahkan secrets berikut:

```
PROVIDER_1_API_KEY=sk-...        # OpenAI API key
PROVIDER_2_API_KEY=...           # Gemini 1 API key
PROVIDER_3_API_KEY=...           # Gemini 2 API key
PROVIDER_4_API_KEY=...           # Gemini 3 API key
PROVIDER_5_API_KEY=...           # OpenRouter API key
```

### Income Agent Secrets (opsional)

```
TOKOPEDIA_AFFILIATE_ID=...       # ID affiliate Tokopedia
TOKOPEDIA_API_KEY=...            # API key Tokopedia (jika tersedia)
NEWS_API_KEY=...                 # NewsAPI key
GOOGLE_SEARCH_API_KEY=...        # Google Custom Search API key
GOOGLE_CSE_ID=...                # Google Custom Search Engine ID
SOCIAL_POSTING_API_KEY=...       # Social posting API key
```

**Catatan:** Jika secret tidak tersedia, agent berjalan dalam mode draft/manual.

**PENTING:** Jangan pernah menulis API key di kode atau file apapun.

## Cara Penggunaan

### Via GitHub Issue

1. Buat issue baru dengan format: `[EBOOK] Judul Ebook`
2. Pilih label `generate-ebook`
3. Isi form sesuai kebutuhan
4. Monitor progress di Actions tab

### Via Workflow Dispatch (Ebook)

1. Buka tab Actions
2. Pilih workflow "DIL Ebook Agent Run"
3. Klik "Run workflow"
4. Isi parameter sesuai kebutuhan
5. Klik "Run workflow"

### Income Agent via Issue

1. Buat issue baru dengan template "Income Agent"
2. Pilih mode (affiliate_research, news_research, dll.)
3. Isi niche, audiens, dan brief
4. Centang approval
5. Monitor di Actions tab

### Income Agent via Workflow Dispatch

1. Buka tab Actions
2. Pilih workflow "DIL Income Agent Run"
3. Klik "Run workflow"
4. Pilih mode dan isi parameter
5. Klik "Run workflow"

## Output Artifacts

| File | Deskripsi |
|------|-----------|
| ebook.md | Konten ebook utama |
| task_plan.json | Rencana tugas dan struktur |
| outline.json | Outline detail dengan subbab |
| run_report.json | Laporan eksekusi |
| cost_report.json | Rincian biaya dan token |
| review_report.json | Hasil validasi konten |
| routing_decision.json | Pilihan provider API |
| fallback_info.json | Info jika fallback dipakai |

## Reading Reports

### run_report.json

```json
{
  "status": "SUCCESS",
  "mode": "session",
  "fallback_info": {
    "fallback_used": false,
    "provider_used": "OpenAI",
    "fallback_reason": ""
  },
  "execution": {
    "agents_executed": ["memory_agent", "task_planner_agent", ...],
    "agents_failed": []
  }
}
```

### cost_report.json

```json
{
  "total_tokens": 5000,
  "total_cost_usd": 0.025,
  "provider_breakdown": {
    "provider_1": {"tokens": 5000, "cost": 0.025, "requests": 3}
  },
  "limit_exceeded": false
}
```

### review_report.json

```json
{
  "status": "PASS",
  "score": 95,
  "issues": [],
  "foreign_text_detected": false,
  "secret_leak_detected": false
}
```

## Mengetahui Fallback

Jika provider tidak tersedia atau API call gagal:
- File `fallback_info.json` akan menunjukkan `fallback_used: true`
- Field `fallback_reason` menjelaskan alasan
- Konten tetap dihasilkan menggunakan template lokal

## Mengetahui Provider yang Dipakai

- Cek `routing_decision.json` untuk melihat provider yang dipilih
- Cek `run_report.json` field `fallback_info.provider_used`
- Provider dipilih berdasarkan priority terendah yang tersedia

## Struktur Repository

```
.
├── .github/
│   ├── workflows/
│   │   ├── agent_run.yml           # Ebook workflow
│   │   └── income_agent_run.yml    # Income agent workflow
│   └── ISSUE_TEMPLATE/
│       ├── generate_ebook.yml
│       └── income_agent.yml        # Income agent template
├── config/
│   ├── model_pool.json
│   ├── cost_limits.json
│   ├── monetization_rules.json     # Income agent rules
│   ├── affiliate_rules.json        # Affiliate rules
│   ├── news_sources.json           # News source config
│   ├── publishing_rules.json       # Publishing rules
│   └── compliance_rules.json       # Compliance rules
├── src/
│   ├── agents/
│   │   ├── memory_agent.py
│   │   ├── task_planner_agent.py
│   │   ├── router_agent.py
│   │   ├── outline_agent.py
│   │   ├── writer_agent.py
│   │   ├── reviewer_agent.py
│   │   ├── repair_agent.py
│   │   ├── affiliate_commerce_agent.py    # NEW
│   │   ├── affiliate_product_research_agent.py  # NEW
│   │   ├── affiliate_content_agent.py     # NEW
│   │   ├── news_research_agent.py         # NEW
│   │   ├── news_content_agent.py          # NEW
│   │   ├── publishing_planner_agent.py    # NEW
│   │   └── compliance_agent.py            # NEW
│   ├── core/
│   │   ├── logger.py
│   │   ├── secret_manager.py
│   │   ├── run_context.py
│   │   ├── cost_guard.py
│   │   ├── api_client.py
│   │   ├── approval_gate.py               # NEW
│   │   ├── source_manager.py              # NEW
│   │   └── platform_policy_guard.py       # NEW
│   ├── validators/
│   │   ├── json_validator.py
│   │   ├── markdown_validator.py
│   │   ├── affiliate_validator.py         # NEW
│   │   ├── news_validator.py              # NEW
│   │   └── publishing_validator.py        # NEW
│   ├── generator.py                       # Ebook generator
│   └── income_generator.py                # Income agent generator
├── docs/
│   ├── MONETIZATION_WORKFLOW.md           # NEW
│   ├── AFFILIATE_AGENT_GUIDE.md           # NEW
│   ├── NEWS_AGENT_GUIDE.md                # NEW
│   └── PLATFORM_SAFETY_RULES.md           # NEW
├── memory/
│   ├── AFFILIATE_MEMORY/                  # NEW
│   ├── NEWS_MEMORY/                       # NEW
│   └── PUBLISHING_REPORTS/                # NEW
└── requirements.txt
```

## Pengembangan Lokal

```bash
# Clone repository
git clone https://github.com/pusakamediaid-dotcom/dil-autonomous-ebook-agent.git
cd dil-autonomous-ebook-agent

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export INPUT_MODE=test
export INPUT_EBOOK_TITLE="Test Ebook"
export INPUT_TARGET_AUDIENCE="Pengembang"
export INPUT_CONTENT_BRIEF="Test brief"

# Run generator
python src/generator.py
```

## Troubleshooting

### Provider tidak tersedia
- Verifikasi GitHub Secrets sudah benar
- Pastikan nama secret sesuai format

### Biaya melebihi budget
- Cek cost_limits.json untuk limit
- Gunakan mode test untuk percobaan
- Kurangi jumlah bab

### Output tidak maksimal
- Cek run_report.json untuk melihat agents yang gagal
- Cek fallback_info.json jika fallback dipakai
- Review review_report.json untuk validasi konten

## Website Export Layer

Repository sekarang mendukung pembuatan **preview website statis** dan **export PDF** (best-effort) dari ebook yang dihasilkan.

### Cara Menjalankan Test Export (Tanpa API)

Workflow `test_export.yml` dapat dijalankan secara manual untuk memvalidasi pipeline export tanpa memerlukan API key:

1. Buka tab **Actions** di repository.
2. Pilih workflow **Test Export**.
3. Klik **Run workflow** → **Run workflow**.
4. Tunggu hingga selesai dan unduh artifact.

### Cara Menjalankan Deploy Website (GitHub Pages)

Workflow `deploy_site.yml` membangun folder `site/` dan menerbitkannya ke GitHub Pages:

1. Pastikan **GitHub Pages** diaktifkan di repository Settings (Source: GitHub Actions).
2. Buka tab **Actions**.
3. Pilih workflow **Deploy Site to GitHub Pages**.
4. Klik **Run workflow** → **Run workflow**.
5. Akses website di URL GitHub Pages repository.

### Cara Melihat Artifact

Setelah workflow berjalan, artifact tersedia di halaman run workflow. Artifact berisi:
- `site/` — HTML, CSS, dan metadata preview.
- `output/` — ebook.md, laporan validasi, dan fallback PDF jika ada.
- `samples/` — contoh ebook dan preview statis.

### Catatan Penting

- **Produksi besar belum dibuka** sampai mode test lulus sepenuhnya.
- **API memiliki kuota dan biaya**; tidak ada klaim gratis tanpa limit.
- **PDF export bersifat best-effort**: jika `pandoc` tersedia, PDF akan dibuat otomatis. Jika tidak, tersedia file fallback dengan instruksi manual.
- **Website validation** menghasilkan `output/website_validation_report.json`.
- **PDF validation** menghasilkan `output/pdf_validation_report.json`.

## Batasan

- Tidak ada klaim gratis tanpa limit
- Semua API memiliki kuota masing-masing
- Biaya dihitung berdasarkan penggunaan token
- Mode full memerlukan approval eksplisit