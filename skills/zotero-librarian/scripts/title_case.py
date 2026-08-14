"""Title Case conversion tuned for academic titles.

Every rule here exists because a simpler version got it wrong on a real
library: Peer-To-Peer, Trade-off, "the Bird in the Hand", U.S.-china.

    from title_case import tcase, is_cjk
    tcase('evidence from the U.S.-china trade war')
    # 'Evidence from the U.S.-China Trade War'

Extend KEEP / PROPER / TERM for a specific library's vocabulary.
"""
import re

# Lowercased inside a title (articles, conjunctions, prepositions)
LOWER = {
    'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'so', 'yet',
    'at', 'by', 'in', 'of', 'on', 'to', 'up', 'as', 'from', 'into', 'with',
    'over', 'under', 'than', 'via', 'per', 'vs', 'versus', 'amid', 'among',
    'between', 'during', 'through', 'without', 'within', 'across', 'against',
    'along', 'around', 'about', 'after', 'before', 'upon', 'onto', 'off',
    'out', 'near', 'toward', 'towards', 'de', 'van', 'von', 'der', 'del',
    'la', 'le',
}

# Inside hyphenated compounds only function words stay lowercase.
# Adverbs/particles keep their capital: Trade-Off, Take-Up, Spin-Off.
HYPH_LOWER = {'to', 'of', 'and', 'or', 'the', 'a', 'an', 'in', 'for',
              'with', 'by', 'at', 'on', 'from', 'de', 'la', 'le',
              'van', 'von', 'der'}

# Acronyms and names with fixed casing
KEEP = {
    'U.S.', 'US', 'UK', 'EU', 'ESG', 'CEO', 'CEOs', 'CFO', 'CFOs', 'IPO',
    'IPOs', 'M&A', 'R&D', 'AI', 'ETS', 'GVC', 'GDP', 'TFP', 'FDI', 'WTO',
    'SME', 'SMEs', 'DID', 'IV', 'RDD', 'SOX', 'NBER', 'ETF', 'ETFs', 'CSR',
    'COVID', 'COVID-19', 'LLM', 'LLMs', 'GPT', 'ChatGPT', 'SEC', 'IRS',
    'EPA', 'OSHA', 'PCAOB', 'GAAP', 'NGO', 'NGOs', 'OECD', 'IMF', 'G7',
    'ICT', 'IT', 'TARP', 'QE', 'SPAC', 'SPACs', 'CDS', 'NPL', 'P2P', 'B2B',
    'REIT', 'REITs', 'PSM', 'SMM', 'GMM', 'OLS', 'NLP', 'API', 'SOE',
    'SOEs', 'MBA', 'PhD', 'Ph.D.', 'A-share', 'H-share',
}

# Proper nouns that must stay capitalized even mid-title
PROPER = {
    'china', 'chinese', 'america', 'american', 'americans', 'europe',
    'european', 'japan', 'japanese', 'india', 'indian', 'germany', 'german',
    'france', 'french', 'britain', 'british', 'england', 'korea', 'korean',
    'taiwan', 'russia', 'russian', 'africa', 'african', 'asia', 'asian',
    'brazil', 'canada', 'australia', 'mexico', 'turkey', 'turkish',
    'syrian', 'israel', 'singapore', 'vietnam', 'indonesia', 'netherlands',
    'dutch', 'swedish', 'sweden', 'norway', 'denmark', 'finland', 'italy',
    'italian', 'spain', 'spanish', 'greece', 'poland', 'london', 'beijing',
    'shanghai', 'washington', 'york', 'california', 'texas', 'wall',
    'street', 'hong', 'kong', 'macau', 'shenzhen', 'soviet', 'ukraine',
    'greek', 'swiss', 'switzerland', 'belgium', 'austria', 'ireland',
    'irish', 'scotland', 'wales', 'argentina', 'chile', 'colombia', 'peru',
    'thailand', 'malaysia', 'philippines', 'pakistan', 'bangladesh',
    'egypt', 'nigeria', 'kenya', 'saudi', 'emirates', 'qatar', 'iran',
    'iraq',
    # people and eponyms
    'bayesian', 'nash', 'popper', 'keynesian', 'schumpeterian', 'tobin',
    'sarbanes', 'oxley', 'dodd', 'frank', 'gaussian', 'poisson', 'monte',
    'carlo', 'pareto', 'markov', 'granger', 'heckman', 'oaxaca', 'blinder',
    'shapley',
    # organizations and products
    'glassdoor', 'google', 'facebook', 'instagram', 'amazon', 'apple',
    'microsoft', 'twitter', 'medicare', 'medicaid', 'brexit', 'trump',
    'biden', 'obama', 'covid', 'lasso', 'bert', 'openai', 'nasdaq', 'nyse',
    'fed', 'federal', 'reserve', 'treasury', 'congress', 'congressional',
    'senate', 'asean', 'opec', 'nato',
}

