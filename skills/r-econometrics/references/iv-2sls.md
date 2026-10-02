# IV and 2SLS

## Design before estimation

Name the endogenous regressor, excluded instrument, included exogenous controls, variation after FE, first-stage population, and target effect. Explain instrument relevance, exclusion and independence using institutional facts. For a binary-treatment LATE interpretation, also discuss monotonicity and compliers; it is not a universal interpretation of every linear IV coefficient.

Avoid controls affected by the instrument/treatment unless the estimand and identification argument justify them. The first and second stage must use consistent observations, controls, FE, weights and inference.

## R implementations

For an IV model with FE:

```r
iv_fit <- fixest::feols(y ~ x | id + time | endog ~ z,
                        data = df, vcov = ~ assignment_cluster)
summary(iv_fit, stage = 1)
summary(iv_fit, stage = 2)
```

The last formula part identifies the endogenous regressor and excluded instrument; included exogenous controls also enter the first stage. For several instruments use `endog ~ z1 + z2`. Check support in the installed package before using multiple endogenous variables.

For conventional cross-sectional diagnostics:

```r
iv_fit <- ivreg::ivreg(y ~ endog + x | z + x, data = df)
summary(iv_fit, diagnostics = TRUE)
V <- sandwich::vcovCL(iv_fit, cluster = df$assignment_cluster, type = "HC1")
lmtest::coeftest(iv_fit, vcov. = V)
```

Use a deliberately complete-case input `df` in this illustration so its cluster vector is aligned to fitted rows. The covariance-aware `coeftest` is the inferential output here; default `summary` diagnostic tests may use a different covariance. Verify robust diagnostic support rather than relabeling default tests as cluster-robust.

## Diagnostics and interpretation

Report the first-stage excluded-instrument test with its exact test name, covariance, instrument count and sample. A conventional F > 10 heuristic does not certify instrument strength with clustering, many instruments, multiple endogenous regressors or heterogeneous designs. Distinguish ordinary first-stage F from robust weak-identification diagnostics.

When weak identification is plausible, investigate valid weak-IV-robust inference such as Anderson-Rubin under the actual design. Do not substitute ordinary 2SLS t-tests or normal intervals. Overidentification-test nonrejection does not prove all instruments valid, and an exactly identified model has no overidentification test.

Compare OLS, first stage, reduced form and IV only with matching samples and a clear explanation of their different quantities. Preserve signed coefficients, raw units and the population interpretation.

Primary sources: [fixest IV support](https://lrberge.github.io/fixest/articles/fixest_walkthrough.html), [ivreg diagnostics](https://zeileis.github.io/ivreg/articles/ivreg.html).
