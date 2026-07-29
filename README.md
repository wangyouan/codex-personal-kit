# Codex Personal Kit

This repository is the shared source of truth for portable Codex skills, rules, and durable memory across multiple computers. It deliberately excludes Codex runtime state, authentication, secrets, caches, sessions, and SQLite databases.

## Layout

```text
skills/               Self-maintained skills copied by the installer.
archive/              Recoverable skills that are intentionally not installed.
skills-manifest.toml  Install policy and pinned third-party skill sources.
rules/                Portable rules and operating notes.
memories/global/      Shared, curated memory.
memories/local/       Ignored templates for machine-local notes.
docs/                 Human-readable inventory used for the Joplin mirror.
scripts/              Install, export, validation, and mirror helpers.
```

## Install On A Computer

Clone this repository to a stable local path. Preview first, then write only after review:

```powershell
.\scripts\install.ps1 -DryRun
.\scripts\install.ps1 -Apply
```

Use `-Apply -RefreshExternal` only when deliberately reinstalling a pinned external skill. The installer copies only manifest-declared managed skills and never deletes unknown local skills.

## Capture Local Changes

Export only allowlisted managed skills, rules, and global memory. The export script checks for secrets, credentials, local caches, databases, and hard-coded user paths before copying:

```powershell
.\scripts\backup-from-codex.ps1 -DryRun
.\scripts\backup-from-codex.ps1 -Apply
git status
git diff
```

Review and commit intentionally. The scripts never commit or push automatically.

## Memory Model

Track durable cross-computer knowledge under `memories/global/`. Keep machine-specific notes under `~/.codex/memories/local/`, which Git ignores. Use `docs/skill-inventory.md` as the source for Joplin migration-note mirrors.

## What Not To Commit

Never commit credentials, auth files, `.env` files, tokens, SQLite databases, logs, session data, caches, or local tool configuration. The `.gitignore` file blocks the common cases, but review every diff before pushing.
