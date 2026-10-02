---
name: r-econometrics
description: Implement and audit applied econometric designs in R, including panel fixed effects, IV/2SLS, difference-in-differences and staggered event studies, and sharp/fuzzy RDD. Use for estimator selection, identification diagnostics, R regression code, or reproduction of empirical results. Includes extension routing for synthetic control, synthetic DiD, DML and causal forests; manuscript polishing alone belongs to econ-fin-writing.
metadata:
  version: "1.0.0"
---

# R Econometrics

A self-maintained methods package for this personal kit. Read the project's design and code before choosing an estimator. Preserve the user's target estimand and audit-versus-edit scope. This package draws workflow ideas from Barrios but its instructions and examples are newly authored; no Barrios R file or embedded script is installed.

## Route to the relevant method

| Request/design | Read |
|---|---|
| Panel FE, PPML, clustered inference, cross-software reproduction | [Panel and inference](references/panel-and-inference.md) |
| Endogenous regressor and excluded instrument | [IV and 2SLS](references/iv-2sls.md) |
| Policy/event adoption, DiD, dynamic effects or pre-trends | [DiD and event studies](references/did-event-study.md) |
| Assignment at a cutoff, sharp or fuzzy discontinuity | [RDD](references/rdd.md) |
| Donor-weighted comparison or ML-based causal effects | [Method extensions](references/method-extensions.md) |
| New runtime or a package API check | [Runtime and sources](references/runtime-and-sources.md) |

Read only the needed module plus panel/inference when reconciling covariance or samples. These modules supply established package calls, not a custom estimator library.

## From question to a verified result

1. Establish observation unit, outcome, treatment/endogenous variable, target population and horizon, available identifying variation, design assumptions, FE, clustering, weights, timing, and intended output. Infer them from existing scripts when documented; clarify choices that materially change identification.
2. Inspect keys, missingness, cohort/threshold support and control timing. Record source-to-model exclusions, units and transformations. Diagnose unknown cleaning choices before inventing replacements.
3. Select an established implementation consistent with the design. Staggered adoption, treatment reversals, weak instruments and few clusters require attention beyond a generic regression template. Check installed package help/version for arguments that vary by release.
4. Save the fitted object, exact estimation sample identifiers, formula/options, warnings, covariance choice, package versions and source hashes with each model ID. Extract coefficients, SEs, p-values and intervals from that same object and inference specification.
5. Assess assumptions with design-relevant evidence. Pre-tests and robustness checks do not certify untestable assumptions. Explain changes in samples, estimands or aggregation before comparing estimates.
6. Report the actual result, diagnostics, limitations and output paths at the requested depth. Use `format-econ-fin-tables` for publication tables and `econ-fin-writing` for manuscript prose when installed. A result-writing request does not itself authorize recomputing the model.

## Runtime

Resolve `RSCRIPT_EXE`, then `Get-Command Rscript`, then installed R directories. Prefer an existing project `renv` library. Record `sessionInfo()` and the project lockfile when available. Do not hard-code a personal machine path into the skill or automatically install every optional package.

The synthetic validation script can be run without research data:

```powershell
& $rscript --vanilla "<skill-dir>/scripts/smoke_test.R"
```

It requires `fixest`, `did`, `rdrobust`, and `rddensity`; missing dependencies produce a failure with an explicit list. A missing R runtime is a documented execution limitation, not evidence that a method was tested. Python tasks may use the installed `pyfixest` skill; Stata execution belongs to `stata-runner` / `stata-regression-workflow`.
