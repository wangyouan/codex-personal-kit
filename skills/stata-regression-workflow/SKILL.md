---
name: stata-regression-workflow
description: Use when Codex needs to run, reproduce, debug, or document empirical regression workflows involving Stata, including calling Stata from Windows batch mode, running .do files, checking .log errors, comparing Stata with R/fixest or Python reproductions, and organizing regression outputs into CSV/XLSX reports.
---

# Stata Regression Workflow

Use this skill for empirical regression tasks where Stata is part of the workflow, even if the final reproduction is done in R/fixest or Python.

## Core Workflow

1. Locate the project root and identify the active regression file, data file, output directory, and expected result format.
2. Determine whether the task should run Stata directly, reproduce Stata results in R/Python, or only inspect existing logs/results.
3. If running Stata, use batch mode and write logs to a dated output directory.
4. After running, inspect the `.log` before trusting output files.
5. Summarize sample restrictions, fixed effects, clustering, key coefficients, and any failed models.
6. If creating `.xlsx` reports, use the spreadsheet skill/artifact-tool workflow and keep generated inspection files out of final outputs.

## Finding Stata on Windows

First check whether a path is already configured:

```powershell
$env:STATA_EXE
Get-Command stata,stata-mp,StataMP-64,StataSE-64,StataBE-64 -ErrorAction SilentlyContinue
```

If not found, search likely install locations without assuming a fixed version:

```powershell
Get-ChildItem 'C:\Program Files','D:\Program Files' -Recurse -Filter 'Stata*.exe' -ErrorAction SilentlyContinue | Select-Object -First 20 FullName
```

Prefer storing the resolved path in a local variable for the current run. Do not hard-code it into project files unless the user asks.

## Running a `.do` File

Use batch mode so Codex can wait for completion and inspect logs:

```powershell
& $stataExe -b do 'D:\path\to\regression.do'
```

If a Stata edition does not accept `-b do`, try the edition-specific executable's documented batch syntax. Always use absolute paths for the do file, data files, and output locations when possible.

If the do file relies on working directory, inspect the first lines for `cd`, globals, and path macros. Update paths only after explaining the edit.

## Log Inspection Checklist

After every run, inspect the newest `.log` or the log explicitly created by the do file. Search for:

- `r(` Stata return-code errors
- `command ... is unrecognized`
- `file ... not found`
- `variable ... not found`
- `no observations`
- `last estimates not found`
- `conformability error`
- `type mismatch`
- `option ... not allowed`
- missing user-written commands such as `reghdfe`, `ivreghdfe`, `esttab`, `outreg2`, `winsor2`, `astile`

If a user-written Stata package is missing, report it and ask before installing via `ssc install` if network access or environment changes are needed.

## Result Reporting

When reporting regression output, include:

- sample window and exclusions
- dependent variable and main variable
- controls, fixed effects, and clustering
- coefficient, t-stat, significance, observations, and R-squared if available
- whether the result came from Stata, R/fixest reproduction, or Python reproduction
- where output files were saved

For interaction terms, display publication-facing names such as `Female_ratio x low_group`, not raw Stata factor-variable names unless debugging.

## R/fixest Reproduction

If Stata is unavailable, slow, or hard to automate, reproduce linear FE models in R/fixest when the do-file specification is clear. Match:

- sample restrictions
- scaling of dependent variables and regressors
- fixed effects
- clustering level
- interaction construction
- IV first and second stage definitions

Report any expected differences from Stata commands, especially if Stata used specialized estimators or finite-sample corrections.

## Project-Specific References

If a project has its own path conventions, sample restrictions, report naming, or current result workflow, keep those notes in `references/` and read the relevant file before editing or running regressions.


