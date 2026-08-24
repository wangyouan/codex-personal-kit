# Research Integrity Checks

Formatting must not conceal specification choices or sample construction. The
long-format importer therefore records review flags as metadata; a flag is not
a statistical conclusion and must be checked against the research design.

## Sample audit rows

When present in an input export, retain the following stages or counts:

- defined sample units;
- outcome nonmissing observations;
- treatment merge success;
- controls merge success;
- all-controls-nonmissing observations;
- final estimation sample (`e(sample)`).

For panel data, also report the unit count separately from observations. A
change in observations or units across columns should be explained by sample
restrictions, missingness, an unbalanced panel, or another documented reason.

## Specification review flags

Review the specification set when any of the following occurs:

- the sign of a focal coefficient changes across columns;
- observations or units change across columns;
- fixed effects, controls, estimator, or clustering change across columns;
- the denominator or outcome definition changes without a visible label.

Do not alter coefficients, standard errors, p-values, or stars to make a set of
specifications look consistent. If a specification search occurred, preserve
the full sensitivity set and disclose the search or selection rule.

## Output profiles

- `chinese-journal`: Chinese labels, four decimals by default, and Chinese notes.
- `english-paper`: English labels, three decimals by default, and English notes.
- `compact-report`: compact working output with four decimals by default; use it
  for internal review, not as a substitute for a journal template.
