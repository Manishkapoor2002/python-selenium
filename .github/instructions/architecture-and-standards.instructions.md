---
description: "Repository structure, coding standards, and repo hygiene for the python-selenium TAF. Use when scaffolding files, reviewing layout, or enforcing general Python conventions."
applyTo:
  - "**/*"
---

# Architecture & Coding Standards

## Project Structure

### Good Practices
- Put UI BDD tests under `step_definitions/`.
- Put API tests under `tests_api/`.
- Keep:
  - Features → `features/`
  - Pages → `pages/`
  - API services → `api/endpoints/`
  - Models → `api/models/`
  - Schemas → `api/schemas/`
  - Shared helpers → `utils/`
  - Browser/driver/config core → `core/`

### Bad Practices
- Do not place `test_*.py` inside `pages/`, `api/`, `core/`, or `utils/`
  (only `step_definitions/` and `tests_api/` are in `pytest.ini > testpaths`).
- Do not create new top-level folders to "organize" things.
- Do not duplicate existing utilities/helpers from `utils/` or `core/`.

---

## Coding Standards

### Good Practices
- Follow PEP 8; 4-space indentation.
- Add type hints to all new public functions/methods.
- Use `from __future__ import annotations` in new modules
  (matches the existing API layer style).
- Organize imports: stdlib → third-party → local, separated by blank lines.
- Add concise module/class/method docstrings (see
  [api/base_client.py](../../api/base_client.py),
  [utils/response_validator.py](../../utils/response_validator.py)).
- Export public APIs via `__all__` in new model/util modules.
- Raise domain-specific exceptions where they exist
  (`ApiClientError`, `ResponseValidationError`); otherwise use
  `AssertionError` with a descriptive message.

### Bad Practices
- No wildcard imports (`from x import *`).
- No tabs or mixed indentation.
- No undocumented modules or untyped public APIs.
- No excessively long, unformatted lines.
- No top-level imports between two pages that import each other —
  use **deferred imports** to break cycles.

---

## Repository Hygiene

### Good Practices
- Keep generated files only in `reports/`, `logs/`, and `__pycache__/`
  (already gitignored).
- Run targeted test slices instead of the whole suite when iterating:
  ```powershell
  pytest tests_api -m api
  pytest step_definitions
  pytest -m smoke -n auto
  ```
- Use Allure CLI for reports: `allure serve reports/allure-results`.

### Bad Practices
- Never commit `.venv/`, `venv/`, `.pytest_cache/`, `reports/`, `logs/`,
  or `__pycache__/`.
- Do not override `--alluredir` / `--clean-alluredir` from `pytest.ini`
  without a deliberate reason.
- Do not commit local-only config tweaks
  (e.g. `headless: True`, personal `BASE_URL`).
