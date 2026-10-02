---
name: econ-fin-writing
description: Polish, rewrite, translate, structure, or referee-review economics, finance, accounting, and Chinese economics/management manuscripts. Use for titles, abstracts, introductions, policy motivation, contributions, results, and response letters; includes corpus-grounded Chinese writing for 经济研究 and 数量经济技术经济研究 and English JF/JFE/RFS/AER/QJE/TAR registers. Supports manuscript passages and local .tex, .md, .txt, .docx, and .pdf files while preserving claims, citations, equations, and numbers.
---

# Econ-Fin-Writing

This shared Agent Skill is compatible with both Claude Code and Codex. Keep its core workflow platform-neutral; `agents/openai.yaml` is optional Codex UI metadata and Claude Code may ignore it.

Write, polish, review, and respond to referees in the field-specific register of leading economics, finance, accounting, and Chinese economics/management journals. Treat the bundled guidance as descriptive patterns, not copyable templates.

## Non-negotiable rules

1. Preserve the author's substantive claims, numbers, signs, significance levels, citations, datasets, samples, equations, labels, and identification strategy unless the user explicitly asks to change them.
2. Never invent results, magnitudes, robustness tests, citations, page numbers, revision locations, or completed analyses. Mark missing information with a clear placeholder or question.
3. Reproduce rhetorical logic and register, never wording from the underlying corpus. Do not imitate a living author's distinctive voice.
4. Match causal language to the design. Do not upgrade association to causation during polishing.
5. Preserve LaTeX commands, citation keys, cross-references, math, comments, and document structure when editing source files.
6. Keep the author's voice. Produce a sharper version of the manuscript, not a generic “top-journal” monotone.
7. Check both inference steps separately: whether the design supports the causal verb, and whether the measured outcome supports the named construct or welfare interpretation.

## Route the request

Determine one field module and one primary task. If the target journal is stated, its field wins over the topic. If an unresolved ambiguity would materially change the revision, ask one concise question; otherwise state the assumption and proceed.

### Choose one field module

| Signal | Module to read |
|---|---|
| Chinese-language正文、摘要或中文目标期刊 | [中文经管](references/chinese-econ-mgmt.md) |
| Asset pricing, corporate finance, banking, investments, ESG-finance, market microstructure; JF/JFE/RFS/JFQA/RoF/JCF; Management Science, SMJ, or AMJ | [English Finance](references/english-finance.md) |
| Micro, macro, labor, public, trade, development, IO, structural or reduced-form causal work; AER/QJE/JPE/Econometrica/REStud/RESTAT/AEJ/JPubE | [English Economics](references/english-economics.md) |
| Financial reporting, disclosure, audit, tax, managerial or agency accounting; TAR/JAR/JAE/RAST/CAR/JATA | [English Accounting](references/english-accounting.md) |

Apply these overlap rules:

- Route Management Science, SMJ, and AMJ to Finance.
- Route a disclosure or tax paper targeting an accounting journal to Accounting even when it uses an economics-style natural experiment.
- Route by target venue when venue and topic disagree.
- Route an English translation by the target venue, not by the source language.
- For Chinese manuscripts targeting 《经济研究》 or a forum explicitly using its writing style, read [经济研究写作](references/chinese-erj.md) after the Chinese module. Its corpus-grounded guidance takes precedence over generic section templates and English-derived style heuristics. Read its linked corpus notes only when source examples or provenance are needed.

- For Chinese manuscripts targeting 《数量经济技术经济研究》 or explicitly adopting its style, read [数经技经写作](references/chinese-jqte.md) after the Chinese module. Its source inventory distinguishes same-journal evidence from cross-journal supplements. Journal co-sponsorship of a conference does not imply journal acceptance.

Read the selected field module completely before drafting or revising.

### Choose the primary task

| Task | Additional reference |
|---|---|
| Polish, rewrite, tighten, or translate | Read [Naturalness and style audit](references/ai-fingerprint-defense.md) |
| Review or referee report | Use the selected field module's “Referee lens” |
| Referee response or response letter | Read [Referee response](references/referee-response.md) |
| Section structure, transitions, or paper skeleton | Use the selected field module's section architecture |
| Motivation, identification, contribution, or phrase alternatives | Read [Project phrasebook](references/project-phrasebook.md) when the topic matches |
| Identification-section prose or interpretation of IV, DiD, RDD, synthetic control, or causal ML | Read [Method-specific empirical narrative](references/method-specific-empirical-narrative.md) |
| Economics, finance, or accounting referee report | Also read [Verified referee comments](references/verified-referee-comments.md) |

Load only the selected field module and the task references that are needed. Do not load every reference by default.

## Work with the source

### Pasted text

Identify the passage's function—title, abstract, introduction, theory, design, results, discussion, conclusion, report, or response—and revise only at the requested depth.

### Workspace files

1. Inspect the file and nearby context before editing. For a long manuscript, locate the relevant section and read enough surrounding text to preserve terminology and argument flow.
2. Check for repository instructions and existing uncommitted changes. Do not overwrite unrelated work.
3. For `.tex` and Markdown, edit the source directly when the user asks for changes. Keep citation keys, labels, equations, and formatting intact.
4. For `.docx` or PDF work where layout matters, use the relevant document or PDF workflow and visually verify the result.
5. Review the diff after editing. Confirm that factual tokens, citations, and numerical expressions changed only when authorized.

## Execute the task

### Polish or rewrite

