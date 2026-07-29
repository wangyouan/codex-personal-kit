#!/usr/bin/env bash
# Export the tables we need from a Zotero library into JSON.
#
# Why a shell script: some Python installs (notably Anaconda on Windows) ship a
# broken _sqlite3 DLL, so we shell out to the sqlite3 CLI instead of importing
# sqlite3 in Python.
#
# Usage:
#   ./export_zotero.sh [ZOTERO_DIR] [OUT_DIR]
# Defaults:
#   ZOTERO_DIR=$HOME/Zotero    OUT_DIR=./corpus_raw
#
# Always works on a COPY of zotero.sqlite — never query the live database while
# Zotero is running.

set -euo pipefail

ZOTERO_DIR="${1:-$HOME/Zotero}"
OUT_DIR="${2:-./corpus_raw}"
DB_SRC="$ZOTERO_DIR/zotero.sqlite"
DB="$OUT_DIR/z.sqlite"

command -v sqlite3 >/dev/null || { echo "sqlite3 not found on PATH" >&2; exit 1; }
[ -f "$DB_SRC" ] || { echo "no zotero.sqlite at $DB_SRC" >&2; exit 1; }

mkdir -p "$OUT_DIR"
cp "$DB_SRC" "$DB"

# Zotero stores every field as a row in itemData -> itemDataValues, so we pull
# each field we want with a correlated subquery.
F="(SELECT idv.value FROM itemData id JOIN fields f ON id.fieldID=f.fieldID JOIN itemDataValues idv ON id.valueID=idv.valueID WHERE id.itemID=i.itemID AND f.fieldName="

sqlite3 "$DB" ".mode json" ".once $OUT_DIR/items.json" "
SELECT i.itemID AS id,
 ${F}'title') AS title,
 ${F}'publicationTitle') AS venue,
 ${F}'date') AS date,
 ${F}'abstractNote') AS abstract
FROM items i JOIN itemTypes it ON i.itemTypeID=it.itemTypeID
WHERE it.typeName='journalArticle';"

sqlite3 "$DB" ".mode json" ".once $OUT_DIR/pdfs.json" "
SELECT ia.parentItemID AS parent, att.key AS key, ia.path AS path
FROM itemAttachments ia JOIN items att ON ia.itemID=att.itemID
WHERE ia.contentType='application/pdf' AND ia.path LIKE 'storage:%';"

sqlite3 "$DB" ".mode json" ".once $OUT_DIR/colls.json" "
SELECT ci.itemID AS id, c.collectionName AS coll
FROM collectionItems ci JOIN collections c ON ci.collectionID=c.collectionID;"

echo "wrote items.json / pdfs.json / colls.json to $OUT_DIR"
