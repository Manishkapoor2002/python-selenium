---
mode: agent
description: Diagnose and auto-heal a failing test
tools: [filesystem, terminal]
---
# Task: Self-Heal Failing Test

Target test: **${input:test_path}**

## Diagnostic Protocol
1. Run: `pytest ${input:test_path} --alluredir=reports/allure-results -v`
2. Read `logs/pytest-logs.txt` and terminal output
3. Classify the failure:
   - **NoSuchElementException** → re-scan the relevant file in `pages/`, propose locator fix
   - **DependencyError / ImportError** → check `requirements.txt`
   - **AssertionError** → analyze expected vs actual; check if spec changed
   - **TimeoutException** → review wait strategy in Page Object
4. Propose the minimal fix as a unified diff
5. Apply the fix and re-run until exit code is 0
6. Report: root cause, fix applied, final status

## Constraints
- Do NOT modify `core/`
- Preserve all Allure decorators
- Max 3 healing iterations; escalate to human if still failing