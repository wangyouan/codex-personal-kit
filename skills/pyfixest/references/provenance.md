# Provenance and adaptation

Upstream workflow: [Barrios88/barrios-skills](https://github.com/Barrios88/barrios-skills/tree/d50afc62f4c67535a1949d029dfa0462feb906fd/skills/econometrics/pyfixest), MIT, reviewed at commit `d50afc62f4c67535a1949d029dfa0462feb906fd`.

This kit maintains an adapted skill, so its manifest mode is `vendor` and the upstream repository/path/ref are retained as separate provenance fields. It is not silently refreshed from upstream. Local changes remove unsupported discovery metadata, unavailable sibling-skill links, and generic state-policy/firm-clustering defaults. The instructions and validation script are maintained here.

Official interfaces were checked at [PyFixest](https://pyfixest.org/), including [inference](https://pyfixest.org/reference/estimation.api.feols.feols.html) and [DiD](https://pyfixest.org/difference-in-differences.html). PyFixest itself is separately distributed and licensed; this skill does not vendor the estimator library.

Synthetic validation covers:

- FE slopes against saturated OLS with the same unit/time dummies.
- Unadjusted cluster-sandwich SEs against an independent matrix calculation with the same residuals and clusters.
- FE-IV slopes against an independent 2SLS projection.
- A two-stage DiD call on staggered synthetic adoption with a known constant treatment effect.

On 2026-11-23, PyFixest 0.70.0 passed these checks under Windows/Python 3.12
with the bracketed IV formula. FE coefficient: 1.4362023069111596; clustered
SE: 0.0403844846306934; IV coefficient: 1.5616390816151482; DiD effect:
1.9957723064596213 (true effect 2). Dependency consistency also passed.
The resolved packages are recorded in `../scripts/requirements-lock.txt`.

Optional PPML, plotting, bootstrap and other methods must be checked when actually used. These small tests do not certify every new feature or replace real-project replication checks.
