# Provenance and adaptation

Upstream workflow: [Barrios88/barrios-skills](https://github.com/Barrios88/barrios-skills/tree/d50afc62f4c67535a1949d029dfa0462feb906fd/skills/econometrics/pyfixest), MIT, reviewed at commit `d50afc62f4c67535a1949d029dfa0462feb906fd`.

This kit maintains an adapted skill, so its manifest mode is `vendor` and the upstream repository/path/ref are retained as separate provenance fields. It is not silently refreshed from upstream. Local changes remove unsupported discovery metadata, unavailable sibling-skill links, and generic state-policy/firm-clustering defaults. The instructions and validation script are maintained here.

Official interfaces were checked at [PyFixest](https://pyfixest.org/), including [inference](https://pyfixest.org/reference/estimation.api.feols.feols.html) and [DiD](https://pyfixest.org/difference-in-differences.html). PyFixest itself is separately distributed and licensed; this skill does not vendor the estimator library.

Synthetic validation covers:

- FE slopes against saturated OLS with the same unit/time dummies.
- Unadjusted cluster-sandwich SEs against an independent matrix calculation with the same residuals and clusters.
- FE-IV slopes against an independent 2SLS projection.
- A two-stage DiD call on staggered synthetic adoption with a known constant treatment effect.

Optional PPML, plotting, bootstrap and other methods must be checked when actually used. Validation results and environment versions are recorded in the personal kit's dated review document.
