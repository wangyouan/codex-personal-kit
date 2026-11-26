---
name: auto-mining-did
description: Explore economically justified data-construction and baseline specifications for a DID project, including industry inclusion, observation windows and outcome definitions. Use for DID auto mining, 基准结果探索 or a bounded DID trial with design-appropriate event-study checks, applicable HonestDiD and SA/CS/BJS comparisons when needed. Single-model estimation belongs to the existing econometrics skills.
metadata:
  version: "0.4.0"
---

# DID Auto Mining

An agent-operated workflow: inspect a project, write and run reproducible project-specific scripts with established estimators, and return baseline candidates plus necessary identification checks. This skill does not contain a generic executable regression engine or promise a significant finding.

## Scope and entry

Keep analysis to baseline effects and necessary checks, delivered in declared stages. An initial practice can complete baseline estimation and same-sample event-study/pretrend checks, plus pre-only detrending when requested. Schedule HonestDiD for the declared sensitivity stage/evaluation set; an explicit user deferral stays effective. Mark it `deferred_by_user`, retain its inputs, and finish the current stage without treating the deferral as a statistical failure. Before viewing sensitivity results, specify which targets, source series and restrictions will be evaluated. Do not require advanced checks on every listed Y before showing the initial full comparison. For a single common treatment date with eligible never-treated controls, an appropriate ordinary FE DID and its event study can supply the baseline and diagnostics; SA/CS/BJS are optional comparisons unless the user requests them. For staggered adoption, retain design-appropriate SA/CS/BJS comparisons and distinguish their targets. A prior user waiver remains effective. Matching balance is needed only when matching is used. Do not automatically add mechanisms, subgroup effects, placebo batteries, leave-one-industry-out checks, alternative causal designs or holdout splitting.

Respect the project's existing language. Reuse installed sibling skills when relevant: `r-econometrics` for method/runtime guidance, `stata-regression-workflow` for data construction and Stata analysis, `stata-runner` for execution, and `pyfixest` for supported Python models. Resolve companions from the current skills directory; absence does not prevent planning, but never claim unsupported execution. Tables may use `format-econ-fin-tables` after models are complete.

First infer inputs from the user's named project, scripts and dictionary. Ask together only for indispensable information that is still missing:

- Project/data location and any baseline script.
- Outcome, unit ID, time, real treatment definition/first treatment date and never-treated coding; reversals and anticipation when relevant.
- Assignment/inference unit, target population and ATT/horizon, existing controls/FE, panel vs repeated cross-section.
- Industry variable, coding system/version and grouping; permitted construction choices.
- Existing observation window and any permitted start/end alternatives; source coverage needed for earlier years. The real policy date remains fixed.

Do not invent a policy, industry code mapping, target parameter or instrument. If data are not supplied, provide a usable project brief and proposed trial plan, clearly mark unrun items, and stop before estimation. The user can copy [the trial brief](assets/trial-brief.md); completing every field manually is unnecessary when existing code supplies it.

## Modes and budget

- `plan`: inspect authorized data/code and runtime; write the construction registry and execution plan without fitting outcome models.
- `trial` (default for an initial try): freeze existing measurement, controls, timing and inference; compare the four combinations of financial-sector and utilities inclusion if the mapping and sample support permit. Existing user instructions override these starting dimensions. If industry mapping is unresolved, retain the existing baseline and list the unresolved variants instead of inventing codes. Run necessary checks for every feasible trial candidate.
- `explore`: activate additional justified dimensions from [the search and output contract](references/search-contract.md), within a stated budget. Define which candidates receive full checks before viewing their effects; preserve all other candidates and their status.

Default trial budget: at most four construction candidates, 60 top-level estimation calls and 30 elapsed minutes; report these defaults before running and honor user overrides. Before fitting, count the complete grid of unique construction/window candidates, outcomes, baseline/event fits, requested comparisons and sensitivity calculations. Outcomes and estimators multiply model calls even when they do not create new construction candidates. Package-internal group estimates/bootstrap repetitions are recorded with their settings rather than each counted as a candidate. User-requested scope expansions receive an explicit revised budget and retain the earlier attempt log. Stop launching new work when the budget is reached; report unfinished checks. Never stop at the first significant result or silently expand the grid because no result is significant.

## Practice scope and progression

