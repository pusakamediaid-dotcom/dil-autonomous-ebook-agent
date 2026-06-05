# DIL Autonomous Ebook Agent

Agent AI berbasis GitHub Actions untuk produksi ebook teknis premium.

## Deskripsi

DIL Autonomous Ebook Agent adalah sistem yang secara otomatis menghasilkan ebook teknis berkualitas tinggi dari GitHub Issues. Sistem ini dirancang untuk produksi bertahap dan aman.

## Mode Produksi

| Mode | Deskripsi | Kebutuhan |
|------|-----------|-----------|
| planning | Hanya membuat task_plan.json dan estimasi biaya | - |
| test | Membuat 1 bab pendek untuk validasi | - |
| session | Membuat 3-4 bab untuk satu sesi produksi | Approval jika > 4 bab |
| full | Ebook penuh | Wajib approval |
| review | Mengecek output yang sudah ada | - |
| repair | Memperbaiki output yang gagal | - |
| html | Konversi Markdown ke HTML | Siap untuk development |
| pdf | Persiapan konversi PDF | Siap untuk development |

## API Providers

Sistem mendukung 5 provider API:

| ID | Provider | SDK Type |
|----|----------|----------|
| provider_1 | OpenAI (GPT) | openai |
| provider_2 | Gemini 1 | google-genai |
| provider_3 | Gemini 2 | google-genai |
| provider_4 | Gemini 3 | google-genai |
| provider_5 | OpenRouter | openai-compatible |

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

**PENTING:** Jangan pernah menulis API key di kode atau file apapun.

## Cara Penggunaan

### 1. Buat GitHub Issue

Buat issue baru dengan judul format: `[EBOOK] Judul Ebook`

### 2. Isi Form

Isi field sesuai kebutuhan:
- Judul Ebook
- Target Pembaca
- Level Pembaca
- Mode Produksi (pilih: test, session, dll)
- Jumlah Bab
- Brief Konten
- Approval (centang untuk mode besar)

### 3. Tambahkan Label

Tambahkan label `generate-ebook` atau `agent-run` ke issue.

### 4. Monitor Actions

Buka tab Actions untuk melihat progress. Download artifacts saat selesai.

## Output Artifacts

Setelah proses selesai, artifacts berikut tersedia:

| File | Deskripsi |
|------|-----------|
| ebook.md | Konten ebook utama |
| task_plan.json | Rencana tugas dan struktur |
| outline.json | Outline detail dengan subbab |
| run_report.json | Laporan eksekusi |
| cost_report.json | Rincian biaya dan token |
| review_report.json | Hasil validasi konten |
| routing_decision.json | Pilihan provider API |
| memory_context.json | Konteks dari dokumentasi |

## Struktur Repository

```
.
├── .github/
│   ├── workflows/
│   │   └── agent_run.yml
│   └── ISSUE_TEMPLATE/
│       └── generate_ebook.yml
├── config/
│   ├── model_pool.json
│   ├── cost_limits.json
│   ├── agent_roles.json
│   └── output_rules.json
├── docs/
│   ├── PROJECT_BIBLE.md
│   ├── STYLE_GUIDE.md
│   ├── TERMINOLOGY_RULES.md
│   ├── SAFETY_RULES.md
│   ├── WORKFLOW.md
│   └── HOW_TO_USE.md
├── src/
│   ├── agents/
│   │   ├── memory_agent.py
│   │   ├── task_planner_agent.py
│   │   ├── router_agent.py
│   │   ├── outline_agent.py
│   │   ├── writer_agent.py
│   │   ├── reviewer_agent.py
│   │   └── repair_agent.py
│   ├── core/
│   │   ├── logger.py
│   │   ├── secret_manager.py
│   │   ├── run_context.py
│   │   ├── cost_guard.py
│   │   ├── report_builder.py
│   │   ├── task_schema.py
│   │   └── api_client.py
│   ├── validators/
│   │   ├── json_validator.py
│   │   ├── markdown_validator.py
│   │   ├── output_validator.py
│   │   └── safety_validator.py
│   └── generator.py
├── memory/
│   ├── DECISION_LOG.md
│   └── ERROR_HISTORY.md
└── requirements.txt
```

## Pengembangan Lokal

```bash
# Clone repository
git clone https://github.com/pusakamediaid-dotcom/dil-autonomous-ebook-agent.git
cd dil-autonomous-ebook-agent

# Install dependencies
pip install -r requirements.txt

# Setup environment
export PROVIDER_1_API_KEY=sk-your-key
export GITHUB_ISSUE_TITLE="Test Ebook"

# Run generator
python src/generator.py
```

## Keamanan

- Semua API key dibaca dari GitHub Secrets
- Tidak ada API key di kode atau log
- Logging menggunakan MaskingFilter
- Validasi konten untuk deteksi secrets
- Cost guard untuk mencegah budget overrun

## Lisensi

MIT