# Workflow Documentation

## GitHub Actions Workflow

### Trigger Conditions

1. **Issue Label Trigger**
   - Issue labeled with `generate-ebook`
   - Or Issue labeled with `agent-run`

2. **Manual Trigger**
   - Workflow dispatch dengan inputs

### Environment Setup

```yaml
Environment Variables:
  - GITHUB_RUN_ID
  - GITHUB_ISSUE_NUMBER
  - GITHUB_ISSUE_TITLE
  - GITHUB_ISSUE_BODY
  
Secrets:
  - PROVIDER_1_API_KEY
  - PROVIDER_2_API_KEY
  - PROVIDER_3_API_KEY
  - PROVIDER_4_API_KEY
  - PROVIDER_5_API_KEY
```

## Execution Modes

### Test Mode (Default)
- 1 chapter only
- 2-3 subsections per section
- Max 5000 tokens
- Max $0.05

### Planning Mode
- Generate task plan only
- No actual content generation
- Skip router, outline, writer agents
- Max 10000 tokens

### Production Mode
- Full content generation
- All chapters as specified
- Max 100000 tokens
- Max $0.50

## Agent Execution Order

```
1. Memory Agent
   └─> Load docs & context
   
2. Task Planner Agent
   └─> Create task plan
   
3. [IF mode != planning]
   └─> Router Agent
       └─> Select provider
   
   └─> Outline Agent
       └─> Generate outline
   
   └─> Writer Agent
       └─> Write ebook

4. Report Builder
   └─> Create run & cost reports
```

## Output Artifacts

All artifacts uploaded to GitHub Actions artifacts:
- `task_plan.json`
- `outline.json`
- `ebook.md`
- `run_report.json`
- `cost_report.json`
- `memory_context.json`
- `routing_decision.json`
- `error_log.txt`

## Error Handling Flow

```
Agent Fails
    ↓
Log Error (masked)
    ↓
Mark agent as failed
    ↓
Continue to next agent
    ↓
Include in final report
```

## Success Criteria

- All required artifacts generated
- No API key exposure
- Cost within limits
- JSON valid
- Markdown formatted correctly