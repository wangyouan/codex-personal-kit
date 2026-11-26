# Codex Skills Inventory

This repository is the editable source of truth for portable Codex skills, rules, and global memory. Joplin migration notes are read-only mirrors of this document.

## Daily Workflow

On a new computer, clone this repository, run `scripts/install.ps1 -DryRun`, review the proposed actions, and then run `scripts/install.ps1 -Apply`. On an existing computer, first use `git pull --ff-only`.

To capture intentional local changes to managed skills, rules, or global memory, run `scripts/backup-from-codex.ps1 -DryRun`, review the Git diff, and then run it again with `-Apply`. The scripts never commit or push automatically.

## Consolidated Entry Points (2026-11-26)

- Use `stata-regression-workflow` for Stata estimation and execution. `stata-runner` is an explicit-only compatibility alias; its old script path forwards to the canonical runner.
- Use `systematic-literature-review` in `scope`, `review`, or `alignment` mode. `get-review-theme` and `check-review-alignment` are explicit-only compatibility aliases. Citation backend scripts/config remain at their stable old paths; instructions are maintained in the review references.
- Use `theoretical-economics-orchestrator` for theory work. The old unmanaged `pAI-Econ-claude` installation is archived outside the active skills directory on this computer, including its research outputs; those outputs are not part of this repository.
- Compatibility packages remain vendor-managed to preserve old project calls. This is entrypoint consolidation, not removal of the underlying tools.

## Managed Skills

The repository copies these self-maintained skills into `~/.codex/skills`: `econ-fin-writing`, `format-econ-fin-tables`, `stata-regression-workflow`, `stata-runner`, `r-econometrics`, `pyfixest`, `xmu-mail`, `systematic-literature-review`, `check-review-alignment`, `get-review-theme`, `guide-updater`, `joplin-notes`, and `build-conference-latex-slides`.

The repository also manages eight NSFC proposal skills: `nsfc-qc`, `nsfc-ref-alignment`, `nsfc-length-aligner`, `nsfc-abstract`, `nsfc-research-content-writer`, `nsfc-research-foundation-writer`, `nsfc-reviewers`, and `nsfc-justification-writer`.

`auto-mining-did` is an agent-operated workflow for bounded baseline-specification exploration, including industry inclusion, observation start/end windows and outcome definitions. It selects necessary methods for common versus staggered adoption, retains event-study/pretrend evidence and applicable HonestDiD, and runs SA/CS/BJS comparisons when the design or user scope calls for them. Requested component/complement comparisons use compatible source definitions and joint inference. It uses project-specific scripts and established econometric implementations; no standalone regression engine, research dataset or runtime is bundled. Start with `skills/auto-mining-did/assets/trial-brief.md` and verify dependencies on the target computer.

`audio-transcribe-archive` transcribes local recordings with faster-whisper, preserves timestamped transcripts and source hashes, and supports task-authorized archival and proofreading. Each computer needs a compatible Python 3.12 environment, audio dependencies and a local model; GPU use also needs matching CUDA libraries. Use `CODEX_AUDIO_PYTHON`, `--libs` and `--model` for local configuration. Recordings, transcripts, personal case details, model weights and runtime dependencies are not synchronized with the skill.

`amdserver-access` records the user's AMD intranet server connection workflow, verified research-data locations, and project runtime navigation. It uses existing SSH access and includes checks for the expected hostname, transfer destinations, and task authorization. Each computer needs its own authorized private-network route and SSH authentication; the skill does not contain or synchronize keys or credentials. Recorded paths and verification dates are navigation aids and must be rechecked before use.

The repository includes three research skills migrated from the local Claude kit: `academic-paper-reviewer`, `theoretical-economics-orchestrator`, and `zotero-librarian`. The theoretical economics skill retains its upstream MIT license and attribution. The reviewer skill is read-only; the Zotero skill reads the database read-only and generates scripts for the user to run inside Zotero.

`econ-fin-writing` is the active academic economics, finance, and accounting writing skill. The old JF writing guide is archived in `archive/jf-writing-style-guide` and is never installed.

