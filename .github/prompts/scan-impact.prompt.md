---
mode: agent
description: Scan codebase to find impact of a change
tools: [filesystem, terminal]
---
# Task: Impact Analysis

Change description: **${input:change}**

## Steps
1. Use filesystem search and text search tools to find affected files in:
   - `pages/` (Page Objects)
   - `step_definitions/` (BDD steps)
   - `features/` (Feature files)
   - `api/endpoints/` (API clients)
   - `data/` (test data)
2. Analyze UI ↔ API dependencies (e.g., if login changes, check `data/user_credentials.json`)
3. Produce an impact report:
   - Files requiring changes
   - Risk level (low/medium/high)
   - Suggested modification order
4. Output as a checklist; do NOT modify files yet