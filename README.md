# Codex Personal Kit

This repository is the shared source of truth for Codex skills, rules, and durable memory across multiple computers.

It is intentionally not a full copy of `~/.codex`. Runtime state, secrets, auth files, caches, sessions, and SQLite databases should stay local to each machine.

## Layout

```text
skills/              Personal Codex skills that can be synced.
rules/               Personal rules or reusable operating notes.
memories/global/     Shared memory used on every computer.
memories/local/      Machine-local memory templates; real local notes are ignored by Git.
config/              Example config only. Do not commit real secrets.
scripts/             Install and backup helpers.
```

## Memory Model

Use two layers:

1. Global memory: tracked in this repository under `memories/global/`.
2. Local memory: kept on each computer, normally under `~/.codex/memories/local/`.

This avoids Git conflicts in Codex runtime databases while still letting you carry stable knowledge between machines.

## Install On A Computer

From this repository:

```powershell
.\scripts\install.ps1
```

By default, this copies tracked `skills`, `rules`, and `memories/global` into:

```text
$env:USERPROFILE\.codex
```

Use `-DryRun` to preview:

```powershell
.\scripts\install.ps1 -DryRun
```

## Back Up Current Local Skills And Rules

If a computer already has useful personal skills or rules:

```powershell
.\scripts\backup-from-codex.ps1
```

Review the diff before committing:

```powershell
git status
git diff
```

## What Not To Commit

Never commit:

- `auth.json`
- `.sandbox-secrets/`
- `cap_sid`
- `installation_id`
- `logs_*.sqlite*`
- `state_*.sqlite*`
- `memories_*.sqlite*`
- `sessions/`
- `cache/`
- `plugins/cache/`

The `.gitignore` file blocks these by default.