`csmar-proxy-download` is a sanitized favorite migrated from the Workbuddy kit. It preserves the authorized CSMAR browser-download workflow and Excel integrity check, but remains in `archive/csmar-proxy-download` because it depends on third-party services, interactive credentials, and changing page selectors. It is never installed automatically.

`format-econ-fin-tables` creates and audits publication-ready regression, descriptive, correlation, variable-definition, difference-test, and robustness tables in LaTeX, editable Word, and Excel. Its core instructions and canonical specification are shared by Claude Code and Codex; the Codex Excel adapter uses the bundled spreadsheet runtime.

The 2026-09-02 external skill review is recorded in `docs/skill-review-2026-09-02.md`. It selectively incorporated Stata silent-failure checks and Python panel-data safeguards into `skills/stata-regression-workflow`, and added AERS-inspired Python result provenance and empirical prose-audit rules to the table and writing skills. `StatsPAI==1.23.0` is installed in the local Anaconda `codex` environment as an optional backend.

## External Skills

`humanizer`, `academic-research-suite`, and the 15 Context Engineering skills are installed from immutable upstream references recorded in `skills-manifest.toml`. They are not copied from one computer to another.

## Empirical Methods and Barrios Integration

The 2026-10-02 integration is documented in `docs/skill-review-2026-10-02.md`. `r-econometrics` is a newly authored methods package with FE/inference, IV/2SLS, staggered DiD/event-study, and sharp/fuzzy RDD modules, plus implementation routes for synthetic control/SDID, DML and causal forests. It uses established R packages. R 4.6.1 and 27 direct research packages were subsequently installed locally on this computer; core FE/IV/DiD/RDD synthetic tests passed. R itself and package libraries are not synchronized.

`pyfixest` is an audited, maintained adaptation of the Barrios skill, with its MIT notice and immutable upstream provenance. It uses `vendor` mode because inference guidance and companion-skill links were adapted for this kit. Its Python library is installed separately in an isolated local environment. The direct package version is pinned in `scripts/requirements-pyfixest.txt`; the tested Windows/Python 3.12 dependency set is recorded in `scripts/requirements-lock.txt`. Set `CODEX_PYFIXEST_PYTHON` locally or discover the environment under `~/.codex/runtimes/pyfixest-py`; never sync the runtime directory.

`stata-regression-workflow` now includes a data-construction audit: key/cardinality checks, merge diagnostics, missingness, variable units/timing, winsorization provenance and ordered sample flow. `econ-fin-writing` adds method-specific narrative and verified referee comments. `academic-paper-reviewer` uses evidence-anchored empirical comments without changing its existing review modes. The writing skill retains this computer's latest Chinese journal modules.

## Local-Only Setup

R installation and the 27-package research starter set are maintained in
`scripts/install-r.ps1` and `scripts/install-r-research-packages.R`. Setup,
dependency scope and verification are documented in `docs/research-runtime-setup.md`.

`sec-edgar` is an MIT-attributed maintained Barrios adaptation for public SEC
filings and XBRL research. Its separate AGPL-3.0 MCP runtime is local-only;
the manifest declares the dependency and local identity configuration. Startup
and live Apple company/10-K metadata checks passed on 2026-10-02. Restart Codex
after registering the MCP if tools are not yet visible in the current session.

- Set `STATA_EXE` locally only when `stata-runner` cannot discover Stata automatically.
- Detect Rscript or set `RSCRIPT_EXE` locally for R methods; keep project `renv` libraries local.
- Recreate the isolated PyFixest environment and run its synthetic checks; the skill files alone do not install Python packages.
- Create the XMU mailbox credential locally with `skills/xmu-mail/scripts/xmu-mail.ps1 save-credential`.
- Keep Joplin token and MCP configuration local. Never commit token files or `.env` files.
- Codex authentication, logs, sessions, caches, SQLite databases, and local memories stay on each computer.

## Joplin Mirror

Set `JOPLIN_TOKEN` locally and run `scripts/update-joplin-mirror.ps1 -NoteId <note-id> -Apply` for each migration note. The script only writes this document's body to the selected note; edit this GitHub document instead of editing the mirror.
