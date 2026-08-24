---
name: zotero-librarian
description: "Organize, clean up, and maintain a local Zotero library — sorting new papers into collections, normalizing tags, fixing broken metadata from PDF imports, unifying journal names and title capitalization, deduplicating, and auditing which working papers have since been published. Works by reading zotero.sqlite read-only and generating an idempotent JavaScript file the user runs inside Zotero (Tools → Developer → Run JavaScript), so the library is never written to directly. Use this skill whenever the user mentions Zotero, their reference library, .bib/citation management, 'I added some new papers', wants papers filed into collections, tags cleaned or translated to English, metadata or author names fixed, journal titles standardized, or asks to check whether their working papers got published — even if they only say something vague like 'tidy up my library' or 'I added a few articles, sort them out'."
---

# Zotero Librarian

Maintain a research library that stays consistent as it grows. The core problem: Zotero imports arrive with inconsistent metadata (PDF-scraped titles, ALL-CAPS authors, journal names with and without "The"), and new papers pile up unfiled. Manual cleanup does not scale past a few hundred items; blind bulk edits corrupt good data.

The approach that works: **read the library read-only, decide everything up front, then hand the user a script that applies the decisions.** You never write to their database. They keep the veto.

## Why generate a script instead of editing directly

Editing `zotero.sqlite` from outside is a bad idea even when it looks convenient. Zotero holds the DB open, bypassing its API skips sync bookkeeping and validation, and a half-applied write can corrupt the library. The user's data is worth more than the convenience.

So: **analysis in Python (read-only) → decisions → emit one `.js` file → the user runs it in Zotero.** Zotero's built-in JavaScript runner has full API access, participates in sync, and the user can read the script before running it. This also means every change is reviewable, and reruns are safe.

## The workflow

### 1. Read the library without disturbing it

Do not ask the user to close Zotero. `scripts/scan_library.py` creates a
consistent temporary SQLite snapshot with the SQLite online backup API, reads
only that snapshot, and deletes the temporary directory when the scan exits.
The original `zotero.sqlite` is never written to. This also includes the
current `-wal` state seen by SQLite while the snapshot is made, so Zotero can
remain open during the scan.

Use the scanner rather than querying the live file directly:

```python
DB = '/sessions/<session>/mnt/Zotero/zotero.sqlite'   # translate the user's Zotero path
c = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
```

`scripts/scan_library.py` does a full inventory in one pass — collections tree with counts, tag frequencies, per-item collections/tags, and the common data-quality problems. Start there rather than writing ad-hoc queries; the schema is fiddly and it is already handled. See `references/zotero_schema.md` when you need a query it does not cover. If a sync is actively changing the library and the snapshot fails, retry after the sync settles; do not close Zotero as a routine prerequisite.

When the task needs the exact live collection state while Zotero remains open,
prefer a read-only JavaScript snippet executed inside Zotero. The generated
script path already follows this pattern:

```javascript
var libraryID = Zotero.Libraries.userLibraryID;
var allColls = Zotero.Collections.getByLibrary(libraryID, true);
```

Resolve collections by their full parent/child path, not by name alone. The
internal API is the best route for live collection membership and Zotero's
cached objects; the Python snapshot route is better for larger SQL inventories
and machine-readable audits.

Bash calls time out around 45s, so wrap long scans in `timeout 42` and keep each query focused.

### 2. Decide, and show your work before generating anything

Print the proposed changes and read them. This is where errors get caught, and it is cheap compared to a user discovering a mangled library later. Two habits that repeatedly caught real bugs:

- **Sample the diffs.** Print 10–20 before/after pairs and actually inspect them. A title-case pass looked fine in aggregate but was producing `Peer-To-Peer`, `Trade-off`, and lowercasing the first word inside quotes — all only visible by reading examples.
- **Check the destructive direction specifically.** Filter for changes that *remove* information (uppercase→lowercase, non-empty→empty) and review those separately. An email-stripping regex using `\w` silently matched Chinese characters and would have blanked 8 author names; the guard caught it because empty results were being counted.

