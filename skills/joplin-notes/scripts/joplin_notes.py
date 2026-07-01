import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_PROFILE = Path.home() / ".config" / "joplin-desktop"
DEFAULT_DB = DEFAULT_PROFILE / "database.sqlite"
DEFAULT_PORTS = range(41184, 41195)


def print_json(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def ms_to_iso(ms: int | None) -> str | None:
    if not ms:
        return None
    import datetime as _dt

    return _dt.datetime.fromtimestamp(ms / 1000).isoformat(timespec="seconds")


def note_summary(item: dict) -> dict:
    data = dict(item)
    for key in ("created_time", "updated_time", "user_created_time", "user_updated_time"):
        if key in data:
            data[key + "_iso"] = ms_to_iso(data.get(key))
    if "body" in data:
        data["body_len"] = len(data.get("body") or "")
        del data["body"]
    return data


def load_settings_token(profile: str | None) -> str | None:
    profile_path = Path(profile).expanduser() if profile else DEFAULT_PROFILE
    settings_path = profile_path / "settings.json"
    if not settings_path.exists():
        return None
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return settings.get("api.token") or settings.get("apiToken")


def resolve_token(args) -> str | None:
    return (
        args.token
        or os.environ.get("JOPLIN_TOKEN")
        or os.environ.get("JOPLIN_API_TOKEN")
        or load_settings_token(args.profile)
    )


def ping_port(port: int, timeout: float = 1.5) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/ping", timeout=timeout) as res:
            return b"JoplinClipperServer" in res.read()
    except Exception:
        return False


def resolve_port(args) -> int | None:
    if args.port:
        return int(args.port)
    env_port = os.environ.get("JOPLIN_PORT")
    if env_port:
        return int(env_port)
    for port in DEFAULT_PORTS:
        if ping_port(port):
            return port
    return None


def api_base(args) -> tuple[str, str]:
    token = resolve_token(args)
    if not token:
        raise SystemExit("Joplin API token not found. Pass --token, set JOPLIN_TOKEN, or enable it in Joplin settings.")
    port = resolve_port(args)
    if not port:
        raise SystemExit("Joplin Web Clipper API is not reachable on ports 41184-41194.")
    return f"http://127.0.0.1:{port}", token


def api_request(args, method: str, path: str, params: dict | None = None, payload: dict | None = None) -> dict:
    base, token = api_base(args)
    query = dict(params or {})
    query["token"] = token
    url = f"{base}{path}?{urllib.parse.urlencode(query)}"
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            raw = res.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Joplin API error {exc.code}: {detail}") from exc
    if not raw:
        return {}
    return json.loads(raw)


def api_paginate(args, path: str, params: dict | None = None) -> list[dict]:
    page = 1
    out = []
    while True:
        query = dict(params or {})
        query["page"] = page
        data = api_request(args, "GET", path, query)
        out.extend(data.get("items", []))
        if not data.get("has_more"):
            return out
        page += 1


def api_list_notebooks(args) -> None:
    rows = api_paginate(args, "/folders", {"fields": "id,parent_id,title,updated_time", "limit": 100})
    print_json(rows)


def api_recent(args) -> None:
    data = api_request(
        args,
        "GET",
        "/notes",
        {
            "fields": "id,parent_id,title,updated_time,user_updated_time",
            "order_by": "updated_time",
            "order_dir": "DESC",
            "limit": args.limit,
        },
    )
    rows = data.get("items", [])
    print_json([note_summary(r) for r in rows])


def api_search(args) -> None:
    data = api_request(
        args,
        "GET",
        "/search",
        {
            "query": args.query,
            "type": "note",
            "fields": "id,parent_id,title,updated_time,user_updated_time",
            "limit": args.limit,
        },
    )
    rows = data.get("items", [])
    print_json([note_summary(r) for r in rows])


def api_find_note_by_title(args, title: str) -> dict:
    rows = api_paginate(
        args,
        "/search",
        {
            "query": title,
            "type": "note",
            "fields": "id,parent_id,title,updated_time,user_updated_time",
            "limit": 100,
        },
    )
    matches = [r for r in rows if r.get("title") == title]
    if len(matches) != 1:
        raise SystemExit(
            json.dumps(
                {
                    "error": "expected exactly one note with this exact title",
                    "title": title,
                    "match_count": len(matches),
                    "matches": [note_summary(r) for r in matches],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return matches[0]


def api_find_folder_id(args, title: str | None) -> str | None:
    if not title:
        return None
    rows = api_paginate(args, "/folders", {"fields": "id,parent_id,title", "limit": 100})
    matches = [r for r in rows if r.get("title") == title]
    if len(matches) != 1:
        raise SystemExit(
            json.dumps(
                {
                    "error": "expected exactly one notebook with this exact title",
                    "title": title,
                    "match_count": len(matches),
                    "matches": matches,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return matches[0]["id"]


def api_create_notebook(args) -> None:
    rows = api_paginate(args, "/folders", {"fields": "id,parent_id,title", "limit": 100})
    parent_id = None
    if args.parent:
        parent_matches = [r for r in rows if r.get("title") == args.parent]
        if len(parent_matches) != 1:
            raise SystemExit(
                json.dumps(
                    {
                        "error": "expected exactly one parent notebook with this exact title",
                        "title": args.parent,
                        "match_count": len(parent_matches),
                        "matches": parent_matches,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        parent_id = parent_matches[0]["id"]
    existing = [r for r in rows if r.get("title") == args.title and (not parent_id or r.get("parent_id") == parent_id)]
    if existing and not args.force:
        print_json({"created": False, "already_exists": True, "notebook": existing[0]})
        return
    payload = {"title": args.title}
    if parent_id:
        payload["parent_id"] = parent_id
    data = api_request(args, "POST", "/folders", payload=payload)
    print_json({"created": True, "notebook": data})


def api_read_id(args, note_id: str, metadata_only: bool = False) -> None:
    fields = "id,parent_id,title,updated_time,user_updated_time" if metadata_only else "id,parent_id,title,body,updated_time,user_updated_time"
    data = api_request(args, "GET", f"/notes/{note_id}", {"fields": fields})
    print_json(note_summary(data) if metadata_only else data)


def api_read_title(args) -> None:
    note = api_find_note_by_title(args, args.title)
    api_read_id(args, note["id"], args.metadata_only)


def api_create_note(args) -> None:
    body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else (args.body or "")
    payload = {"title": args.title, "body": body}
    folder_id = api_find_folder_id(args, args.notebook)
    if folder_id:
        payload["parent_id"] = folder_id
    data = api_request(args, "POST", "/notes", payload=payload)
    print_json({"created": True, "id": data.get("id"), "title": data.get("title"), "parent_id": data.get("parent_id")})


def api_update_title(args) -> None:
    body = Path(args.body_file).read_text(encoding="utf-8")
    note = api_find_note_by_title(args, args.title)
    data = api_request(args, "PUT", f"/notes/{note['id']}", payload={"body": body})
    print_json({"updated": True, "id": note["id"], "title": data.get("title", args.title)})


def api_append_title(args) -> None:
    addition = Path(args.body_file).read_text(encoding="utf-8")
    note = api_find_note_by_title(args, args.title)
    current = api_request(args, "GET", f"/notes/{note['id']}", {"fields": "id,title,body"})
    existing = current.get("body") or ""
    separator = "\n\n" if existing.strip() else ""
    body = existing.rstrip() + separator + addition.strip() + "\n"
    data = api_request(args, "PUT", f"/notes/{note['id']}", payload={"body": body})
    print_json({"appended": True, "id": note["id"], "title": data.get("title", args.title)})


def sqlite_connect(db_path: str | None, write: bool = False) -> sqlite3.Connection:
    path = Path(db_path).expanduser() if db_path else DEFAULT_DB
    if not path.exists():
        raise SystemExit(f"Joplin database not found: {path}")
    con = sqlite3.connect(str(path) if write else f"file:{path}?mode=ro", uri=not write)
    con.row_factory = sqlite3.Row
    return con


def row_to_dict(row: sqlite3.Row, include_body: bool = False) -> dict:
    data = dict(row)
    for key in ("created_time", "updated_time", "user_created_time", "user_updated_time"):
        if key in data:
            data[key + "_iso"] = ms_to_iso(data[key])
    if not include_body and "body" in data:
        data["body_len"] = len(data.get("body") or "")
        del data["body"]
    return data


def sqlite_list_notebooks(args) -> None:
    con = sqlite_connect(args.db)
    rows = con.execute(
        "SELECT id, title, parent_id, updated_time FROM folders WHERE deleted_time = 0 ORDER BY lower(title)"
    ).fetchall()
    print_json([row_to_dict(r) for r in rows])


def sqlite_recent(args) -> None:
    con = sqlite_connect(args.db)
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


def sqlite_search(args) -> None:
    con = sqlite_connect(args.db)
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


def sqlite_find_note_by_title(con: sqlite3.Connection, title: str) -> sqlite3.Row:
    rows = con.execute(
        """
        SELECT id, title, parent_id, body, updated_time, user_updated_time, is_conflict
        FROM notes
        WHERE deleted_time = 0 AND title = ?
        """,
        (title,),
    ).fetchall()
    if len(rows) != 1:
        raise SystemExit(
            json.dumps(
                {
                    "error": "expected exactly one non-deleted note with this title",
                    "title": title,
                    "match_count": len(rows),
                    "matches": [row_to_dict(r) for r in rows],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return rows[0]


def sqlite_read_title(args) -> None:
    con = sqlite_connect(args.db)
    row = sqlite_find_note_by_title(con, args.title)
    print_json(row_to_dict(row, include_body=not args.metadata_only))


def sqlite_update_title(args) -> None:
    body = Path(args.body_file).read_text(encoding="utf-8")
    con = sqlite_connect(args.db, write=True)
    row = sqlite_find_note_by_title(con, args.title)
    now = int(time.time() * 1000)
    con.execute("UPDATE notes SET body = ?, updated_time = ?, user_updated_time = ? WHERE id = ?", (body, now, now, row["id"]))
    con.commit()
    print_json({"updated": True, "backend": "sqlite", "title": args.title, "id": row["id"], "updated_time_iso": ms_to_iso(now)})


def sqlite_append_title(args) -> None:
    addition = Path(args.body_file).read_text(encoding="utf-8")
    con = sqlite_connect(args.db, write=True)
    row = sqlite_find_note_by_title(con, args.title)
    current = row["body"] or ""
    separator = "\n\n" if current.strip() else ""
    body = current.rstrip() + separator + addition.strip() + "\n"
    now = int(time.time() * 1000)
    con.execute("UPDATE notes SET body = ?, updated_time = ?, user_updated_time = ? WHERE id = ?", (body, now, now, row["id"]))
    con.commit()
    print_json({"appended": True, "backend": "sqlite", "title": args.title, "id": row["id"], "updated_time_iso": ms_to_iso(now)})


def should_use_api(args) -> bool:
    if args.backend == "api":
        return True
    if args.backend == "sqlite":
        return False
    return bool(resolve_token(args) and resolve_port(args))


def dispatch(args) -> None:
    backend_api = should_use_api(args)
    api_funcs = {
        "list-notebooks": api_list_notebooks,
        "recent": api_recent,
        "search": api_search,
        "read-title": api_read_title,
        "read-id": lambda a: api_read_id(a, a.id, a.metadata_only),
        "create-notebook": api_create_notebook,
        "create-note": api_create_note,
        "update-title": api_update_title,
        "append-title": api_append_title,
    }
    sqlite_funcs = {
        "list-notebooks": sqlite_list_notebooks,
        "recent": sqlite_recent,
        "search": sqlite_search,
        "read-title": sqlite_read_title,
        "update-title": sqlite_update_title,
        "append-title": sqlite_append_title,
    }
    funcs = api_funcs if backend_api else sqlite_funcs
    if args.command not in funcs:
        raise SystemExit(f"Command '{args.command}' requires the Joplin Web Clipper API. Use --backend api.")
    funcs[args.command](args)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Access local Joplin notes via Web Clipper API, with SQLite fallback.")
    parser.add_argument("--backend", choices=["auto", "api", "sqlite"], default="auto")
    parser.add_argument("--token", help="Joplin Web Clipper API token. Prefer JOPLIN_TOKEN for repeat use.")
    parser.add_argument("--port", type=int, help="Joplin Web Clipper port. Defaults to JOPLIN_PORT or scan 41184-41194.")
    parser.add_argument("--profile", help="Joplin profile path for settings.json token discovery.")
    parser.add_argument("--db", help="SQLite fallback database path.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-notebooks")

    p = sub.add_parser("recent")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("search")
    p.add_argument("--query", required=True)
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("read-title")
    p.add_argument("--title", required=True)
    p.add_argument("--metadata-only", action="store_true")

    p = sub.add_parser("read-id")
    p.add_argument("--id", required=True)
    p.add_argument("--metadata-only", action="store_true")

    p = sub.add_parser("create-notebook")
    p.add_argument("--title", required=True)
    p.add_argument("--parent", help="Exact parent notebook title.")
    p.add_argument("--force", action="store_true", help="Create even if a matching title already exists under the parent.")

    p = sub.add_parser("create-note")
    p.add_argument("--title", required=True)
    p.add_argument("--notebook", help="Exact notebook title.")
    body_group = p.add_mutually_exclusive_group()
    body_group.add_argument("--body")
    body_group.add_argument("--body-file")

    p = sub.add_parser("update-title")
    p.add_argument("--title", required=True)
    p.add_argument("--body-file", required=True)

    p = sub.add_parser("append-title")
    p.add_argument("--title", required=True)
    p.add_argument("--body-file", required=True)

    args = parser.parse_args(argv)
    dispatch(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
