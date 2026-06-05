# DIL Autonomous Ebook Agent

Agent AI berbasis GitHub Actions untuk produksi ebook teknis premium.

## Sesi 1 MVP

Target Sesi 1: GitHub Issue → GitHub Actions → Task Planner → Router → Outline Agent → Writer Agent → ebook.md + reports

### Fitur
- Memory Agent - Load documentation context
- Task Planner Agent - Plan ebook structure
- Router Agent - Select API provider
- Outline Agent - Generate detailed outline
- Writer Agent - Write ebook content
- Cost Guard - Track and limit spending
- Report Builder - Generate execution reports

### Prerequisites

1. Python 3.11+
2. GitHub Secrets configured:
   - `PROVIDER_1_API_KEY` - OpenAI key
   - `PROVIDER_2_API_KEY` - Anthropic key
   - `PROVIDER_3_API_KEY` - Google Gemini key
   - `PROVIDER_4_API_KEY` - Cohere key
   - `PROVIDER_5_API_KEY` - Mistral AI key

### Setup

```bash
# Clone repository
git clone https://github.com/pusakamediaid-dotcom/dil-autonomous-ebook-agent.git
cd dil-autonomous-ebook-agent

# Install dependencies
pip install -r requirements.txt

# Run locally
python src/generator.py
```

### Usage

1. Buat GitHub Issue dengan label `generate-ebook`
2. Workflow akan dijalankan otomatis
3. Download artifacts dari Actions tab

### Output Artifacts

- `ebook.md` - Main content
- `task_plan.json` - Task plan
- `outline.json` - Detailed outline
- `run_report.json` - Execution report
- `cost_report.json` - Cost breakdown

## Documentation

- [PROJECT_BIBLE.md](docs/PROJECT_BIBLE.md) - Project overview
- [STYLE_GUIDE.md](docs/STYLE_GUIDE.md) - Writing style guide
- [TERMINOLOGY_RULES.md](docs/TERMINOLOGY_RULES.md) - Terminology rules
- [SAFETY_RULES.md](docs/SAFETY_RULES.md) - Security guidelines
- [WORKFLOW.md](docs/WORKFLOW.md) - Workflow documentation
- [HOW_TO_USE.md](docs/HOW_TO_USE.md) - Usage guide

## License

MIT