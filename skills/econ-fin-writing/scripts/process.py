# -*- coding: utf-8 -*-
"""Classify a Zotero library into the skill's four field modules and dump abstracts.

Reads the JSON produced by export_zotero.sh (items/pdfs/colls), buckets every
journal article into finance / economics / accounting / chinese by venue, and
writes per-module abstract dumps plus metadata used by select_extract.py.

Usage:
    python process.py [RAW_DIR] [OUT_DIR] [--storage ZOTERO_STORAGE]
Defaults:
    RAW_DIR=./corpus_raw   OUT_DIR=./corpus   storage=$HOME/Zotero/storage

Deliberately avoids `import sqlite3` — see export_zotero.sh for why.
"""
import os, re, json, sys, argparse

FIN = {"Journal of Financial Economics","The Review of Financial Studies","Review of Financial Studies",
 "The Journal of Finance","Journal of Finance","Journal of Corporate Finance","Review of Finance",
 "Journal of Financial and Quantitative Analysis","Journal of Banking & Finance","Management Science",
 "Strategic Management Journal","Academy of Management Journal","Financial Management",
 "Journal of Financial Intermediation","The Review of Corporate Finance Studies","Financial Review",
 "Journal of Financial Markets"}
ECON = {"American Economic Review","The Quarterly Journal of Economics","Quarterly Journal of Economics",
 "Journal of Political Economy","The Review of Economics and Statistics","Review of Economics and Statistics",
 "The Review of Economic Studies","Review of Economic Studies","Journal of Economic Literature",
 "Journal of Economic Perspectives","Econometrica","Journal of Monetary Economics","Journal of Public Economics",
 "Journal of International Economics","Journal of Econometrics",
 "American Economic Journal: Applied Economics","American Economic Journal: Economic Policy",
 "American Economic Journal: Macroeconomics","Journal of Development Economics","Journal of Labor Economics"}
ACC = {"Journal of Accounting and Economics","The Accounting Review","Accounting Review",
 "Journal of Accounting Research","Review of Accounting Studies","Contemporary Accounting Research",
 "Journal of the American Taxation Association","Accounting, Organizations and Society"}


def module(venue):
    """Map a venue to a field module. CJK in the name => Chinese module."""
    if not venue:
        return None
    if re.search(r"[一-鿿]", venue):
        return "chinese"
    if venue in FIN:
        return "finance"
    if venue in ECON:
        return "economics"
    if venue in ACC:
        return "accounting"
    return None


def year(date):
    if not date:
        return 0
    m = re.search(r"(19|20)\d\d", date)
    return int(m.group()) if m else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_dir", nargs="?", default="./corpus_raw")
    ap.add_argument("out_dir", nargs="?", default="./corpus")
    ap.add_argument("--storage", default=os.path.join(os.path.expanduser("~"), "Zotero", "storage"))
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    load = lambda n: json.load(open(os.path.join(a.raw_dir, n), encoding="utf-8"))
    items, pdfs, colls = load("items.json"), load("pdfs.json"), load("colls.json")

    pdf = {}
    for r in pdfs:
        pdf.setdefault(r["parent"], os.path.join(a.storage, r["key"], r["path"].replace("storage:", "")))
    coll = {}
    for r in colls:
        coll.setdefault(r["id"], []).append(r["coll"])

    buckets = {"finance": [], "economics": [], "accounting": [], "chinese": []}
    for it in items:
        mod = module(it.get("venue"))
        if not mod:
            continue
        iid = it["id"]
        buckets[mod].append({
            "id": iid, "title": it.get("title"), "venue": it.get("venue"),
            "year": year(it.get("date")), "abstract": (it.get("abstract") or "").strip(),
            "pdf": pdf.get(iid), "colls": coll.get(iid, []),
        })

    report = {}
    for mod, its in buckets.items():
        its.sort(key=lambda x: -x["year"])
        with open(os.path.join(a.out_dir, f"{mod}_abstracts.txt"), "w", encoding="utf-8") as f:
            for it in its:
                if not it["abstract"]:
                    continue
                f.write(f"### [{it['year']}] {it['venue']} — {it['title']}\n{it['abstract']}\n\n")
        json.dump(its, open(os.path.join(a.out_dir, f"{mod}_meta.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        report[mod] = {
            "n": len(its),
            "with_abs": sum(1 for x in its if x["abstract"]),
            "with_pdf": sum(1 for x in its if x["pdf"] and os.path.exists(x["pdf"])),
        }
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
