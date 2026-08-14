# Collections and tags

## The division of labor

Collections and tags answer different questions, and a library stays usable when each does its own job:

- **Collections = one durable subject taxonomy**, two levels deep. Where does this paper live?
- **Project folders** = a separate top-level area (`Projects/`, `Topics/`) for whatever the user is actively working on. Papers live in both — subject *and* project. These are working sets and can be messy, empty, or short-lived; that is fine and not a defect to clean up.
- **Tags = cross-cutting facets** collections cannot express: method (DID, RDD, IV, Structural Model), geography (China), data source (Glassdoor, 10-K), JEL codes.

A useful shape, from a working finance/accounting library of ~2,500 items:

```
Corporate Finance
  Capital Structure
  Financial Constraints
  Investment Decisions
  M&A & Restructuring
ESG & Sustainability
  Climate Risk
  ESG Performance
  Green Finance
Quantitative Methods
  Econometrics
  Machine Learning
  Meta-Analysis & Reviews
Projects
  TradeWar
  DGFL
Topics
  GreenWashing
  Supply Chain & Firm Boundaries
    Customer-Supplier Relationships
```

Two levels is enough for subject; a third level occasionally earns its place under a large project theme.

## Filing new items

Most new items arrive already in *some* collection — the user filed them into a project folder or a top-level bucket while importing. The real gap is usually items sitting in a top-level category with no subcollection, so target that:

```python
for iid in recent:
    for cid in item_colls[iid]:
        if parent[cid] is None and children.get(cid) and cname[cid] not in ('Projects', 'Topics'):
            if not (set(item_colls[iid]) & set(children[cid])):
                gap[cname[cid]].append(iid)      # in the parent, in none of its children
```

Then match within that parent's children only — a much easier problem than classifying against the whole tree, and it respects the filing the user already did.

Matching signals, in order of reliability:

1. **Existing tags.** An author- or user-supplied tag is a strong, deliberate signal.
2. **Title.** High precision.
3. **Abstract.** Higher recall, more noise — good for suggesting, risky for auto-assigning alone.

Exclude false friends explicitly. These bite in practice:

| Pattern | Excludes |
|---|---|
| `\bunion\b` | European Union, credit union, Soviet Union, monetary union |
| `\belection` | shareholder voting, proxy voting |
| `analyst` | data analyst, systems analyst |
| `\bbank\b` | World Bank (when the topic is banking) |

Report unmatched items rather than forcing them somewhere. A leftover pile the user can eyeball beats confident misfiling — and it often reveals a genuinely missing collection.

## When to propose a new subcollection

A subject deserves its own folder when it has accumulated real mass and is currently scattered. Quantify before proposing:

```
Disclosure & Transparency   ~134 papers, spread across Corporate Finance,
                            Accounting, Political Economy
Labor Unions                 ~64 papers, spread across Labor Markets,
                            Corporate Finance, ESG
```

Roughly 25+ items scattered across three or more parents is a strong case. Present counts and current locations, propose the tree, and let the user approve before generating anything. Name new folders in the user's established style — if their folders are `M&A & Restructuring`, write `Hedge Funds & Activism`, not `hedge-funds`.

## Tag hygiene

**One language, consistently.** For an English-language research library, English tags with Title Case. Keep native-language terms only where no standard English equivalent exists (a specific local policy or concept). Map the rest onto vocabulary the library already uses:

| Chinese | English |
|---|---|
| 融资约束 / 信贷约束 | Financial Constraint |
| 出口 | Export |
| 企业创新 / 技术创新 | Innovation |
| 全要素生产率(TFP) | TFP |
| 对外直接投资 | FDI |
| 结构式估计 | Structural Model |
| 贸易自由化 | Trade Liberalization |
| 准自然实验 | Quasi-Natural Experiment |

Reuse the existing tag rather than inventing a synonym — check the tag list first. Adding `Financing Constraints` when `Financial Constraint` already has 44 items just splits the facet.

**Merge case and spacing variants.** Normalize (lowercase, strip non-alphanumerics) to find collisions, then keep the most-used spelling:

```
Corporate Governance (69)  ←  CorporateGovernance (1)
Political Economy (32)     ←  PoliticalEconomy (1)
Board diversity (2)        ←  BoardDiversity (1)
```

`Zotero.Tags.rename(libraryID, old, new)` does this library-wide in one call — much better than per-item edits.

**Clean up import junk.** Publisher exports produce malformed compound tags:

```
"Models of Trade with Imperfect Competition and Scale Economies; Fragmentation"
"Multinational Firms; International Business"
```

Split them into real tags (`Multinational Firms`, `Firm Heterogeneity`) and drop what is not a useful facet. Lowercase imports (`firm dynamics`, `selection`) should be case-normalized to match the library convention.

**Single-use tags are not automatically wrong.** A library with 391 tags used exactly once is normal — highly specific papers get highly specific tags. Flag them for the user's review; do not bulk-delete. They only merit attention when they are near-duplicates of an existing tag.

**JEL codes** work well as tags (`JEL-G`, `JEL-G3`, `JEL-C`) — they give a stable, standard cross-cut that survives taxonomy changes.

## Adding a new item

When the user adds one paper and asks you to file it:

1. Read title, abstract, journal, existing tags.
2. Assign to **2–4 collections** — an interdisciplinary paper legitimately spans several (a GenAI-and-investor-judgment paper belongs in `AI & Finance`, `Investor Behavior`, and `Psychology & Organizational Behavior`). More than four usually means guessing.
3. Add tags in the library's existing vocabulary, and normalize any lowercase tags that came with the import.
4. If it belongs to an active project, add the project folder too — that is what makes the project folder useful later.
