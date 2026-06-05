# DIL Autonomous Ebook Agent

Agent AI berbasis GitHub Actions untuk produksi ebook teknis premium.

## Deskripsi

DIL Autonomous Ebook Agent adalah sistem yang secara otomatis menghasilkan ebook teknis berkualitas tinggi dari GitHub Issues atau workflow manual.

## Mode Produksi

| Mode | Deskripsi | Kebutuhan |
|------|-----------|-----------|
| planning | Hanya membuat task_plan.json dan estimasi biaya | - |
| test | Membuat 1 bab pendek untuk validasi | - |
| session | Membuat 3-4 bab untuk satu sesi produksi | Approval jika > 4 bab |
| review | Mengecek output yang sudah ada | - |
| repair | Memperbaiki output yang gagal | - |

**Mode full belum dibuka untuk umum.**

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

**PENTING:** Jangan pernah menulis API key di kode atau file apapun.

## Cara Penggunaan

### Via GitHub Issue

1. Buat issue baru dengan format: `[EBOOK] Judul Ebook`
2. Pilih label `generate-ebook`
3. Isi form sesuai kebutuhan
4. Monitor progress di Actions tab

### Via Workflow Dispatch

1. Buka tab Actions
2. Pilih workflow "DIL Ebook Agent Run"
3. Klik "Run workflow"
4. Isi parameter sesuai kebutuhan
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
│   ├── workflows/agent_run.yml
│   └── ISSUE_TEMPLATE/generate_ebook.yml
├── config/
│   ├── model_pool.json
│   ├── cost_limits.json
│   └── ...
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
│   │   ├── api_client.py
│   │   └── ...
│   ├── validators/
│   │   ├── json_validator.py
│   │   ├── markdown_validator.py
│   │   └── ...
│   └── generator.py
├── docs/
├── memory/
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

## Batasan

- Tidak ada klaim gratis tanpa limit
- Semua API memiliki kuota masing-masing
- Biaya dihitung berdasarkan penggunaan token
- Mode full memerlukan approval eksplisit