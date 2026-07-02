"""Indonesian review cleaning - the SAME pipeline used to train the topic models, so new
text is processed identically before prediction:
lowercase -> strip URLs/mentions/symbols -> cut elongation -> normalize slang -> letters only.
"""
import re
import pandas as pd
from utils.paths import LEXICON

_slang = None


def _slang_map():
    """Lazy-load the colloquial Indonesian lexicon (slang -> formal)."""
    global _slang
    if _slang is None:
        lex = pd.read_csv(LEXICON)
        _slang = dict(zip(lex["slang"].astype(str), lex["formal"].astype(str)))
    return _slang


def clean_review(text: str) -> str:
    t = str(text).lower()
    t = re.sub(r"http\S+|www\.\S+", " ", t)     # URLs
    t = re.sub(r"@\w+", " ", t)                 # mentions
    t = re.sub(r"[^a-z\s]", " ", t)             # keep letters + spaces
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)        # cut elongation: "bagusss" -> "baguss"
    t = re.sub(r"\s+", " ", t).strip()
    t = " ".join(_slang_map().get(w, w) for w in t.split())   # slang -> formal
    t = re.sub(r"[^a-z\s]", " ", t)             # formal forms may add hyphens
    return re.sub(r"\s+", " ", t).strip()
