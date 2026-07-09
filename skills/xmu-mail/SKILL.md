---
name: xmu-mail
description: Access Xiamen University email through the official XMU IMAP and SMTP servers. Use when the user asks Codex to read, search, summarize, triage, or draft/send messages for an @xmu.edu.cn mailbox or XMU mail account; use environment variables or interactive prompts for credentials and never store mailbox passwords in the skill.
---

# XMU Mail

## Overview

Use Xiamen University mail through standards-based IMAP/SMTP. Prefer read-only operations unless the user explicitly asks for a mailbox change or send action.

Official settings are summarized in `references/server-settings.md`. For repeatable access, use `scripts/xmu_mail.py`.

## Credentials

- Never write the user's password, app password, session token, or recovery answer into any skill file, repo file, note, or command history.
- Read `XMU_MAIL_USER` and `XMU_MAIL_PASSWORD` from the environment when available.
- If credentials are missing, let the script prompt interactively with `getpass`; do not ask the user to paste a password into chat.
- Use SSL endpoints by default: IMAP 993 and SMTP 465.

## Common Tasks

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
- If login fails, suggest checking the account name format, password, mailbox status, SSL use, and whether the mailbox has been opened through the university service.

Source: Xiamen University Information and Network Center mail server guide, published 2022-07-06.
