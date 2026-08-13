# Author House Style Derived from Prior Manuscripts

Use these patterns only after an explicit journal/template and before the generic defaults.

## Stable patterns to retain

- English tables commonly use Times New Roman around 10 pt, a bold title above the table, model numbers `(1)`, `(2)`, and dependent-variable labels beneath them.
- Regression rows show a coefficient followed by a parenthesized t-statistic or standard error. Controls, fixed effects, clustering, observations, and R-squared appear in a compact metadata block.
- Heterogeneity tables use centered group labels spanning multiple model columns.
- Chinese tables put `表X` and a centered title above the table and a `注：` paragraph below it. Chinese regression tables often use 9–10.5 pt text and Latin variable symbols.
- Descriptive tables generally report N, mean, standard deviation, quartiles/median, and sometimes min/max.
- Excel working shells may include PURPOSE and EXPECTED RESULT explanations above editable cells.

## Defects not to inherit

- Do not reproduce full grids or vertical borders found in some Chinese drafts.
- Do not allow continuation pages to begin without a repeated title/header.
- Do not split a coefficient from its statistic or leave a panel heading at the bottom of a page.
- Do not permit narrow columns to break variable names mid-token, as occurred with long English variable names.
- Do not mix `\hline` and `booktabs` within one LaTeX project.
- Do not use whole-table scaling merely to force a wide table onto one page.
