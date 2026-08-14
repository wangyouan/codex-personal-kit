# Metadata normalization

## Title capitalization

Libraries drift into a mix of Title Case and sentence case because different import routes produce different conventions. Pick one and convert.

**Convert toward Title Case, not away from it.** This is not a style preference — it is the only direction that is information-preserving. Sentence case has already discarded which words are proper nouns, so going Title → sentence cannot know whether "China" should stay capitalized. Going the other way, proper nouns are already marked. The damage is visible in real libraries: `evidence from the U.S.-china trade war` is what a sentence-case conversion did to *China*.

Check the split before proposing (`scan_library.py --case-audit`). Title Case is usually the majority anyway.

Rules that produce clean output:

- Capitalize content words; lowercase articles, coordinating conjunctions, and prepositions (`of the and or from about versus through during`).
- Always capitalize: first word, last word, and the first word after `:` `?` `!` `—`.
- Capitalize the first word inside quotes — `"The Bird in the Hand" Fallacy`, not `"the Bird..."`.
- Leave acronyms alone: `U.S. ESG CEO IPO M&A R&D AI FDI WTO GVC TFP COVID-19`.
- Capitalize proper nouns wherever they appear: `China Bayesian Nash Popper Sarbanes-Oxley`.
- Hyphenated compounds split by part of speech: function words stay lowercase (`Peer-to-Peer`), adverbs and particles do not (`Trade-Off`, `Take-Up`).
- Preserve deliberate lowercase in technical terms: `q-theory`, `i.i.d.`, and journal names like `npj Climate Action`.
- Leave CJK titles untouched.

`scripts/title_case.py` implements this. Each rule above exists because a naive implementation got it wrong on a real library — worth reusing rather than rewriting.

**Always sample the diffs.** Filter for changes that lowercase something and read those specifically; that is where the errors are. Legitimate lowercasing (`Versus`→`versus`, `About`→`about`) and bugs (`Peer-To-Peer`) look the same in aggregate statistics.

## Journal names

The same journal appears in several spellings. Real distribution from one library:

```
'Journal of Finance'  ×86     vs  'The Journal of Finance'  ×78
'The Review of Financial Studies' ×205  vs  'Review of Financial Studies' ×37
'Journal of Banking & Finance' ×12      vs  '... and Finance' ×7
```

**Standardize to the journal's official title, not the majority spelling.** Majority is an accident of import history; the official name is verifiable and matches how CSL styles and other tools expect it.

Official names that are commonly wrong:

| Correct | Common error |
|---|---|
| The Journal of Finance | Journal of Finance |
| The Review of Financial Studies | Review of Financial Studies |
| The Accounting Review | Accounting Review |
| The Quarterly Journal of Economics | Quarterly Journal of Economics |
| The Review of Economic Studies | Review of Economic Studies |
| The Review of Economics and Statistics | Review of Economics and Statistics |
| The RAND Journal of Economics | RAND Journal of Economics |
| Journal of Financial and Quantitative Analysis | *The* JFQA, or `&` |
| Academy of Management Journal / Review | *The* Academy of… |
| Journal of Economic Literature | *The* JEL |
| Journal of Banking & Finance | …and Finance |
| Journal of Business Finance & Accounting | …and Accounting |
| PLOS ONE | PLoS ONE |

The `&`-vs-`and` choice follows the publisher: Elsevier and Wiley use `&` for these titles, while JFQA spells out `and`.

To find variants, normalize (lowercase, drop leading "the", strip non-alphanumerics and `and`/`&`) and group — see `references/zotero_schema.md`.

**Do not "fix" names that only look wrong.** `npj Artificial Intelligence` (Nature's npj series), `Revue française d'études américaines`, and `Canadian Journal of Economics/Revue canadienne d'économique` are all correct as written.

## Author names

Three recurring problems:

**ALL-CAPS from publisher exports.** `RITTER JAY R.` → `Ritter, Jay R.` Preserve `McDonald`, `O'Brien`, `van der`, and initials with periods (`J. R.`).

**Emails glued to names**, typical of CNKI/Chinese-database imports: `刘贯春liuguanchun1@126.Com`. Strip the address, keep the name. Use an ASCII-only email pattern — Python's `\w` matches CJK and will delete the name along with the address:

```python
EMAIL = re.compile(r'[A-Za-z0-9._%\-]+@[A-Za-z0-9._%\-]+')   # not [\w.\-]+
```

**Split CJK names.** Zotero stores `lastName=金, firstName=浩` after some imports. Merging into single-field mode (`fieldMode=1`, `lastName=金浩`) is safer for citation output — English CSL styles otherwise render it as "浩 金" or "金, 浩". Ask the user before doing this to 80+ authors; it is a real choice, not an obvious fix.

**Never write an empty name.** Add a guard that skips any transformation whose result would be blank, and count the skips — that counter is what catches a bad regex before it reaches the user's library.

## Broken PDF imports

Dragging a PDF into Zotero without a DOI produces items where the "title" is scraped page-header text: `Nber working paper series`, `Untitled`, `Microsoft Word - draft.docx`. They also land as `journalArticle` when they are working papers.

Fix by searching for the real paper (distinctive abstract phrases work well — "380 trillion tokens of realized AI consumption" identifies one paper exactly), then:

1. Set the item type first (`preprint` for NBER/SSRN/arXiv working papers), *then* the fields.
2. Fill `title`, `date`, `repository` (e.g. `National Bureau of Economic Research`), `number`/`archiveID`, `DOI` (NBER: `10.3386/w<number>`), `url`, `abstractNote`.
3. Verify author order against the official listing — scraped author blocks are often reordered.
4. Record alternate versions in `extra` (`arXiv:2606.30583; Cowles Discussion Paper`).

Zotero's own **right-click → Reinstall/Refresh Metadata** is worth suggesting alongside the script when the item has a DOI — it is authoritative and free.
