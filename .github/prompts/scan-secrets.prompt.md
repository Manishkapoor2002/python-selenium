# Secrets Scanner

Scan the codebase for exposed secrets, credentials, and sensitive data.

## Context
This project uses:
- `.env` for secrets (loaded by `python-dotenv`)
- `config.yaml` with `*_env` references for auth
- `data/*.json` for test data (may contain test credentials)
- `BaseApiClient` with header masking for logs/Allure
- Allure reports that attach HTTP request/response details

## Scan Scope
Target: #{selection} or entire repository

## What to Find

### 1. Hardcoded Secrets (CRITICAL)
Scan all `.py`, `.yaml`, `.json`, `.feature`, `.md`, `.ini` files for:
- Passwords / passphrases
- API keys / tokens (Bearer, JWT, OAuth)
- Connection strings
- Private keys / certificates
- Base64-encoded credentials

### 2. Secret Leakage Paths (HIGH)
- Logger calls that output password/token variables
- Allure attachments with unmasked auth headers
- Screenshot filenames containing usernames
- pytest output capturing sensitive fixture values
- Error messages that include credential values

### 3. Configuration Risks (MEDIUM)
- `config.yaml` entries with literal secret values (not `*_env` refs)
- `.env` file committed to git (check `.gitignore`)
- `.env.example` containing real values instead of placeholders
- Test data files with production-like credentials

### 4. Missing Protections (LOW)
- Auth header types not covered by `BaseApiClient._mask_headers()`
- New HTTP clients not using `BaseApiClient` (bypassing masking)
- Fixtures that don't clean up auth state

## Output

### Secrets Scan Report

**Status**: 🔴 SECRETS FOUND | ✅ CLEAN

#### Hardcoded Secrets
| File | Line | Type | Value (first 4 chars) | Severity |
|------|------|------|-----------------------|----------|

#### Leakage Paths
| File | Line | How Secret Could Leak | Severity |
|------|------|-----------------------|----------|

#### Recommendations
1. [Prioritized list of actions]