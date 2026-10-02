---
name: pyfixest
description: Run and audit Python econometric models with PyFixest, including high-dimensional fixed effects, OLS/IV/PPML, explicit clustered inference, supported modern DiD estimators, and traceable regression output. Use for Python FE estimation or reproducing Stata/R results with PyFixest; manuscript editing alone belongs to econ-fin-writing.
license: MIT
metadata:
  upstream: "https://github.com/Barrios88/barrios-skills"
  upstream_ref: "d50afc62f4c67535a1949d029dfa0462feb906fd"
  tested_pyfixest: "0.60.0"
---

# PyFixest

A maintained adaptation of [Barrios PyFixest](https://github.com/Barrios88/barrios-skills/tree/d50afc62f4c67535a1949d029dfa0462feb906fd/skills/econometrics/pyfixest). This kit replaces generic clustering defaults and collection-relative links with design-specific inference and installed companion skills. Consult [official PyFixest documentation](https://pyfixest.org/) for version-sensitive APIs.

## Establish the specification

Identify outcome/scale, endogenous regressor or treatment, controls and their timing, FE, target estimand, weights, assignment/dependence level and sample. Verify keys, missingness and actual identifying variation. Use the project's existing specification when reproducing results; explain changes before making them.

State `vcov` explicitly. Firm-year data exposed to a region policy may require region clustering. Cluster choice follows assignment and residual correlation rather than the observation-unit name. Record cluster counts and address few-cluster inference when necessary. FE do not substitute for clustered covariance or prove causal identification.

## Core calls

```python
import pyfixest as pf

ols = pf.feols("y ~ treatment + x | id + time", data=df,
               vcov={"CRV1": "assignment_cluster"})
iv = pf.feols("y ~ x | id + time | endog ~ z", data=df,
              vcov={"CRV1": "assignment_cluster"})
ppml = pf.fepois("nonnegative_y ~ treatment + x | id + time", data=df,
                 vcov={"CRV1": "assignment_cluster"})
results = ols.tidy()
```

Names are illustrative. Inspect dropped rows, collinearity, singleton/perfect-fit removals, IV first-stage diagnostics and PPML convergence. Retain source row identifiers before estimation. Endogenous variables belong in the IV formula part; included exogenous controls also enter the first stage. Check the installed version's IV support for multiple endogenous variables.

## DiD

Use the design to select supported `did2s`, saturated/Sun-Abraham or local-projection interfaces in [official DiD documentation](https://pyfixest.org/difference-in-differences.html). Check cohort coding, never-treated/control group, anticipation and reversals. Do not treat a pooled staggered TWFE coefficient or naive lead-lag plot as automatically estimating a causal ATT. Describe aggregation and cohort support; distinguish simultaneous from pointwise inference.

The installed `r-econometrics` references supply method assumptions; its calls are R-specific. Use `stata-regression-workflow` when the replication is Stata-first. A financial abnormal-return event study is a different workflow from policy DiD.

## Traceable output

Save the model, exact options/formula, estimation row keys, warnings and versions with a model ID. Read coefficients, SEs, p-values and intervals from the same model/covariance; derive stars from unrounded p-values. Distinguish within/overall R-squared and sample changes. Match small-sample corrections and singleton treatment before declaring agreement with Stata/R.

Use `format-econ-fin-tables` for final tables and `econ-fin-writing` for authorized manuscript work. For IV, report the actual first-stage and weak-identification diagnostics without treating F > 10 as a universal validity test.

## Portable runtime

Prefer `CODEX_PYFIXEST_PYTHON` or a project's virtual environment. This computer's managed environment can be discovered with `Join-Path $env:USERPROFILE '.codex\runtimes\pyfixest-py\Scripts\python.exe'`; if absent, detect a Python installation and create an isolated environment as needed. Record resolved versions in the project rather than relying on the name `python`.

The tested direct dependency is in `scripts/requirements-pyfixest.txt`; `scripts/requirements-lock.txt` records the resolved Windows/Python 3.12 test environment. Use the direct requirement and retest when a different platform cannot satisfy the lock. No Python runtime or binary is synced as part of the skill.

```powershell
& $python "<skill-dir>/scripts/smoke_test.py"
```

The script uses synthetic data and independently checks FE coefficients, clustered covariance, IV coefficients and a known DiD effect. Passing it validates the installed API, not a real study's assumptions. See [Provenance](references/provenance.md) for the adaptation and test scope.
