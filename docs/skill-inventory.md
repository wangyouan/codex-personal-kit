# Codex Skills Inventory

This repository is the editable source of truth for portable Codex skills, rules, and global memory. Joplin migration notes are read-only mirrors of this document.

## Daily Workflow

On a new computer, clone this repository, run `scripts/install.ps1 -DryRun`, review the proposed actions, and then run `scripts/install.ps1 -Apply`. On an existing computer, first use `git pull --ff-only`.

To capture intentional local changes to managed skills, rules, or global memory, run `scripts/backup-from-codex.ps1 -DryRun`, review the Git diff, and then run it again with `-Apply`. The scripts never commit or push automatically.

## Managed Skills

The repository copies these self-maintained skills into `~/.codex/skills`: `econ-fin-writing`, `format-econ-fin-tables`, `stata-regression-workflow`, `stata-runner`, `xmu-mail`, `systematic-literature-review`, `check-review-alignment`, `get-review-theme`, `guide-updater`, `joplin-notes`, and `build-conference-latex-slides`.

The repository also manages eight NSFC proposal skills: `nsfc-qc`, `nsfc-ref-alignment`, `nsfc-length-aligner`, `nsfc-abstract`, `nsfc-research-content-writer`, `nsfc-research-foundation-writer`, `nsfc-reviewers`, and `nsfc-justification-writer`.

The repository includes three research skills migrated from the local Claude kit: `academic-paper-reviewer`, `theoretical-economics-orchestrator`, and `zotero-librarian`. The theoretical economics skill retains its upstream MIT license and attribution. The reviewer skill is read-only; the Zotero skill reads the database read-only and generates scripts for the user to run inside Zotero.

`econ-fin-writing` is the active academic economics, finance, and accounting writing skill. The old JF writing guide is archived in `archive/jf-writing-style-guide` and is never installed.

`csmar-proxy-download` is a sanitized favorite migrated from the Workbuddy kit. It preserves the authorized CSMAR browser-download workflow and Excel integrity check, but remains in `archive/csmar-proxy-download` because it depends on third-party services, interactive credentials, and changing page selectors. It is never installed automatically.

`format-econ-fin-tables` creates and audits publication-ready regression, descriptive, correlation, variable-definition, difference-test, and robustness tables in LaTeX, editable Word, and Excel. Its core instructions and canonical specification are shared by Claude Code and Codex; the Codex Excel adapter uses the bundled spreadsheet runtime.

## External Skills

`humanizer`, `academic-research-suite`, and the 15 Context Engineering skills are installed from immutable upstream references recorded in `skills-manifest.toml`. They are not copied from one computer to another.

## Local-Only Setup

- Set `STATA_EXE` locally only when `stata-runner` cannot discover Stata automatically.
- Create the XMU mailbox credential locally with `skills/xmu-mail/scripts/xmu-mail.ps1 save-credential`.
- Keep Joplin token and MCP configuration local. Never commit token files or `.env` files.
- Codex authentication, logs, sessions, caches, SQLite databases, and local memories stay on each computer.

## Joplin Mirror

Set `JOPLIN_TOKEN` locally and run `scripts/update-joplin-mirror.ps1 -NoteId <note-id> -Apply` for each migration note. The script only writes this document's body to the selected note; edit this GitHub document instead of editing the mirror.
