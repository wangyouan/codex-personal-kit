# zotero.sqlite — schema notes for read-only analysis

Read a consistent temporary snapshot, never write to the live library:

```python
source = sqlite3.connect(Path(DB).resolve().as_uri() + '?mode=ro', uri=True)
snapshot = sqlite3.connect(TEMP_DB)
source.backup(snapshot)
snapshot.close()
source.close()
c = sqlite3.connect(f'file:{TEMP_DB}?mode=ro', uri=True)
```

The bundled `scan_library.py` performs this backup in a temporary directory and
removes it automatically after reading. If a backup fails during an active
sync, retry after the sync settles. Do not close Zotero as a routine
prerequisite.

## Item basics

Fields live in a value-lookup table, not columns on `items`:

```sql
items(itemID, itemTypeID, key, dateAdded, dateModified)
itemTypes(itemTypeID, typeName)
fields(fieldID, fieldName)
itemData(itemID, fieldID, valueID)
itemDataValues(valueID, value)
deletedItems(itemID)              -- trash
```

Regular items only, trash excluded — the pattern every query starts from:

```python
REGULAR = ('journalArticle','preprint','report','bookSection','book',
           'thesis','newspaperArticle','magazineArticle','conferencePaper')
deleted = set(r[0] for r in cur.execute("SELECT itemID FROM deletedItems"))
rows = cur.execute(
  "SELECT i.itemID, i.key, it.typeName, i.dateAdded FROM items i "
  "JOIN itemTypes it ON i.itemTypeID = it.itemTypeID "
  "WHERE it.typeName IN %s" % str(REGULAR)).fetchall()
items = {r[0]: {'key': r[1], 'type': r[2], 'added': r[3]}
         for r in rows if r[0] not in deleted}
```

Excluding attachments/notes/annotations matters — they inflate counts several-fold (a 2,500-paper library has ~2,700 attachments).

Reading one field for all items:

```python
fieldID = {n: i for i, n in cur.execute("SELECT fieldID, fieldName FROM fields")}

def field_values(name, ids):
    fid = fieldID.get(name)
    out = {}
    for iid, val in cur.execute(
        "SELECT id.itemID, idv.value FROM itemData id "
        "JOIN itemDataValues idv ON id.valueID = idv.valueID "
        "WHERE id.fieldID = ?", (fid,)):
        if iid in ids:
            out[iid] = val
    return out
```

## Creators

```sql
creators(creatorID, firstName, lastName, fieldMode)
itemCreators(itemID, creatorID, creatorTypeID, orderIndex)
```

`fieldMode` 0 = two-field, 1 = single-field. `orderIndex` preserves author order — always `ORDER BY itemID, orderIndex`.

```python
creators = defaultdict(list)
for iid, last, first, fm, o in cur.execute(
    "SELECT ic.itemID, c.lastName, c.firstName, c.fieldMode, ic.orderIndex "
    "FROM itemCreators ic JOIN creators c ON ic.creatorID = c.creatorID "
    "ORDER BY ic.itemID, ic.orderIndex"):
    if iid in items:
        creators[iid].append({'last': last or '', 'first': first or '',
                              'fm': fm, 'o': o})
```

Note `orderIndex` — the generated script uses it to address the right creator slot.

## Collections

```sql
collections(collectionID, collectionName, parentCollectionID)
collectionItems(collectionID, itemID)
```

Arbitrarily nested; `parentCollectionID IS NULL` means top level. An item can belong to many collections.

```python
colls  = cur.execute("SELECT collectionID, collectionName, parentCollectionID "
                     "FROM collections").fetchall()
cname  = {r[0]: r[1] for r in colls}
parent = {r[0]: r[2] for r in colls}

def path(cid):
    parts = []
    while cid is not None:
        parts.append(cname[cid])
        cid = parent[cid]
    return '/'.join(reversed(parts))
```

Full paths, not bare names — the same subcollection name often appears under different parents.

Recursive counts (direct + descendants) are what you want when reporting tree size:

```python
children = defaultdict(list)
for cid, n, p in colls:
    children[p].append(cid)

def total(cid):
    return direct.get(cid, 0) + sum(total(ch) for ch in children.get(cid, []))
```

## Tags

```sql
tags(tagID, name)
itemTags(itemID, tagID, type)     -- type 0 = manual, 1 = automatic
```

`tags` accumulates orphans — rows no longer attached to any item. A library with 755 tags in use can carry ~3,000 orphan rows; count usage through `itemTags`, not `tags`.

## Attachments

```sql
itemAttachments(itemID, parentItemID, contentType, path)
```

`parentItemID IS NULL` means an orphan attachment (a PDF with no parent record).

## Useful diagnostics

Duplicate DOIs — same DOI on different items is either a true duplicate or a data-entry error:

```python
from collections import defaultdict
dm = defaultdict(list)
for iid, d in doi.items():
    if d.strip():
        dm[d.strip().lower()].append(iid)
dupes = {k: v for k, v in dm.items() if len(v) > 1}
```

Journal-name variants — normalize aggressively, then group:

```python
def norm(s):
    s = re.sub(r'^the\s+', '', s.lower().strip())
    return re.sub(r'[^a-z0-9]+', '', s.replace('and', '').replace('&', ''))
```

This catches `Journal of Finance` / `The Journal of Finance` and `Journal of Banking & Finance` / `... and Finance` in one pass.

## Python gotchas

`\w` in Python's `re` matches CJK characters. An email-stripping pattern like `[\w.\-]+@[\w.\-]+` will eat a Chinese name attached to an address. Use explicit ASCII classes:

```python
EMAIL = re.compile(r'[A-Za-z0-9._%\-]+@[A-Za-z0-9._%\-]+')
```

Detect CJK with `re.search(r'[一-鿿]', s)` and branch on it — capitalization and name-splitting rules do not apply.
