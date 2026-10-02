# Panel models and inference

## Identification and data

Check unique unit-period keys and missing IDs before indexing a panel. Explain balanced versus unbalanced coverage and attrition. Unit FE remove time-invariant heterogeneity, not all endogeneity. A regressor constant within the absorbed FE has no separately identified slope. FE interactions and regressor interactions are different specifications.

Covariance choices follow assignment and residual dependence. Firm observations exposed to a state policy may require state-level clustering; firm clustering is not sufficient merely because the dataset is firm-year. Record number of clusters and treated clusters. For few independent clusters consider design-appropriate randomization inference, wild cluster bootstrap, or bias-corrected small-sample methods, with their assumptions; adding another cluster dimension is not a generic cure.

## Established R calls

```r
library(fixest)
stopifnot(!anyNA(df[c("id", "time")]),
          !anyDuplicated(df[c("id", "time")]))
fit <- feols(y ~ treatment + x | id + time, data = df, vcov = ~ policy_region)
ct <- coeftable(fit)
ci <- confint(fit)
```

Here `policy_region` is illustrative and must match the actual design. For justified two-way dependence use `vcov = ~ id + time`; state why each dimension is needed and whether either has too few clusters. Report the covariance used for the extracted table, not a later default re-summary.

For nonnegative outcomes whose conditional mean supports PPML:

```r
fit_ppml <- fepois(y ~ treatment + x | id + time, data = df,
                  vcov = ~ policy_region)
```

PPML is not interchangeable with log-OLS. Preserve zeros where the design requires them; inspect separation, dropped observations and convergence before interpreting the fit.

## Sample and output reconciliation

Use `fixest::obs(fit)` to locate the used rows in the exact input data, retaining their stable source keys. Explain NA, collinearity, singleton/perfect-fit removals and weights. Report overall versus within R-squared using their correct labels; likelihood/pseudo-R-squared for nonlinear models is not OLS R-squared.

When comparing specifications, either deliberately use a common sample or explain model-specific samples. When comparing Stata/Python, align FE, intercept, interactions, weights, singleton handling, covariance type, degrees of freedom and small-sample correction. Compare coefficients separately from inference. Retain raw unrounded values and add stars from the actual p-values.

For a reproduction that requires explicit small-sample choices, inspect `fixest::ssc()` and save the supplied arguments. Do not change the correction to force agreement without reporting why.

Primary sources: [fixest walkthrough](https://lrberge.github.io/fixest/articles/fixest_walkthrough.html), [standard errors and small samples](https://lrberge.github.io/fixest/articles/standard_errors.html).
