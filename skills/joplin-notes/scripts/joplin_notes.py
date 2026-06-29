import argparse
import json
import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
import time
from pathlib import Path

DEFAULT_DB = Path.home() / ".config" / "joplin-desktop" / "database.sqlite"


def connect(db_path: str | None, write: bool = False) -> sqlite3.Connection:
    path = Path(db_path).expanduser() if db_path else DEFAULT_DB
    if not path.exists():
        raise SystemExit(f"Joplin database not found: {path}")
    if write:
        con = sqlite3.connect(str(path))
    else:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def ms_to_iso(ms: int | None) -> str | None:
    if not ms:
        return None
    import datetime as _dt

    return _dt.datetime.fromtimestamp(ms / 1000).isoformat(timespec="seconds")


def row_to_dict(row: sqlite3.Row, include_body: bool = False) -> dict:
    data = dict(row)
    for key in ("created_time", "updated_time", "user_created_time", "user_updated_time"):
        if key in data:
            data[key + "_iso"] = ms_to_iso(data[key])
    if not include_body and "body" in data:
        data["body_len"] = len(data.get("body") or "")
        del data["body"]
    return data


def print_json(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def list_notebooks(args) -> None:
    con = connect(args.db)
    rows = con.execute(
        """
        SELECT id, title, parent_id, updated_time
        FROM folders
        WHERE deleted_time = 0
        ORDER BY lower(title)
        """
    ).fetchall()
    print_json([row_to_dict(r) for r in rows])


def recent(args) -> None:
    con = connect(args.db)
    rows = con.execute(
        """
        SELECT id, title, parent_id, updated_time, user_updated_time, length(body) AS body_len
        FROM notes
        WHERE deleted_time = 0
        ORDER BY updated_time DESC
        LIMIT ?
        """,
        (args.limit,),
    ).fetchall()
    print_json([row_to_dict(r) for r in rows])


def search(args) -> None:
    con = connect(args.db)
    like = f"%{args.query}%"
    rows = con.execute(
        """
        SELECT id, title, parent_id, updated_time, user_updated_time, length(body) AS body_len,
               CASE WHEN title LIKE ? THEN 1 ELSE 0 END AS title_hit
        FROM notes
        WHERE deleted_time = 0 AND (title LIKE ? OR body LIKE ?)
        ORDER BY title_hit DESC, updated_time DESC
        LIMIT ?
        """,
        (like, like, like, args.limit),
    ).fetchall()
    print_json([row_to_dict(r) for r in rows])


def find_note_by_title(con: sqlite3.Connection, title: str) -> sqlite3.Row:
    rows = con.execute(
        """
        SELECT id, title, parent_id, body, updated_time, user_updated_time, is_conflict
        FROM notes
        WHERE deleted_time = 0 AND title = ?
        """,
        (title,),
    ).fetchall()
    if len(rows) != 1:
        candidates = [row_to_dict(r) for r in rows]
        raise SystemExit(
            json.dumps(
                {
                    "error": "expected exactly one non-deleted note with this title",
                    "title": title,
                    "match_count": len(rows),
                    "matches": candidates,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return rows[0]


def read_title(args) -> None:
    con = connect(args.db)
    row = find_note_by_title(con, args.title)
    data = row_to_dict(row, include_body=not args.metadata_only)
    print_json(data)


def update_title(args) -> None:
    body = Path(args.body_file).read_text(encoding="utf-8")
    con = connect(args.db, write=True)
    row = find_note_by_title(con, args.title)
    now = int(time.time() * 1000)
    con.execute(
        """
        UPDATE notes
        SET body = ?, updated_time = ?, user_updated_time = ?
        WHERE id = ?
        """,
        (body, now, now, row["id"]),
    )
    con.commit()
    print_json({"updated": True, "title": args.title, "id": row["id"], "updated_time_iso": ms_to_iso(now)})


def append_title(args) -> None:
    addition = Path(args.body_file).read_text(encoding="utf-8")
    con = connect(args.db, write=True)
    row = find_note_by_title(con, args.title)
    current = row["body"] or ""
    separator = "\n\n" if current.strip() else ""
    body = current.rstrip() + separator + addition.strip() + "\n"
    now = int(time.time() * 1000)
    con.execute(
        """
        UPDATE notes
        SET body = ?, updated_time = ?, user_updated_time = ?
        WHERE id = ?
        """,
        (body, now, now, row["id"]),
    )
    con.commit()
    print_json({"appended": True, "title": args.title, "id": row["id"], "updated_time_iso": ms_to_iso(now)})


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Search, read, and safely update local Joplin notes.")
    parser.add_argument("--db", help="Path to Joplin database.sqlite. Defaults to the Windows Joplin Desktop profile path.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list-notebooks")
    p.set_defaults(func=list_notebooks)

    p = sub.add_parser("recent")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=recent)

    p = sub.add_parser("search")
    p.add_argument("--query", required=True)
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=search)

    p = sub.add_parser("read-title")
    p.add_argument("--title", required=True)
    p.add_argument("--metadata-only", action="store_true")
    p.set_defaults(func=read_title)

    p = sub.add_parser("update-title")
    p.add_argument("--title", required=True)
    p.add_argument("--body-file", required=True)
    p.set_defaults(func=update_title)

    p = sub.add_parser("append-title")
    p.add_argument("--title", required=True)
    p.add_argument("--body-file", required=True)
    p.set_defaults(func=append_title)

    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
