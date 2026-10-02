# Regression discontinuity

## Assignment and local population

Verify the running variable, cutoff, treatment assignment direction, sharp/fuzzy compliance, and whether other rules change at the same cutoff. The design identifies a local effect, not automatically the full-sample ATE. Preserve the running-variable units; rescaling affects reported bandwidths.

Inspect support on both sides, mass points/discrete scores, heaping, sorting and missingness. Use local polynomial estimation rather than defaulting to a high-order global polynomial.

## Maintained implementation

```r
ok <- complete.cases(df[c("y", "running")])
rd_data <- df[ok, ]
sharp <- rdrobust::rdrobust(y = rd_data$y, x = rd_data$running,
                            c = cutoff, p = 1, kernel = "triangular")
summary(sharp)
rdrobust::rdplot(y = rd_data$y, x = rd_data$running, c = cutoff)
density <- rddensity::rddensity(X = rd_data$running, c = cutoff)
summary(density)
```

For fuzzy treatment, establish a discontinuous first stage and the additional IV assumptions before using `fuzzy = rd_data$treatment`; include treatment in the complete-case preparation. Where clustering is warranted, pass an aligned cluster vector and inspect the package's available variance options.

Report the point-estimate convention and robust bias-corrected inference explicitly. Do not combine an unqualified conventional estimate/SE with the robust p-value while presenting all as one conventional regression row. Preserve bandwidths, polynomial orders, kernel, cutoff, effective N on both sides and warnings.

## Design checks

Use bandwidth sensitivity, justified donut exclusions, predetermined-covariate continuity and placebo cutoffs to probe specific threats. Do not choose bandwidth or exclusions by statistical significance. A density-test nonrejection does not establish no manipulation; consider institutional sorting and discrete support.

For geographic or multi-cutoff designs, local-randomization approaches, or very discrete scores, consult the appropriate specialized package and assumptions. They are not interchangeable applications of the standard one-dimensional continuity design.

Primary source: [RD Packages and its maintained implementations](https://rdpackages.github.io/).
