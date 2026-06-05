# How to Use - DIL Ebook Agent

## Quick Start

### 1. Setup GitHub Secrets

Di repository Settings, tambahkan secrets:

```
PROVIDER_1_API_KEY=sk-your-openai-key
PROVIDER_2_API_KEY=your-gemini-key
PROVIDER_3_API_KEY=your-gemini-key
PROVIDER_4_API_KEY=your-gemini-key
PROVIDER_5_API_KEY=your-openrouter-key
```

### 2. Buat GitHub Issue

```yaml
title: "[EBOOK] Belajar Python untuk Pemula"
labels: [generate-ebook]

ebook_title: Belajar Python untuk Pemula
target_audience: Pengembang web baru
reading_level: beginner
mode: test
total_chapters: 1
content_brief: |
  Ebook panduan Python untuk pemula web developer.
  Mencakup variabel, fungsi, dan aplikasi web dasar.
approval: true
```

### 3. Tambahkan Label

Tambahkan label `generate-ebook` atau `agent-run` ke issue.

### 4. Pantau Actions

Monitor progress di tab Actions. Download artifacts saat selesai.

## Mode Produksi

### Mode Test
- 1 bab pendek
- 2-3 subbab
- Untuk validasi awal
- Biaya minimal

### Mode Session
- 3-4 bab
- Untuk satu sesi produksi ebook besar
- Maksimal 4 sesi untuk ebook penuh
- Perlu approval untuk lebih dari 4 bab

### Mode Full
- Ebook lengkap sesuai jumlah bab
- Wajib approval eksplisit
- Biaya lebih tinggi

### Mode Planning
- Hanya membuat task plan
- Estimasi biaya
- Tidak menghasilkan konten

## Reading Output

### run_report.json

```json
{
  "status": "SUCCESS",
  "mode": "session",
  "execution": {
    "agents_executed": ["memory_agent", "task_planner_agent", ...],
    "agents_failed": []
  },
  "summary": {
    "total_tokens_used": 5000,
    "total_cost_usd": 0.025
  }
}
```

### cost_report.json

```json
{
  "total_tokens": 5000,
  "total_cost_usd": 0.025,
  "limits": {
    "max_tokens_per_run": 100000,
    "max_cost_per_run": 0.50
  }
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

## Local Development

```bash
# Clone repo
git clone https://github.com/pusakamediaid-dotcom/dil-autonomous-ebook-agent.git
cd dil-autonomous-ebook-agent

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PROVIDER_1_API_KEY=sk-your-key
export GITHUB_ISSUE_TITLE="Test Ebook"
export GITHUB_ISSUE_BODY="mode: test\n..."
export GITHUB_RUN_ID=local_test

# Run generator
python src/generator.py
```

## Troubleshooting

### Issue tidak memicu workflow
- Pastikan label sudah ditambahkan: `generate-ebook` atau `agent-run`
- Cek spelling label dengan tepat

### Provider tidak tersedia
- Verifikasi secrets sudah benar
- Pastikan nama secret sesuai: `PROVIDER_1_API_KEY`, dll

### Biaya melebihi budget
- Cek cost_limits.json untuk limit
- Gunakan mode test untuk percobaan
- Kurangi jumlah bab

### Output JSON invalid
- Cek logging untuk error details
- Validasi struktur JSON
- Periksa apakah file terpotong

## Batasan

- Tidak ada klaim gratis tanpa limit
- Semua API memiliki kuota masing-masing
- Biaya dihitung berdasarkan penggunaan token
- Mode full memerlukan approval eksplisit