# DIL Autonomous Ebook Agent - Project Bible

## Vision

DIL Autonomous Ebook Agent adalah sistem AI berbasis GitHub Actions yang secara otomatis menghasilkan ebook teknis premium dari GitHub Issues. Sistem ini dirancang untuk developer yang ingin memproduksi konten teknis berkualitas tinggi dengan efisiensi tinggi dan biaya minimal.

## Mission

- Mengotomatisasi pembuatan ebook teknis dari ide hingga output
- Mengurangi waktu produksi dari hari ke menit
- Memastikan konsistensi kualitas dan style
- Mengontrol biaya produksi dengan guardrails

## Architecture Overview

```
GitHub Issue → GitHub Actions → Agent Pipeline → Ebook Output
                    ↓
              ┌─────────┐
              │ Memory  │ ← Load docs & context
              │ Planner │ ← Plan chapters & tasks
              │ Router  │ ← Select API provider
              │ Outline │ ← Generate structure
              │ Writer  │ ← Write content
              └─────────┘
```

## Core Principles

1. **Cost First**: Selalu hitung dan batasi biaya sebelum eksekusi
2. **Safety**: Jangan pernah expose API keys atau secrets
3. **Incremental**: MVP dulu, expand later
4. **Deterministic**: Hasil konsisten untuk input yang sama
5. **Observable**: Selalu generate reports dan logs

## Terminology

| Term | Definition |
|------|------------|
| Agent | AI component yang выполняет specific task |
| Session | Single execution cycle dari generator |
| Artifact | Output file yang dihasilkan |
| Provider | AI API provider (OpenAI, Anthropic, etc) |
| Mode | Execution mode (test/planning/production) |

## Session Phases

### Session 1 (MVP)
GitHub Issue → Agent Pipeline → ebook.md + reports

### Session 2 (Enhanced)
+ API integration → Real content generation

### Session 3 (Premium)
+ PDF generation → Professional output

## Quality Standards

- Semua Python files harus punya docstring
- Semua functions harus typed parameters
- Logging dengan context yang jelas
- Error handling yang robust

## Risk Management

- API key exposure: Mitigation dengan MaskingFilter
- Cost overrun: Mitigation dengan CostGuard
- Agent failure: Mitigation dengan graceful degradation