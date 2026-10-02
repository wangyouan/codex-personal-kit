# Barrios Skills Integration: 2026-10-02

Reviewed collection: [Barrios88/barrios-skills](https://github.com/Barrios88/barrios-skills) at commit `d50afc62f4c67535a1949d029dfa0462feb906fd`. This document records the user's approved selective integration into the personal kit.

## Installed and Updated Skills

| Skill | Change | Migration mode |
|---|---|---|
| pyfixest | Maintained adaptation: explicit design-based covariance, installed-companion routing, provenance and synthetic validation | vendor; immutable upstream provenance in manifest |
| r-econometrics | Newly authored modular FE, IV/2SLS, DiD/event-study, RDD package, with optional-method routing | vendor |
| stata-regression-workflow | Data contract, keys/merges, sample flow, units and winsorization audit | existing vendor |
| econ-fin-writing | Method-specific empirical prose and verified referee comments; preserve latest local journal modules | existing vendor |
| academic-paper-reviewer | Evidence-anchored empirical review reference | existing vendor |

The Barrios R skill was not installed or copied: its reviewed file contained an unrelated HTML/localhost reporting script. The new R skill uses primary implementation documentation and original templates. No external connector or WRDS account was configured in this task.

## Numerical Validation

Python runtime: isolated local environment `~/.codex/runtimes/pyfixest-py`, Python 3.12; PyFixest 0.60.0. The runtime and generated caches are excluded from synchronization. The resolved dependency lock is included with the skill for reproducibility.

The synthetic Python test used 600 observations and passed:

- FE coefficient versus saturated OLS: 1.4362023069.
- Unadjusted cluster covariance versus independent sandwich calculation: SE 0.0403844846.
- FE-IV coefficient versus independent 2SLS projection: 1.5616390816.
- Two-stage DiD recovered 1.9957723065 for a true effect of 2.
- Fitted-model result extraction returned finite inference values.

These checks validate API execution and arithmetic reconciliation on controlled data, not the identification assumptions of a research project. Optional PPML, bootstrap, plotting and other interfaces were not exercised.

Rscript was initially absent. In the follow-up authorized setup on 2026-10-02,
official R 4.6.1 and 27 direct research packages were installed locally. All
requested packages loaded. The synthetic fixture was corrected to index unit
effects by `df$id`, matching `expand.grid` row order, before runtime testing.
The R smoke script passed FE and 2SLS reconciliation against independent
references, group-time DiD (2.020821 for true effect 2), and RDD (2.011586 for
true effect 2). Core versions: fixest 0.14.2, did 2.5.1, rdrobust 4.0.0,
rddensity 3.0. Method-specific dependencies remain the normal analysis scope.

SEC EDGAR was added as a sixth maintained skill in the follow-up. Its MCP 1.1.0
was registered locally using the user's own contact User-Agent. Initialization
and live Apple company/10-K metadata checks passed. Identity and local config
are not included in the kit. See `docs/research-runtime-setup.md` for scope.

All five affected skills passed the skill-creator structure validator and portable-content scan. In an isolated temporary CodexHome, the manifest-driven `-DryRun` created no files and `-Apply` installed all five skills with matching source hashes. These checks did not touch the live Codex configuration or credentials.

## Adoption Decisions

- Keep the current writing entry point. Use journal/language guidance before generic method exposition; ordinary polishing does not trigger an econometric audit.
- Do not prescribe universal winsorization, generic state-policy firm clustering, a universal F > 10 test, or mandatory TWFE plus modern DiD for every project.
- Bind substantive reviewer comments to actual manuscript evidence and label unavailable evidence unverified.
- Record sources, units, timing, sample exclusions, estimator settings, covariance and model IDs so each table is reproducible.
- The adapted PyFixest skill is maintained in this repository. Upstream updates must be reviewed before importing them.

## Reinstallation

Use the manifest-driven installer for the selected entries, then create local runtimes and validate them. A sample preview is:

```powershell
.\scripts\install.ps1 -DryRun -SkillName r-econometrics,pyfixest,stata-regression-workflow,econ-fin-writing,academic-paper-reviewer
```

Apply the reviewed plan with `-Apply`. For numerical dependencies, follow each skill's runtime instructions. Check Git diff before committing or pushing. Existing local-only credentials and unrelated skill edits are outside this integration.
