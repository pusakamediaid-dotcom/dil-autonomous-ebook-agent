# Workflow Documentation - DIL Ebook Agent

## GitHub Actions Workflow

### Trigger Conditions

1. **Issue Label Trigger**
   - Issue memiliki label `generate-ebook`
   - Atau issue memiliki label `agent-run`

2. **Manual Trigger**
   - Workflow dispatch dengan input parameters

### Environment Variables

```yaml
Environment Variables:
  - GITHUB_RUN_ID: Run ID
  - GITHUB_ISSUE_NUMBER: Issue number
  - GITHUB_ISSUE_TITLE: Issue title
  - GITHUB_ISSUE_BODY: Issue body dengan form fields

Secrets:
  - PROVIDER_1_API_KEY: OpenAI key
  - PROVIDER_2_API_KEY: Gemini 1 key
  - PROVIDER_3_API_KEY: Gemini 2 key
  - PROVIDER_4_API_KEY: Gemini 3 key
  - PROVIDER_5_API_KEY: OpenRouter key
```

## Execution Flow

```
GitHub Issue
    |
    v
[Label: generate-ebook / agent-run]
    |
    v
GitHub Actions Trigger
    |
    v
Python Syntax Validation
    |
    v
Memory Agent
    | Load docs & context
    v
Task Planner Agent
    | Create task_plan.json
    v
[Mode Check]
    |
    +-- planning --> Generate report --> DONE
    |
    v
Approval Gate
    |
    v
Router Agent
    | Select API provider
    v
Cost Guard
    | Check budget
    v
Outline Agent
    | Generate outline.json
    v
Writer Agent
    | Generate ebook.md
    v
Reviewer Agent
    | Validate content
    v
[Review Status]
    |
    +-- PASS --> Continue
    +-- REPAIR --> Repair Agent (max 2 iterations)
    +-- REJECT --> Stop with error
    |
    v
Output Validator
    | Validate artifacts
    v
Report Builder
    | Generate reports
    v
Artifact Upload
    |
    v
Issue Comment
    |
    v
DONE
```

## Mode Details

### Test Mode
- Generate 1 bab pendek
- 2-3 subbab per bab
- Max 5000 tokens
- Max $0.05

### Session Mode
- Generate 3-4 bab
- 3-5 subbab per bab
- Max 50000 tokens
- Max $0.25
- Approval jika > 4 bab

### Full Mode
- Generate semua bab sesuai request
- Max 100000 tokens
- Max $0.50
- Wajib approval

### Planning Mode
- Generate task_plan.json only
- No content generation
- Max 10000 tokens

## Agent Execution Order

| Order | Agent | Function |
|-------|-------|----------|
| 1 | MemoryAgent | Load documentation and context |
| 2 | TaskPlannerAgent | Create task plan from issue |
| 3 | RouterAgent | Select best available API provider |
| 4 | OutlineAgent | Generate detailed outline |
| 5 | WriterAgent | Write ebook content |
| 6 | ReviewerAgent | Validate output quality |
| 7 | RepairAgent | Fix issues (if needed) |

## Output Artifacts

All artifacts uploaded to GitHub Actions:

| Artifact | File | Description |
|----------|------|-------------|
| All Output | ebook-output/ | All files in output/ directory |

### Individual Files

- `task_plan.json` - Task plan with structure
- `outline.json` - Detailed outline with subtopics
- `ebook.md` - Main ebook content
- `run_report.json` - Execution report
- `cost_report.json` - Cost breakdown
- `review_report.json` - Quality validation
- `routing_decision.json` - Provider selection
- `memory_context.json` - Loaded documentation
- `ebook_repaired.md` - Fixed content (if needed)

## Error Handling

```
Agent Fails
    |
    v
Log Error (masked - no secrets)
    |
    v
Mark agent as failed
    |
    v
Continue to next agent (if possible)
    |
    v
Include in final report
    |
    v
Status: PARTIAL_SUCCESS or FAILED
```

## Cost Management

- CostGuard checks budget before each API call
- Estimated cost shown in task_plan.json
- Actual cost tracked in cost_report.json
- Pipeline stops if budget exceeded

## Success Criteria

- All required artifacts generated
- No API key exposure
- Cost within limits
- JSON files valid
- Markdown properly formatted
- No foreign text in content
- All 5 layers present in each subsection