#Project : python-selenium

- **UI tests** with Selenium WebDriver + pytest-bdd (Gherkin features).
- **API tests** with `requests` + `jsonschema`, organized as endpoint
  services + dataclass models + JSON schemas.
- **Allure** reporting, file/CLI logging, and on-failure screenshot capture.

Use these instructions as the source of truth for conventions, layout,
and dependencies. Prefer editing/extending existing modules over creating
parallel ones.

---

## 1. Tech Stack & Dependencies

Declared in [requirements.txt](../requirements.txt):

| Purpose            | Packages                                                |
|--------------------|---------------------------------------------------------|
| Test runner        | `pytest`, `pytest-bdd`, `pytest-xdist`, `pytest_check`  |
| UI automation      | `selenium`, `webdriver-manager`                         |
| API automation     | `requests`, `jsonschema`                                |
| Reporting          | `allure-pytest`                                         |
| Config / data      | `PyYAML`, `python-dotenv`                               |

Runtime expectations:

- Python 3.10+ (uses `from __future__ import annotations` and modern typing).
- A local Chrome / Firefox / Edge browser. Selenium Manager (built into
  Selenium 4) resolves drivers; `webdriver-manager` is listed but not
  required by [core/browser_factory.py](../core/browser_factory.py).
- Allure CLI installed separately to render `reports/allure-results/`.

---

## 2. Project Structure

```
python-selenium/
├── api/                      # API automation layer
│   ├── base_client.py        # requests.Session wrapper (retries, auth, Allure)
│   ├── endpoints/            # One *Service class per resource (e.g. ProductService)
│   ├── models/               # @dataclass response/request models with from_dict()
│   └── schemas/              # JSON Schema (draft-07) files used by validators
├── config/
│   └── config.yaml           # Shared UI + API config (env overrides supported)
├── core/
│   ├── browser_factory.py    # Static factory: chrome | firefox | edge
│   ├── config_loader.py      # YAML + .env loader with caching + API overlay
│   └── driver_manager.py     # Thread-safe Singleton + per-thread WebDriver
├── data/                     # JSON/YAML test data (loaded via *DataLoader)
├── features/                 # Gherkin .feature files (pytest-bdd)
├── pages/                    # Page Objects, all inherit BasePage
├── step_definitions/         # pytest-bdd step modules (test_*.py)
├── tests_api/                # API pytest tests + API-only fixtures
├── utils/                    # Cross-cutting helpers (loaders, validators, logging)
├── reports/
│   ├── allure-results/       # Raw Allure output (cleaned each run)
│   └── screenshots/          # Failure screenshots
├── logs/                     # pytest log file output
├── conftest.py               # Root fixtures + failure screenshot hook
├── pytest.ini                # markers, logging, allure dir, testpaths
└── requirements.txt
```

`pytest.ini` restricts discovery to `step_definitions` and `tests_api`.
Do **not** put runnable tests in `pages/`, `api/`, `core/`, or `utils/`.

---

## 3. Configuration

- Single source of truth: [config/config.yaml](../config/config.yaml).
- Loaded by `ConfigLoader` ([core/config_loader.py](../core/config_loader.py)); cached.
  Pass `reload=True` to force re-read.
- `.env` is auto-loaded via `python-dotenv`. Recognized overrides:
  - `BROWSER`, `BASE_URL` (UI)
  - `API_ENV` (selects an entry under `api.environments`)
  - `API_BASE_URL` (overrides API base URL)
  - `API_BEARER_TOKEN`, `API_USERNAME`, `API_PASSWORD`, `API_KEY` (auth)
- Access API config via `ConfigLoader.get_api_config()`; never re-parse YAML.
- **Never commit secrets.** Use `.env` plus the `*_env` fields in
  `config.yaml > api.auth`.

---

## 4. UI Test Conventions

### Page Objects (`pages/`)

- Every page inherits [`BasePage`](../pages/base_page.py) and takes `driver` in `__init__`.
- Use `self.wait` (10s `WebDriverWait`) and the helpers `click`, `enter_text`,
  `get_text`, `is_displayed` — do not call Selenium directly unless adding a
  new helper to `BasePage`.
- Locators are **method-local tuples** of `(By.X, "selector")`. Prefer
  `data-qa` / stable attributes over brittle text or absolute XPath.
- Navigation methods that move to another page must return the next
  Page Object. Use **deferred imports** to avoid circular imports
  (see `HomePage.navigate_to_login_page`).
