# Security Scanner Skill

## Description
Automated security analysis capability tailored for the python-selenium
test automation framework. Understands the project's layered architecture,
configuration patterns, and reporting pipeline.

## Capabilities

### 1. Full Security Audit
Comprehensive review across all layers:
- Secrets scan (Python, YAML, JSON, .feature, .env)
- API client security (TLS, auth, sessions, retries)
- Selenium security (browser flags, driver lifecycle, JS execution)
- Configuration security (YAML loading, validation, env vars)
- Dependency audit (pinning, known CVEs)
- Logging/reporting security (masking, Allure attachments)

### 2. Targeted Scans
- **Secrets only**: Scan for hardcoded credentials across all file types
- **API layer only**: Review base_client, services, models, schemas, tests
- **UI layer only**: Review browser factory, driver manager, pages, steps
- **Config only**: Review config.yaml, .env handling, ConfigLoader
- **Dependencies only**: Audit requirements.txt

### 3. Pre-Commit Security Check
Quick scan of changed files for:
- New hardcoded secrets
- New `verify=False` usage
- New `yaml.load()` (unsafe) usage
- New `execute_script()` with string interpolation
- New log statements exposing sensitive variables
- Unmasked headers in new Allure attachments

### 4. New Code Security Review
When adding new components:
- New endpoint service → check URL construction, auth, session handling
- New page object → check input masking, JS execution, locator safety
- New fixture → check teardown guarantees, credential handling
- New data file → check for real credentials
- New dependency → check version pinning, CVE status

### 5. Security Fix Generation
Given a finding, generate:
- Root cause analysis
- Framework-consistent fix
- Verification steps
- Prevention guidance

## Usage Examples
Full audit
"Run a complete security audit of the project"

Targeted
"Scan api/base_client.py for security issues" "Check if any test data files contain real credentials" "Review the browser factory configuration for security" "Audit requirements.txt for vulnerable dependencies"

Pre-commit style
"Security check these changed files: [files]"

New code
"Security review this new endpoint service I'm adding" "Is this page object handling passwords securely?"

Fix
"Fix the hardcoded API key in tests_api/test_product.py" "Make this execute_script call safe from injection"


## Integration Points

This skill works with:
- `@security-reviewer` agent for interactive reviews
- `/review-security` prompt for full reviews
- `/scan-secrets` prompt for credential scanning
- `/review-api-security` prompt for API layer deep-dive
- `/review-selenium-security` prompt for UI layer deep-dive
- `/fix-vulnerability` prompt for generating fixes
