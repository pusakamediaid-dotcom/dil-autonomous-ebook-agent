# Error History

## Format
| Date | Error | Solution |
|------|-------|----------|

## Entries

| Date | Error | Solution |
|------|-------|----------|
| 2026-06-05 | API key exposure in logs | Implemented MaskingFilter |
| 2026-06-05 | Cost exceeded budget | Added CostGuard pre-check |
| 2026-06-05 | Invalid JSON output | Added validation before save |
| 2026-06-05 | Missing config files | Create with defaults if missing |
| 2026-06-05 | Provider not available | Graceful fallback to next provider |