# Terms whose lowercase is deliberate
TERM = {'q-theory': 'q-Theory', 'i.i.d.': 'i.i.d.', 'e-commerce': 'E-Commerce'}


def is_cjk(s):
    """True if the string contains CJK characters (skip capitalization)."""
    return bool(re.search(r'[一-鿿]', s or ''))


def tcase(t):
    """Convert an academic title to Title Case."""
    toks = re.split(r'(\s+)', t)
    out = []
    force_up = True                       # first word, and after : ? ! —
    n_word = sum(1 for x in toks if x.strip())
    wi = 0

    for tok in toks:
        if not tok.strip():
            out.append(tok)
            continue
        wi += 1

        m = re.match(r'^([\("\'“‘\[]*)(.*?)'
                     r'([\)\]"\'”’:;,\.\?\!]*)$', tok, re.S)
        pre, word, post = m.group(1), m.group(2), m.group(3)
        if not word:
            out.append(tok)
            continue

        bare = word.strip('.')

        if word.lower() in TERM:
            out.append(pre + TERM[word.lower()] + post)
            force_up = False
            continue

        # Acronyms: leave exactly as-is
        if (word in KEEP or bare in KEEP
                or (word.isupper() and len(bare) > 1
                    and re.fullmatch(r'[A-Z&\.\-0-9]+', word))):
            out.append(pre + word + post)

        elif '-' in word and len(word) > 1:
            segs = word.split('-')
            fixed = []
            for si, s in enumerate(segs):
                if not s:
                    fixed.append(s)
                elif s in KEEP or s.strip('.') in KEEP or (s.isupper() and len(s) > 1):
                    fixed.append(s)
                elif s.lower() in PROPER:
                    fixed.append(s[0].upper() + s[1:])
                elif s.lower() in HYPH_LOWER and si > 0:
                    fixed.append(s.lower())
                else:
                    fixed.append(s[0].upper() + s[1:])
            out.append(pre + '-'.join(fixed) + post)

        elif word.lower() in PROPER:
            out.append(pre + word[0].upper() + word[1:] + post)

        # First word, last word, after terminal punctuation, or opening a quote
        elif force_up or wi == n_word or re.search(r'["\'“‘\[(]', pre):
            out.append(pre + word[0].upper() + word[1:] + post)

        elif word.lower() in LOWER:
            out.append(pre + word.lower() + post)

        else:
            # Content word: capitalize the first letter, keep the rest
            # (protects iPhone, eBay, McKinsey-style internal capitals)
            out.append(pre + word[0].upper() + word[1:] + post)

        force_up = (bool(re.search(r'[:\?\!—–]$', post))
                    or re.fullmatch(r'[-–—]+', word) is not None)

    return ''.join(out)


def clean_title(t):
    """Fix ligatures and whitespace, then apply Title Case. CJK passes through."""
    t = (t.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
          .replace('ﬀ', 'ff').replace('ﬃ', 'ffi'))
    t = re.sub(r'\s{2,}', ' ', t).strip()
    return t if is_cjk(t) else tcase(t)


if __name__ == '__main__':
    for s in [
        'Trade networks and firm value: evidence from the U.S.-china trade war',
        'Does democracy cause innovation? An empirical test of the popper hypothesis',
        'Peer-to-Peer Lenders Versus Banks: Substitutes or Complements?',
        'Optimal Debt and Profitability in the Trade-Off Theory',
        'Imperfect Information, Dividend Policy, and "The Bird in the Hand" Fallacy',
        'The 52-week high, q-theory, and the cross section of stock returns',
        'Are CEOs born leaders? Lessons from traits of a million individuals',
    ]:
        print(f'  {s}\n->{clean_title(s)}\n')