- Log meaningful actions via `self.logger.info(...)`.

### BDD (`features/` + `step_definitions/`)

- One `.feature` per user-facing capability, tagged with `@smoke` /
  `@regression` (declared in `pytest.ini > markers`).
- Step modules call `scenarios('../features/<file>.feature')` at the top.
- Steps share state through the `context_state` fixture
  (`{"driver": ..., "wait": WebDriverWait(driver, 10)}`). Store page
  objects on it (`context_state["homepage"] = ...`) instead of using globals.
- Data comes from the `users_data` fixture (JSON in `data/`); do not
  hardcode credentials inside steps.
- Use `pytest_check.is_true` for soft assertions where appropriate.

### Browser & Driver Lifecycle

- `DriverManager` is a thread-safe Singleton with a **per-thread** WebDriver
  (safe under `pytest-xdist`). Always go through
  `DriverManager().get_driver(...)` / `.quit_driver()`; never instantiate
  `webdriver.Chrome()` directly outside `BrowserFactory`.
- The root `driver` fixture (in [conftest.py](../conftest.py)) is
  function-scoped, navigates to `base_url`, maximizes the window, and registers
  the driver in `_driver_store` so the screenshot hook can find it.
- Failure screenshots: handled by `pytest_runtest_makereport` plus
  [`ScreenshotManager`](../utils/screenshot_manager.py); attached to Allure
  automatically. Do not duplicate this logic in tests.

---

## 5. API Test Conventions

### Layered model — keep these layers separate

1. **Client** — [`BaseApiClient`](../api/base_client.py)
   - Owns `requests.Session`, retry policy (`urllib3 Retry`), authentication,
     structured logging, and Allure step/attachments.
   - Exposes verb helpers `get / post / put / patch / delete`, all returning
     the raw `requests.Response`.
   - Reads config via `ConfigLoader.get_api_config()`; do not bypass it.

2. **Service** — `api/endpoints/<resource>_service.py`
   - Subclass `BaseApiClient`.
   - Declare path constants (e.g. `PRODUCTS_LIST_PATH = "productsList"`).
   - One method per operation, returning `Response`. Keep them thin —
     no assertions, no business logic.

3. **Model** — `api/models/<resource>_models.py`
   - `@dataclass` definitions with a `from_dict(cls, data: dict)` classmethod.
   - Optional fields default to `None` so the model tolerates upstream changes
     (see [product_models.py](../api/models/product_models.py)).
   - Export public types via `__all__`.

4. **Schema** — `api/schemas/<name>.json`
   - JSON Schema draft-07, referenced by file name from tests.

5. **Test** — `tests_api/test_<resource>.py`
   - Use module-scoped service fixtures (`yield service; service.close()`).
   - Validate via [`ResponseValidator`](../utils/response_validator.py):
     `assert_status_code`, `get_json`, `assert_json_contains`,
     `assert_matches_schema`, `assert_response_time_under`.
   - Mark tests with `@pytest.mark.api` and where appropriate
     `@pytest.mark.crud` / `@pytest.mark.smoke` / `@pytest.mark.regression`.
   - Raise `AssertionError` with a descriptive message on contract violations.

### Shared API fixtures

- [tests_api/conftest.py](../tests_api/conftest.py) provides a
  **session-scoped** `api_client` (connection pooling). Add new generic
  fixtures here; resource-specific service fixtures live next to the test.

### Adding a new endpoint — required order

1. Add path/auth config to `config/config.yaml` if needed.
2. Add a JSON Schema under `api/schemas/`.
3. Add dataclass models under `api/models/`.
4. Add a `Service` class under `api/endpoints/`.
5. Add tests under `tests_api/` using `ResponseValidator`.

---

## 6. Data Loading

- UI / general data → `TestDataLoader.load_json("file.json")`
  ([utils/test_data_loader.py](../utils/test_data_loader.py)) — cached, read-only.
- API data → `ApiDataLoader.load("file.json|yaml")`
  ([utils/api_data_loader.py](../utils/api_data_loader.py)) — cached **and
  deep-copied** so tests can safely mutate the result.
- All data files live under `data/`. Do not read JSON/YAML inline in tests.

---

## 7. Logging & Reporting

- Logging is initialized once in `setup_logging()`
  ([utils/logger_config.py](../utils/logger_config.py)); also configured by
  `pytest.ini` for CLI and `logs/pytest-logs.txt`.
- Get a logger with `logging.getLogger(__name__)`; do not call
  `logging.basicConfig` again.
