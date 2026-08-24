# Zotero JavaScript API — patterns for generated scripts

Runs in **Tools → Developer → Run JavaScript**. Zotero wraps the pasted code in an async function, so top-level `await` and `return` work. `return` a string to display it in the result pane.

## Skeleton

```javascript
var libraryID = Zotero.Libraries.userLibraryID;
var log = [];
var changed = 0, already = 0, skipped = 0, missing = 0;

await Zotero.DB.executeTransaction(async function () {
  for (var i = 0; i < DATA.length; i++) {
    var rec = DATA[i];
    var item = Zotero.Items.getByLibraryAndKey(libraryID, rec.key);
    if (!item) { missing++; continue; }
    // ... mutate ...
    await item.save();          // inside a transaction: save(), NOT saveTx()
    changed++;
  }
});

log.push("done: changed " + changed + ", already " + already + ", skipped " + skipped);
return log.join("\n");
```

## Transactions: the one thing to get right

- Inside `Zotero.DB.executeTransaction(...)` → `await item.save()`
- Outside a transaction → `await item.saveTx()`

Using `saveTx()` inside a transaction throws a nested-transaction error; using `save()` outside silently does not commit. When a script "runs without error but nothing changed", this is almost always why.

Batch related edits in one transaction — it is faster and atomic. For a handful of items, `saveTx()` without a transaction is fine.

## Items

```javascript
var item = Zotero.Items.getByLibraryAndKey(libraryID, "ABCD1234");  // by 8-char key
var all  = await Zotero.Items.getAll(libraryID, true);              // true = top-level only
item.isRegularItem();          // excludes attachments/notes/annotations
item.getDisplayTitle();
```

### Fields

```javascript
item.getField("title");
item.setField("publicationTitle", "The Journal of Finance");
```

Setting a field invalid for the item type throws. Guard when the type may vary:

```javascript
function setIf(item, field, value) {
  var fid = Zotero.ItemFields.getID(field);
  if (fid && Zotero.ItemFields.isValidForType(fid, item.itemTypeID)) {
    item.setField(field, value);
    return true;
  }
  return false;
}
```

Common field names: `title`, `abstractNote`, `publicationTitle`, `date`, `DOI`, `url`, `volume`, `issue`, `pages`, `ISSN`, `language`, `extra`, `shortTitle`. Working papers use `repository`, `archiveID`, `number`, `seriesTitle`, `genre`.

### Item type

```javascript
var preID = Zotero.ItemTypes.getID("preprint");
if (item.itemTypeID !== preID) item.setType(preID);
```

Changing type drops fields invalid for the new type — set the type *first*, then the fields, so `isValidForType` checks against the new type.

Useful types: `journalArticle`, `preprint`, `report`, `bookSection`, `book`, `thesis`, `conferencePaper`.

## Creators

`getCreators()` returns a copy; mutate it and set it back.

```javascript
var cs = item.getCreators();
cs[0].lastName  = "Ritter";
cs[0].firstName = "Jay R.";
cs[0].fieldMode = 0;          // 0 = two-field (last, first); 1 = single-field
item.setCreators(cs);
await item.save();
```

Replacing wholesale:

```javascript
item.setCreators([
  { creatorType: "author", firstName: "Nicola", lastName: "Borri" },
  { creatorType: "author", firstName: "Yukun",  lastName: "Liu" }
]);
```

`fieldMode: 1` puts the whole name in `lastName` and leaves `firstName` empty — right for institutions and for CJK names where splitting is unnatural.

## Tags

```javascript
var names = item.getTags().map(function (t) { return t.tag; });
if (names.indexOf("Trade War") === -1) item.addTag("Trade War", 0);   // 0 = manual, 1 = automatic
item.removeTag("trade war");
await item.save();
```

Renaming a tag across the whole library, rather than per item:

```javascript
await Zotero.Tags.rename(libraryID, "old name", "New Name");
```

## Collections

```javascript
var all = Zotero.Collections.getByLibrary(libraryID, true);   // true = recursive

function findByPath(path) {           // "Corporate Finance/Capital Structure"
  var parts = path.split('/');
  var cur = null;
  for (var i = 0; i < parts.length; i++) {
    var pid = cur ? cur.id : null;
    cur = all.find(function (c) {
      return c.name === parts[i] && ((pid === null && !c.parentID) || c.parentID === pid);
    });
    if (!cur) return null;
  }
  return cur;
}
```

For a read-only live collection export while Zotero remains open, use the same
API without calling `save`, `saveTx`, or `eraseTx`:

```javascript
var libraryID = Zotero.Libraries.userLibraryID;
var collections = Zotero.Collections.getByLibrary(libraryID, true);
var byID = {};
collections.forEach(function (c) { byID[c.id] = c; });
function pathOf(c) {
  var parts = [];
  while (c) {
    parts.unshift(c.name);
    c = c.parentID ? byID[c.parentID] : null;
  }
  return parts.join('/');
}
var rows = collections.map(function (c) {
  return { id: c.id, name: c.name, parentID: c.parentID, path: pathOf(c) };
});
return JSON.stringify(rows, null, 2);
```

This reads Zotero's current in-memory/library state and does not require
closing the application. Use the Python scanner's temporary SQLite snapshot
when a full SQL inventory is needed instead.

Matching on name alone breaks when the same name exists under several parents (e.g. `Machine Learning` under both `Quantitative Methods` and `Topics`). Always resolve by full path.

Creating, adding, removing:

```javascript
var coll = new Zotero.Collection();
coll.libraryID = libraryID;
coll.name = "Labor Unions";
coll.parentID = parent.id;      // omit for top level
await coll.saveTx();

if (!item.getCollections().includes(coll.id)) {
  item.addToCollection(coll.id);
  await item.save();
}

item.removeFromCollection(coll.id);
await coll.eraseTx();           // deletes the collection; items stay in the library
```

After creating collections, re-fetch `Zotero.Collections.getByLibrary(...)` before looking them up — the cached array is stale.

## Trash

```javascript
item.deleted = true;            // move to trash (recoverable)
await item.save();
await item.eraseTx();           // permanent — avoid in generated scripts
```

Prefer trashing over erasing. Removing something from a collection is not deletion; it stays in the library.