Separate the main observation window from prehistory and longer-follow-up robustness windows. Follow explicit project dates; otherwise motivate a moderate response horizon from the policy and outcome instead of automatically ending at the latest database year. A later user instruction can revise the window without another permission round: register it as adaptive if earlier results were already viewed. Keep the actual policy year fixed. See [window and stage rules](references/search-contract.md#observation-windows-and-budget).

When the user supplies a Y list, construct, estimate and plot it in batches until every entry has an estimate or a specific documented limitation within the agreed budget. Do not stop after two easy outcomes or the first significant result. Distinguish a promising raw result, a result conditional on detrending, and a data-limited result; do not discard or endorse a candidate just because one diagnostic p-value crosses a threshold. Read [pre-only detrending](references/did-methods.md#事前去趋势与条件性候选) when using it, and [source and execution checks](references/data-execution.md) when constructing many outcomes or combining local databases.

## Execution

When pretrends raise concerns or the user requests adjustment exploration, read [the diagnosis-to-adjustment menu](references/pretrend-adjustments.md). Register a small, reasoned set of routes from the suspected source of differences; do not run every method on every Y or stop when a pretest first becomes insignificant. Keep raw specifications and distinguish conditional DID, weighting, trend extrapolation and alternative identification designs.

1. **Preflight.** Read existing baseline code before generating replacements. Determine common versus staggered timing and the requested method set before checking software/help and packages. Resolve an equivalent established backend when appropriate; report missing dependencies without quietly dropping a required estimator. For R, honor a project library first; otherwise inspect `CODEX_DID_R_LIBRARY` or the optional local library under the resolved Codex home at `runtimes/auto-mining-did-r/library`. On Windows, sandbox-redirection of the user profile/library can hide existing R packages: inspect `.libPaths()` and actual installed user libraries before declaring them absent. Combine compatible runtime/user libraries only for the current process/project. Authorized local package setup may proceed under normal environment permissions, but do not upgrade unrelated packages or change a shared environment merely to run this skill.
2. **Data contract.** Preserve raw inputs. Verify observation unit, keys, merge cardinality, units, time availability, first-adoption coding, comparison-group eligibility, treatment/cohort support and outcome coverage. Reconcile an existing baseline before exploring. When adding totals, components or complementary outcomes, audit source definitions and count identities before transforming them. Record input hashes and ordered sample loss, including estimator-specific loss.
3. **Construction registry.** Read [search-contract.md](references/search-contract.md). Register every candidate, economic/data reason, sample rule, construction order, population/estimand, exact model and inference choices before estimating. Log later changes as adaptive. Correct factual data errors and then fix them; do not keep an erroneous variant as a candidate.
4. **Baseline models.** Fit the declared main outcome/effect for each candidate. TWFE is an appropriate causal baseline only when its design assumptions support that interpretation; a requested legacy TWFE can be reproduced and labeled as a benchmark. Retain finite estimates, failed fits, null and opposite-sign results alike.
5. **Necessary DID checks.** Read [did-methods.md](references/did-methods.md) before method execution. Run the method set declared for the design and user scope. Record optional unrequested comparisons as `not_requested`; reserve `not_applicable` for a method/design mismatch. Align outcomes, treatment, event windows and target aggregation as far as each required method supports, and disclose actual control, sample and weighting differences. Retain event-study coefficients, their joint covariance and valid pretrend joint tests. When HonestDiD is scheduled in the current stage, apply it to one predetermined, correctly adapted series: ordinary FE DID can be the source under common timing; use a suitable SA/CS source for staggered timing. Do not choose the source by its p-value.
6. **Extract and compare.** Retrieve estimates, SEs, CIs and p-values from the fitted object and declared inference. Display main effects and necessary checks together; distinguish changes of population or post-period target from same-estimand specification changes. If the research question compares effects across outcomes, use a formal contrast with their joint clustered covariance; significant versus nonsignificant coefficients alone do not establish a difference. Do not add cross-outcome tests when the question does not require them. Use same-sample diagnostic fits only to resolve a concrete discrepancy, not automatically for all models.
7. **Deliver.** Write the small result bundle below. State completed/failed/unrun/deferred counts and dependencies for the current stage, then explain which construction choices the findings depend on. A completed practice stage is not a claim that deferred robustness or identification work is complete. Optional display filters can highlight nominally significant candidates; retain the complete denominator and exploratory label. Necessary diagnostics do not turn a selected p-value into confirmatory evidence.

## Required result bundle

Use a new project output directory such as `outputs/auto-mining-did/<run_id>/`; never replace prior runs or the user's baseline script. Exact fields are in [search-contract.md](references/search-contract.md).

- `run_manifest.json`, `spec_registry.jsonl`, `sample_flow.csv` and `results.csv`: provenance, candidates, samples and full estimates/status.
- `checks.csv`: declared-method coverage, pretrend diagnostics, HonestDiD applicability/results and explicit unfinished reasons.
- `report.md`: baseline table, estimator comparison, event-study figure(s), HonestDiD figure/table when executed (otherwise its explicit stage/status), concise interpretation and limitations.
- `code/`, `logs/`, `models/`, `figures/`: reproducible scripts, logs, fitted objects/joint covariance and necessary visuals. Include source-variable definitions when construction changes them.

Report separately: nominal effect significance, estimator differences, pretrend evidence and HonestDiD sensitivity. Do not combine them into an invented pass/fail score or require every estimator to be significant. Match algorithms by quality/balance, not the treatment-effect p-value; determine clustering and test direction from the design. No extra multiple-testing exercise is required by default, but disclose the search and never describe its minimum p-value as pre-specified confirmation.
