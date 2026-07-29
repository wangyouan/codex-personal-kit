# econ-fin-writing

`econ-fin-writing` is a shared Agent Skill for **Claude Code and OpenAI Codex**. It helps write, polish, translate, structure, referee-review, and draft referee responses for economics, finance, accounting, and Chinese economics/management manuscripts.

This repository is the canonical source. Maintain one set of instructions and references here; do not fork separate Claude and Codex rule sets unless a capability genuinely requires platform-specific behavior.

## Compatibility

| Host | Personal skill location | Invocation |
|---|---|---|
| Codex | `~/.agents/skills/econ-fin-writing` | `$econ-fin-writing` or automatic matching |
| Claude Code | `~/.claude/skills/econ-fin-writing` | `/econ-fin-writing` or automatic matching |

Some existing Codex installations still discover skills under `~/.codex/skills`. The installer writes to both Codex locations by default so that the skill works during the transition.

The shared runtime contract is the root `SKILL.md`, which uses the common Agent Skills frontmatter (`name` and `description`). `agents/openai.yaml` supplies optional Codex UI metadata; Claude Code can ignore it safely.

## What it does

The skill routes each request to one field register:

| Field | Typical venues |
|---|---|
| English Finance | JF, JFE, RFS, JFQA, RoF, JCF, Management Science, SMJ, AMJ |
| English Economics | AER, QJE, JPE, Econometrica, REStud, RESTAT, AEJ, JPubE |
| English Accounting | TAR, JAR, JAE, RAST, CAR, JATA |
| 中文经管 | 《经济研究》《管理世界》《金融研究》《会计研究》《中国工业经济》等 |

Supported tasks include polishing and de-formulaic editing, Chinese-to-English translation, section design, phrase alternatives, referee reports, and response letters. The core safeguards are: preserve claims and evidence, never invent results or citations, never copy corpus wording, and match causal language and construct interpretation to the evidence.

## Install from this checkout

Keep one local clone as the maintenance checkout, then install copies for the host tools:

```powershell
.\scripts\install.ps1 -Target Both
```

Preview without changing files:

```powershell
.\scripts\install.ps1 -Target Both -DryRun
```

If PowerShell blocks local scripts, invoke it explicitly:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Target Both
```

For one host only, use `-Target Codex` or `-Target Claude`. Restart the relevant host if a newly installed skill is not listed.

## Install from GitHub

Clone this repository wherever you keep personal tool configuration, then run the installer from that checkout:

```powershell
git clone https://github.com/wangyouan/econ-fin-writing.git
Set-Location econ-fin-writing
.\scripts\install.ps1 -Target Both
```

For a project-scoped installation, copy or symlink the checkout to `.agents/skills/econ-fin-writing` for Codex, or `.claude/skills/econ-fin-writing` for Claude Code. Project-scoped skills should be committed only when every collaborator should use them.

## Layout

```text
econ-fin-writing/
├── SKILL.md                 # shared workflow and task router
├── agents/openai.yaml        # optional Codex UI metadata
├── references/               # field registers and task-specific guidance
│   ├── english-finance.md
│   ├── english-economics.md
│   ├── english-accounting.md
│   ├── chinese-econ-mgmt.md
│   ├── ai-fingerprint-defense.md
│   ├── referee-response.md
│   └── project-phrasebook.md
└── scripts/
    ├── install.ps1           # install into Codex and/or Claude Code
    ├── style_audit.py        # reproducible prose diagnostics
    ├── process.py            # optional Zotero corpus maintenance
    ├── select_extract.py
    └── export_zotero.sh
```

## Maintain the skill as your writing develops

When a new article or journal target exposes a recurring writing need, update this repository rather than relying on a one-off chat instruction.

1. Put cross-field workflow changes in `SKILL.md`.
2. Put stable field-specific conventions in the relevant file under `references/`.
3. Add project-specific framing only when it has repeated value, and state it as an evidence-aware pattern rather than a claim to insert blindly.
4. Keep the no-fabrication, non-copying, causal-calibration, and construct-validity safeguards intact.
5. Run the validation commands below, then reinstall with `scripts/install.ps1`.

Avoid encoding a preference from one draft as a universal rule. A good update captures a repeatable decision rule, a journal-specific convention, or a failure mode that has occurred more than once.

## Validate

Validate the shared skill structure:

```powershell
python -X utf8 "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
```

Run the prose diagnostics on a plain-text or Markdown passage:

```powershell
python .\scripts\style_audit.py path\to\passage.txt
```

The audit is an editing diagnostic, not an authorship or AI-detector prediction.

## Corpus maintenance

The Zotero extraction scripts are optional maintenance tools, not part of the normal writing workflow. They help refresh field references when the source library changes:

```powershell
python .\scripts\process.py
python .\scripts\select_extract.py
```

`select_extract.py` requires `pdftotext` on `PATH`. Chinese PDF body extraction may be unreliable, so the Chinese module should continue to rely on readable evidence and journal conventions rather than automatic text extraction alone.

## License

Private. The references describe writing patterns in original language; they do not reproduce journal text.
