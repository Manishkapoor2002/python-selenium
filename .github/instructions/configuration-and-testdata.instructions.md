---
description: "Rules for configuration management, environments, secrets, and test data handling. Use when editing config, .env handling, or loading data files."
applyTo:
  - "config/**"
  - "data/**"
  - "core/**"
  - "tests_api/**"
  - "step_definitions/**"
---

# Configuration & Test Data

## Configuration

### Good Practices
- Use:
  - `ConfigLoader.load_config()`
  - `ConfigLoader.get_api_config()`
  ([core/config_loader.py](../../core/config_loader.py))
- Use `.env` overrides:
  - UI: `BROWSER`, `BASE_URL`
  - API: `API_ENV`, `API_BASE_URL`
  - Auth: `API_BEARER_TOKEN`, `API_USERNAME`, `API_PASSWORD`, `API_KEY`
- Add new environments under `api.environments.<name>` in
  [config/config.yaml](../../config/config.yaml).
- Reference auth secrets via the `*_env` fields in
  `config.yaml > api.auth`.

### Bad Practices
- Never hardcode URLs, credentials, browser names, or timeouts.
- Never parse `config.yaml` manually with `yaml.safe_load` — go through
  `ConfigLoader`.
- Never commit real secrets to `.env`, `config.yaml`, or test data.
- Do not bypass `ConfigLoader` caching by re-reading the file.

---

## Test Data

### Good Practices
- UI / general data → `TestDataLoader.load_json("file.json")`
  ([utils/test_data_loader.py](../../utils/test_data_loader.py)).
- API data → `ApiDataLoader.load("file.json|yaml")`
  ([utils/api_data_loader.py](../../utils/api_data_loader.py)) — already
  deep-copies, safe to mutate.
- Store all test data files under `data/`.

### Bad Practices
- No inline `open(...)`, `json.load(...)`, or `yaml.safe_load(...)`
  inside tests or page objects.
- Do not store test data inside `pages/`, `api/`, or `step_definitions/`.
- Do not reach into `ApiDataLoader._cache` to share state across tests.
