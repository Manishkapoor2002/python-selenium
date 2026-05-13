# `.github/` Directory — Complete Usage Guide

> **Audience:** Anyone working in this repo — SDETs, developers, reviewers, and CI maintainers.
> This document explains every file inside `.github/`, when and why to use it, and how the pieces connect.

---

## Table of Contents

1. [How the System Fits Together](#1-how-the-system-fits-together)
2. [Instructions Files](#2-instructions-files)
   - 2.1 [copilot-instructions.md (Root)](#21-copilot-instructionsmd-root)
   - 2.2 [ui-automation.instructions.md](#22-ui-automationinstructionsmd)
   - 2.3 [api-automation.instructions.md](#23-api-automationinstructionsmd)
   - 2.4 [architecture-and-standards.instructions.md](#24-architecture-and-standardsinstructionsmd)
   - 2.5 [configuration-and-testdata.instructions.md](#25-configuration-and-testdatainstructionsmd)
   - 2.6 [security-standards.instructions.md](#26-security-standardsinstructionsmd)
3. [Agents](#3-agents)
   - 3.1 [taf-maintainer](#31-taf-maintainer)
   - 3.2 [security-reviewer](#32-security-reviewer)
4. [Prompts](#4-prompts)
   - 4.1 [heal-failing-test](#41-heal-failing-test)
   - 4.2 [scan-impact](#42-scan-impact)
   - 4.3 [update-page-object](#43-update-page-object)
   - 4.4 [review-security](#44-review-security)
   - 4.5 [review-api-security](#45-review-api-security)
   - 4.6 [review-selenium-security](#46-review-selenium-security)
   - 4.7 [scan-secrets](#47-scan-secrets)
   - 4.8 [fix-vulnerability](#48-fix-vulnerability)
5. [Skills](#5-skills)
   - 5.1 [api-test-generator](#51-api-test-generator)
   - 5.2 [security-scanner](#52-security-scanner)
6. [Quick Reference Matrix](#6-quick-reference-matrix)

---

## 1. How the System Fits Together

The `.github/` directory forms a **layered Copilot configuration system**:

```
┌─────────────────────────────────────────────────────┐
│  copilot-instructions.md   (ALWAYS loaded, global)  │  ← Foundation
├─────────────────────────────────────────────────────┤
│  instructions/*.instructions.md  (auto-scoped)      │  ← Rules per domain
├──────────────────────┬──────────────────────────────┤
│  agents/*.agent.md   │  prompts/*.prompt.md         │  ← Actors & Tasks
├──────────────────────┴──────────────────────────────┤
│  skills/*/SKILL.md                                  │  ← Reusable expertise
└─────────────────────────────────────────────────────┘
```

### Layer Definitions

| Layer | Loaded When | By Whom | Purpose |
|-------|-------------|---------|---------|
| **Instructions** | Automatically, based on `applyTo` file glob | Copilot (every session) | Passive rules — "always follow these" |
| **Agents** | User invokes `@agent-name` | User, or CI trigger | Active actors — autonomous workflows |
| **Prompts** | User runs `/prompt-name` | User (on demand) | Task templates — structured one-shot tasks |
| **Skills** | Agent or Copilot detects a matching task | Copilot Chat / Agents | Domain expertise — "how to do X" |

### Directory Structure

```
.github/
├── copilot-instructions.md                          # Master rulebook (always loaded)
├── README.md                                        # This file
├── agents/
│   ├── taf-maintainer.agent.md                      # Autonomous SDET agent
│   └── security-reviewer.agent.md                   # Security audit agent
├── instructions/
│   ├── ui-automation.instructions.md                # Page Objects, BDD, driver rules
│   ├── api-automation.instructions.md               # Services, models, schemas, tests
│   ├── architecture-and-standards.instructions.md   # Structure, PEP 8, imports
│   ├── configuration-and-testdata.instructions.md   # Config, env vars, data loading
│   └── security-standards.instructions.md           # 10-domain security rulebook
├── prompts/
│   ├── heal-failing-test.prompt.md                  # Diagnose + auto-fix failing test
│   ├── scan-impact.prompt.md                        # Impact analysis for code changes
│   ├── update-page-object.prompt.md                 # Add elements/methods to a page
│   ├── review-security.prompt.md                    # Full security review (umbrella)
│   ├── review-api-security.prompt.md                # Deep-dive API security review
│   ├── review-selenium-security.prompt.md           # Deep-dive Selenium security review
│   ├── scan-secrets.prompt.md                       # Scan for exposed credentials
│   └── fix-vulnerability.prompt.md                  # Generate a fix for a vulnerability
└── skills/
    ├── api-test-generator/
    │   └── SKILL.md                                 # Generate Model + Service + Test
    └── security-scanner/
        └── SKILL.md                                 # Security analysis capabilities
```

---

## 2. Instructions Files

Instructions are **passive guardrails**. You never "run" them — Copilot loads
them automatically whenever you edit files matching their `applyTo` glob. They
shape every suggestion, completion, and chat response.

---

### 2.1 `copilot-instructions.md` (Root)

| | |
|---|---|
| **File** | `.github/copilot-instructions.md` |
| **Activates** | Always — every chat, every inline completion, every agent run |
| **Scope** | Global (all files) |

**What it is:** The master rulebook for the entire repository. Loaded on
**every** Copilot interaction regardless of which file you're editing.

**Why it exists:** Provides a single source of truth so Copilot never generates
code that violates the project's architecture, naming, or security conventions.

**What it covers (12 sections):**

| Section | Governs |
|---------|---------|
| §1 Tech Stack | Which packages to use and assume |
| §2 Project Structure | Where files belong |
| §3 Configuration | How to read config, env vars |
| §4 UI Conventions | Page Objects, BDD, driver lifecycle |
| §5 API Conventions | Client → Service → Model → Schema → Test flow |
| §6 Data Loading | `TestDataLoader` vs `ApiDataLoader` |
| §7 Logging & Reporting | Logger setup, masking, Allure |
| §8 Running Tests | pytest commands |
| §9 Coding Standards | PEP 8, type hints, imports |
| §10 Do/Don't Cheatsheet | Quick reference rules |
| §11 Security Awareness | Summary of security-standards |
| §12 References | Links to key source files |

**Practical example — when this helps:**

You ask Copilot: *"Create a new fixture for the user API"*

Copilot reads §5 and knows to create a module-scoped fixture with
`yield service; service.close()`, place it in `tests_api/`, and use
`ResponseValidator` — without you reminding it.

---

### 2.2 `ui-automation.instructions.md`

| | |
|---|---|
| **File** | `.github/instructions/ui-automation.instructions.md` |
| **Activates** | When you edit files matching `pages/**`, `step_definitions/**`, `features/**`, `core/**`, `conftest.py` |
| **Scope** | Selenium / BDD layer |

**What it is:** Focused rules for the Selenium/BDD layer only.

**Why it exists:** Prevents common Selenium anti-patterns. When you're writing
a Page Object, you don't need API rules cluttering context — this file provides
laser-focused UI guidance.

**Use this when you are:**

- Creating or modifying a Page Object in `pages/`
- Writing BDD step definitions in `step_definitions/`
- Adding a new `.feature` file
- Touching `conftest.py` driver fixtures or `core/browser_factory.py`

**Key rules it enforces:**

| Rule | Why |
|------|-----|
| Inherit `BasePage`, use its helpers | Consistency; no raw `driver.find_element` |
| Locators as method-local `(By.X, "sel")` tuples | Encapsulation; no shared mutable state |
| Prefer `data-qa` attributes | Stability; decoupled from CSS/text changes |
| Return next Page Object from nav methods | Fluent API; type-safe page transitions |
| No `time.sleep()` | Explicit waits via `self.wait` are reliable |
| Share state via `context_state` fixture | Thread-safe; no module-level globals |
| No assertions in Page Objects | Separation of concerns |

**Practical example:**

You type in `pages/checkout_page.py`:

```python
class CheckoutPage(BasePage):
    def enter_card_number(self, card):
```

Copilot auto-completes with
`self.enter_text((By.CSS_SELECTOR, "[data-qa='card-number']"), card)`
and logs with masking — because this instruction file told it to.

---

### 2.3 `api-automation.instructions.md`

| | |
|---|---|
| **File** | `.github/instructions/api-automation.instructions.md` |
| **Activates** | When you edit files matching `api/**`, `tests_api/**` |
| **Scope** | API test layer |

**What it is:** Rules for the API test layer (services, models, schemas, tests).

**Why it exists:** Enforces the strict
`Client → Service → Model → Schema → Test` architecture. Without it, Copilot
might suggest calling `requests.get()` directly in a test.

**Use this when you are:**

- Adding a new endpoint service in `api/endpoints/`
- Creating dataclass models in `api/models/`
- Writing JSON schemas in `api/schemas/`
- Writing API test cases in `tests_api/`

**Key rules it enforces:**

| Rule | Why |
|------|-----|
| Services inherit `BaseApiClient` | Centralised auth, retries, logging |
| One service per resource | Clean separation |
| Services return raw `Response` | Keep services thin, assertions in tests |
| Models use `@dataclass` + `from_dict()` | Type safety, defensive deserialization |
| Optional fields default to `None` | Tolerates API schema evolution |
| Use `ResponseValidator` for all assertions | Consistent error messages, Allure integration |
| Module-scoped service fixtures with `yield` | Connection pooling + guaranteed cleanup |
| Mark tests with `@pytest.mark.api` | Enables selective test runs |

**Endpoint creation order (mandatory):**

```
1. config/config.yaml  (if new path/auth needed)
2. api/schemas/<name>.json
3. api/models/<name>_models.py
4. api/endpoints/<name>_service.py
5. tests_api/test_<name>.py
```

**Practical example:**

You ask: *"Add a test for the DELETE user endpoint"*

Copilot follows the endpoint creation order: suggests schema first, then model,
then service method, then test — and uses
`ResponseValidator.assert_status_code()` instead of bare `assert`.

---

### 2.4 `architecture-and-standards.instructions.md`

| | |
|---|---|
| **File** | `.github/instructions/architecture-and-standards.instructions.md` |
| **Activates** | On **all files** (`applyTo: "**/*"`) |
| **Scope** | Global — coding style and project structure |

**What it is:** General coding standards and project structure rules.

**Why it exists:** Ensures every Python file follows PEP 8, uses type hints,
organises imports correctly, and lands in the right directory.

**Use this when you are:**

- Creating any new file anywhere in the project
- Reviewing code for style compliance
- Deciding where a new module should live

**Key rules it enforces:**

| Rule | Why |
|------|-----|
| Tests only in `step_definitions/` or `tests_api/` | `pytest.ini` testpaths — tests elsewhere won't run |
| `from __future__ import annotations` in new modules | Consistent with existing API layer |
| stdlib → third-party → local import order | PEP 8; readability |
| Deferred imports for Page Object cycles | Prevents `ImportError` from circular deps |
| Don't commit `reports/`, `logs/`, etc. | Repo hygiene |
| Don't create new top-level folders | Flat, predictable structure |

---

### 2.5 `configuration-and-testdata.instructions.md`

| | |
|---|---|
| **File** | `.github/instructions/configuration-and-testdata.instructions.md` |
| **Activates** | When you edit files matching `config/**`, `data/**`, `core/**`, `tests_api/**`, `step_definitions/**` |
| **Scope** | Configuration and test data |

**What it is:** Rules for config management and test data loading.

**Why it exists:** Prevents hardcoded URLs/credentials and ensures all config
flows through `ConfigLoader` and all data through the `*DataLoader` utilities.

**Use this when you are:**

- Adding a new environment to `config.yaml`
- Creating test data files in `data/`
- Adding `.env` overrides for a new secret
- Using config values in fixtures or tests

**Key rules it enforces:**

| Rule | Why |
|------|-----|
| Use `ConfigLoader.load_config()` / `.get_api_config()` | Caching, env override resolution |
| Never parse YAML manually | ConfigLoader handles `yaml.safe_load` + caching |
| UI data → `TestDataLoader`, API data → `ApiDataLoader` | Different caching/copy semantics |
| All data files under `data/` | Single location; not scattered in test dirs |
| Never commit real secrets | Security; use `.env` + `*_env` references |

**Practical example:**

You add a new API endpoint that needs a special header. Instead of hardcoding
it, Copilot suggests adding a `config.yaml` entry with an `*_env` reference and
reading it via `ConfigLoader.get_api_config()`.

---

### 2.6 `security-standards.instructions.md`

| | |
|---|---|
| **File** | `.github/instructions/security-standards.instructions.md` |
| **Activates** | Referenced by `copilot-instructions.md` §11, both agents, and all security prompts |
| **Scope** | Global — the authoritative security rulebook |

**What it is:** The single source of truth for security across the entire
framework — 10 sections covering every attack surface in the TAF.

**Why it exists:** Test frameworks handle real credentials, connect to real
services, and produce shared artifacts. A leaked token in an Allure report is a
production incident.

**Use this when you are:**

- Reviewing any code for security
- Adding authentication logic
- Logging or attaching HTTP details to Allure
- Configuring browser options
- Adding dependencies to `requirements.txt`

**The 10 domains it covers:**

| # | Domain | Critical Rule |
|---|--------|---------------|
| 1 | Secrets Management | Never hardcode; use `*_env` pattern |
| 2 | TLS/SSL | Never `verify=False` |
| 3 | YAML Safety | Always `yaml.safe_load()` |
| 4 | Browser Flags | Never `--disable-web-security` |
| 5 | Selenium Input | Parameterised `execute_script` only |
| 6 | Logging & Reporting | Mask `Authorization`, passwords in logs |
| 7 | Session & Driver Lifecycle | `yield` fixtures with unconditional cleanup |
| 8 | Dependencies | Pin versions; audit CVEs |
| 9 | Retry Policy | Exclude 401/403 from `status_forcelist` |
| 10 | Code Generation | Mask, `urljoin`, pin, `yield`, mask Allure |

---

## 3. Agents

Agents are **autonomous actors**. You invoke them with `@agent-name` in Copilot
Chat and they execute multi-step workflows — reading files, running commands,
and making changes.

---

### 3.1 `taf-maintainer`

| | |
|---|---|
| **File** | `.github/agents/taf-maintainer.agent.md` |
| **Invocation** | `@taf-maintainer <task description>` in Copilot Chat |
| **Role** | Autonomous SDET — diagnoses, fixes, and maintains the TAF |

**When to use:**

| Scenario | What to say | What the agent does |
|----------|-------------|---------------------|
| **A test is failing** | `@taf-maintainer The test step_definitions/test_login.py is failing with NoSuchElementException` | Runs the `heal-failing-test` playbook: executes the test, reads logs, classifies the failure, proposes a locator fix, applies it, re-runs (up to 3 iterations) |
| **A broad code change landed** | `@taf-maintainer The login page was redesigned, assess impact` | Runs the `scan-impact` playbook: searches all `pages/`, `step_definitions/`, `features/`, and `data/` for affected files, produces a risk-rated checklist |
| **A page object needs updating** | `@taf-maintainer Update pages/checkout_page.py to add a promo code field` | Runs the `update-page-object` playbook: reads the file, adds locators/methods following conventions, flags any affected step definitions |

**Why it exists:** Automates the most repetitive SDET maintenance tasks — test
triage, impact analysis, and page object updates — so you don't manually trace
dependencies.

**How it works internally (5 phases):**

```
Phase 1: Triage      → Classifies your task into one of 3 playbooks
Phase 2: Load Context → Reads the playbook + relevant instruction files
Phase 3: Plan         → Summarises proposed changes as a diff
Phase 4: Execute      → Applies changes, runs pytest, self-heals up to 3 times
Phase 5: Report       → Outputs: playbook used, changes made, test results, escalations
```

**Constraints to know:**

- Will **never** modify `core/` without your approval
- Escalates to you if: self-healing fails after 3 tries, >10 files affected, or
  schema breaks backward compatibility
- Always includes `--alluredir=reports/allure-results` in test commands
- Preserves all Allure decorators

---

### 3.2 `security-reviewer`

| | |
|---|---|
| **File** | `.github/agents/security-reviewer.agent.md` |
| **Invocation** | `@security-reviewer <scope or task>` in Copilot Chat |
| **Role** | Senior AppSec engineer — audits code and generates fixes |

**When to use:**

| Scenario | What to say | What the agent does |
|----------|-------------|---------------------|
| **Full security audit** | `@security-reviewer Run a complete security audit of the project` | Scans all layers: secrets, API client, Selenium config, config loading, dependencies, logging |
| **Review a specific file** | `@security-reviewer Review api/base_client.py for security issues` | Deep-dive: checks TLS config, header masking, retry policy, session lifecycle |
| **Check a PR** | `@security-reviewer Security check these changed files: pages/login_page.py, step_definitions/test_login.py` | Pre-commit style: looks for new hardcoded secrets, `verify=False`, unsafe `execute_script`, leaked passwords in logs |
| **Fix a finding** | `@security-reviewer Fix the hardcoded timeout in tests_api/test_product.py` | Generates root cause + fix + verification steps |

**Why it exists:** Security review of test infrastructure is often skipped. This
agent ensures every change is checked against the 10-domain security standard
automatically.

**How it works internally (5 phases):**

```
Phase 1: Scope    → Determines: full audit, targeted scan, or fix request
Phase 2: Context  → Reads security-standards.instructions.md + relevant files
Phase 3: Analyse  → Applies checklist from the appropriate prompt
Phase 4: Report   → Findings table: Severity, CWE, Location, Finding, Fix
Phase 5: Summary  → Overall risk level + prioritised remediation roadmap
```

**Key constraint:** Read-only by default — reports findings but doesn't modify
code unless you explicitly ask it to fix something.

**Capabilities:**

| Capability | Description |
|------------|-------------|
| Full Security Audit | Scan all layers end-to-end |
| Secrets Scan | Detect hardcoded credentials in `.py`, `.yaml`, `.json`, etc. |
| API Layer Review | TLS, auth, masking, session lifecycle, retry policy |
| Selenium Layer Review | Browser flags, driver lifecycle, JS injection, input masking |
| Config Review | YAML safety, env var patterns, secret references |
| Dependency Audit | Version pinning, known CVEs |
| Fix Generation | Framework-consistent remediations |

---

## 4. Prompts

Prompts are **structured task templates**. You invoke them with `/prompt-name`
in Copilot Chat. They're one-shot tasks with defined inputs and outputs —
unlike agents, they don't loop or self-heal.

---

### 4.1 `heal-failing-test`

| | |
|---|---|
| **File** | `.github/prompts/heal-failing-test.prompt.md` |
| **Invocation** | `/heal-failing-test` |
| **Input** | `${input:test_path}` — e.g. `step_definitions/test_login.py` |

**When to use:** A specific test is failing and you want automated diagnosis +
fix.

**What it does (step by step):**

1. Runs `pytest <test_path> --alluredir=reports/allure-results -v`
2. Reads `logs/pytest-logs.txt` and terminal output
3. Classifies the failure:
   - `NoSuchElementException` → locator fix in `pages/`
   - `ImportError` → dependency fix in `requirements.txt`
   - `AssertionError` → expected-vs-actual analysis
   - `TimeoutException` → wait strategy review
4. Proposes minimal diff
5. Applies fix + re-runs (max 3 iterations)
6. Reports: root cause, fix applied, final status

**Why use this instead of debugging manually:** It automates the repetitive
cycle of run → read logs → guess → fix → re-run. Especially useful for locator
drift after UI changes.

**Relationship to `@taf-maintainer` agent:** The agent uses this prompt as its
"failing test" playbook. You can also use it standalone.

---

### 4.2 `scan-impact`

| | |
|---|---|
| **File** | `.github/prompts/scan-impact.prompt.md` |
| **Invocation** | `/scan-impact` |
| **Input** | `${input:change}` — e.g. *"Login page HTML was restructured, all data-qa attributes renamed"* |

**When to use:** A significant code change has been made (or is planned) and you
need to understand which tests, pages, features, and data files are affected.

**What it does:**

1. Searches `pages/`, `step_definitions/`, `features/`, `api/endpoints/`, and
   `data/` for affected files
2. Analyses cross-layer dependencies (e.g. login change →
   `data/user_credentials.json`)
3. Produces an impact report: files requiring changes, risk level, suggested
   modification order
4. Outputs a checklist — does **not** modify files

**Why use this:** Before making a broad change, you get a clear picture of the
blast radius. Prevents the *"I changed one page and broke 5 tests"* surprise.

---

### 4.3 `update-page-object`

| | |
|---|---|
| **File** | `.github/prompts/update-page-object.prompt.md` |
| **Invocation** | `/update-page-object` |
| **Inputs** | `${input:page_file}` — e.g. `pages/checkout_page.py`; `${input:description}` — e.g. *"Add promo code input field and apply button"* |

**When to use:** You need to add new elements or methods to an existing Page
Object.

**What it does:**

1. Reads the target page file
2. Verifies it inherits from `BasePage`
3. Adds locators as method-local tuples (per convention)
4. Adds methods following fluent pattern (return `self` or next page)
5. Wraps actions in `@allure.step`
6. Checks `step_definitions/` for steps using this page — flags if they need
   updates
7. Outputs the diff

**Why use this:** Ensures new page elements follow all conventions (locator
format, logging, fluent returns, Allure steps) without you remembering each rule.

---

### 4.4 `review-security`

| | |
|---|---|
| **File** | `.github/prompts/review-security.prompt.md` |
| **Invocation** | `/review-security` |
| **Input** | Selected code or a file path |
| **Role** | **Umbrella** security review — covers all layers |

**When to use:** You want a **comprehensive security review** across all layers
of specified code or the whole project.

**What it checks (6 categories):**

| Category | Key Checks |
|----------|------------|
| A. Secrets & Credentials | No hardcoded passwords, `*_env` pattern, `.env` gitignored |
| B. API Security | TLS on, safe URL construction, sessions closed, retries exclude 401/403 |
| C. Selenium Security | No dangerous browser flags, parameterised `execute_script`, driver cleanup |
| D. Configuration | `yaml.safe_load()`, no secrets in config.yaml |
| E. Dependencies | Pinned versions, no known CVEs |
| F. Logging & Reporting | Headers masked, Allure attachments sanitised |

**Output format:**

```
Risk Level: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | 🟢 LOW | ✅ CLEAN

| # | Severity | Category | CWE | Location | Finding | Fix |
```

**Relationship to other security prompts:** This is the **umbrella** prompt. Use
`/review-api-security` or `/review-selenium-security` for deep dives into
specific layers.

---

### 4.5 `review-api-security`

| | |
|---|---|
| **File** | `.github/prompts/review-api-security.prompt.md` |
| **Invocation** | `/review-api-security` |
| **Role** | **Deep-dive** API layer security review |

**When to use:** You want a thorough security review of the API layer only —
`base_client.py`, services, models, schemas, tests, and response validation.

**What it checks (9 review points):**

| # | Area | What It Verifies |
|---|------|------------------|
| 1 | TLS Configuration | `session.verify` always `True`, no `verify=False` overrides |
| 2 | Authentication Security | Credentials from `ConfigLoader` only, auth header on session |
| 3 | Header Masking | `_mask_headers()` covers Authorization, X-API-Key, Cookie, Set-Cookie |
| 4 | Retry Policy | `status_forcelist` excludes 401/403, POST retry safety |
| 5 | Session Lifecycle | `session.close()` in all teardown paths |
| 6 | URL Construction | Paths are hardcoded constants, no user input interpolation |
| 7 | Request Body Security | Payloads from models, not raw dicts |
| 8 | Validation Before Trust | Status code checked before `.json()`, schema validation applied |
| 9 | Error Information Leakage | Error responses don't expose server internals in CI logs |

**When to choose this over `/review-security`:** When you've made changes
specifically to `api/base_client.py`, added a new service, or modified API test
fixtures and want a thorough API-focused audit rather than a broad scan.

---

### 4.6 `review-selenium-security`

| | |
|---|---|
| **File** | `.github/prompts/review-selenium-security.prompt.md` |
| **Invocation** | `/review-selenium-security` |
| **Role** | **Deep-dive** Selenium / UI layer security review |

**When to use:** You want a thorough security review of the browser/UI
automation layer — browser factory, driver manager, page objects, step
definitions, and screenshot handling.

**What it checks (9 review points):**

| # | Area | What It Verifies |
|---|------|------------------|
| 1 | Chrome Flags Audit | No `--disable-web-security`, `--allow-running-insecure-content`, `--ignore-certificate-errors` |
| 2 | Download/File Handling | Download dirs set to temp, auto-downloads disabled |
| 3 | Thread Safety | Threading lock used properly in driver get/quit |
| 4 | Cleanup Guarantees | `quit_driver()` handles exceptions, conftest uses `yield` |
| 5 | Sensitive Input Handling | Passwords masked in logs, `send_keys()` used (not `execute_script`) |
| 6 | JavaScript Execution | All `execute_script()` uses parameterised `arguments[N]` |
| 7 | Locator Security | Stable attributes, no XPath with user data interpolation |
| 8 | Screenshot Security | Filenames don't contain sensitive data |
| 9 | Allure Attachments | Failure screenshots don't attach page source with tokens |

**When to choose this over `/review-security`:** When you've modified
`core/browser_factory.py`, added a new Page Object, or changed the conftest
driver fixture.

---

### 4.7 `scan-secrets`

| | |
|---|---|
| **File** | `.github/prompts/scan-secrets.prompt.md` |
| **Invocation** | `/scan-secrets` |
| **Input** | Selected code or entire repository |

**When to use:** You want to scan the codebase (or a selection) specifically for
**exposed secrets, credentials, and sensitive data leakage paths**.

**What it scans for (4 tiers):**

| Tier | Severity | Examples |
|------|----------|---------|
| 1. Hardcoded Secrets | CRITICAL | Passwords, API keys, JWT tokens, Base64 creds in `.py`/`.yaml`/`.json`/`.feature` |
| 2. Leakage Paths | HIGH | Logger calls outputting password vars, unmasked Allure attachments, screenshot filenames |
| 3. Configuration Risks | MEDIUM | `config.yaml` with literal secrets, `.env` committed to git, `.env.example` with real values |
| 4. Missing Protections | LOW | Auth headers not covered by `_mask_headers()`, HTTP clients bypassing `BaseApiClient` |

**Output:**

```
Status: 🔴 SECRETS FOUND | ✅ CLEAN

| File | Line | Type | Value (first 4 chars) | Severity |
```

**When to use this vs `/review-security`:** `/scan-secrets` is narrower and
faster — use it as a pre-commit check or when you specifically suspect a
credential leak. `/review-security` covers secrets *plus* 5 other categories.

---

### 4.8 `fix-vulnerability`

| | |
|---|---|
| **File** | `.github/prompts/fix-vulnerability.prompt.md` |
| **Invocation** | `/fix-vulnerability` |
| **Input** | Vulnerability description + selected affected code |

**When to use:** You've **identified a specific vulnerability** and want a
framework-consistent fix generated.

**What it produces:**

1. **Root Cause** — why the vulnerability exists
2. **Fix Strategy** — which files change and why
3. **Code Changes** — before/after with framework-consistent patterns (e.g. uses
   `ConfigLoader`, `BaseApiClient`, `DriverManager`)
4. **Verification** — how to confirm the fix works (test commands, log checks)
5. **Prevention** — guidance to avoid re-introducing the same class of issue

**Why use this:** Ensures fixes follow framework conventions. A raw fix might
introduce new anti-patterns (e.g. replacing a hardcoded secret with a different
hardcoded secret). This prompt ensures fixes use `*_env` pattern, `ConfigLoader`,
masking, etc.

---

## 5. Skills

Skills are **reusable expertise modules**. They don't have a direct invocation
command — instead, Copilot and agents automatically detect when a task matches a
skill's domain and load its instructions. You can also reference them explicitly
in chat.

---

### 5.1 `api-test-generator`

| | |
|---|---|
| **File** | `.github/skills/api-test-generator/SKILL.md` |
| **Activates** | When you ask Copilot to create an API test case or automate a new endpoint |
| **Also used by** | `@taf-maintainer` agent for all API test creation |

**What it is:** A blueprint for generating all three components needed for a new
API test: Model + Service + Test.

**How to trigger it:**

```
Create an API test for the DELETE /api/deleteAccount endpoint
```

Copilot recognises this as an API test generation task and loads the skill.

**What it enforces:**

| Step | Output | Convention |
|------|--------|------------|
| 1. Model | `api/models/<name>_models.py` | `@dataclass` with typed fields |
| 2. Service | `api/endpoints/<name>_service.py` | Inherits `BaseApiClient`, uses `self.post()`/`self.get()` |
| 3. Test | `tests_api/test_<name>.py` | Uses `ResponseValidator` exclusively |

**Available `ResponseValidator` methods:**

```python
ResponseValidator.assert_status_code(response, expected_code)
ResponseValidator.get_json(response)
ResponseValidator.assert_json_contains(response, {"key": expected_value})
ResponseValidator.assert_matches_schema(response, "schema_file.json")
ResponseValidator.assert_response_time_under(response, max_seconds)
```

**Why it exists:** Without this skill, Copilot might generate a flat test file
with `requests.get()` calls and bare `assert` statements. The skill ensures
every generated test follows the layered architecture.

---

### 5.2 `security-scanner`

| | |
|---|---|
| **File** | `.github/skills/security-scanner/SKILL.md` |
| **Activates** | When you ask Copilot for any security-related analysis |
| **Also used by** | `@security-reviewer` agent as its core capability set |

**What it is:** An automated security analysis capability that understands the
project's specific architecture, configuration patterns, and reporting pipeline.

**5 capabilities it provides:**

| # | Capability | Trigger Example |
|---|-----------|-----------------|
| 1 | Full Security Audit | *"Run a complete security audit of the project"* |
| 2 | Targeted Scan | *"Scan api/base_client.py for security issues"* |
| 3 | Pre-Commit Check | *"Security check these changed files: [files]"* |
| 4 | New Code Review | *"Security review this new endpoint service"* |
| 5 | Fix Generation | *"Fix the hardcoded API key in tests_api/test_product.py"* |

**Integration points:**

```
security-scanner SKILL
    ├── @security-reviewer agent (uses as core engine)
    ├── /review-security prompt (full review checklist)
    ├── /review-api-security prompt (API deep-dive)
    ├── /review-selenium-security prompt (UI deep-dive)
    ├── /scan-secrets prompt (credentials scan)
    └── /fix-vulnerability prompt (remediation)
```

**Why it exists:** Centralises what "security scanning" means for this specific
project. Generic security advice doesn't know about `BaseApiClient`'s masking,
`ConfigLoader`'s `*_env` pattern, or `BrowserFactory`'s flag restrictions. This
skill does.

---

## 6. Quick Reference Matrix

### "I want to do X — which file helps?"

| Task | Use This | Type | Invocation |
|------|----------|------|------------|
| Write a new Page Object | `ui-automation.instructions.md` | Instruction | Auto (edit `pages/**`) |
| Write a new API test | `api-test-generator/SKILL.md` | Skill | Ask Copilot to create an API test |
| Add a new endpoint (full stack) | `api-automation.instructions.md` | Instruction | Auto (edit `api/**`) |
| Fix a failing test | `heal-failing-test.prompt.md` | Prompt | `/heal-failing-test` |
| Assess impact of a change | `scan-impact.prompt.md` | Prompt | `/scan-impact` |
| Update a Page Object | `update-page-object.prompt.md` | Prompt | `/update-page-object` |
| Full security audit | `review-security.prompt.md` | Prompt | `/review-security` |
| Deep-dive API security | `review-api-security.prompt.md` | Prompt | `/review-api-security` |
| Deep-dive Selenium security | `review-selenium-security.prompt.md` | Prompt | `/review-selenium-security` |
| Scan for hardcoded secrets | `scan-secrets.prompt.md` | Prompt | `/scan-secrets` |
| Fix a known vulnerability | `fix-vulnerability.prompt.md` | Prompt | `/fix-vulnerability` |
| Autonomous test maintenance | `taf-maintainer.agent.md` | Agent | `@taf-maintainer <task>` |
| Interactive security review | `security-reviewer.agent.md` | Agent | `@security-reviewer <scope>` |
| Add new config / env vars | `configuration-and-testdata.instructions.md` | Instruction | Auto (edit `config/**`) |
| General coding style check | `architecture-and-standards.instructions.md` | Instruction | Auto (all files) |
| Security compliance check | `security-standards.instructions.md` | Instruction | Referenced by agents/prompts |

---

### Security Prompt Relationship Map

```
/review-security  ←──── umbrella (all 6 categories)
    ├── /review-api-security  ←── deep-dive (API only, 9 points)
    ├── /review-selenium-security  ←── deep-dive (UI only, 9 points)
    └── /scan-secrets  ←── targeted (credentials only, 4 tiers)
            │
            └── /fix-vulnerability  ←── remediation (after finding)
```

**Rule of thumb:**

- **Broad review** → `/review-security`
- **Changed API code** → `/review-api-security`
- **Changed UI code** → `/review-selenium-security`
- **Quick secret check** → `/scan-secrets`
- **Have a finding, need a fix** → `/fix-vulnerability`

---

### Agent Decision Tree

```
Is the task about security?
  ├── YES → @security-reviewer
  └── NO → Is a test failing?
              ├── YES → @taf-maintainer (or /heal-failing-test for one-shot)
              └── NO → Is it impact analysis or page update?
                          ├── YES → @taf-maintainer
                          └── NO → Use instructions (auto-loaded) or prompts
```

---

> **Maintained by:** Manish kapoor
> **Last updated:** May 2026

