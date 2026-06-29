---
name: joplin-notes
description: Search, read, list, and safely update the user's local Joplin notebooks and notes through the Joplin desktop SQLite database. Use when the user asks Codex to access Joplin, find a Joplin notebook or note, search note titles or bodies, read a Joplin note, update an existing Joplin note, append a section to a note, or summarize Joplin note contents. This skill is for local Joplin Desktop data, not remote Joplin Cloud unless the local database has already synced.
---

# Joplin Notes

## Core rules

Use the bundled script `scripts/joplin_notes.py` for deterministic database access. Default to read-only operations. Write only when the user explicitly asks to create, update, append, or modify a Joplin note.

Never expose secrets such as Joplin Web Clipper API tokens. This workflow does not need a token because it reads the local SQLite database.

Prefer exact title matching for writes. If a title query matches zero or multiple non-deleted notes, stop and ask the user to disambiguate.

The default Windows Joplin Desktop database path is usually:

```text
$env:USERPROFILE\.config\joplin-desktop\database.sqlite
```

If that file is missing, locate likely profiles before giving up:

```powershell
Get-ChildItem -Path $env:USERPROFILE -Recurse -Force -Filter database.sqlite -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'joplin' }
```

## Common tasks

List notebooks:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" list-notebooks
```

Search note titles and bodies:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" search --query "keyword" --limit 20
```

Read one note by exact title:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" read-title --title "Exact note title"
```

Update one note by exact title from a Markdown file:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" update-title --title "Exact note title" --body-file C:\tmp\updated-note.md
```

Append text from a Markdown file to one note by exact title:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" append-title --title "Exact note title" --body-file C:\tmp\section.md
```

## Workflow

1. For discovery requests, run `list-notebooks`, `recent`, or `search` first.
2. For reading, prefer `read-title` only when the title is exact. Otherwise search first and ask the user to choose among matches.
3. For writing, prepare the new Markdown body or appended section in a workspace or temporary file, then run `update-title` or `append-title`.
4. After writing, verify with `search` or `read-title --metadata-only` and report the updated note title plus timestamp.
5. If Joplin Desktop is open, warn that sync state may update after Joplin notices the database change.

## SQLite details

Important tables:

- `folders`: notebooks. Use `id`, `title`, `parent_id`, `deleted_time`.
- `notes`: notes. Use `id`, `parent_id`, `title`, `body`, `updated_time`, `user_updated_time`, `deleted_time`, `is_conflict`.

Use `deleted_time = 0` for normal visible notebooks and notes.

When writing, update both `updated_time` and `user_updated_time` to current epoch milliseconds.
