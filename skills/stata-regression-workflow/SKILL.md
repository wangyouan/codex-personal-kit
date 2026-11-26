---
name: stata-regression-workflow
description: Run, reproduce, debug, or document Stata regressions, including high-dimensional fixed-effect OLS/WLS with fereg and PPML with feppml, Stata batch jobs and log checks, cross-software reproduction, and regression output.
---

# Stata Regression Workflow

Use this skill for empirical regression tasks where Stata is part of the workflow, even if the final reproduction is done in R/fixest or Python.

## Core Workflow

1. Locate the project root and identify the active regression file, data file, output directory, and expected result format.
   For raw-data preparation, merges, variable construction, or unexplained sample changes, read [Data construction and sample audit](references/data-construction-audit.md).
2. Determine whether the task should run Stata directly, reproduce Stata results in R/Python, or only inspect existing logs/results.
3. If running Stata, use batch mode and write logs to a dated output directory.
4. After running, inspect the `.log` before trusting output files.
5. Summarize sample restrictions, fixed effects, clustering, key coefficients, and any failed models.
6. If creating `.xlsx` reports, use the spreadsheet skill/artifact-tool workflow and keep generated inspection files out of final outputs.

## Default High-Dimensional Fixed-Effect Commands

- For new routine Stata specifications, prefer Schmieder's `fereg` for supported linear OLS/WLS with absorbed effects and `feppml` for supported PPML with a nonnegative outcome. Select the model and clustering from the research design first.
- For an exact replication, preserve the original command, version and options. Keep `reghdfe` and `ppmlhdfe` as comparison and fallback commands; preserve dedicated estimators for IV, modern DiD, and other designs outside these two model classes.
- Read [Schmieder fereg and feppml](references/fereg-feppml.md) for the pinned installation, local benchmark, and checks before changing the estimator implementation in a project.

## Execute Stata on Windows

The canonical batch runner is [scripts/run_stata.ps1](scripts/run_stata.ps1). It discovers Stata from the supplied executable, STATA_EXE or common installations, starts it hidden, waits and checks the batch log. Invoke with `-DoFile <absolute-path>` and optionally `-StataExe <absolute-path>`. Use the project's working directory and preserve raw data. Do not open a manual log with the same basename as the batch log. Inspect warnings and output completeness even when the runner exits successfully.

For execution-only requests, run the existing do-file and inspect its log; do not redesign its model. For estimation or data-construction requests, use the methodological sections below. `$stata-runner` and its old script path remain compatibility aliases; maintain execution logic here only.

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
- missing user-written commands such as `fereg`, `feppml`, `reghdfe`, `ppmlhdfe`, `ivreghdfe`, `esttab`, `outreg2`, `winsor2`, `astile`

If a package is missing, report it and install from its approved source only when the task authorizes installation. For `fereg`/`feppml`, use the author's versioned catalog in the linked reference.

## Methodological Guardrails

Apply these checks before trusting generated Stata code or regression output:

- Stata numeric missing values sort above every finite number. Guard comparisons and sample restrictions with `!missing(...)` when missingness could otherwise be treated as a large value.
- Use factor-variable notation deliberately: `i.` for categorical variables and `c.` for continuous variables. For interactions, distinguish `##` (main effects plus interaction) from `#` (interaction term only).
- After every `merge`, inspect `_merge`, verify the expected match pattern, and only then drop the diagnostic variable.
- Use `bysort` unless the data have been explicitly sorted before a `by` prefix. Create stable IDs before any `preserve`/`restore` block that sorts or subsets data.
- Preserve estimation results before running commands that overwrite `e()`. Check `_rc` after `capture`; a suppressed error is still a failed step.
- Do not treat `fweight`, `aweight`, `pweight`, and `iweight` as interchangeable. Record the weighting rationale in the analysis notes.
- For event studies and staggered treatment timing, state the omitted period, treatment cohort definition, pre-trend test, and estimator-specific identifying assumptions. Do not present a two-way fixed-effects coefficient as automatically causal.

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

Use the installed `r-econometrics` skill for R-specific IV, staggered DiD, and RDD implementation. Use `pyfixest` for Python high-dimensional FE and supported DiD estimators. Preserve the original design when changing software; differences in estimands require explicit explanation.

## Python Panel Reproduction

When reproducing a panel model in the Anaconda `codex` environment, make the panel structure explicit before estimation:

- Validate entity and time identifiers, duplicate entity-time rows, missingness, and balanced versus unbalanced coverage.
- Set a clear entity-time index for `linearmodels`, and specify entity effects, time effects, and clustering explicitly rather than relying on defaults.
- Match Stata's sample restrictions, variable scaling, fixed effects, interaction construction, and clustering level before comparing coefficients.
- Treat Python output as a reproduction only after reconciling observations, absorbed effects, standard errors, and any estimator-specific finite-sample correction.

## Project-Specific References

If a project has its own path conventions, sample restrictions, report naming, or current result workflow, keep those notes in `references/` and read the relevant file before editing or running regressions.