- Never log secrets. `BaseApiClient` already masks `Authorization` and
  `X-API-Key` headers — preserve that behavior.
- Every HTTP call and failure produces Allure attachments via `BaseApiClient`.
  UI failures get a PNG attached via the root hook.

---

## 8. Running Tests

From the repo root (Windows PowerShell, with the project venv activated):

```powershell
# All tests (UI + API)
pytest

# Only API tests
pytest tests_api -m api

# Only UI BDD tests
pytest step_definitions

# Smoke subset, in parallel
pytest -m smoke -n auto

# Generate & open Allure report (Allure CLI required)
allure serve reports/allure-results
```

`pytest.ini` already sets `--alluredir=reports/allure-results --clean-alluredir`;
do not override unless intentional.

---

## 9. Coding Standards

- **Style**: PEP 8, 4-space indent, type hints on new public functions.
  Use `from __future__ import annotations` in new modules (matches the API layer).
- **Imports**: stdlib → third-party → local, separated by blank lines.
  Avoid wildcard imports. Use deferred imports only to break Page-Object cycles.
- **Errors**: raise domain-specific exceptions where they already exist
  (`ApiClientError`, `ResponseValidationError`); otherwise raise
  `AssertionError` with context.
- **No silent excepts.** If you must catch broadly (e.g. teardown),
  log the exception.
- **Docstrings**: short module/class/method docstrings in the style of
  existing files (`api/base_client.py`, `utils/response_validator.py`).
- **Public API**: expose types via `__all__` in new model/util modules.

---

## 10. Do / Don't Cheatsheet

Do:
- Reuse `BasePage`, `BaseApiClient`, `ResponseValidator`, `ConfigLoader`,
  `DriverManager`, and `*DataLoader`.
- Put new tests under `step_definitions/` (UI BDD) or `tests_api/` (API).
- Add Gherkin tags that match `pytest.ini > markers`.
- Keep services thin and tests assertion-rich.

Don't:
- Instantiate `webdriver.*` outside `BrowserFactory`.
- Call `requests` directly in tests — go through a `Service`.
- Hardcode URLs, credentials, or timeouts — read from config / `.env`.
- Add tests outside the two `testpaths` declared in `pytest.ini`.
- Commit anything under `reports/`, `logs/`, `.venv/`, `venv/`,
  `.pytest_cache/`, or `__pycache__/`.

---

## 11. Security Awareness (Global)

All code suggestions MUST follow security standards defined in
@security-standards.instructions.md. Key rules that apply everywhere:

### Always
- Use `yaml.safe_load()` for any YAML parsing
- Use `ConfigLoader` / `.env` for all credentials and URLs
- Use `BaseApiClient`'s session (never raw `requests` calls in tests)
- Use `DriverManager` / `BrowserFactory` (never raw `webdriver.*`)
- Mask passwords and tokens in all log messages
- Validate responses before trusting their content
- Close/quit all resources in teardown paths

### Never
- Hardcode secrets in Python, YAML, JSON, or .feature files
- Set `verify=False` on any HTTP request
- Use `yaml.load()` with unsafe loaders
- Log or attach raw `Authorization` / `X-API-Key` headers
- Use `execute_script()` with string-interpolated user input
- Add `--disable-web-security` or `--ignore-certificate-errors` to browser flags
- Commit `.env`, `reports/`, `logs/`, or `screenshots/`

### When Generating Code
- If a function handles passwords/tokens → mask in log statements
- If constructing URLs → use `urljoin` / `quote`, not f-strings with raw input
- If adding a new dependency → pin the version
- If creating fixtures → ensure teardown runs even on failure (use `yield`)
- If attaching to Allure → mask sensitive headers/bodies first

When a security concern is identified, prefix with:
⚠️ **SECURITY [SEVERITY]**: description


## 12. References

- Root fixtures & failure hook: [conftest.py](../conftest.py)
- Pytest config: [pytest.ini](../pytest.ini)
- HTTP foundation: [api/base_client.py](../api/base_client.py)
- Example service / model / test:
  [api/endpoints/product_service.py](../api/endpoints/product_service.py),
  [api/models/product_models.py](../api/models/product_models.py),
  [tests_api/test_product.py](../tests_api/test_product.py)
- Example UI flow: [features/login.feature](../features/login.feature) +
  [step_definitions/test_login.py](../step_definitions/test_login.py) +
  [pages/home_page.py](../pages/home_page.py) /
  [pages/login_page.py](../pages/login_page.py)