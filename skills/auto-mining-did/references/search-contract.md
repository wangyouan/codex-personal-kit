# Search dimensions and output contract

## Candidate registry

Start from existing code. Each candidate needs a stable `spec_id`, `parent_spec_id`, `reason`, `created_at`, `adaptive`, `population_id`, `estimand_id`, complete construction rules, baseline model, inference, required checks and status. Store exact code/options or an immutable script hash; a label such as "winsorized" is insufficient.

Dimensions are a menu, not a mandatory checklist:

| Block | Potential choices | Required distinction |
|---|---|---|
| Industry | Financial, utilities and other justified groups: include/exclude/vary | Taxonomy/version, code mapping, treatment-preceding vs contemporaneous classification, missing codes, overlaps |
| Measurement | Consolidated vs parent financials; numerator/denominator, deflator, levels/logs | Which economic object is measured; zero/negative handling; contemporaneous denominators may be affected by treatment |
| Timing | Fiscal/calendar alignment, partial/full exposure year, justified response lag | Actual treatment date stays factual; missing calendar periods are not previous rows |
| Observation window | Declared start-year and end-year lists with a limited set of justified pairs | Keep the policy date fixed; preperiod support, response horizons, sample composition and target post-period average change with the window |
| Sample | Baseline eligibility, IPO comparability, minimum prehistory, panel coverage | Avoid selecting on post-treatment survival, ST status, losses or outcome availability without addressing selection |
| Outliers | Justified thresholds, winsor/trim, threshold reference population and order | Changing values vs dropping observations; annual/industry-year groups and small-cell support |
| Entity linkage | IDs, normalized historical names, geographic/time restrictions, ambiguity | Validate identities independently of effect estimates; retain failed/ambiguous links |
| Causal matching | Distance/exact constraints, caliper, ratio, replacement, overlap | Pre-treatment timing, balance, retained treated units, weights and dependence induced by reused controls |
| Controls and FE | Small theory-based groups, appropriate timing and FE combinations | Post-treatment controls can remain post-treatment when lagged; avoid absorbing assignment variation |
| Missingness/weights | Complete-case vs defined common sample; justified baseline weights | Zero is not missing; weighting or dropping treated can change the target population |

Industry trial grid: with valid disjoint financial and utilities definitions, generate all four inclusion combinations, leaving other industries at baseline eligibility. Preserve overlapping group semantics or split into mutually exclusive groups before enumerating. Never assume SIC codes apply to NAICS, GICS or Chinese industry classifications. Record retained treated units, controls, cohorts and assignment clusters for every combination, not just total N. Unknown mapping means an unresolved candidate, not an invented filter.

Keep grouping/measurement facts separate from discretionary definitions. Match valid data, fix verified errors and deduplicate equivalent configurations before fitting. Pure linear rescaling on an identical sample/model/inference is not a new significance-search dimension; nonlinear transformations may change the estimand. Larger grids use predeclared blocks and a few justified interactions, not an unconstrained Cartesian product.

### Observation windows and budget

Declare allowed start/end years and their rationale before viewing their effects. Cross only the requested window pairs with industry/sample choices and outcomes. A static DID needs supported untreated and treated periods; an event-study pretrend test needs at least one nonnormalized preperiod coefficient in addition to its reference period. One such coefficient is a single-lead test with weak information, not a rich joint pretrend assessment. Record the number of preperiods, postperiods, supported units and assignment clusters for each candidate; label insufficient support instead of shortening a window after seeing its p-value. Default to retaining the existing prehistory when available, and motivate end dates by exposure or response horizons. Record `window_role` (`main`, `longer_followup`, `longer_prehistory`, or `coverage_limited`) separately from start/end years. Available data through a recent year do not make that year the preferred endpoint. Longer follow-up may include different macroeconomic conditions, later policies and changing composition; explain these concerns without adding an automatic battery of extra tests.

For a small practice, use the user's chosen main window first and reserve longer endpoints for later robustness. For example, a user may choose 2014–2020 for a 2017 policy with 2016 as reference, then request follow-up through 2021/2024 and longer prehistory separately. This is an illustration, not a universal date rule or evidence that those shorter-window regressions have been run. Do not silently create a full start-year × end-year grid. If the change follows inspection of an earlier long-window result, retain that result and record the new window's actual decision time and adaptive status.

Truncating follow-up changes the post-period target and can change the FE estimate/sample. Refit the baseline and event study on each window's identical rows and controls; do not just crop an existing figure. Reestimate a sample-specific first-stage pretrend if its input rows change. Distinguish actual coverage restrictions from discretionary window choices; when only a static model or partial event path is identified, report that estimable part and its missing diagnostics rather than inventing unsupported periods.

Earlier years can be added only after locating and auditing actual outcome, controls and treatment data with compatible definitions. A wide patent file alone does not establish a complete earlier analysis panel. Never generate earlier observations, carry controls backward or fill missing outcomes with zero merely to create additional preperiods. Distinguish a documented zero from a failed match or absent coverage.

Give each complete model a key including candidate, outcome, estimator, term/target and inference settings. Deduplicate only after verifying equivalent estimating observations, outcome/control/weight contents, design and target; identical sample hashes alone do not prove equivalent models. Preserve all four industry labels as aliases if absent sectors make some samples identical. The declared call budget includes baseline and event fits per outcome, scheduled applicable HonestDiD calculations and requested cross-outcome contrasts. Numerical retries consume calls too; loading a verified cached result does not.

### Totals, components and complementary outcomes

