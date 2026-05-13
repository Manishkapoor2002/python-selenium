---
name: api-test-generator
description: Generate API test components (models, services, and tests) for the Automation Exercise TAF. Use this when creating new API test cases or automating endpoints.
---

# Automation Exercise API Testing Skill

You are an expert test automation engineer. When the user asks to create an API test case, you must strictly follow the `python-selenium` TAF structure and conventions.

## Framework Constraints
- **Base URL:** `https://automationexercise.com/api`
- **Architecture:** 
  - Request/Response data must use `dataclasses` in `api/models/`.
  - API logic must reside in classes inheriting from `BaseApiClient` in `api/endpoints/`.
  - Assertions must use the `ResponseValidator` utility in `utils/response_validator.py`.
- **Markers:** Use `@pytest.mark.api` and `@pytest.mark.crud` where applicable.

## Workflow Instructions

### 1. Create the Model (`api/models/`)
Define a Python dataclass for the request payload or response.
- Example: `from dataclasses import dataclass`

### 2. Create the Endpoint Service (`api/endpoints/`)
Create a service class that inherits from `BaseApiClient`.
- Use `self.post()`, `self.get()`, etc., from the base client.
- Methods should return the response object.

### 3. Create the Test Script (`tests_api/`)
- File naming: `test_<feature>.py`.
- Fixtures: Use the `api_client` fixture.
- Validation: Do NOT use bare `assert` statements. Use `ResponseValidator` methods:
  - `ResponseValidator.assert_status_code(response, expected_code)`
  - `ResponseValidator.get_json(response)`
  - `ResponseValidator.assert_json_contains(response, {"key": expected_value})`
  - `ResponseValidator.assert_matches_schema(response, "schema_file.json")`
  - `ResponseValidator.assert_response_time_under(response, max_seconds)`

## Required Response Format
When generating the code, provide it in three distinct blocks:
1. **Model:** `api/models/<name>_models.py`
2. **Service:** `api/endpoints/<name>_service.py`
3. **Test:** `tests_api/test_<name>.py`