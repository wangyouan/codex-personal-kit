# Data construction and sample audit

Use when preparing economic microdata, merging sources, constructing variables, or tracing discrepancies across datasets and tables. This reference develops the reproducibility ideas in [Barrios Stata data cleaning](https://github.com/Barrios88/barrios-skills/tree/d50afc62f4c67535a1949d029dfa0462feb906fd/skills/econometrics/stata-data-cleaning) for this kit. Its example code is not copied.

## Establish the data contract

Read existing code and the source dictionary before choosing a transformation. Record observation unit, unique key, source period, currency, price basis, decimal versus percent scale, and expected panel frequency. Preserve IDs with leading zeros as strings when appropriate.

Keep raw inputs immutable. Use project-relative paths and a separate output directory. In an audit-only task, produce a diagnostic copy and report before changing production variables or estimates.

## Keys, duplicates, and merges

Declare merge cardinality from the data's observation units. Validate keys on both sides; an unexpected many-to-many merge usually indicates a missing key or inconsistent frequency. Document unmatched rows before deciding whether to retain or exclude them. Preserve source identifiers to trace affected observations.

```stata
* For a firm-year panel; choose keys appropriate to the actual source.
assert !missing(firm_id, year)
duplicates report firm_id year
duplicates tag firm_id year, generate(duplicate_key)
count if duplicate_key > 0
list firm_id year if duplicate_key > 0 in 1/30
isid firm_id year
drop duplicate_key
```

`duplicates report` does not create `_dup`. Do not use undefined flags, drop duplicates blindly, or bypass a failed `isid` with `capture`. Resolve whether duplicates are errors or valid lower-frequency observations first.

For an intended one-to-one merge, verify uniqueness in the using file before `merge 1:1 firm_id year using ...`. After merging, report `_merge` counts, row counts, and unique-key counts. Assert the expected key again. Restrict matches only when the research sample calls for it.

## Missingness, outliers, and construction

- Recode sentinel values such as -99 only when the dictionary identifies them as missing; legitimate negative values can be economically meaningful.
- Guard upper-bound comparisons with `!missing(var)` because Stata's numeric missing values exceed finite numbers.
- Record source columns, formula, timing, units, and missing-value rules for each derived variable. Check denominator zeros and whether lagged values are truly available at the event date.
- Winsorization is a research choice. Preserve the project's existing tails, grouping, eligible population, order relative to merges, and handling of missingness. Record cutoffs and affected counts; keep raw and transformed columns distinguishable. Do not add a generic 1% rule without support from the analysis protocol.
- Avoid automatic `log(x+1)` and imputation. Explain how a proposed transformation changes the measure and estimand.
- For returns and event measures, distinguish calendar/trading days, estimation/event windows, cumulative/average statistics, benchmark model, and multiplication by 100.

## Sample and variable deliverables

Use ordered, mutually accounted-for steps in a sample-flow CSV: `step, restriction, rows_before, rows_removed, rows_after, units_after, reason`. A zero-exclusion step should still be recorded when the user asks for an explicit flow. Compare model-specific complete cases with any deliberately common sample, including absorbed-FE singleton losses.

The variable dictionary should retain `variable, raw_source, source_column, formula, unit, scale, timing, winsorization, missing_rule`. For affected variables, compare N, missingness, mean, SD, min, percentiles, and max before and after construction. Compare excluded observations to retained ones when attrition may affect interpretation.

Save logs, warnings, input hashes, and the software/package versions. Map each output table to its dataset, model ID, and script; retrieve coefficients, SEs, p-values, and stars from the same fitted model and covariance specification.

Reference: [Stata Data Management Manual](https://www.stata.com/manuals/d.pdf), [DIME Analytics Data Handbook](https://worldbank.github.io/dime-data-handbook/).