When a judgment call is genuinely the user's — which of two collection names is canonical, whether to merge Chinese author names into one field — ask rather than guess. But do not ask about things you can determine yourself: which journal name is official is a fact you can look up.

### 3. Generate the script

Write one `.js` file per task with a comment header stating what it changes and why, so the user can review before running. Follow the patterns in `references/zotero_js_api.md` — particularly transaction handling (`item.save()` inside `Zotero.DB.executeTransaction`, `item.saveTx()` outside), which is the most common source of silent failures.

Three properties every generated script needs:

**Idempotent.** Check current state before changing it (`if (item.getCollections().includes(target.id)) continue;`). Users rerun scripts, and a second run should report "already in place" rather than duplicating or erroring.

**Verifying.** For value replacements, compare against the expected old value and skip on mismatch — the user may have edited that item since you scanned:
```javascript
if (cur !== rec.old) { skip++; continue; }
```

**Non-destructive by default.** Add to collections rather than moving between them (Zotero items live in many collections). Never write an empty string over existing data. Leave title/author alone unless that is the task.

End with a log summarizing counts, so the user sees `changed 47, already 12, skipped 2` rather than silence.

Validate syntax before handing it over — Zotero's runner wraps your code in an async function, so top-level `await`/`return` are legal there but not to `node --check`:
```bash
python3 -c "src=open('x.js').read(); open('/tmp/c.js','w').write('(async function(){\n'+src+'\n})();')"
node --check /tmp/c.js
```

### 4. Hand it over

Deliver the `.js` file with `present_files` and explain in a few lines what it will do and roughly how many items it touches. Tell the user to run it via **Tools → Developer → Run JavaScript**, paste, Run — and to sync afterward.

## Task-specific guidance

Read the relevant reference file when you hit one of these:

| Task | Reference |
|---|---|
| Filing new items, designing/extending the collection tree | `references/organizing.md` |
| Tag normalization, English-first policy, JEL codes | `references/organizing.md` |
| Title case, journal names, author names, broken PDF imports | `references/metadata.md` |
| Any Zotero JS API call, transactions, item types | `references/zotero_js_api.md` |
| SQL against zotero.sqlite | `references/zotero_schema.md` |

## Working with a library you have not seen

Do not impose a taxonomy. Read the existing tree and tag vocabulary first (`scan_library.py` prints both), then extend in the user's established style — if their collections are `Corporate Finance/Capital Structure`, a new subcollection should be `Corporate Finance/Financial Constraints`, not `corp-fin > constraints`. Match their tag conventions too: if tags are Title Case English with `JEL-G` codes, follow that.

For assigning items to collections, keyword matching on title + abstract + existing tags gets most of the way. Two things make it reliable: match against tags as well as text (an author-supplied tag is a strong signal), and exclude the obvious false friends explicitly — `\bunion\b` needs to not match "European Union", "credit union", or "Soviet Union". Always report what did not match rather than force-assigning it; a leftover pile is more useful than silently wrong filing.

## Verifying publication status of working papers

A library accumulates NBER/SSRN working papers that have since appeared in journals. Search per paper (title + first author), and when you find the published version, record journal, year, volume/issue/pages, and DOI.

Two cautions learned the hard way. **Papers get renamed on publication** — Fulmer's "Political Contributions and the Severity of Government Enforcement" became "Negation of Sanctions" in JFQA; Korinek's "Language Models and Cognitive Automation" became "Generative AI for Economic Research" in JEL. Search on author + topic, not just the exact title. And **verify author identity**, since same-surname confusion is common: a "Whited" paper on propensity score matching turned out to be Robert Whited (accounting), not Toni Whited.

Only write metadata you actually confirmed. Search snippets frequently give journal, year, and volume but not DOI — filling in a plausible-looking DOI is worse than leaving it empty. Mark uncertain findings for the user to check rather than guessing.

Deliver findings as a spreadsheet (status / journal / year / volume-issue-pages / DOI / notes, color-coded by status) plus a script that updates only the confirmed ones.
