# Selenium & UI Layer Security Review

Deep security review of the browser automation layer.

## Context
- `core/browser_factory.py` → Creates Chrome/Firefox/Edge with options
- `core/driver_manager.py` → Thread-safe singleton, per-thread WebDriver
- `pages/base_page.py` → Base class with wait, click, enter_text, etc.
- `pages/*_page.py` → Page Objects inheriting BasePage
- `features/*.feature` → Gherkin scenarios
- `step_definitions/test_*.py` → BDD step implementations
- `conftest.py` → driver fixture + screenshot-on-failure hook
- `utils/screenshot_manager.py` → Failure screenshot capture

## Review Points

### Browser Configuration (`core/browser_factory.py`)
1. **Chrome Flags Audit**
   - ❌ `--disable-web-security` (disables same-origin policy)
   - ❌ `--allow-running-insecure-content` (mixed content)
   - ❌ `--ignore-certificate-errors` (MITM vulnerable)
   - ⚠️ `--no-sandbox` (acceptable in Docker/CI only)
   - ✅ `--disable-extensions` (reduces attack surface)
   - Are flags different for CI vs local? Should they be?

2. **Download/File Handling**
   - Are download directories set to temp paths?
   - Are auto-downloads disabled to prevent drive-by downloads?

### Driver Lifecycle (`core/driver_manager.py`)
3. **Thread Safety**
   - Is the threading lock properly used for get/quit?
   - Can a race condition leave zombie browser processes?

4. **Cleanup Guarantees**
   - Does `quit_driver()` handle `WebDriverException` during quit?
   - Is cleanup registered with `atexit` as a safety net?
   - Does the conftest fixture use `yield` + unconditional teardown?

### Page Objects (`pages/`)
5. **Sensitive Input Handling**
   - Do `enter_password()` / similar methods mask values in logs?
   - Is `send_keys()` used for sensitive fields (not `execute_script`)?

6. **JavaScript Execution**
   - Are all `execute_script()` calls using parameterized `arguments[N]`?
   - Is there any string interpolation of test data into JS?

7. **Locator Security**
   - Are locators using stable attributes (`data-qa`, `id`)?
   - Could XPath with user data enable injection?
   ```python
   # ❌ XPath injection
   driver.find_element(By.XPATH, f"//input[@name='{user_input}']")
   # ✅ Safe
   driver.find_element(By.CSS_SELECTOR, "[data-qa='login-input']")
   ```

### Screenshots & Reporting
8. **Screenshot Security**
   - Do screenshot filenames contain sensitive data (usernames, tokens)?
   - Are screenshots stored only in `reports/screenshots/` (gitignored)?
   - Does `ScreenshotManager` sanitise names before writing?

9. **Allure Attachments**
   - Are failure screenshots attached without sensitive metadata?
   - Does the conftest hook avoid attaching page source that contains tokens?

## Output
Structured findings table + detailed fixes following the format in
@security-reviewer.agent.md
