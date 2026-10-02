# DiD and event studies

## Decide which design is present

Record first treatment date, untreated observations, anticipation, reversals/repeated exposure, event horizon and comparison group. A first-adoption cohort estimator is inappropriate for reversible treatment unless its assumptions specifically accommodate that process. Distinguish a return-based financial event study from policy DiD.

For common timing with a defensible untreated comparison, a conventional FE DiD can be appropriate. For staggered timing and heterogeneous effects, define the ATT/cohort-time/dynamic estimand before choosing a modern estimator. A pooled TWFE coefficient or naive lead-lag plot need not equal that estimand.

## Callaway-Sant'Anna group-time effects

The `did` package codes never-treated units as `g = 0`, with first-treatment cohort constant within unit. Verify unit-time uniqueness and actual outcome coverage.

```r
att <- did::att_gt(
  yname = "y", tname = "time", idname = "id", gname = "g",
  xformla = ~ 1, data = df, panel = TRUE,
  control_group = "nevertreated", anticipation = 0,
  bstrap = TRUE, biters = 999, cband = TRUE,
  clustervars = "assignment_cluster"
)
overall <- did::aggte(att, type = "simple")
dynamic <- did::aggte(att, type = "dynamic")
summary(overall)
did::ggdid(dynamic)
```

These choices are examples, not defaults for every project. Change control group to `notyettreated` only if justified by the design. Explain covariate timing and conditional parallel trends when adding `xformla`; do not automatically include post-treatment controls. Record panel balancing/attrition and any small-group or overlap warnings.

## Sun-Abraham using fixest

`sunab()` has different cohort coding from `did`. A never-treated code should lie beyond all observed periods when supplying calendar time; do not indiscriminately pass `g = 0` to `sunab`. Remove or explicitly handle units already treated before the sample: an out-of-range past cohort must not be accidentally treated as never-treated.

```r
df_sa <- df
never_code <- max(df_sa$time) + 100L
df_sa$g_sa <- ifelse(df_sa$g == 0, never_code, df_sa$g)
sa <- fixest::feols(y ~ sunab(g_sa, time, ref.p = -1) | id + time,
                    data = df_sa, vcov = ~ assignment_cluster)
fixest::iplot(sa)
summary(sa, agg = "ATT")
```

Check cohort support and aggregation weights before comparing this estimator with group-time ATT. Do not require a Bacon decomposition or an extra TWFE benchmark automatically. If requested, distinguish the decomposition of TWFE comparisons from a robust effect estimator.

## Interpretation and inference

Specify omitted period, event-window binning, cohort coverage at each horizon, and pointwise versus simultaneous intervals. Dynamic effects can change with cohort composition; use supported balanced-horizon aggregation where appropriate and report the sample cost.

Pre-period nonrejection does not prove parallel trends. Discuss power, anticipation, placebo timing, concurrent policies and spillovers as relevant. Do not select the lead-lag window or preferred estimator by which version produces significance. Consider sensitivity analysis for plausible violations when the research question requires it.

Keep pre-treatment diagnostics distinct from post-treatment effects. Save group-time estimates, aggregation definition, warnings, sample and the exact estimator configuration so each reported column is traceable.

Primary sources: [did introduction](https://bcallaway11.github.io/did/articles/did-basics.html), [Sun-Abraham implementation and cohort rules](https://lrberge.github.io/fixest/reference/sunab.html), [PyFixest DiD](https://pyfixest.org/difference-in-differences.html).
