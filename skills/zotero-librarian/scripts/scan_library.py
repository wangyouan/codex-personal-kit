#!/usr/bin/env python3
"""Read-only inventory of a Zotero library.

Never writes. Open the live zotero.sqlite read-only rather than copying it —
copying a large library races with Zotero's own writes and often yields
'database disk image is malformed'. Ask the user to close Zotero first.

    python3 scan_library.py /path/to/zotero.sqlite
    python3 scan_library.py DB --tree --tags
    python3 scan_library.py DB --recent 2026-08-01     # newly added items
    python3 scan_library.py DB --unfiled              # no collection / no tag
    python3 scan_library.py DB --quality              # dupes, journal variants, bad names
    python3 scan_library.py DB --case-audit           # Title vs sentence case split
    python3 scan_library.py DB --json out.json        # machine-readable dump

With no flags it prints a summary of everything.
"""
import argparse
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict

REGULAR = ('journalArticle', 'preprint', 'report', 'bookSection', 'book',
           'thesis', 'newspaperArticle', 'magazineArticle', 'conferencePaper')

CJK = re.compile(r'[一-鿿]')
EMAIL = re.compile(r'[A-Za-z0-9._%\-]+@[A-Za-z0-9._%\-]+')   # ASCII only: \w eats CJK


