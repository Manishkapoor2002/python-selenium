# API Layer Security Review

Deep security review of the API automation layer.

## Context
The API layer follows this architecture:
- `api/base_client.py` → `requests.Session` wrapper with auth, retries, Allure
- `api/endpoints/*_service.py` → Thin service classes extending BaseApiClient
- `api/models/*_models.py` → @dataclass response/request models
- `api/schemas/*.json` → JSON Schema draft-07 validation
- `tests_api/test_*.py` → Tests using ResponseValidator
- `utils/response_validator.py` → Assertion helpers

## Review Points

### BaseApiClient (`api/base_client.py`)
1. **TLS Configuration**
   - Is `session.verify` always `True`?
   - Are there any `verify=False` overrides?
   - Is certificate pinning considered?

2. **Authentication Security**
   - Are credentials read from `ConfigLoader.get_api_config()` only?
   - Is the auth header set once on session (not per-request where it could be missed)?
   - Are auth tokens refreshed/rotated properly?

3. **Header Masking**
   - Does `_mask_headers()` cover: Authorization, X-API-Key, Cookie, Set-Cookie?
   - Is masking applied to BOTH request and response headers?
   - Are Allure attachments masked before attachment?

4. **Retry Policy**
   - Does `status_forcelist` exclude 401/403?
   - Are non-idempotent methods (POST/PUT/DELETE) excluded from retry?
   - Is there a maximum backoff to prevent hanging?

5. **Session Lifecycle**
   - Is `session.close()` called in all teardown paths?
   - Are there any code paths that create sessions outside BaseApiClient?

### Service Classes (`api/endpoints/`)
6. **URL Construction**
   - Are paths hardcoded constants (safe) or dynamically built (risky)?
   - Is user/test input ever interpolated into URLs without encoding?
   - Could path traversal reach unintended endpoints?

7. **Request Body Security**
   - Are request payloads built from models (safe) or raw dicts (risky)?
   - Is there input validation before sending?

### Response Handling
8. **Validation Before Trust**
   - Is `ResponseValidator.assert_status_code()` called before `.json()`?
   - Is schema validation applied for critical responses?
   - Are `from_dict()` methods defensive against missing/extra fields?

9. **Error Information Leakage**
   - Do error responses get fully logged (may contain server internals)?
   - Are assertion messages safe to appear in CI logs?

## Output
Structured findings table + detailed fixes following the format in
@security-reviewer.agent.md