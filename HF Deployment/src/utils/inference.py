"""Theme prediction without the full BERTopic stack: embed the review, then cosine-match it
against the exported topic vectors (artifacts/topic_index.*). Pure functions (no Streamlit) so
they can be unit-tested. The heavy model loads once and is cached as a module-level singleton.
"""
import os
import json
import numpy as np

from utils.paths import ARTIFACTS
from utils.preprocess import clean_review

_E = None        # normalized topic-vector matrix (n_topics x dim)
_meta = None     # list of {topic, theme, sentiment}
_model = None    # SentenceTransformer


def _load():
    global _E, _meta, _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _E = np.load(os.path.join(ARTIFACTS, "topic_index.npz"))["embeddings"]
        cfg = json.load(open(os.path.join(ARTIFACTS, "topic_index.json"), encoding="utf-8"))
        _meta = cfg["topics"]
        _model = SentenceTransformer(cfg["model_name"])
    return _E, _meta, _model


def predict_theme(text: str, topk: int = 3):
    """Return (cleaned_text, [(sentiment, theme, similarity), ...]) ranked best-first.
    Similarity is aggregated to theme level (best matching topic per theme)."""
    E, meta, model = _load()
    cleaned = clean_review(text)
    if not cleaned:
        return cleaned, []

    q = model.encode([cleaned])[0]
    q = q / (np.linalg.norm(q) + 1e-9)
    sims = E @ q   # cosine (E is pre-normalized)

    best = {}
    for i, t in enumerate(meta):
        key = (t["sentiment"], t["theme"])
        if key not in best or sims[i] > best[key]:
            best[key] = float(sims[i])

    ranked = sorted(best.items(), key=lambda kv: -kv[1])
    return cleaned, [(s, th, sim) for (s, th), sim in ranked[:topk]]
