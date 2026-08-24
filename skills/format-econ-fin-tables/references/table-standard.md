# Economics and Finance Table Standard

## Style precedence

Apply, in order: an explicit journal/template; an established current-project convention that does not violate data integrity; the defaults below. Never copy a visible defect merely because it appears in an old manuscript.

## Table argument and column plan

Before choosing a layout, state the comparison the table is designed to make:
the outcome, observation unit, sample restrictions, model sequence, and what
changes from one column to the next. Every adjacent column should have a clear
reason to exist. Preserve the actual sample by column and make changes in
controls, fixed effects, estimators, weights, or denominators discoverable in a
specification row or note.

If a heterogeneity claim compares groups, report an interaction or equality
test rather than inferring a difference from one coefficient having stars and
another not having stars. In event-study displays, identify the omitted period
and do not treat it as an estimated zero.

## Default visual grammar

- Put the table number and concise title above the table.
- Use three horizontal rules: top rule, rule below the complete header, and bottom rule. Add a light rule between panels only when it aids reading.
- Do not use vertical rules, full cell grids, colored fills, shadows, or alternating bands in publication mode.
- Left-align row labels. Center model columns. Align comparable numbers by decimal point when the target format permits it.
- Use Times New Roman 10 pt for English Word tables by default. For Chinese Word tables, use the manuscript's Chinese body font with Times New Roman for Latin text and numerals, normally 9–10.5 pt.
- Use bold for titles, panel labels, and final header labels only. Use italics for mathematical variable symbols when consistent with the manuscript.
- Prefer portrait for up to four compact model columns and landscape for wider tables. Reduce font size only after tightening spacing and column widths.

## Numeric presentation

- Preserve supplied precision unless a journal or user instruction changes it.
- Within a semantic row, use one precision rule. Typical defaults are three decimals for regression results and two to four decimals for descriptive statistics depending on scale.
- Use a true minus sign only when the renderer and target journal support it consistently; otherwise use ASCII hyphen-minus everywhere.
- Display exact zero consistently as `0.000`, not a mixture of `0`, `.000`, and `0.000`.
- Use thousands separators for observations when the journal permits them. Store observations as integer values in Excel.
- Never add or remove significance stars by looking at rounded numbers. Use supplied p-values or supplied stars.

## Inference and notes

For regression tables, state the estimator/design, dependent variable, statistic shown in parentheses, standard-error correction, clustering level, fixed effects, sample restrictions when non-obvious, and significance thresholds.

Use the conventional note: `*, **, and *** denote significance at the 10%, 5%, and 1% levels, respectively.` Reverse the order only when the target journal does so. Chinese default: `*、**和***分别表示在10%、5%和1%的水平上显著。`

Distinguish standard errors, t-statistics, and z-statistics. Do not label all parenthesized values as standard errors.

## Pagination

- Keep a coefficient row and its statistic row together.
- Repeat all column headers on every continuation page.
- Add `Table X (continued)` or `表X（续）` above every continuation segment.
- Put general notes below the final segment only.
- Avoid single-row panel fragments and orphaned panel headings.
