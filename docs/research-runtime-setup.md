# Research runtime setup

## R on Windows

Use the [official CRAN Windows installer](https://cran.r-project.org/bin/windows/base/),
not an unrelated bundled R distribution. The reviewed release is R 4.6.1.
The kit's script uses a current-user installation, official checksum validation
and a valid Authenticode signature. It sets local `RSCRIPT_EXE` for skill discovery.

```powershell
.\scripts\install-r.ps1
.\scripts\install-r.ps1 -Apply
```

The script's default is preview-only. It refuses invalid versions, checksum or
signature failures. An existing downloaded installer is reused only after
verification; remove the stale download manually if verification fails.
Older release checksums may move; use CRAN's archive when reinstalling an old
release rather than bypassing verification.

The package installer requests CRAN Windows binaries, installs required
dependencies (not every suggested package), then checks all requested packages
can load. It does not silently compile source packages. The library is local
and version-specific. It leaves unrelated installed packages unchanged.

| Group | Requested packages |
|---|---|
| Data cleaning and Stata/Excel IO | data.table, dplyr, tidyr, readr, haven, readxl, openxlsx, stringr, lubridate, janitor |
| Econometrics | fixest, did, rdrobust, rddensity, ivreg, sandwich, lmtest, plm |
| Plots and paper tables | ggplot2, modelsummary, broom, flextable, officer |
| Reproducibility and APIs | renv, here, jsonlite, httr2 |

These 27 direct packages form a research starter set; transitive dependencies
are installed automatically. They are not every package on CRAN. Install
`grf`, `DoubleML`, `Synth` and `synthdid` only when the design needs them, checking
their official availability and source-build requirements first.
`fwildclusterboot` had no available CRAN Windows binary during this setup and
was excluded from the core set. Install its reviewed upstream separately when
wild-cluster bootstrap is needed; do not silently substitute a different test.

[RStudio](https://docs.posit.co/ide/user/) is an optional editor, not the R runtime.
[Rtools](https://cran.r-project.org/bin/windows/Rtools/) is needed for source
compilation; it is unnecessary when compatible CRAN binaries suffice. Neither
is installed by this script. Use project-level `renv` and commit its lockfile
for exact research replication, not a global package library copied between PCs.

For package-only setup with an already installed R:

```powershell
& $env:RSCRIPT_EXE --vanilla .\scripts\install-r-research-packages.R
& $env:RSCRIPT_EXE --vanilla .\skills\r-econometrics\scripts\smoke_test.R
```

Validation on 2026-10-02: all 27 direct packages loaded under R 4.6.1. FE and
FE-IV coefficients matched independent OLS/2SLS references; DiD recovered
2.020821 and RDD 2.011586 for a true effect of 2. See
`docs/r-research-packages-2026-10-02.csv` for the installed direct versions.
This version inventory is not a complete transitive `renv` lockfile.

The package script accepts an optional CRAN mirror URL and an optional versions
CSV path as positional arguments. If downloads fail, use a trusted CRAN mirror
and retry; do not suppress install/load failures.

## SEC EDGAR

The `sec-edgar` skill installs from this kit. Its separate MCP runtime and
current-user contact User-Agent must be configured on each PC. See
`skills/sec-edgar/references/local-setup.md` for reproducible setup.

On 2026-10-02, sec-edgar-mcp 1.1.0 was installed in an isolated Python 3.12
environment. MCP initialization exposed 21 tools. Live checks inspected Apple
Inc., CIK 0000320193, and 10-K accession 0000320193-25-000079, filed 2025-10-31
for period ending 2025-09-27. This tests startup and submission metadata;
financial-statement extraction and large-scale downloading are not claimed
validated. The source filing index is
[SEC](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/0000320193-25-000079-index.html).

Do not synchronize the actual email/User-Agent, local Codex configuration,
Python/R binaries, package libraries, or downloaded filing caches.
