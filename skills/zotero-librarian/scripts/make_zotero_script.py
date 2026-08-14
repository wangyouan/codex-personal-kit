"""Emit an idempotent Zotero JavaScript file from a plan.

The JS boilerplate (path-based collection lookup, transaction handling,
old-value verification, counters) is identical every time and easy to get
subtly wrong, so build it here instead of by hand.

    from make_zotero_script import build

    build('out.js',
          title='File new ESG papers',
          description=['Adds 24 recently imported papers to subcollections.',
                       'Existing collections are preserved.'],
          collections=[{'key': 'ABCD1234',
                        'path': 'ESG & Sustainability/Climate Risk',
                        't': 'Climate risk and firm value'}],
          tags=[{'key': 'ABCD1234', 'add': ['Climate'], 'remove': ['climate'],
                 't': 'Climate risk and firm value'}],
          fields=[{'key': 'ABCD1234',
                   'set': {'publicationTitle': 'The Journal of Finance'},
                   'expect': {'publicationTitle': 'Journal of Finance'},
                   't': 'Climate risk and firm value'}],
          new_collections=[{'path': 'ESG & Sustainability/Green Finance'}])

Every section is optional. Validate the result before handing it over:

    python3 make_zotero_script.py --check out.js
"""
import json
import subprocess
import sys
import tempfile

_HEADER = """/* ===================================================================
   {title}
   Generated {stamp}

{description}

   Safe to run more than once: every change is checked against the current
   state first, and value replacements are skipped if the item no longer
   matches what was scanned.

   How to run: Zotero -> Tools -> Developer -> Run JavaScript -> paste -> Run
   =================================================================== */

var libraryID = Zotero.Libraries.userLibraryID;
var log = [];
var nAdd = 0, nHave = 0, nSkip = 0, nMiss = 0, nField = 0, nTagAdd = 0, nTagDel = 0;

var allColls = Zotero.Collections.getByLibrary(libraryID, true);

/* Resolve by full path — the same subcollection name often exists under
   several parents, so matching on name alone picks the wrong one. */
function findByPath(path) {{
  var parts = path.split('/');
  var cur = null;
  for (var i = 0; i < parts.length; i++) {{
    var pid = cur ? cur.id : null;
    cur = allColls.find(function (c) {{
      return c.name === parts[i] && ((pid === null && !c.parentID) || c.parentID === pid);
    }});
    if (!cur) return null;
  }}
  return cur;
}}

function setIf(item, field, value) {{
  var fid = Zotero.ItemFields.getID(field);
  if (fid && Zotero.ItemFields.isValidForType(fid, item.itemTypeID)) {{
    item.setField(field, value);
    return true;
  }}
  return false;
}}
"""

_NEW_COLLS = """
/* ---- create collections that do not exist yet ---- */
var NEW_COLLS = {data};
for (var i = 0; i < NEW_COLLS.length; i++) {{
  var spec = NEW_COLLS[i];
  if (findByPath(spec.path)) continue;
  var parts = spec.path.split('/');
  var name = parts.pop();
  var parent = parts.length ? findByPath(parts.join('/')) : null;
  if (parts.length && !parent) {{ log.push("! parent missing for " + spec.path); continue; }}
  var coll = new Zotero.Collection();
  coll.libraryID = libraryID;
  coll.name = name;
  if (parent) coll.parentID = parent.id;
  await coll.saveTx();
  log.push("+ new collection: " + spec.path);
  allColls = Zotero.Collections.getByLibrary(libraryID, true);   // refresh cache
}}
"""

