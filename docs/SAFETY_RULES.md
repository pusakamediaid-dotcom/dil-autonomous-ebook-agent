# Safety Rules

## Critical Rules

### 1. API Keys
- **NEVER** hardcode API keys in source code
- **ALWAYS** read from environment variables
- **NEVER** log API key values
- Use MaskingFilter for all logging

### 2. Cost Control
- **ALWAYS** check cost before API calls
- **ALWAYS** set token limits
- **NEVER** exceed configured budget
- Use CostGuard for all cost tracking

### 3. GitHub Secrets
- Store all API keys in GitHub Secrets
- Reference via `${{ secrets.KEY_NAME }}`
- **NEVER** commit .env files
- **NEVER** commit actual credentials

### 4. Error Handling
- Catch all exceptions
- Log errors without exposing secrets
- Graceful degradation on failure
- Continue other agents on partial failure

### 5. Output Validation
- Validate JSON before writing
- Check file paths exist before write
- Sanitize user input
- Validate markdown structure

## Security Checklist

- [ ] No API keys in code
- [ ] No .env files committed
- [ ] MaskingFilter on all loggers
- [ ] Cost limits configured
- [ ] Secrets via GitHub Actions only
- [ ] Input validation on all user data

## Incident Response

If API key is exposed:
1. Immediately rotate the key
2. Update GitHub Secret
3. Review logging for leaked data
4. Document incident

## Dependency Security

- Use pinned versions in requirements.txt
- Audit dependencies regularly
- Avoid unknown packages
- Check licenses