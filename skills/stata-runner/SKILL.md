---
name: stata-runner
description: Compatibility alias for executing Stata do-files through stata-regression-workflow. Use when the user explicitly names stata-runner.
---

# Compatibility entry

Use [stata-regression-workflow](../stata-regression-workflow/SKILL.md), execution-only mode. The old `scripts/run_stata.ps1` forwards its unchanged parameters to the canonical runner. Preserve the existing do-file specification; do not expand an execution request into model exploration.
