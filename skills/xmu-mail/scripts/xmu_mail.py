#!/usr/bin/env python3
"""Small IMAP/SMTP helper for Xiamen University mail."""

from __future__ import annotations

import argparse
import email
import getpass
import imaplib
import os
import smtplib
import ssl
import sys
from email.header import decode_header
from email.message import EmailMessage
from email.utils import parsedate_to_datetime


IMAP_HOST = "imap.xmu.edu.cn"
IMAP_PORT = 993
SMTP_HOST = "smtp.xmu.edu.cn"
SMTP_PORT = 465


def credential_pair(args: argparse.Namespace) -> tuple[str, str]:
    user = args.user or os.environ.get("XMU_MAIL_USER")
    password = os.environ.get("XMU_MAIL_PASSWORD")
    if not user:
        user = input("XMU mail username/email: ").strip()
    if not password:
        password = getpass.getpass("XMU mail password: ")
    return user, password


def decode_value(value: str | None) -> str:
    if not value:
        return ""
    pieces: list[str] = []
    for payload, charset in decode_header(value):
        if isinstance(payload, bytes):
            pieces.append(payload.decode(charset or "utf-8", errors="replace"))
        else:
            pieces.append(payload)
    return "".join(pieces)


def connect_imap(args: argparse.Namespace) -> imaplib.IMAP4_SSL:
    user, password = credential_pair(args)
    client = imaplib.IMAP4_SSL(args.imap_host, args.imap_port, ssl_context=ssl.create_default_context())
    client.login(user, password)
    return client


def extract_text(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = (part.get("Content-Disposition") or "").lower()
            if content_type == "text/plain" and "attachment" not in disposition:
                payload = part.get_payload(decode=True) or b""
                return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True) or b""
                return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        return ""
    payload = msg.get_payload(decode=True)
    if isinstance(payload, bytes):
        return payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    return str(msg.get_payload())


def command_folders(args: argparse.Namespace) -> int:
    with connect_imap(args) as client:
        status, data = client.list()
        if status != "OK":
            raise RuntimeError(f"Could not list folders: {status}")
        for row in data:
            print(row.decode(errors="replace"))
    return 0


def command_search(args: argparse.Namespace) -> int:
    with connect_imap(args) as client:
        client.select(args.folder, readonly=True)
        status, data = client.uid("SEARCH", None, args.query)
        if status != "OK":
            raise RuntimeError(f"Search failed: {status}")
        uids = data[0].split()[-args.limit :]
        for uid in reversed(uids):
            status, fetched = client.uid("FETCH", uid, "(BODY.PEEK[HEADER.FIELDS (DATE FROM TO SUBJECT)])")
            if status != "OK" or not fetched or not isinstance(fetched[0], tuple):
                continue
            msg = email.message_from_bytes(fetched[0][1])
            date = decode_value(msg.get("Date"))
            try:
                parsed = parsedate_to_datetime(date).isoformat()
            except Exception:
                parsed = date
            print(f"UID: {uid.decode()}")
            print(f"Date: {parsed}")
            print(f"From: {decode_value(msg.get('From'))}")
            print(f"To: {decode_value(msg.get('To'))}")
            print(f"Subject: {decode_value(msg.get('Subject'))}")
            print()
    return 0


def command_read(args: argparse.Namespace) -> int:
    with connect_imap(args) as client:
        client.select(args.folder, readonly=True)
        status, fetched = client.uid("FETCH", str(args.uid), "(BODY.PEEK[])")
        if status != "OK" or not fetched or not isinstance(fetched[0], tuple):
            raise RuntimeError(f"Read failed for UID {args.uid}: {status}")
        msg = email.message_from_bytes(fetched[0][1])
        print(f"From: {decode_value(msg.get('From'))}")
        print(f"To: {decode_value(msg.get('To'))}")
        print(f"Cc: {decode_value(msg.get('Cc'))}")
        print(f"Date: {decode_value(msg.get('Date'))}")
        print(f"Subject: {decode_value(msg.get('Subject'))}")
        print()
        body = extract_text(msg)
        if args.max_chars and len(body) > args.max_chars:
            body = body[: args.max_chars] + "\n[truncated]"
        print(body)
    return 0


def command_send(args: argparse.Namespace) -> int:
    if args.confirm_send != "SEND":
        raise SystemExit("Refusing to send without --confirm-send SEND")
    user, password = credential_pair(args)
    body = args.body or ""
    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as handle:
            body = handle.read()
    msg = EmailMessage()
    msg["From"] = args.from_addr or user
    msg["To"] = ", ".join(args.to)
    if args.cc:
        msg["Cc"] = ", ".join(args.cc)
    msg["Subject"] = args.subject
    msg.set_content(body)
    recipients = args.to + (args.cc or [])
    with smtplib.SMTP_SSL(args.smtp_host, args.smtp_port, context=ssl.create_default_context()) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg, from_addr=msg["From"], to_addrs=recipients)
    print("Sent.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Access XMU mail through IMAP/SMTP.")
    parser.add_argument("--user", help="Mailbox username/email. Defaults to XMU_MAIL_USER.")
    parser.add_argument("--imap-host", default=IMAP_HOST)
    parser.add_argument("--imap-port", type=int, default=IMAP_PORT)
    parser.add_argument("--smtp-host", default=SMTP_HOST)
    parser.add_argument("--smtp-port", type=int, default=SMTP_PORT)
    subparsers = parser.add_subparsers(dest="command", required=True)

    folders = subparsers.add_parser("folders", help="List IMAP folders.")
    folders.set_defaults(func=command_folders)

    search = subparsers.add_parser("search", help="Search messages and print headers.")
    search.add_argument("--folder", default="INBOX")
    search.add_argument("--query", default="ALL", help='IMAP search query, e.g. "UNSEEN" or "FROM example@xmu.edu.cn".')
    search.add_argument("--limit", type=int, default=10)
    search.set_defaults(func=command_search)

    read = subparsers.add_parser("read", help="Read one message by UID.")
    read.add_argument("--folder", default="INBOX")
    read.add_argument("--uid", required=True)
    read.add_argument("--max-chars", type=int, default=12000)
    read.set_defaults(func=command_read)

    send = subparsers.add_parser("send", help="Send a plain-text email.")
    send.add_argument("--to", action="append", required=True)
    send.add_argument("--cc", action="append")
    send.add_argument("--from-addr")
    send.add_argument("--subject", required=True)
    send.add_argument("--body")
    send.add_argument("--body-file")
    send.add_argument("--confirm-send", required=True)
    send.set_defaults(func=command_send)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