Before constructing an aggregate or complement, align source universe, unit/entity scope, ownership treatment, calendar basis, count type, category coverage and duplicate handling. For patent data, application versus grant, parent versus consolidated group, and invention/utility/design coverage are substantive definitions. Retain source files, original field names, key/merge counts and the calculation in the project audit.

Add counts before nonlinear transformation: `log1p(A + B)` is not `log1p(A) + log1p(B)`. A complement such as nongreen patents may be `all patents - green patents` only when the two counts share a documented universe and green is a subset. Verify count identities, nonnegativity and missingness; investigate negative complements or inconsistent totals instead of clipping them to zero. An unmatched raw-source row is not automatically a zero. Retain original components to make every transformed outcome traceable.

If the question is whether treatment affects one component more than another, test the coefficient difference on a comparable sample with the cross-outcome covariance. For linear OLS with identical rows, regressors, weights and FE, fitting the outcome difference is an equivalent way to estimate the contrast and its clustered uncertainty. Stacked models or jointly retained score covariances are alternatives. State whether the contrast compares counts, transformed outcomes or shares; a difference in log1p effects alone does not establish a reallocation of raw totals. Do not infer a difference from one p-value below a threshold and another above it, or infer equality from a nonsignificant contrast. These tests are required only when the research question requests the comparison.

## Model comparability

Store construction-candidate ID separately from estimator/model ID. Preserve each estimator's actual observations, cohorts, event-time support and weights. A fixed input data frame does not ensure identical estimation samples or aggregation. Cross-language data exchange must preserve ID precision, dates, missing/never-treated values and numeric types.

`sample_hash` is a hash of stable IDs of actual estimating observations, not a hash of the input file. Record separate content hashes for weights, matching relationships and transformed variables. DID methods can use different comparison units across group-times: save group-time support and aggregation weights when applicable, not only a pooled sample hash.

## Output schema

Use UTF-8 JSON/JSONL and CSV. Save valid zeros as zeros and unavailable values as null/blank, with reason columns. Save scripts in project-relative paths; no research data or credentials enter the skill repository.

`run_manifest.json`:

- `run_id`, mode, start/end, software/package versions, input/code hashes, seed, actual protocol, budget and stop reason.
- Counts of planned, attempted, completed, failed and unrun construction candidates/model calls; list incomplete necessary checks.

`spec_registry.jsonl`:

- One full candidate definition per record, with version/parent relationships for changes. Include `dimensions`, economic rationale, `adaptive`, exact model, window start/end, outcome construction and target post-period aggregation, industry map and timing, covariance/test direction, required checks, `analysis_stage`, per-check schedule, `window_role`, and evaluation-set rule.
- Do not overwrite earlier definitions or reuse a `spec_id` for a different specification.

`sample_flow.csv`:

- `spec_id, model_id, step, restriction, rows_before, rows_removed, rows_after, units_after, treated_units_after, clusters_after, reason`.
- Account for merges, data rules, missingness and estimator losses; counts of group-time support can live in a separate support file linked to the model.

`results.csv` (long format):

- `run_id, spec_id, model_id, estimator, population_id, estimand_id, term, event_time, estimate, se, ci_low, ci_high, p_raw, inference_method, interval_type, n_obs, n_units, n_clusters, sample_hash, weights_hash, status, reason`.
- Retain baseline coefficients, target aggregate ATT and dynamic effects as distinct terms. Label pointwise vs simultaneous intervals and the associated test; do not infer a p-value from a different type of interval.
- Keep failed/unrun model rows, without fabricated numeric values. `p_adjusted` or confirmatory fields are optional and only populated when an applicable protocol was actually executed.

`checks.csv`:

- `spec_id, model_id, check, status, statistic, p_value, parameter, lower, upper, reason, artifact`.
- Status values: `planned`, `awaiting_input`, `completed`, `not_requested`, `not_applicable`, `missing_dependency`, `insufficient_support`, `failed`, `interrupted`, `not_run_budget`, `deferred_by_user`. Use `planned` before an available run and `awaiting_input` for unresolved data/semantics; neither means budget exhaustion. `not_requested` marks an optional comparison outside the chosen scope, not a statistical failure. Keep user-interrupted attempts distinct from completed fits or exhausted budgets. `deferred_by_user` records an explicit postponement, its scope and the future stage; do not relabel it as method inapplicability or a failed test. `completed` means executed, not "identification proved".
- HonestDiD rows include restriction, sensitivity parameter, target `l_vec`, source model and interval; do not represent its sensitivity curve as a pretrend p-value. Retain exact computational settings in a linked JSON/model object.

`report.md`:

1. Actual scope, baseline definitions and construction candidates; how many were attempted and evaluated fully.
2. Baseline effect table and the declared estimator comparisons, with sample, window, aggregation differences and unfinished statuses visible.
3. Event-study plot and valid pretrend joint test; single-source HonestDiD sensitivity when scheduled and executed, with target and restriction stated; otherwise the explicit deferral/status.
4. Which choices change the result, economic magnitude and identification limits. Keep exploratory candidates labeled; no extra mechanism, subgroup or placebo sections.

Full logs and candidate rows remain available even if the front-page table focuses on a subset. A budget limit or unavailable required estimator is a documented incomplete check, not permission to declare the full trial successful. Explicitly postponed checks do not block delivery of the agreed initial stage. Report numeric economic magnitude and direction, policy-preperiod movement, and postperiod persistence for each feasible Y. Show significant positive and negative years even when their direction differs from the static coefficient; do not hide a dynamic signal by filtering to the static sign. A first statistically significant year is not proof of the true onset date. If the user asks whether one year drives the effect, distinguish descriptive leave-one-event-point averages from actual leave-one-year-out refits; reserve extra fits for the requested candidates instead of expanding every model by default.
