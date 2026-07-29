---
name: build-conference-latex-slides
description: Create, revise, audit, and synchronize academic conference presentations authored in LaTeX/Beamer, including story architecture, claim-led titles, evidence and identification framing, citation integration, appendix/reference design, Overleaf updates, PDF visual QA, and aligned speech drafts. Use for requests mentioning conference slides, academic slides, Beamer, presentation .tex files, Overleaf conference projects, AMES/ISAFE or similar meeting decks, or turning manuscript evidence into a conference talk. Keep LaTeX canonical and do not create PowerPoint unless explicitly requested.
---

# Build Conference LaTeX Slides

Build an academic talk as a cumulative argument, not a compressed paper or a sequence of tables. Preserve the research record while making the question, answer, design limits, and contribution easy to follow aloud.

## Load the right context

1. Read repository or workspace instructions, `MEMORY.md`, and the current revision plan before editing.
2. Locate the newest active `.tex` source and its figures with `rg`; distinguish active local work, synchronized results, and read-only archives.
3. Treat the local LaTeX source as canonical. Use Overleaf as a synchronized collaboration copy, not the only source of truth.
4. Read [references/tradewar-project.md](references/tradewar-project.md) when the workspace is the TradeWar project.
5. Read [references/content-and-citation-rules.md](references/content-and-citation-rules.md) for every full-deck creation or substantive story revision.
6. Also use the available presentation, field-specific academic-writing, PDF, browser, and notes skills when their trigger conditions apply.

## Establish the communication job

State internally:

> By the end, the academic audience should understand the answer and its limits because the deck connects the research question, design, evidence, and interpretation in a cumulative sequence.

Infer the requested talk length, audience, venue, and current empirical status. Do not impose an arbitrary slide limit. Let the argument and speaking time determine the number of main slides; move verification material to the appendix.

## Build or revise the story

Use this default sequence unless the paper requires another order:

1. Minimal title page.
2. Motivating fact, event, or news item.
3. Research question and interpretation of the empirical break.
4. Results preview with magnitudes and the decisive caveat.
5. Conceptual tension or competing forces.
6. Empirical roadmap or boundary tests.
7. Sample scale and identifying-event count.
8. Treatment, outcome, and measurement risks.
9. Estimating equation and identifying interpretation.
10. Main evidence with claim-led titles.
11. Completed checks and material open validation.
12. Explicit identification boundaries.
13. Substantive conclusion that resolves the opening.

Give each slide one narrative job. Prefer titles that state the finding. Do not end on a generic “Thank you” slide.

## Preserve research integrity

- Preserve numbers, signs, significance levels, equations, labels, samples, citations, and data sources unless the user authorizes a substantive change.
- Match causal language to the design. Distinguish a broad event-time break from a clean treatment coefficient.
- Separate descriptive heterogeneity, boundary conditions, and mechanism tests.
- Put sparse treated-event counts and outcome-classification risks in the main talk when they materially govern inference.
- Mark planned analyses as open. Never present an unrun check or proposed recoding as completed.

## Apply the citation policy

- Keep a full visible source for externally sourced news, quotations, images, and non-author-generated charts.
- Integrate literature citations into the sentence or construct they support. Use one or two anchor references per visible idea.
- Do not add page-bottom inventories labeled “Related work,” “Evidence,” “Construction references,” “Foundations,” or similar.
- Keep the full source trail in `\note{[Sources] ...}` and appendix reference slides.
- Keep data and method sources adjacent to the relevant construction when that improves comprehension.

Run the bundled audit after editing:

```powershell
python scripts/audit_beamer.py path\to\presentation.tex
```

Use `--json` for machine-readable output and `--strict` when warnings should fail validation.

## Edit safely

- Use `apply_patch` for source edits.
- Preserve the existing theme, macros, figure paths, navigation targets, and appendix frame-number behavior unless the user requests a redesign.
- Keep the title page minimal: title, authors, affiliation, conference, place, and date. Omit session title, room, and time unless explicitly requested.
- Shorten text before reducing font size.
- Keep speaker notes audience-invisible and use them for sources, delivery cues, and caveats.
- Do not create or maintain a PowerPoint version unless explicitly requested.

## Compile and inspect

1. Compile only the canonical source state.
2. Require zero LaTeX errors. Resolve warnings that indicate overflow, missing references, missing assets, or broken links.
3. Confirm page count and main/appendix split without forcing a predetermined count.
4. Render the compiled PDF to PNG.
5. Inspect every changed slide individually at full size; use a montage only for deck-level flow.
6. Check title wrapping, citation wrapping, clipping, overlap, table legibility, chart labels, footers, and page numbering.
7. Recompile and re-inspect after every layout-affecting correction.
8. Delete temporary PDFs and rendered QA images after validation.

## Synchronize and record

- Search for an Overleaf connector or API before using browser control. If none exists, update the authenticated Overleaf project through the browser and verify the compile log.
- Update any reproducible upload ZIP from the exact canonical source and required figures; verify hashes or contents.
- Put active code and QA artifacts in the local workspace. Put only intentional final result artifacts in synchronized result storage.
- When the work materially changes the project state, update the relevant Joplin execution/status note and `MEMORY.md`.
- If a speech draft is requested, align it slide by slide with the final main-deck order, include delivery cues and Q&A, and store it where project instructions require.

## Completion gate

Do not report completion until all applicable items hold:

- Canonical local source and synchronized copy match.
- Compilation succeeds with the expected pages.
- Changed slides pass full-size visual inspection.
- Main-talk citations are natural and traceable.
- Claims and magnitudes remain unchanged unless authorized.
- No PowerPoint was generated without an explicit request.
- Project records were updated when required.
