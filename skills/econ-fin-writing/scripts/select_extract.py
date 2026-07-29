# -*- coding: utf-8 -*-
"""Pick exemplar papers per module and extract their front matter for style distillation.

Scores candidates by recency, top-journal status, and membership in the
collections matching my active projects, then runs pdftotext over the first
three pages to capture abstract + introduction.

Usage:
    python select_extract.py [CORPUS_DIR]
Default: CORPUS_DIR=./corpus  (as written by process.py)

Requires pdftotext on PATH. Note: CJK extraction from Chinese PDFs is unreliable
(CID fonts come out empty), so the Chinese module is built from abstracts —
see chinese_abstracts.txt rather than chinese_intros.txt.
"""
import os, re, json, subprocess, argparse

TOP = {
    "finance": {"The Journal of Finance", "Journal of Finance", "Journal of Financial Economics",
                "The Review of Financial Studies", "Review of Financial Studies", "Management Science",
                "Review of Finance", "Journal of Financial and Quantitative Analysis"},
    "economics": {"American Economic Review", "The Quarterly Journal of Economics", "Quarterly Journal of Economics",
                  "Journal of Political Economy", "The Review of Economic Studies", "Review of Economic Studies",
                  "The Review of Economics and Statistics", "Review of Economics and Statistics", "Econometrica"},
    "accounting": {"The Accounting Review", "Accounting Review", "Journal of Accounting Research",
                   "Journal of Accounting and Economics", "Review of Accounting Studies",
                   "Contemporary Accounting Research"},
    "chinese": None,
}

# Collections tracking my active projects — weight these subfields up.
PROJECT_COLLS = {"BoardGenderDiversity", "Board Gender Diversity", "Labor Unions", "Climate Risk",
                 "ESG & Sustainability", "International Finance", "Political Connections", "Political Economy",
                 "International Trade", "Human Capital", "Tax Accounting", "Disclosure & Transparency",
                 "Corporate Social Responsibility", "ESG Performance", "Labor & Human Capital",
                 "Labor Markets", "Corporate Finance", "Investment Decisions"}

N = {"finance": 12, "economics": 10, "accounting": 10, "chinese": 12}


def score(it, mod):
    s = it["year"]
    if TOP[mod] and it["venue"] in TOP[mod]:
        s += 40
    if set(it["colls"]) & PROJECT_COLLS:
        s += 25
    return s


def extract_intro(pdf):
    try:
        r = subprocess.run(["pdftotext", "-f", "1", "-l", "3", "-nopgbrk", "-q", pdf, "-"],
                           capture_output=True, timeout=60)
        t = r.stdout.decode("utf-8", "ignore")
    except Exception as e:
        return f"[extract failed: {e}]"
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_dir", nargs="?", default="./corpus")
    a = ap.parse_args()

    for mod in ["finance", "economics", "accounting", "chinese"]:
        meta = os.path.join(a.corpus_dir, f"{mod}_meta.json")
        its = [x for x in json.load(open(meta, encoding="utf-8"))
               if x["pdf"] and os.path.exists(x["pdf"])]
        its.sort(key=lambda x: -score(x, mod))
        sel = its[:N[mod]]
        out = os.path.join(a.corpus_dir, f"{mod}_intros.txt")
        with open(out, "w", encoding="utf-8") as f:
            for it in sel:
                f.write("=" * 90 + "\n")
                f.write(f"{it['venue']} [{it['year']}] — {it['title']}\n")
                f.write(f"collections: {', '.join(it['colls'][:6])}\n")
                f.write("-" * 90 + "\n")
                f.write(extract_intro(it["pdf"])[:6000] + "\n\n")
        print(mod, "selected", len(sel), "venues:", sorted({x["venue"] for x in sel}))


if __name__ == "__main__":
    main()
