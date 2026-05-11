---
description: "Rules for API framework architecture, services, models, schemas, validation, and API tests. Use when adding endpoints or writing API tests."
applyTo:
  - "api/**"
  - "tests_api/**"
---

# API Automation Rules

## API Architecture

Required flow:

```
Client → Service → Model → Schema → Test
```

- **Client**: [`BaseApiClient`](../../api/base_client.py) — owns
  `requests.Session`, retries, auth, logging, Allure.
- **Service**: `api/endpoints/<resource>_service.py`.
- **Model**: `api/models/<resource>_models.py`.
- **Schema**: `api/schemas/<name>.json` (JSON Schema draft-07).
- **Test**: `tests_api/test_<resource>.py`.

---

## Services

### Good Practices
- Services must inherit `BaseApiClient`.
- One service per resource (e.g. `ProductService`, `BrandService`).
- One method per HTTP operation, returning the raw `requests.Response`.
- Store path constants on the service
  (e.g. `PRODUCTS_LIST_PATH = "productsList"`).

### Bad Practices
- Never call `requests.get/post/...` directly in tests — go through a
  Service.
- Never put assertions or business logic inside service classes.
- Never duplicate retry/auth/logging logic — it lives in
  `BaseApiClient`.

---

## Models & Schemas

### Good Practices
- Use `@dataclass` definitions.
- Add a `from_dict(cls, data: dict)` classmethod.
- Make optional fields `Optional[...] = None` so the model tolerates
  upstream changes
  (see [product_models.py](../../api/models/product_models.py)).
- Export public types via `__all__`.
- Store JSON schemas under `api/schemas/` and reference them by file
  name from tests.

### Bad Practices
- No bare dicts in test assertions when a model exists.
- No schema definitions inlined in tests.
- No mutable defaults (`= []`, `= {}`) — use `field(default_factory=...)`.

---

## Validation

### Good Practices
Use [`ResponseValidator`](../../utils/response_validator.py):
- `assert_status_code`
- `get_json`
- `assert_json_contains`
- `assert_matches_schema`
- `assert_response_time_under`

Mark tests with `@pytest.mark.api` plus, where appropriate,
`@pytest.mark.crud` / `@pytest.mark.smoke` / `@pytest.mark.regression`.

Use **module-scoped** service fixtures:
```python
@pytest.fixture(scope="module")
def product_service():
    service = ProductService()
    yield service
    service.close()
```

### Bad Practices
- No manual `jsonschema` calls — use `assert_matches_schema`.
- No raw `response.json()` — use `ResponseValidator.get_json(response)`.
- No duplicated validation helpers in tests.
- No bare `assert response.status_code == 200` without a clear message.

---

## Endpoint Creation Order

When adding a new endpoint, follow this exact order:

1. Update `config/config.yaml` (only if a new path/auth is needed).
2. Add a JSON Schema in `api/schemas/`.
3. Add dataclass models in `api/models/`.
4. Add a `Service` class in `api/endpoints/`.
5. Add tests in `tests_api/` using `ResponseValidator`.