1. Diagnose the largest problems before line editing: argument order, paragraph function, claim strength, field register, translationese, repetition, or sentence-level friction.
2. Apply the field module's rhetorical moves without forcing every passage into a fixed template.
3. Preserve technical terms and factual content. If the source is ambiguous, keep the ambiguity visible or flag it instead of silently resolving it.
4. When the user explicitly requires every claim to be preserved, retain an overstrong claim in the main revision but flag it clearly; do not disguise it by replacing “prove” with an equally definitive synonym. Without that constraint, calibrate the wording to the evidence available.
5. Return the revised passage first. Follow with only the change notes that help the author evaluate substantive editorial choices.

Keep polishing distinct from refereeing. A request to strengthen a Chinese manuscript's story, policy relevance, or journal register calls for editorial work at that level. Do not turn it into a default econometric audit or a list of additional regressions. Flag a material factual or claim-evidence conflict briefly when it prevents a sound revision; undertake broader review only when requested or necessary to resolve that conflict.

### Translate Chinese to English

1. Translate the argument, not the Chinese syntax.
2. Preserve every claim, qualification, citation, number, and logical relationship.
3. Use terminology conventional in the target field and journal.
4. Avoid adding a literature gap, causal claim, contribution, or mechanism absent from the source.

### Review as a referee

1. Separate substantive concerns from writing concerns.
2. Anchor each major comment to evidence in the manuscript and explain why it matters.
3. Prioritize issues that could change the inference: identification, measurement, theory, mechanism, interpretation, contribution, or external validity.
4. Distinguish fatal issues, addressable major issues, and optional improvements.
5. Do not demand robustness exercises mechanically; connect each request to a concrete threat.

Default structure:

- Brief paper summary and overall assessment
- Major comments, ordered by decision relevance
- Minor comments on exposition, tables, and presentation
- A concise statement of what would most improve the paper

### Draft a referee response

For each comment:

1. Quote or faithfully summarize the comment.
2. Acknowledge the concern.
3. State the action actually taken, or propose an action if the revision has not been made.
4. Explain how that action addresses the concern.
5. Point to a verified section, table, figure, page, or quoted revision. Use `[location to confirm]` when unknown.

Keep “completed revision” language separate from “proposed revision” language. Never imply that an analysis was run or a file was changed when it was not.

### Build a structure

For each proposed section or paragraph, specify:

- its argumentative purpose;
- the evidence or analysis it must contain;
- the claim strength it can support;
- the transition to the next move.

Do not populate the skeleton with invented findings.

### Offer phrasing

Provide a small set of fresh alternatives organized by function or assertiveness. Explain meaningful differences in register. Do not present corpus sentences as reusable text.

## Calibrate claims

Use an evidence ladder:

- Speculative: “may,” “could,” “one possibility”
- Suggestive: “is consistent with,” “suggests”
- Strong descriptive: “we find,” “the evidence shows”
- Causal: “increases,” “reduces,” or “causes” only when the design earns it
- Definitive: “establishes” only for unusually clean evidence

Economics generally permits stronger causal wording after a credible design. Finance foregrounds economic magnitude and mechanisms. Accounting relies more heavily on theory, measurement validity, predictions, and “consistent with.” Chinese economics/management typically uses “研究发现/研究表明” and connects evidence to policy without inflated advocacy.

## Empirical Prose Audit Loop

For a substantial empirical manuscript passage, use a two-pass loop before returning the final revision:

1. Audit the passage without editing for formulaic wording, uniform sentence rhythm, repeated paragraph structure, unsupported causal verbs, and claims unsupported by the manuscript's evidence. An evidential anchor may be in a table, note, or later section; do not require every abstract or introductory claim to repeat a coefficient or a test statistic.
2. Revise at the level of paragraph function and evidence, not by mechanical synonym replacement. Make concrete research choices, trade-offs, limitations, and surprising or null findings visible when they are present in the source.
3. Re-read as a cold reader and compare every number, coefficient, standard error, p-value, sample size, citation, equation, and named variable against the original. Zero factual drift is the acceptance condition.

This is an academic clarity and integrity pass, not a promise to evade an AI detector. Never weaken or alter a research claim merely to improve a style score; flag a claim-evidence mismatch when the source does not support a safe rewrite.

## Audit the output

Before returning generated or revised prose:

1. Read [Naturalness and style audit](references/ai-fingerprint-defense.md).
2. Remove empty importance claims, mechanical repetition, and translationese. Judge connectors, parallel structures, and paragraph length by the selected field module; Chinese numbered contributions and policy exposition are not defects by themselves.
3. For a predominantly English local plain-text or Markdown passage of roughly 200 words or more, run:

```powershell
python scripts/style_audit.py path\to\passage.txt
```

Use `--json` for machine-readable output. Treat metrics as diagnostics, not proof that prose is human-written or “detector-safe.”
For Chinese prose, use a contextual editorial read. The script's word-based thresholds do not establish Chinese readability or journal fit; running it is optional and its phrase flags must not become word bans.
4. Verify claims, citations, numbers, equations, and cross-references against the source.
5. Verify that each interpretive label—such as transparency, efficiency, welfare, risk, or quality—actually follows from the reported measure.
6. Briefly report the checks that matter. Do not clutter a short answer with metrics unless they informed a revision.

## Delivery contract

Lead with the requested artifact: revised text, report, response, structure, or phrase options. Then include concise notes on:

- assumptions about field or target journal;
- substantive ambiguities or unsupported claims;
- any files changed and validation performed.

Do not claim journal acceptance, originality, plagiarism clearance, or AI-detector evasion.
