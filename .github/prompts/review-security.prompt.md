# Full Security Review

Perform a comprehensive security review of the specified code.

## Context
This is a Python Selenium + API test automation framework.
Refer to @security-standards.instructions.md for all rules.

## Input
Code to review: #{selection} or #{file}

## Review Checklist

### A. Secrets & Credentials
- [ ] No hardcoded passwords, tokens, API keys
- [ ] Config references use `*_env` pattern
- [ ] Test data files use placeholder credentials
- [ ] `.env` is gitignored

### B. API Security (if reviewing `api/` or `tests_api/`)
- [ ] TLS verification enabled (no `verify=False`)
- [ ] URLs constructed safely (no raw f-string interpolation)
- [ ] Sessions properly closed in all code paths
- [ ] Retry policy excludes 401/403
- [ ] Responses validated before use (schema + status code)
- [ ] Sensitive headers masked in logs and Allure attachments

### C. Selenium Security (if reviewing `core/`, `pages/`, `step_definitions/`)
- [ ] No dangerous browser flags (`--disable-web-security`, etc.)
- [ ] `execute_script()` uses parameterized arguments
- [ ] Driver properly quit in teardown (even on failure)
- [ ] Passwords masked in Page Object log statements
- [ ] No sensitive data exposed in screenshot filenames/paths

### D. Configuration (if reviewing `config/`, `core/config_loader.py`)
- [ ] `yaml.safe_load()` used exclusively
- [ ] Config values validated (type, format, range)
- [ ] No secrets in `config.yaml`
- [ ] Environment variable names don't leak values

### E. Dependencies (if reviewing `requirements.txt`)
- [ ] All packages pinned to specific versions or ranges
- [ ] No packages with known critical CVEs
- [ ] No unnecessary packages

### F. Logging & Reporting
- [ ] Auth headers masked in all log outputs
- [ ] Allure attachments don't contain raw secrets
- [ ] Error messages don't expose internal file paths
- [ ] `reports/` and `logs/` are gitignored

## Output Format

### Security Review: [scope]

**Risk Level**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | 🟢 LOW | ✅ CLEAN
**Files Reviewed**: [list]

| # | Severity | Category | CWE | Location | Finding | Fix |
|---|----------|----------|-----|----------|---------|-----|

#### Finding [#]: [Title]
**Severity**: [level]
**CWE**: [id and name]
**Location**: `file.py:line`

**Vulnerable Code**:
```python
# current code