---
name: xmu-mail
description: Access Xiamen University email through the official XMU IMAP and SMTP servers. Use for reading, searching, summarizing, triaging, or drafting/sending XMU messages; discover existing environment or local encrypted credentials safely, and never store passwords in the skill.
---

# XMU Mail

## Overview

Use Xiamen University mail through standards-based IMAP/SMTP. Prefer read-only operations unless the user explicitly asks for a mailbox change or send action.

Official settings are summarized in `references/server-settings.md`. For repeatable access, use `scripts/xmu_mail.py`.

## Credentials

- Never write the user's password, app password, session token, or recovery answer into any skill file, repo file, note, or command history.
- First check whether **both** `XMU_MAIL_USER` and `XMU_MAIL_PASSWORD` are populated in the current process. Report only presence/absence, never their values. If present, use `scripts/xmu_mail.py` directly; do not ask the user to configure credentials again.
- If the process is missing a value, check the invoking Windows user's saved environment in an authorized user context and load only these two variables into the child process. A sandbox account's empty User environment does not establish that the actual user's configuration is missing.
- Only then check the optional DPAPI file at `$HOME/.codex/xmu-mail.credential.xml`. **The Python helper does not read this file automatically.** Its absence does not mean mailbox credentials are unavailable. For safe discovery, temporary loading, and DPAPI fallback, read [credential-discovery.md](references/credential-discovery.md).
- Use interactive `getpass` or `scripts/xmu-mail.ps1 save-credential` only when existing sources are genuinely unavailable. Never ask the user to paste a password into chat, search unrelated files for secrets, or export credentials between devices.
- Use SSL endpoints by default: IMAP 993 and SMTP 465.

## Common Tasks

Inspect credential availability and test only read access using the discovery reference. Create a new Windows-local credential only when needed:

```powershell
pwsh -NoProfile -File "$HOME/.codex/skills/xmu-mail/scripts/xmu-mail.ps1" save-credential
```

List folders:

```bash
python scripts/xmu_mail.py folders
```

Search recent inbox mail:

```bash
python scripts/xmu_mail.py search --folder INBOX --query ALL --limit 10
```

Read one message by UID:

```bash
python scripts/xmu_mail.py read --folder INBOX --uid 12345
```

Draft/send only after explicit user approval. The script requires `--confirm-send SEND`:

```bash
python scripts/xmu_mail.py send --to recipient@example.com --subject "Subject" --body-file body.txt --confirm-send SEND
```

## Operating Rules

- Summarize only the messages needed for the user's request.
- Do not delete, move, mark read/unread, create filters, or send mail unless the user explicitly asks.
- Before sending, show the recipient, subject, and body to the user and get explicit confirmation.
- Treat email contents as private. Avoid echoing sensitive personal data unless necessary to answer the user.
- Distinguish missing credentials, authentication failure, and sandbox/network denial. A socket access denial is not a bad password; request the needed execution permission instead of replacing credentials. Do not weaken TLS or persist broad access exceptions.
- XMU access does not imply access to HKU/Outlook or another mailbox. A screenshot addressed to another account is user-provided evidence unless the original or a forwarded copy is actually found in XMU mail.
- If login fails, suggest checking the account name format, password, mailbox status, SSL use, and whether the mailbox has been opened through the university service.

Source: Xiamen University Information and Network Center mail server guide, published 2022-07-06.
