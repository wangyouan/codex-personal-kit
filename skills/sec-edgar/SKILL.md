---
name: sec-edgar
description: Retrieve and audit public SEC EDGAR filings, XBRL financial facts, and insider Forms 3/4/5 for accounting and finance research. Use for CIK lookup, filing sections and accession-pinned datasets; not as a substitute for WRDS Compustat or CRSP panels.
---

# SEC EDGAR

Prefer the registered `sec-edgar` MCP for live queries. If unavailable in this
session, inspect the local configuration and use the installed Python MCP client;
do not claim that the connection is live merely because the skill is installed.
Read [local setup](references/local-setup.md) when configuring a new computer.

## Retrieval and verification

1. Resolve company name/ticker to CIK. Preserve zero-padded CIK and account for
   ticker reuse; do not join longitudinal data solely on current ticker.
2. Choose form, filing-date range and fiscal period explicitly. Retrieve a small
   sample before a bulk pull. Filing date, acceptance timestamp and economic event
   date are different fields.
3. Inspect company, accession, form, period and at least one relevant section or
   numeric fact. An error payload or empty response is not a successful pull.
4. Record original SEC URLs, access date, query filters and package versions.
   Keep accession identifiers alongside extracted tables for replication.

## Numeric and accounting discipline

- Preserve XBRL taxonomy/tag, units, scale, start/end dates, fiscal period, form
  and accession. Distinguish instant balances from duration flows and annual
  values from quarterly or year-to-date values.
- Avoid counting duplicate/restated facts as distinct observations. State the
  selection rule (originally available at the event date versus latest amended).
- Do not convert monetary values through floats when exact precision matters.
  Compute ratios from inspected facts and retain the formula and input units.
- XBRL is not Compustat. Coverage, standardized definitions and restatements
  differ. Use authorized WRDS data for CRSP/CCM/Compustat panel infrastructure.
- Form 4 reports may describe grants, exercises, sales or open-market purchases;
  classify transaction codes and reporting-person roles before interpretation.

## Access and output

Use the user's own real contact User-Agent, stored locally. Respect SEC fair
access limits (at most 10 requests/second across all processes, preferably lower),
cache duplicate requests locally, and back off on 403/429. Never bypass blocks.
No credentials, identity files, filing caches or local runtimes belong in Git.
Extract requested sections rather than putting entire filings into context.

Return CIK, form/accession, date/period, units, inspected sample and source URL.
Report unverified or inaccessible content explicitly. Use `format-econ-fin-tables`
when requested to produce research tables, and the data audit guidance in
`stata-regression-workflow` for merges and sample-flow checks if available.
