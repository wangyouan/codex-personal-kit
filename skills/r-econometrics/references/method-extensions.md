# Method extensions

These are implementation routes and design boundaries. Check current package documentation and project dependencies before writing calls. No extension is installed merely because this skill is selected.

## Synthetic control and synthetic DiD

For a small number of treated units, establish donor eligibility, spillovers/contamination, pre-treatment outcome support, treatment timing, and the target effect. Report fit and donor weights. Select placebo/permutation/jackknife or bootstrap inference based on the estimator and number of treated units, not a universal normal interval.

The maintained [synthdid documentation](https://synth-inference.github.io/synthdid/) describes a block-treatment design in which treated units start simultaneously. Validate this before using `panel.matrices()` and `synthdid_estimate()`. Staggered adoption requires a supported extension or a different design; do not relabel a block estimator as staggered SDID.

Classical synthetic control, augmented synthetic control and synthetic DiD answer related but distinct questions. State weighting, identification and inferential assumptions for the actual method. Avoid donor or pre-period selection tuned to the desired post-treatment result.

## Double/debiased machine learning

Use [DoubleML's R API](https://docs.doubleml.org/r/stable/) for supported partially linear, interactive, or IV models. Specify the target (e.g. PLR coefficient versus ATE/ATT), nuisance learners, identification assumptions, overlap, score and folds. Cross-fitting does not eliminate omitted confounding.

Split at the dependence/assignment level when the design requires clustered resampling. Do not randomly split observations from the same firm across training and evaluation folds without addressing leakage. Record fold membership, seed, repeated splits and hyperparameter tuning. Report overlap, nuisance performance and sensitivity as relevant, without treating predictive fit as causal validation.

## Causal forests and heterogeneous effects

Use [grf](https://grf-labs.github.io/grf/) and its supported causal-forest workflow. Identify treatment, confounders, overlap and the target population. Preserve honest estimation and held-out evaluation; avoid choosing subgroups from noisy individual effect predictions and then using ordinary unadjusted significance tests on the same sample.

Distinguish CATE estimates, group-average effects and the overall effect. Record tuning, clustering and inference choices. Strong predictive heterogeneity is not evidence that treatment is unconfounded.

## Further methods

For shift-share, bunching, structural estimation, or specialized event-study models, start from the actual paper's design and an authoritative implementation. The companion `econ-fin-writing` method-narrative module helps articulate their assumptions but is not a substitute for a verified numerical backend. Add a tested module only when a real project requires it, retaining provenance and software versions.
