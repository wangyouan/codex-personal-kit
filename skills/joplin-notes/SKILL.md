---
name: joplin-notes
description: Access, search, read, organize, create, append to, and safely update the user's local Joplin notebooks and notes through the Joplin Web Clipper API, with a SQLite fallback for local Joplin Desktop data. Use when the user asks Codex to access Joplin, manage Joplin notebooks, search note titles or bodies, read a Joplin note, summarize notes, add content from another thread into Joplin, create a note, update an existing note, append a section, or export/organize local Joplin content.
---

# Joplin Notes

## Core Rules

Use `scripts/joplin_notes.py` for deterministic access. Prefer the Joplin Web Clipper API on `127.0.0.1` because it respects Joplin's normal data model and avoids direct database edits.

Default to read-only operations. Write only when the user explicitly asks to create, update, append, or otherwise modify a note.

Never expose the Joplin API token in final answers, logs, generated files, or note content. Accept a token only from the current user message, `--token`, `JOPLIN_TOKEN`, `JOPLIN_API_TOKEN`, or the local Joplin profile `settings.json`.

When adding mathematical formulas to Joplin notes, use dollar-delimited math syntax. Use inline formulas as `$...$` and display formulas as `$$...$$`; do not use `\(...\)` or `\[...\]` unless the user explicitly asks for that style.

Prefer exact title matching for writes. If a title query matches zero or multiple notes or notebooks, stop and ask the user to disambiguate.

Use SQLite only as a fallback when the Web Clipper API is unavailable, or when the user explicitly asks for database-level inspection. For SQLite writes, warn that Joplin Desktop may need to notice the change before sync state settles.

## Connection

Expected local API:

```text
http://127.0.0.1:41184
```

If the port differs, scan `41184..41194` by calling `/ping`; the bundled script does this automatically.

Useful environment variables:

```powershell
$env:JOPLIN_TOKEN = "<token>"
$env:JOPLIN_PORT = "41184"
```

The default Windows Joplin profile is:

```text
$env:USERPROFILE\.config\joplin-desktop
```

## Common Commands

List notebooks:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" list-notebooks
```

Search note titles and bodies:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" search --query "keyword" --limit 20
```

Show recent notes:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" recent --limit 20
```

Read one note by exact title:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" read-title --title "Exact note title"
```

Create a note in an exact notebook:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" create-note --notebook "ReadingList" --title "New note title" --body-file C:\path\to\note.md
```

Create a notebook, optionally under an exact parent notebook:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" create-notebook --parent "Daily Life" --title "Travel"
```

Append Markdown to one note by exact title:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" append-title --title "Exact note title" --body-file C:\path\to\section.md
```

Replace one note body by exact title:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" update-title --title "Exact note title" --body-file C:\path\to\updated-note.md
```

Force SQLite fallback:

```powershell
python "$env:USERPROFILE\.codex\skills\joplin-notes\scripts\joplin_notes.py" --backend sqlite search --query "keyword"
```

## Workflow

1. For discovery, run `list-notebooks`, `recent`, or `search`.
2. For reading, use `read-title` only when the title is exact; otherwise search first and let the user choose among plausible matches.
3. For adding content from another Codex thread, convert the content to clean Markdown in a workspace file, then use `create-note` or `append-title`.
4. For updates, prefer append or create unless the user explicitly requests replacement.
5. After writing, verify with `read-title --metadata-only`, `read-id --metadata-only`, or `search`, then report the note title and action performed.
6. Keep user-facing summaries concise, and do not paste large private note bodies unless the user asks.

## API Notes

The script uses the local Joplin Web Clipper endpoints:

- `GET /ping`
- `GET /folders`
- `GET /notes`
- `GET /search?query=...&type=note`
- `GET /notes/:id`
- `POST /notes`
- `PUT /notes/:id`

SQLite fallback reads:

- `folders`: notebooks. Use `id`, `title`, `parent_id`, `deleted_time`.
- `notes`: notes. Use `id`, `parent_id`, `title`, `body`, `updated_time`, `user_updated_time`, `deleted_time`, `is_conflict`.

Use `deleted_time = 0` for normal visible notebooks and notes.
