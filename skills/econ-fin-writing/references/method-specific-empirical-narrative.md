# Method-specific empirical narrative

Use for identification prose and interpretation, alongside the selected journal/language module. Preserve the user's editorial scope: writing an identification paragraph does not authorize new regressions or a change of estimator. Inspired by [Barrios econ-writing-plus](https://github.com/Barrios88/barrios-skills/tree/d50afc62f4c67535a1949d029dfa0462feb906fd/skills/writing-and-review/econ-writing-plus), with design-dependent guidance and links to primary method documentation.

## Connect the question to the estimand

Explain the economic question, identifying variation, comparison population, key assumption, and empirical quantity. Use the manuscript's actual implementation to distinguish diagnostics already performed from suggestions. Method names alone do not establish identification. Numerical detail belongs where it helps the argument, subject to the selected journal module.

| Design | What the prose must make clear | Interpretation boundary |
|---|---|---|
| Panel FE | Which within-unit variation remains after each FE, and which time-varying confounders remain possible | FE do not by themselves establish causality |
| IV / 2SLS | Instrument construction, first-stage relevance, exclusion and independence arguments, endogenous regressor, and comparison group | A treatment-effect/LATE interpretation needs additional assumptions; a first-stage F above 10 is not universal proof against weak instruments |
| DiD | Treatment timing/cohorts, comparison group, estimand and aggregation weights, anticipation, parallel trends, inference level | Insignificant leads do not prove parallel trends; distinguish heterogeneous staggered effects from a homogeneous TWFE interpretation |
| RDD | Assignment rule/cutoff, running variable, sharp versus fuzzy treatment, local neighborhood, bandwidth and bias-corrected inference | The estimate is local to the cutoff; nonrejection of a density test does not prove no sorting |
| RCT | Assignment unit, allocation, attrition, compliance, spillovers, ITT versus treatment received | ITT and complier effects answer different questions |
| Synthetic control / synthetic DiD | Donor eligibility, pre-treatment fit, treatment timing, weights, comparison and inference procedure | Pre-fit alone does not identify the effect; synthetic DiD and classical synthetic control are distinct estimators |
| Shift-share / Bartik | Exposure-share dates, shocks, which component supplies exogeneity, concentration and relevant inference | Many shares do not imply many independent shocks; describe the actual identification argument |
| DML / causal forest | Treatment/outcome and confounders, overlap, nuisance models, sample splitting/cross-fitting, validation and target effect | Predictive accuracy does not establish causal identification or validate every subgroup effect |
| Structural | Economic assumptions, identifying variation versus functional form, estimation targets, model fit and counterfactual | A model-implied counterfactual is conditional on the stated model |
| Descriptive / measurement | Sample representativeness, construct definition, validation and measurement error | Preserve descriptive wording and distinguish the measured proxy from the underlying construct |
| Bunching | Kink/notch, counterfactual density, exclusion window, manipulation/frictions and behavioral assumptions | Excess mass does not automatically identify an elasticity without the economic model |

## Match claims and uncertainty

Describe the actual cluster or randomization level and number of independent clusters when it matters. State whether intervals are pointwise or simultaneous. A region-level policy generally requires consideration of region-level residual correlation even with firm-level data. Multiple testing and subgroup discovery need a stated inferential approach when making confirmatory claims.

For staggered DiD, explain why the chosen estimator fits the adoption pattern and target effect. TWFE can be a benchmark where informative; do not prescribe running both TWFE and a modern estimator for every paper or adding a Bacon decomposition as a universal requirement. Discuss differences only after matching samples and estimands.

Convert effects using the manuscript's real scale and an explicitly identified baseline: decimals versus percentages, basis points versus percentage points, level versus log, cumulative versus average effects. Name the horizon. Statistical significance, economic magnitude, and policy relevance are different judgments.

## Replication and journal policy

Record data provenance/access, source-to-analysis transformations, package versions, code order, random seeds, and table/figure-to-program mapping. Restricted inputs should have an accurate access statement. Choose a license compatible with the actual data/code rights; no universal replication-package license applies.

For journal formatting, AI disclosure, or submission requirements, verify the current official outlet policy when the user requests submission preparation. Do not treat a copied skill's policy summary as current authority or impose it on ordinary prose polishing.

## Primary implementation references

- [fixest: FE, IV and inference](https://lrberge.github.io/fixest/articles/fixest_walkthrough.html)
- [did: group-time ATT](https://bcallaway11.github.io/did/articles/did-basics.html)
- [fixest: Sun-Abraham](https://lrberge.github.io/fixest/reference/sunab.html)
- [RD Packages](https://rdpackages.github.io/)
- [DoubleML](https://docs.doubleml.org/stable/index.html) and [grf](https://grf-labs.github.io/grf/)

Use the installed `r-econometrics`, `stata-regression-workflow`, or `pyfixest` skill for authorized computation. This reference guides prose, not implementation certification.
