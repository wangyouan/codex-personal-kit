# Research package update: 2026-11-23

Scope: the kit's 27 R research packages and their required dependencies,
the isolated PyFixest environment, and Stata's FE/PPML comparison stack.
No audio dependencies, project-specific environments, credentials or
application runtimes were migrated. Existing project lockfiles take priority.

## Python

PyFixest 0.60.0 -> 0.70.0, tested on Windows/Python 3.12.12.
The prior environment is retained for rollback. The new environment also
uses pip 26.3. The skill's direct requirement, resolved lock and IV examples
now target 0.70.0. See the [official changelog](https://pyfixest.org/changelog.html).

Dependency consistency and synthetic FE, clustered covariance, IV, DiD and
output checks passed. The IV example now uses a bracketed endogenous block.
The skill notes changed FE interaction syntax, the new default demeaner,
public result components and the changed `fixef()` return type.
PPML, plotting and bootstrap APIs were not validated in this Python check.

## R

Updated 27 out-of-date packages within the required dependency closure,
using CRAN Windows binaries. Prior package directories were backed up locally.
Direct package versions are in `r-research-packages-2026-11-23.csv`; this is
not a full transitive project lockfile. R remains 4.6.0.

Notable updates: fixest 0.14.1 -> 0.14.2, sandwich 3.1-1 -> 3.1-3,
data.table 1.18.4 -> 1.18.6.1, openxlsx 4.2.8.1 -> 4.2.9.
All 27 direct research packages loaded. FE/IV independent-reference checks
and DiD/RDD synthetic tests passed (DiD 2.020821, RDD 1.970274; true effect 2).
R emitted existing Windows locale warnings but completed the tests.

## Stata

Author sources were installed from fixed commits, with the previous local
ado tree backed up before updating:

| Package | Version | Author repository | Commit |
| --- | --- | --- | --- |
| ftools | 2.50.0 | sergiocorreia/ftools | 7b3663e49ea5c5b81638c55be29edf416e68e8b7 |
| reghdfe | 6.14.1 | sergiocorreia/reghdfe | 29b2b203f534413369d675d0c0f674d61291f536 |
| ppmlhdfe | 2.3.4 | sergiocorreia/ppmlhdfe | b85665d8f674e93c1e07446a9a2b29be7f797910 |
| require | 1.4.0 | sergiocorreia/stata-require | 7ee750b12f9c51ec8a879445cbf39357c308bdee |

The new `require` dependency was installed after the first test correctly
failed for a missing dependency. Stata's downloader failed for one help file;
installation succeeded from the same commit's complete downloaded archive.

Against fereg/feppml 0.6.8, the updated stack passed a 2,000-row synthetic
panel comparison: exact sample agreement; absolute slope/clustered-SE
differences 1.11e-16/3.47e-18 (OLS), 1.11e-15/8.64e-15 (PPML).
This is not a performance benchmark or a certification of other options.
