# Runtime and sources

## Dependency scope

| Module | R packages |
|---|---|
| FE/PPML and FE-IV | fixest |
| Conventional IV and covariance diagnostics | ivreg, sandwich, lmtest |
| Group-time DiD | did; fixest for Sun-Abraham |
| RDD and density | rdrobust, rddensity |
| Optional extensions | synthdid, DoubleML, grf, as actually needed |

Use a project's existing package versions first. For a new project, prefer an isolated `renv` library and record the resolved versions in its lockfile. Install only the dependencies required by the authorized analysis. Skill installation does not install R itself.

Run `scripts/smoke_test.R` under an identified `Rscript --vanilla`. It uses synthetic inputs to compare FE and 2SLS against independent linear-algebra references and to exercise group-time DiD and local-polynomial RD. A passed smoke test checks package interoperability, not identification in a real study.

## Validated Environment: 2026-11-23

Windows R 4.6.0: fixest 0.14.2, did 2.5.1, rdrobust 4.1.2,
rddensity 3.0, sandwich 3.1-3, ivreg 0.6-8 and renv 1.3.1.
The FE/IV/DiD/RDD synthetic suite passed after updating the research
dependencies from CRAN Windows binaries. This is a tested snapshot, not
a claim that these versions remain the newest or a project lockfile.

When authorized to update, back up the affected library directories and
compare package versions, not just build timestamps. Install in a fresh R
process without first loading the DLLs being replaced; a loaded package can
prevent Windows from replacing its DLL. Validate in another fresh process.
Keep project `renv` libraries and exact-replication versions unchanged unless
their migration is explicitly requested.

## Provenance

This self-maintained skill was created on 2026-10-02 after reviewing [Barrios r-econometrics](https://github.com/Barrios88/barrios-skills/tree/d50afc62f4c67535a1949d029dfa0462feb906fd/skills/econometrics/r-econometrics) and the collection's related workflows. The reviewed R skill had an unrelated HTML script block; its file was not installed or copied. Templates here are original and use public package APIs.

Primary references checked during creation:

- [fixest walkthrough](https://lrberge.github.io/fixest/articles/fixest_walkthrough.html) and [sunab](https://lrberge.github.io/fixest/reference/sunab.html)
- [ivreg diagnostics](https://zeileis.github.io/ivreg/articles/ivreg.html)
- [did documentation](https://bcallaway11.github.io/did/articles/did-basics.html)
- [RD Packages](https://rdpackages.github.io/)
- [synthdid](https://synth-inference.github.io/synthdid/)
- [DoubleML](https://docs.doubleml.org/stable/index.html) and [grf](https://grf-labs.github.io/grf/)

Consult installed help and current official docs at use time for version-sensitive interfaces. Do not store credentials, datasets, sessions or machine-specific paths in this skill.
