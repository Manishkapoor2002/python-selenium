---
description: "Rules for Selenium UI automation, pytest-bdd, page objects, and browser/driver lifecycle in this TAF. Use when adding pages, features, steps, or touching the driver layer."
applyTo:
  - "pages/**"
  - "step_definitions/**"
  - "features/**"
  - "core/**"
  - "conftest.py"
---

# UI Automation Rules

## Page Objects

### Good Practices
- All pages must inherit from [`BasePage`](../../pages/base_page.py).
- Accept `driver` in `__init__` and call `super().__init__(driver)`.
- Use BasePage helpers: `click`, `enter_text`, `get_text`, `is_displayed`.
- Use `self.wait` (10s `WebDriverWait`) for explicit waits.
- Define locators as **method-local tuples**, e.g.
  `login_button = (By.XPATH, "//button[@data-qa='login-button']")`.
- Locator preference order: `data-qa` → CSS selector → XPath.
- Return the next Page Object from navigation methods (use deferred
  imports to avoid circular references — see
  [`HomePage.navigate_to_login_page`](../../pages/home_page.py)).
- Log meaningful actions with `self.logger.info(...)`.

### Bad Practices
- No raw `driver.find_element(...)` calls — use BasePage helpers or
  add a new helper to `BasePage`.
- No `time.sleep(...)` — always use explicit waits.
- No brittle absolute XPaths or text-only locators.
- Never put assertions inside page objects — assertions belong in
  steps/tests.
- No class-level locator dicts shared across pages.

---

## BDD Steps & Features

### Good Practices
- One `.feature` per user-facing capability.
- Use only declared markers from `pytest.ini`: `@smoke`, `@regression`,
  `@ui`, `@api`, `@crud`.
- Call `scenarios("../features/<file>.feature")` once per step module.
- Share state via the `context_state` fixture
  (`{"driver": ..., "wait": WebDriverWait(driver, 10)}`).
- Store page objects on `context_state` (e.g. `context_state["homepage"] = ...`).
- Pull credentials/data from the `users_data` fixture
  (loaded from `data/user_credentials.json`).
- Use `pytest_check.is_true(...)` for soft assertions where appropriate.

### Bad Practices
- No module-level globals or singletons to pass state between steps.
- No hardcoded credentials, emails, or test data inside step functions.
- No new tags that aren't declared under `markers` in `pytest.ini`.
- No re-instantiating page objects in every step instead of reusing
  the one stored on `context_state`.

---

## Driver Lifecycle

### Good Practices
- Use `DriverManager().get_driver(...)`
  ([core/driver_manager.py](../../core/driver_manager.py)) and release with
  `.quit_driver()`.
- Add new browsers by extending
  [`BrowserFactory`](../../core/browser_factory.py).
- Rely on the root `driver` fixture in [conftest.py](../../conftest.py) —
  it handles navigation to `base_url`, window maximization, and
  `_driver_store` registration for the screenshot hook.

### Bad Practices
- Never instantiate `webdriver.Chrome()`/`.Firefox()`/`.Edge()` directly
  outside `BrowserFactory`.
- No arbitrary new `WebDriverWait` instances with random timeouts —
  reuse `self.wait` or `context_state["wait"]`.
- Never quit the driver manually inside a test (breaks fixture
  teardown and the failure screenshot hook).
