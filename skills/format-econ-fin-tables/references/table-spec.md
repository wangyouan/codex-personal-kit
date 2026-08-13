# Canonical Table Specification

Store one table as UTF-8 JSON. The validator and Excel builder accept either one object or an array; the LaTeX/Word builder accepts one table at a time.

## Required top-level fields

```json
{
  "version": 1,
  "table_type": "regression",
  "language": "en",
  "label": "Table 1",
  "title": "Baseline Results",
  "columns": [
    {"key": "m1", "model": "(1)", "label": "Investment", "group": "Full sample"}
  ],
  "rows": [],
  "notes": []
}
```

Allowed table types are `regression`, `descriptive`, `correlation`, `variable_definition`, `difference`, and `robustness`.

## Rows

Every row has `kind`, `label`, and normally `values`, a mapping from column key to a cell.

- `coefficient`: estimate row; add a unique `pair_id`.
- `statistic`: standard error/t/z row; use the same `pair_id` as the preceding coefficient.
- `data`: ordinary numeric or text data.
- `metadata`: controls, fixed effects, observations, fit statistics, or clustering.
- `panel`: a spanning panel heading; omit values.
- `spacer`: a small visual separation; omit values.

A cell may be a number, string, null, or an object:

```json
{"value": -0.0123, "stars": "***", "decimals": 3, "parentheses": false}
```

Use `display` only when the exact display text must be preserved. Keep `value` typed whenever possible.

## Regression inference

Regression specifications require:

```json
"inference": {
  "statistic_type": "standard_error",
  "cluster": "firm",
  "significance": {"*": 0.10, "**": 0.05, "***": 0.01}
}
```

Allowed statistics are `standard_error`, `t_statistic`, and `z_statistic`. Use `cluster: "none"` only when no clustering is intended.

## Optional fields

- `caption_note`: short explanation directly under the title.
- `mode`: `publication` or `working-shell`.
- `purpose` and `expected_result`: working-shell text.
- `multipage`: force a multipage implementation.
- `rows_per_page`: Word segmentation target; keep paired rows together.
- `source`: a source note, not a confidential path.
