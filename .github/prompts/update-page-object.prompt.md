---
mode: agent
description: Update a Page Object with new elements/methods
tools: [filesystem]
---
# Task: Update Page Object

Target: **${input:page_file}**
Changes needed: **${input:description}**

## Steps
1. Read the target file in `pages/`
2. Verify it inherits from `base_page.py`
3. Add/modify locators as class constants (uppercase, descriptive)
4. Add/modify methods following fluent pattern (return `self` or next page)
5. Wrap actions in `@allure.step("...")`
6. Check `step_definitions/` for steps that use this page — flag if they need updates
7. Output the diff