class Library:
    def __init__(self, path):
        self.db = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
        self.cur = self.db.cursor()
        self._load()

    def _load(self):
        cur = self.cur
        deleted = set(r[0] for r in cur.execute("SELECT itemID FROM deletedItems"))
        rows = cur.execute(
            "SELECT i.itemID, i.key, it.typeName, i.dateAdded FROM items i "
            "JOIN itemTypes it ON i.itemTypeID = it.itemTypeID "
            "WHERE it.typeName IN %s" % str(REGULAR)).fetchall()
        self.items = {r[0]: {'key': r[1], 'type': r[2], 'added': r[3]}
                      for r in rows if r[0] not in deleted}
        self.trash = len(deleted)

        self.fieldID = {n: i for i, n in cur.execute(
            "SELECT fieldID, fieldName FROM fields")}

        self.colls = cur.execute(
            "SELECT collectionID, collectionName, parentCollectionID "
            "FROM collections").fetchall()
        self.cname = {r[0]: r[1] for r in self.colls}
        self.parent = {r[0]: r[2] for r in self.colls}
        self.children = defaultdict(list)
        for cid, _n, p in self.colls:
            self.children[p].append(cid)

        self.item_colls = defaultdict(list)
        self.direct = Counter()
        for cid, iid in cur.execute("SELECT collectionID, itemID FROM collectionItems"):
            if iid in self.items:
                self.item_colls[iid].append(cid)
                self.direct[cid] += 1

        tagname = {r[0]: r[1] for r in cur.execute("SELECT tagID, name FROM tags")}
        self.n_tag_rows = len(tagname)
        self.item_tags = defaultdict(list)
        self.tagfreq = Counter()
        for tid, iid in cur.execute("SELECT tagID, itemID FROM itemTags"):
            if iid in self.items:
                self.item_tags[iid].append(tagname[tid])
                self.tagfreq[tagname[tid]] += 1

        self.creators = defaultdict(list)
        for iid, last, first, fm, o in cur.execute(
                "SELECT ic.itemID, c.lastName, c.firstName, c.fieldMode, ic.orderIndex "
                "FROM itemCreators ic JOIN creators c ON ic.creatorID = c.creatorID "
                "ORDER BY ic.itemID, ic.orderIndex"):
            if iid in self.items:
                self.creators[iid].append(
                    {'last': last or '', 'first': first or '', 'fm': fm, 'o': o})

    def field(self, name):
        fid = self.fieldID.get(name)
        out = {}
        if fid is None:
            return out
        for iid, val in self.cur.execute(
                "SELECT id.itemID, idv.value FROM itemData id "
                "JOIN itemDataValues idv ON id.valueID = idv.valueID "
                "WHERE id.fieldID = ?", (fid,)):
            if iid in self.items:
                out[iid] = val
        return out

    def path(self, cid):
        parts = []
        while cid is not None:
            parts.append(self.cname[cid])
            cid = self.parent[cid]
        return '/'.join(reversed(parts))

    def total(self, cid):
        return self.direct.get(cid, 0) + sum(self.total(c) for c in self.children.get(cid, []))

    # ---------- reports ----------

    def summary(self):
        print(f"items (regular, excl. trash): {len(self.items)}")
        print(f"  by type: {dict(Counter(v['type'] for v in self.items.values()).most_common())}")
        print(f"collections: {len(self.colls)}   tags in use: {len(self.tagfreq)}"
              f"   (orphan tag rows: {self.n_tag_rows - len(self.tagfreq)})")
        print(f"trash: {self.trash}")
        nc = [i for i in self.items if not self.item_colls.get(i)]
        nt = [i for i in self.items if not self.item_tags.get(i)]
        print(f"no collection: {len(nc)}   no tag: {len(nt)}")

    def tree(self):
        print("\n=== COLLECTIONS [direct/total] ===")
        def walk(cid, d=0):
            print('  ' * d + f"{self.cname[cid]} [{self.direct.get(cid,0)}/{self.total(cid)}]")
            for ch in sorted(self.children.get(cid, []), key=lambda x: self.cname[x].lower()):
                walk(ch, d + 1)
        for cid in sorted(self.children.get(None, []), key=lambda x: self.cname[x].lower()):
            walk(cid)

    def tags(self, top=60):
        print(f"\n=== TAGS ({len(self.tagfreq)} in use) ===")
        jel = sorted(t for t in self.tagfreq if t.upper().startswith('JEL'))
        if jel:
            print(f"JEL codes ({len(jel)}): {', '.join(jel)}")
        cn = [t for t in self.tagfreq if CJK.search(t)]
        if cn:
            print(f"non-English tags: {len(cn)}  e.g. {cn[:10]}")
        once = [t for t in self.tagfreq if self.tagfreq[t] == 1]
        print(f"used once: {len(once)}")
        print(f"top {top}:")
        for t, n in [(t, n) for t, n in self.tagfreq.most_common(top)
                     if not t.upper().startswith('JEL')]:
            print(f"  {n:5d}  {t}")
        # case/spacing variants of the same tag
        norm = defaultdict(list)
        for t in self.tagfreq:
            norm[re.sub(r'[^a-z0-9一-鿿]', '', t.lower())].append(t)
        dupes = {k: v for k, v in norm.items() if len(v) > 1}
        if dupes:
            print(f"\nvariant spellings ({len(dupes)} groups) — merge these:")
            for _k, v in sorted(dupes.items(), key=lambda kv: -sum(self.tagfreq[x] for x in kv[1])):
                print("   " + "  |  ".join(f"{t!r}×{self.tagfreq[t]}"
                                           for t in sorted(v, key=lambda x: -self.tagfreq[x])))

    def recent(self, since):
        titles = self.field('title')
        sel = sorted((i for i, v in self.items.items() if v['added'] >= since),
                     key=lambda i: self.items[i]['added'])
        print(f"\n=== ADDED SINCE {since}: {len(sel)} ===")
        for i in sel:
            paths = [self.path(c) for c in self.item_colls.get(i, [])]
            print(f"[{self.items[i]['key']}] {(titles.get(i,'') or '')[:58]:58s} "
                  f"| {('; '.join(paths))[:46] or '(none)':46s} | tags:{len(self.item_tags.get(i,[]))}")
        return sel

    def unfiled(self):
        titles = self.field('title')
        nc = [i for i in self.items if not self.item_colls.get(i)]
        nt = [i for i in self.items if not self.item_tags.get(i)]
        print(f"\n=== NO COLLECTION ({len(nc)}) ===")
        for i in nc:
            print(f"  [{self.items[i]['key']}] {(titles.get(i,'') or '')[:70]}")
        print(f"\n=== NO TAG ({len(nt)}) ===")
        for i in nt[:60]:
            print(f"  [{self.items[i]['key']}] {(titles.get(i,'') or '')[:70]}")
        # in a top-level category but none of its subcollections
        gap = defaultdict(list)
        for i in self.items:
            for cid in self.item_colls.get(i, []):
                if (self.parent[cid] is None and self.children.get(cid)
                        and self.cname[cid] not in ('Projects', 'Topics')):
                    if not (set(self.item_colls[i]) & set(self.children[cid])):
                        gap[self.cname[cid]].append(self.items[i]['key'])
        if gap:
            print(f"\n=== IN A TOP CATEGORY BUT NO SUBCOLLECTION ({sum(len(v) for v in gap.values())}) ===")
            for k, v in sorted(gap.items(), key=lambda kv: -len(kv[1])):
                print(f"  {len(v):4d}  {k}")
        return {'no_collection': nc, 'no_tag': nt, 'gap': dict(gap)}

    def quality(self):
        titles, doi = self.field('title'), self.field('DOI')
        pub = self.field('publicationTitle')

        dm = defaultdict(list)
        for i, d in doi.items():
            if d and d.strip():
                dm[d.strip().lower()].append(i)
        dupes = {k: v for k, v in dm.items() if len(v) > 1}
        print(f"\n=== DUPLICATE DOIs ({len(dupes)}) ===")
        for k, v in dupes.items():
            print(f"  {k}")
            for i in v:
                print(f"     {(titles.get(i,'') or '')[:66]}")

        def jnorm(s):
            s = re.sub(r'^the\s+', '', s.lower().strip())
            return re.sub(r'[^a-z0-9一-鿿]+', '',
                          s.replace(' and ', '').replace('&', ''))
        jg = defaultdict(list)
        jc = Counter(v for v in pub.values() if v)
        for name in jc:
            jg[jnorm(name)].append(name)
        jd = {k: v for k, v in jg.items() if len(v) > 1}
        print(f"\n=== JOURNAL NAME VARIANTS ({len(jd)} groups) ===")
        for _k, v in sorted(jd.items(), key=lambda kv: -sum(jc[x] for x in kv[1])):
            print("   " + "  |  ".join(f"{n!r}×{jc[n]}" for n in sorted(v, key=lambda x: -jc[x])))

        bad = defaultdict(list)
        for i, cs in self.creators.items():
            for c in cs:
                nm = (c['last'] + ' ' + c['first']).strip()
                if EMAIL.search(c['last']) or EMAIL.search(c['first']):
                    bad['email'].append(nm)
                elif c['last'].isascii() and c['last'].isupper() and len(c['last']) > 2:
                    bad['ALLCAPS'].append(nm)
                elif CJK.search(c['last']) and c['first'] and c['fm'] == 0:
                    bad['cjk_split'].append(nm)
        print("\n=== AUTHOR NAME PROBLEMS ===")
        for k, v in bad.items():
            print(f"  {k}: {len(v)}   e.g. {v[:6]}")

        weird = [t for t in titles.values()
                 if t != t.strip() or re.search(r'\s{2,}|[ﬁﬂﬀﬃ]', t)
                 or t.lower().startswith(('untitled', 'microsoft word', 'nber working paper series'))]
        print(f"\n=== SUSPECT TITLES ({len(weird)}) ===")
        for t in weird[:20]:
            print(f"  {t[:76]!r}")

    def case_audit(self):
        titles = self.field('title')
        STOP = {'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'so', 'yet',
                'at', 'by', 'in', 'of', 'on', 'to', 'up', 'as', 'from', 'into',
                'with', 'over', 'under', 'than', 'that', 'is', 'are', 'be',
                'do', 'does', 'it', 'its', 'their', 'his', 'her', 'not', 'no',
                'vs', 'via', 'per', 'after', 'before', 'during', 'between',
                'among', 'through', 'without', 'within', 'across', 'about',
                'against', 'when', 'where', 'how', 'why', 'what', 'which',
                'who', 'whose'}

        def classify(t):
            if CJK.search(t):
                return 'cjk'
            words = re.findall(r"[A-Za-z][A-Za-z'\-\.]*", t)
            if len(words) < 4:
                return 'short'
            cand = [w for w in words[1:] if w.lower() not in STOP and len(w) > 3]
            if not cand:
                return 'short'
            r = sum(1 for w in cand if w[0].isupper()) / len(cand)
            return 'title' if r >= 0.8 else ('sentence' if r <= 0.25 else 'mixed')

        c = Counter(classify(t) for t in titles.values())
        print("\n=== TITLE CASE AUDIT ===")
        for k, n in c.most_common():
            print(f"  {k:9s} {n:5d}  ({n/max(1,len(titles))*100:.1f}%)")
        print("\nConvert toward Title Case: sentence case has already lost which\n"
              "words are proper nouns, so the reverse direction cannot be undone\n"
              "(that is how 'U.S.-china' happens).")

    def dump(self, path):
        titles, abst = self.field('title'), self.field('abstractNote')
        out = []
        for i, v in self.items.items():
            out.append({
                'key': v['key'], 'type': v['type'], 'added': v['added'],
                'title': titles.get(i, ''), 'abstract': (abst.get(i, '') or '')[:600],
                'collections': [self.path(c) for c in self.item_colls.get(i, [])],
                'tags': self.item_tags.get(i, []),
                'creators': [f"{c['last']}, {c['first']}".strip(', ')
                             for c in self.creators.get(i, [])],
            })
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False)
        print(f"\nwrote {len(out)} items to {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('db')
    ap.add_argument('--tree', action='store_true')
    ap.add_argument('--tags', action='store_true')
    ap.add_argument('--recent', metavar='YYYY-MM-DD')
    ap.add_argument('--unfiled', action='store_true')
    ap.add_argument('--quality', action='store_true')
    ap.add_argument('--case-audit', action='store_true')
    ap.add_argument('--json', metavar='PATH')
    a = ap.parse_args()

    try:
        lib = Library(a.db)
    except sqlite3.DatabaseError as e:
        sys.exit(f"cannot read database ({e}).\n"
                 "Zotero is probably still running — ask the user to close it.")

    lib.summary()
    everything = not any([a.tree, a.tags, a.recent, a.unfiled, a.quality,
                          a.case_audit, a.json])
    if a.tree or everything:
        lib.tree()
    if a.tags or everything:
        lib.tags()
    if a.recent:
        lib.recent(a.recent)
    if a.unfiled or everything:
        lib.unfiled()
    if a.quality or everything:
        lib.quality()
    if a.case_audit or everything:
        lib.case_audit()
    if a.json:
        lib.dump(a.json)


if __name__ == '__main__':
    main()
