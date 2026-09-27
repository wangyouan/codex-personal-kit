# Naturalness and style audit

Use this reference for every substantial passage that Codex generates, rewrites, or translates. The goal is clear, field-appropriate prose without formulaic AI mannerisms. This audit cannot establish authorship or guarantee an AI-detector outcome.

## 1. Phrase-level scan

Treat these as editing signals, not forbidden vocabulary in all contexts.

For Chinese academic manuscripts, apply the selected Chinese journal module first. Numbered contributions, parallel policy implications, substantial background paragraphs, and ordinary connectors can be functional journal conventions. Do not infer AI authorship from these features or force Chinese prose into an English sentence-length or paragraph template.

| Marker | Default threshold per manuscript section | Preferred action |
|---|---:|---|
| “Furthermore,” “Moreover,” “Additionally,” or “In addition,” as sentence openers | 0 | Delete or use a substantive logical relation |
| “It is worth noting that,” “It is important to note,” or stacked “Notably” | 0 | State the point directly |
| Em dash as a general-purpose connector | At most 1 per page | Prefer a full stop, comma, or colon |
| “Not X, but Y” binary contrast | At most 1 per section | Use a plain assertion when contrast is not essential |
| “plays a crucial/pivotal/vital role” | At most 1, backed by a fact | Name the mechanism |
| “delve into,” “shed light on,” or repeated “underscore” | At most 1 each | Use a precise field verb |
| “In today's world,” “In recent years,” or “With the rapid development of” | 0 | Open with a fact, tension, question, or claim |
| Formulaic future-work sentences | 0 | State a concrete limitation or omit |
| Chinese “综上所述 / 值得注意的是 / 总而言之 / 众所周知 / 随着……的不断发展” | Contextual; no fixed quota | Keep when functional; revise empty framing, repetition, or unsupported consensus claims |
| Decorative triple adjectives | At most 1 per section | Keep the one adjective that carries information |

Do not replace every flagged phrase mechanically. Check whether it names a real relation that should be expressed more directly.

## 2. Structural self-audit

Ask:

1. Does one paragraph template repeat more than twice?
2. Does the introduction move through territory, gap, answer, and roadmap with suspiciously equal-sized blocks?
3. Are parallel subsections written with identical sentence shapes?
4. Does the manuscript conceal uncertainty, contrary evidence, bounded nulls, or design limits?
5. Does the conclusion replay the introduction in the same order and nearly the same wording?
6. Does every paragraph end with a summary sentence that merely repeats its opening?

Three or more “yes” answers require structural revision. Merge or split paragraphs, vary move lengths, rewrite a parallel subsection around its specific evidence, and state genuine limitations where warranted. Do not manufacture uncertainty for stylistic variety.

For Chinese journal prose, treat the questions as prompts for rereading, not a numerical trigger. Parallel contributions and a conclusion returning to the policy question may be appropriate. Revise when they obscure the argument or merely duplicate text, not because their structure is regular.

## 3. Quantitative diagnostics

Use `scripts/style_audit.py` for a reproducible first pass. Interpret its output in context.

| Metric | Possible concern | Interpretation |
|---|---|---|
| Sentence-length standard deviation | Very low relative to the passage's mean | The prose may be mechanically uniform |
| Connector density | More than 6 listed connectors per 1,000 words | Logical transitions may be formulaic |
| Repeated sentence openers | The same normalized opener begins many sentences | Syntax may be repetitive |
| Extreme paragraph share | No short or long paragraphs in a long section | Paragraph architecture may be over-regular |
| Phrase flags | Several stock markers | Revise the underlying logic, not just vocabulary |

There is no universal “human” threshold. Section type, equations, citations, and the author's normal style affect every metric. Use the numbers to locate passages for rereading, not to certify the result.

The script's word-based thresholds are not calibrated to Chinese prose. For predominantly Chinese passages, a contextual read is the default; script output is optional and cannot establish Chinese readability or 《经济研究》 style.

## 4. Preserve productive unevenness

Good academic prose varies because ideas require different amounts of space. A short finding can stand alone; a design caveat may need a longer sentence; a two-sentence paragraph can mark a pivot. Allow this functional variance.

Do not:

- inject errors, awkwardness, or fake citations;
- alter claims, numbers, or meaning;
- replace ordinary words with rare synonyms merely to increase lexical variety;
- add personal anecdotes or uncertainty not supported by the research;
- optimize prose against a detector score.

## 5. Final read

Read the passage once for argument and once for sound:

- Every transition should name a real relation: cause, contrast, implication, sequence, scope, or evidence.
- Each paragraph should perform a recognizable function.
- Claim strength should track the evidence.
- Terminology should remain stable.
- The result should sound like the same author at their best.
