# How to Use

## Quick Start

### 1. Setup GitHub Secrets

Di repository Settings → Secrets and variables → Actions:

```
PROVIDER_1_API_KEY=sk-your-openai-key
PROVIDER_2_API_KEY=sk-ant-your-anthropic-key
PROVIDER_3_API_KEY=your-gemini-key
# ... dst
```

### 2. Create GitHub Issue

Buat issue baru dengan format:

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

### 3. Add Label

Tambahkan label `generate-ebook` ke issue.

### 4. Watch Actions Run

Monitor progress di Actions tab.

### 5. Download Artifacts

Download generated files dari Artifacts section.

## Manual Trigger

Untuk testing, bisa trigger manual:

1. Go to Actions tab
2. Select "DIL Ebook Agent Run"
3. Click "Run workflow"
4. Fill inputs
5. Click "Run workflow"

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

# Run generator
python src/generator.py
```

## Understanding Output

### run_report.json
```json
{
  "status": "completed",
  "mode": "test",
  "execution": {
    "agents_executed": ["memory_agent", "task_planner_agent", ...],
    "agents_failed": []
  },
  "summary": {
    "total_tokens_used": 1500,
    "total_cost_usd": 0.015
  }
}
```

### cost_report.json
```json
{
  "total_tokens": 1500,
  "total_cost_usd": 0.015,
  "limits": {
    "max_tokens_per_run": 100000,
    "max_cost_per_run": 0.50
  }
}
```

## Troubleshooting

### Issue not triggering
- Check label spelling: `generate-ebook` atau `agent-run`
- Check workflow conditions

### No API provider
- Verify secrets are set
- Check secret names match `PROVIDER_X_API_KEY`

### Cost exceeded
- Check cost_limits.json
- Reduce chapter count
- Use test mode

### Invalid JSON output
- Check logging for errors
- Validate output manually
- Check Python syntax