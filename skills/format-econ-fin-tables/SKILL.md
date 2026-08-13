---
name: format-econ-fin-tables
description: Create, reformat, convert, and audit publication-ready tables for economics, finance, accounting, and Chinese economics/management manuscripts. Use for regression tables, descriptive statistics, correlation matrices, variable definitions, balance or difference tests, and robustness, heterogeneity, or subsample tables; for pasted results, CSV/XLSX, Stata/R exports, or existing .tex, .docx, and .xlsx tables; and when the requested output is LaTeX, editable Word, or Excel. Enforce journal-style three-line tables, inference disclosure, numeric consistency, and safe multipage layout without changing empirical results.
---

# Format Econ-Fin Tables

Produce publication-facing tables without changing the underlying evidence. Treat this skill as the formatting and consistency layer after estimation; do not run regressions here.

This is a shared Agent Skill for Claude Code and Codex at the instruction, canonical-specification, LaTeX, and Word layers. Codex may additionally use `agents/openai.yaml` and the `@oai/artifact-tool` Excel adapter; other clients may ignore or replace those Codex-specific surfaces.

## Non-negotiable rules

1. Preserve every supplied coefficient, statistic, sign, star, sample size, model label, and variable meaning. Never infer a missing result.
2. Ask before proceeding when the statistic under coefficients, clustering level, significance convention, dependent variable, or column mapping is materially ambiguous.
3. Apply style precedence in this order: explicit journal/template, current project style, then the bundled default standard.
4. Default to a three-line table with no vertical rules or cell grid. Use a different rule only when an explicit journal template requires it.
5. Keep each coefficient with its standard error, t-statistic, or z-statistic. Never split the pair across pages.
6. Do not overwrite an input file. Write a new, clearly named output unless the user explicitly authorizes replacement.
7. Generate only the requested format. If no format is named, infer the working format from the manuscript and state the assumption.
8. Keep real manuscripts and confidential results out of this skill repository. Use synthetic examples only.

## Route the task

1. Identify one of the six supported table types. Read [table-types.md](references/table-types.md).
2. Read [table-standard.md](references/table-standard.md) for the shared publication rules.
3. If a project or journal template exists, inspect it before formatting. Read [house-style.md](references/house-style.md) when matching the author's recurring style.
4. Normalize the content to the canonical structure in [table-spec.md](references/table-spec.md). Use `scripts/validate_spec.py` before generation.
5. Read only the requested format section in [formats.md](references/formats.md), then generate and verify the artifact.

## Accept inputs

- Parse pasted model output, CSV/XLSX, Stata `esttab`/`outreg2`, R `modelsummary`/`fixest`, or an existing table.
- Retain original precision unless the user or journal specifies a new display precision.
- Convert raw factor-variable names into publication labels only when the mapping is unambiguous; retain the raw name in a warning otherwise.
- Separate table content from presentation by building a JSON table specification. Use `assets/examples/` as synthetic patterns, never as empirical defaults.
- When converting among formats, reuse one normalized specification so that all outputs share the same values and notes.

## Generate outputs

### LaTeX

Run `scripts/build_table.py SPEC --format latex --output OUTPUT.tex`. Use `booktabs`; use `longtable` for multipage tables; do not use vertical rules or whole-table scaling. Include required packages and keep coefficient/statistic pairs together.

### Word

Run `scripts/build_table.py SPEC --format word --output OUTPUT.docx`. Produce a native editable table with fixed geometry. For long tables, create deterministic page-sized segments with `Table X (continued)` or `表X（续）`, repeated headers, and notes on the final segment only.

Render every final DOCX using the installed document-rendering workflow. Inspect every page for clipped text, unwanted gridlines, broken pairs, missing repeated headers, and bad page breaks.

### Excel

Use `scripts/build_xlsx.mjs` through the Codex spreadsheet artifact-tool runtime. Copy the builder into a writable temporary directory that has a `node_modules` junction to the bundled dependency path; do not vendor dependencies into this skill.

- `publication` mode: hide gridlines; use title, panel headers, three-line borders, typed numbers, and notes.
- `working-shell` mode: add `PURPOSE` and `EXPECTED RESULT` rows and highlight editable placeholders while retaining publication-table structure.

Inspect key ranges, scan formula errors, render every sheet, and export the final workbook only after the visual pass.

## Audit before delivery

Run `scripts/audit_spec.py SPEC` and resolve all errors. After generating LaTeX or Word, run `scripts/audit_output.py OUTPUT`. Treat warnings as issues to review, not automatic failures.

Check that:

- table title, model numbers, dependent variables, panels, and row labels are present;
- the statistic type and clustering level are disclosed for regression tables;
- stars and the significance note agree;
- numeric precision is consistent within a semantic row;
- observations are counts, not decimal strings;
- fixed effects, controls, clustering, and fit statistics use stable labels;
- long variable names are widened, abbreviated with a definition, or wrapped at word boundaries rather than split mid-token;
- multipage outputs repeat headers and show a continuation label;
- notes appear only once, after the final table segment.

## Boundaries and collaboration

- Use `stata-regression-workflow` to run or reproduce models. Return here only after results are fixed.
- Use `econ-fin-writing` to revise prose that discusses a table; do not let prose editing change table values.
- Use the platform document and spreadsheet skills for native file creation and visual verification.
- Keep the core instructions, JSON schema, and LaTeX/Word paths platform-neutral. Isolate Codex-specific UI metadata under `agents/` and the Codex Excel adapter in `scripts/build_xlsx.mjs`.
