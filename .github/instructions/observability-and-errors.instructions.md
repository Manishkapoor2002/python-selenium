---
mode: agent
description: Generate a new API test following the SKILL.md blueprint
tools: [filesystem, terminal]
---
# Task: Generate API Test

Create a new API test for: **${input:endpoint}**

## Steps
1. Read `api-test-generator/SKILL.md` and apply its blueprint strictly
2. Review existing tests in `tests_api/` for naming conventions
3. Check `api/schemas/` for relevant Pydantic models (create if missing)
4. Generate:
   - Endpoint client in `api/endpoints/` (if not present)
   - Pydantic request/response models in `api/schemas/`
   - Test file in `tests_api/` with `@pytest.mark.api`
5. Include Allure decorators: `@allure.feature`, `@allure.story`, `@allure.step`
6. Use `response_validator.py` for schema validation

## Verification
Run: `pytest tests_api/<new_file> -m api --alluredir=reports/allure-results`
Report pass/fail and any issues.