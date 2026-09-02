# Skill Collection Review: 2026-09-02

Source: `D:/Users/Downloads/Skill收集表.xlsx`. The workbook contains a broad list of public skills and repositories, including many duplicate catalog entries. This note records what was reviewed and what was adopted.

## Adopted

### Stata safeguards

The public `dylantmoore/stata-skill` repository provides a progressive-disclosure Stata reference with coverage of core syntax, data management, econometrics, causal inference, graphics, Mata, and community packages. Its most portable value is the compact set of silent-failure checks: missing-value comparisons, factor-variable notation, `_merge` inspection, `e()` result preservation, `capture` return-code handling, and explicit panel/event-study assumptions.

Those rules were integrated into `skills/stata-regression-workflow/SKILL.md`. The full upstream skill was not copied because the current local Stata skills already own execution and workflow routing, and the upstream C-plugin development material assumes a different development environment.

Source: https://github.com/dylantmoore/stata-skill

### Python panel safeguards

The `python-panel-data` entry from `meleantonio/awesome-econ-ai-stuff` adds a useful reminder to validate entity-time identifiers, set the panel index explicitly, specify fixed effects and clustering, and reconcile Python output with the original Stata sample and estimator. These points were integrated into the same regression workflow skill. The small upstream skill was not installed separately because it would overlap with the existing cross-language reproduction workflow.

Source: https://github.com/meleantonio/awesome-econ-ai-stuff/tree/main/_skills/analysis/python-panel-data

### AERS formatting and empirical prose

The AERS Python workflow is useful as a design reference because it keeps one result object connected to publication outputs and a reproducibility record, while its academic de-AIGC workflow requires an audit-before-rewrite pass, claim-evidence matching, and a final fidelity check. These principles were integrated into `skills/format-econ-fin-tables` and `skills/econ-fin-writing`. The full AERS bundle was not copied because it is large, overlaps with the maintained local skills, and includes optional estimator stacks that are not needed for ordinary table formatting or manuscript polishing.

Sources: https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills and https://github.com/brycewang-stanford/StatsPAI

The local Anaconda `codex` environment now has `StatsPAI==1.23.0` installed alongside the existing pandas, statsmodels, linearmodels, and pyfixest stack. It is available as an optional backend for task-specific testing; the maintained default remains the explicit local estimation and table-building workflow until estimator parity is verified on the actual project data.

## Keep As References

- `quarto` from Posit: high-quality authoring, cross-reference, citation, and R Markdown migration guidance. Keep as a future candidate until a local Quarto/R project exists.
- `stata-c-plugins`: technically valuable for high-performance plugin development, but not a normal Stata analysis workflow and the upstream instructions are development-platform-specific.
- The large `Auto-Empirical-Research-Skills` bundle: promising but large and overlapping, so only its transferable formatting and prose-audit principles were adopted. `StatsPAI` is installed locally as an optional backend and still requires evaluation against a real empirical task before becoming the default estimator path.
- `mcp-for-stata` and `mcp-stata`: integration/tooling candidates rather than ordinary skills; defer until an MCP server is explicitly needed and its permissions are reviewed.

## Not Adopted

The remaining entries are mostly duplicates of the current local skills, generic data-science templates, library documentation rather than agent skills, or broad catalogs whose quality and maintenance would need separate task-based evaluation. No automatic global installation was performed from the spreadsheet.
