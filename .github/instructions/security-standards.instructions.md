# Security Standards for python-selenium Framework

These standards apply to ALL code in this test automation framework.
Test infrastructure handles real credentials, connects to real services,
and produces artifacts that may be shared — treat it as production code.

---

## 1. Secrets Management

### Rules
- **NEVER** hardcode passwords, tokens, API keys, or connection strings
  in Python, YAML, JSON, or .feature files
- All secrets MUST flow through `.env` → `ConfigLoader.get_api_config()`
- `config.yaml` auth section MUST use `*_env` field pattern:
  ```yaml
  auth:
    type: bearer
    bearer_token_env: "API_BEARER_TOKEN"  # ✅ env var name
    bearer_token: "abc123"                # ❌ NEVER this
  ```
- Test data files (`data/*.json`) MUST use placeholder credentials only
- `.env` MUST be listed in `.gitignore` — never commit it

---

## 2. TLS / SSL

### Rules
- `verify=True` MUST be the default for all HTTP requests
- **NEVER** set `verify=False` in production or test code
- **NEVER** add `--ignore-certificate-errors` to browser flags
- If a test environment uses self-signed certs, use a custom CA bundle
  via the `REQUESTS_CA_BUNDLE` env var — do not disable verification

---

## 3. YAML Safety

### Rules
- **ALWAYS** use `yaml.safe_load()` for any YAML parsing
- **NEVER** use `yaml.load()` with `Loader=yaml.FullLoader` or
  `Loader=yaml.UnsafeLoader`
- All YAML parsing MUST go through `ConfigLoader` — do not parse
  `config.yaml` manually in tests or utilities

---

## 4. Browser Security Flags

### Rules
- **NEVER** add these Chrome/Edge flags:
  - `--disable-web-security` (disables same-origin policy)
  - `--allow-running-insecure-content` (enables mixed content)
  - `--ignore-certificate-errors` (MITM vulnerable)
- `--no-sandbox` is acceptable **only** in Docker/CI environments
- `--disable-extensions` is recommended (reduces attack surface)
- All browser configuration MUST go through `BrowserFactory` —
  never instantiate `webdriver.*` directly

---

## 5. Selenium Input Security

### Rules
- Use `send_keys()` for all user input — never use
  `execute_script()` to set input values (bypasses DOM events)
- All `execute_script()` calls MUST use parameterised `arguments[N]`:
  ```python
  # ✅ Safe — parameterised
  driver.execute_script("arguments[0].scrollIntoView(true);", element)

  # ❌ Unsafe — string interpolation
  driver.execute_script(f"document.querySelector('{user_input}').click()")
  ```
- XPath locators MUST NOT interpolate user-supplied data:
  ```python
  # ❌ XPath injection risk
  driver.find_element(By.XPATH, f"//input[@name='{user_input}']")

  # ✅ Safe — static locator
  driver.find_element(By.CSS_SELECTOR, "[data-qa='login-input']")
  ```

---

## 6. Logging & Reporting Security

### Rules
- **NEVER** log raw values of `Authorization`, `X-API-Key`, `Cookie`,
  or `Set-Cookie` headers
- `BaseApiClient._log_request()` already masks sensitive headers —
  preserve this behaviour and extend it for new header types
- Allure attachments MUST mask sensitive headers before attachment
- Passwords MUST be masked in Page Object log statements:
  ```python
  # ✅ Masked
  self.logger.info("Entering password: %s", "***")

  # ❌ Exposed
  self.logger.info("Entering password: %s", password)
  ```
- Screenshot filenames MUST NOT contain usernames, emails, or tokens
- Error messages in assertions MUST NOT include credential values

---

## 7. Session & Driver Lifecycle

### Rules
- `session.close()` MUST be called in all teardown paths
  (use `yield` fixtures to guarantee cleanup on failure)
- `DriverManager.quit_driver()` MUST be called in fixture teardown —
  never quit the driver manually inside a test
- Never leave zombie browser processes — register cleanup with
  appropriate fixture scopes
- All fixtures that handle credentials MUST clean up auth state
  in teardown

---

## 8. Dependencies

### Rules
- All packages in `requirements.txt` MUST be pinned to specific
  versions (e.g. `selenium==4.27.1`, not `selenium`)
- Regularly audit dependencies for known CVEs
- Do not add unnecessary packages — each dependency increases
  attack surface
- Verify new packages come from trusted sources (PyPI)

---

## 9. Retry Policy Security

### Rules
- `status_forcelist` MUST exclude `401` and `403` — retrying auth
  failures can trigger account lockout
- Non-idempotent methods (`POST`) should be carefully considered
  for retry to avoid duplicate side effects
- Maximum backoff MUST be bounded to prevent hanging test processes

---

## 10. When Generating Code

- If a function handles passwords/tokens → mask in log statements
- If constructing URLs → use `urljoin` / `quote`, not f-strings
  with raw input
- If adding a new dependency → pin the version
- If creating fixtures → ensure teardown runs even on failure
  (use `yield`)
- If attaching to Allure → mask sensitive headers/bodies first

When a security concern is identified, prefix with:
⚠️ **SECURITY [SEVERITY]**: description
