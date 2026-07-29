---
name: stata-runner
description: Run Stata do-files and Stata-based empirical workflows from Codex. Use when the user asks to run Stata, execute .do files, work with .dta data, run regressions, produce Stata logs or tables, debug Stata code, or automate Stata batch jobs on Windows.
---

# Stata Runner

Use this skill for Stata work on Windows: execute `.do` files, inspect `.log` files, debug errors, and summarize regression outputs.

## Local Stata Discovery

Set `STATA_EXE` locally only when Stata is installed in a nonstandard location. Otherwise `scripts/run_stata.ps1` checks executable names and common Windows installation directories. Do not write a machine-specific executable path into this skill or the repository.

```powershell
$env:STATA_EXE = "C:\\Path\\To\\StataMP-64.exe"
powershell -ExecutionPolicy Bypass -File scripts\\run_stata.ps1 -DoFile "C:\\project\\analysis.do"
```

`/e do` runs Stata in batch mode and exits after the do-file completes. It writes a `.log` next to the do-file unless the do-file opens another log.

## Workflow

1. Keep do-files and data under the current workspace whenever possible.
2. Use absolute paths when Stata path resolution matters; prefer forward slashes inside Stata strings.
3. Start generated do-files with `version`, `clear all`, and `set more off`, and end them with `exit`.
4. Do not open a manual log with the same basename as a `/e do` run; that can produce `r(608)`.
5. Inspect the resulting `.log` after every run. Search for `r(<number>)`, missing files or variables, no observations, convergence failures, collinearity warnings, and table export failures.
6. Treat the log as authoritative even when the process returns exit code 0.

## Output Discipline

- Report the do-file, log path, and generated output files.
- Summarize the relevant coefficients and model specification rather than reproducing the full log.
- Do not overwrite raw data. Write generated outputs under explicit result names.
