# Format-specific Rules

## LaTeX

- Load `booktabs`, `array`, and `threeparttable`; load `longtable` and `threeparttablex` for multipage tables.
- Use `\toprule`, `\midrule`, and `\bottomrule`. Never put `|` in a column specification.
- Use `tabular*` or width-aware columns before considering smaller type. Avoid `\resizebox` and `\scalebox` for complete tables.
- Use `\\*` or `\nopagebreak` between a coefficient and its statistic row.
- In long tables, define `\endfirsthead`, `\endhead`, `\endfoot`, and `\endlastfoot`; repeat the header and add a continuation caption.
- Escape text safely while preserving intentional math/LaTeX supplied in explicit LaTeX fields.

## Word

- Create native tables with `autofit = false`, explicit table width, `tblGrid`, and explicit cell widths.
- Set table indentation to zero and cell margins consistently.
- Remove all default borders, then add only the top, header-bottom, optional panel, and final bottom borders.
- Set header rows to repeat and prevent important rows from splitting. Pair coefficient and statistic paragraphs with keep-with-next rules.
- Segment long tables before a logical pair rather than relying on renderer pagination. Add a continuation title to later segments.
- Place notes as paragraphs after the final segment, not inside every page fragment.

## Excel

- Author with `@oai/artifact-tool`; keep numbers typed and use Excel number formats.
- Hide worksheet gridlines in publication mode.
- Merge title, panel, purpose, expected-result, and note rows across the table width.
- Apply only top, header-bottom, optional panel, and final bottom borders in publication mode.
- Set a print area, repeat header rows where supported, use landscape for wide tables, and fit to one page wide without shrinking text into illegibility.
- In working-shell mode only, use a light yellow fill for editable result cells and retain explanatory rows above the table.