_BODY = """
var COLLS  = {colls};
var TAGS   = {tags};
var FIELDS = {fields};

await Zotero.DB.executeTransaction(async function () {{

  for (var i = 0; i < COLLS.length; i++) {{
    var rec = COLLS[i];
    var item = Zotero.Items.getByLibraryAndKey(libraryID, rec.key);
    if (!item) {{ nMiss++; log.push("? item not found: " + (rec.t || rec.key)); continue; }}
    var target = findByPath(rec.path);
    if (!target) {{ nSkip++; log.push("! collection not found: " + rec.path); continue; }}
    if (item.getCollections().includes(target.id)) {{ nHave++; continue; }}
    item.addToCollection(target.id);
    await item.save();
    nAdd++;
    log.push("-> " + (rec.t || rec.key) + "  =>  " + rec.path);
  }}

  for (var j = 0; j < TAGS.length; j++) {{
    var tr = TAGS[j];
    var it2 = Zotero.Items.getByLibraryAndKey(libraryID, tr.key);
    if (!it2) {{ nMiss++; continue; }}
    var names = it2.getTags().map(function (t) {{ return t.tag; }});
    var touched = false;
    var rm = tr.remove || [];
    for (var r = 0; r < rm.length; r++) {{
      if (names.indexOf(rm[r]) !== -1) {{ it2.removeTag(rm[r]); touched = true; nTagDel++; }}
    }}
    var ad = tr.add || [];
    for (var a = 0; a < ad.length; a++) {{
      if (names.indexOf(ad[a]) === -1) {{ it2.addTag(ad[a], 0); touched = true; nTagAdd++; }}
    }}
    if (touched) {{
      await it2.save();
      log.push("# " + (tr.t || tr.key)
               + (ad.length ? "  +[" + ad.join(", ") + "]" : "")
               + (rm.length ? "  -[" + rm.join(", ") + "]" : ""));
    }}
  }}

  for (var k = 0; k < FIELDS.length; k++) {{
    var fr = FIELDS[k];
    var it3 = Zotero.Items.getByLibraryAndKey(libraryID, fr.key);
    if (!it3) {{ nMiss++; continue; }}

    if (fr.type) {{
      var tid = Zotero.ItemTypes.getID(fr.type);
      /* set the type before the fields: it decides which fields are valid */
      if (it3.itemTypeID !== tid) it3.setType(tid);
    }}

    /* If the item no longer matches what was scanned, the user edited it
       since — leave their version alone. */
    /* Skip only if the field matches neither the scanned value nor the
       intended one — matching the intended value just means this already ran. */
    var stale = false;
    for (var ef in (fr.expect || {{}})) {{
      var now = it3.getField(ef);
      var want = (fr.set || {{}})[ef];
      if (now !== fr.expect[ef] && now !== want) stale = true;
    }}
    if (stale) {{ nSkip++; log.push("~ changed since scan, skipped: " + (fr.t || fr.key)); continue; }}

    var wrote = false;
    for (var f in (fr.set || {{}})) {{
      var val = fr.set[f];
      if (val === "" || val === null || val === undefined) continue;   // never blank a field
      if (it3.getField(f) === val) continue;
      if (setIf(it3, f, val)) wrote = true;
    }}
    if (fr.creators) {{
      /* Compare before writing, otherwise every rerun re-saves the item
         and bumps dateModified for no reason. */
      var cur = it3.getCreators().map(function (c) {{
        return [c.lastName, c.firstName, c.fieldMode || 0].join('\u0001');
      }}).join('\u0002');
      var next = fr.creators.map(function (c) {{
        return [c.lastName, c.firstName || '', c.fieldMode || 0].join('\u0001');
      }}).join('\u0002');
      if (cur !== next) {{ it3.setCreators(fr.creators); wrote = true; }}
    }}
    if (wrote) {{ await it3.save(); nField++; log.push("* " + (fr.t || fr.key)); }}
  }}
}});
"""

_FOOTER = """
log.push("");
log.push("=== done: " + nAdd + " filed (" + nHave + " already), "
         + nField + " items edited, tags +" + nTagAdd + "/-" + nTagDel
         + ", " + nSkip + " skipped, " + nMiss + " not found ===");
return log.join("\\n");
"""


def build(out_path, title, description=None, collections=None, tags=None,
          fields=None, new_collections=None, stamp=None):
    """Write the JS file and return its text."""
    import datetime
    stamp = stamp or datetime.date.today().isoformat()
    desc = description or []
    if isinstance(desc, str):
        desc = [desc]
    desc_block = '\n'.join('   ' + line for line in desc)

    js = _HEADER.format(title=title, stamp=stamp, description=desc_block)
    if new_collections:
        js += _NEW_COLLS.format(data=json.dumps(new_collections, ensure_ascii=False, indent=1))
    js += _BODY.format(
        colls=json.dumps(collections or [], ensure_ascii=False, indent=1),
        tags=json.dumps(tags or [], ensure_ascii=False, indent=1),
        fields=json.dumps(fields or [], ensure_ascii=False, indent=1))
    js += _FOOTER

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(js)
    return js


def check(path):
    """Syntax-check. Zotero wraps the code in an async function, so top-level
    await/return are valid there but not to a bare `node --check`."""
    src = open(path, encoding='utf-8').read()
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False,
                                     encoding='utf-8') as t:
        t.write('(async function(){\n' + src + '\n})();')
        tmp = t.name
    r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"syntax OK: {path}")
        return True
    print(f"SYNTAX ERROR in {path}:\n{r.stderr}")
    return False


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--check':
        sys.exit(0 if check(sys.argv[2]) else 1)
    print(__doc__)
