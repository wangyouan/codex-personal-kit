# Schmieder's fereg and feppml

Use Johannes F. Schmieder's Stata package, which installs both commands. The
similarly named Leo Liu package is a separate implementation. See the
[v0.6.0 release](https://github.com/johannes-schmieder/fereg/releases/tag/v0.6.0),
[installation guide](https://github.com/johannes-schmieder/fereg/blob/v0.6.0/docs/installation.md)
and [working paper](https://doi.org/10.3386/w36017). Version 0.6.0 is the
version tested locally; use the recorded project version for replication.

## Install and Verify

Start a fresh Stata session, especially on Windows where a loaded plugin may
prevent replacement. Check `which fereg` and `which feppml` before reinstalling.
If installation is needed and authorized, run:

```stata
net install fereg, from("https://raw.githubusercontent.com/johannes-schmieder/fereg/v0.6.0/") replace
which fereg
which feppml
fereg, selftest
```

If a per-file transfer fails, download the [same official tagged ZIP](https://github.com/johannes-schmieder/fereg/archive/refs/tags/v0.6.0.zip),
extract it, and compare the Windows plugin's SHA-256 with
`dist/fereg_windows.plugin.sha256` from the archive. Point `from()` to the
extracted folder containing `fereg.pkg` (use its absolute path with forward
slashes), then repeat the version checks and self-test. This fallback was used
successfully on local Windows Stata/MP 18. Check the Stata log for errors and
require a passing self-test and matching ado/plugin versions. The skill does
not bundle the plugin or change another computer's Stata installation.

## Routine Use and Reconciliation

```stata
fereg  y_linear x1 x2 x3, absorb(firm industry_year) vce(cluster firm)
feppml y_count  x1 x2 x3, absorb(firm industry_year) vce(cluster firm)
```

- Use the installed `help fereg` and `help feppml` for supported syntax,
  weights, fixed-effect interactions/slopes and postestimation. Check support
  for the actual specification; do not silently simplify it, substitute a
  different estimator, or interpret a nonconverged fit.
- `feppml` uses a nonnegative outcome in levels, including zeros. Review
  missingness, singleton removals, and separation (including fixed-effect
  groups with only zeros); record the retained sample and reason for drops.
  Keep separation detection and solver acceptance checks enabled.
- Before switching an existing project, or using a material feature not yet
  checked on its data (e.g., weights, multiway clustering, absorbed slopes,
  or a different separation pattern), compare one representative fit against
  `reghdfe` / `ppmlhdfe` as applicable. Match input order, specification, sample
  restrictions, weights and clustering. Compare observation keys in
  `e(sample)`, omitted terms, slopes in `e(b)`, covariance in `e(V)`, cluster
  counts, and degrees of freedom or test conventions. Investigate discrepancies
  before switching; equal N or coefficients alone do not establish agreement.
- Compare identified slopes and, when relevant, fitted values. With absorbed
  effects, intercept reporting or fixed-effect normalization can differ.
  Use the installed help for prediction options and saved effects.
- Compare elapsed command time after a warm-up, with the same inputs and CPU
  budget, alternating command order. Set the Stata/MP processor count and pass
  `threads(#)` explicitly to the new commands for comparable timings. Log
  versions, thread settings, and the solver/convergence messages.

## Local Baseline: 2026-11-17

Windows Stata/MP 18, Ryzen 9 9950X, two processors/threads for comparison;
`fereg`/`feppml` 0.6.0, `reghdfe` 6.13.1, `ppmlhdfe` 2.3.3.
The synthetic unbalanced panel contained 509,967 firm-year observations,
30,000 firms and 1,200 industry-year cells. Both models absorbed firm and
industry-year effects and clustered by firm. Median elapsed command time
over six interleaved repetitions per command, after a warm-up:

| Model | Baseline | Schmieder command | Speed ratio | Max abs. slope difference | Max abs. clustered SE difference |
| --- | ---: | ---: | ---: | ---: | ---: |
| Linear | 0.703 s | 0.074 s | 9.50x | 9.05e-15 | 2.66e-14 |
| PPML | 6.5625 s | 0.510 s | 12.87x | 1.97e-15 | 1.56e-14 |

Samples matched row by row within each pair. Linear retained 509,967 rows;
PPML retained 509,353 after dropping the same 614 rows from 37 entirely
zero-outcome firms. Differences above cover the three slope coefficients.
`ppmlhdfe` reported a constant and `feppml` absorbed it. The comparison
does not establish parity for other specifications or predict their speed.

Run [the synthetic benchmark](../scripts/benchmark_fereg.do) from a dedicated
benchmark output directory with all four commands installed. It writes
`coefficients.csv`, `timings.csv`, and `timing_summary.csv` to the current
directory, replacing files of those names. Pass the argument `accuracy` to
recheck the samples, slopes and clustered standard errors without timing.
