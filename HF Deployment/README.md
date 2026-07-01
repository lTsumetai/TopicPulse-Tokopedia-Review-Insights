---
title: Tokopedia Review Insights
emoji: 🛒
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.31.0
app_file: src/app.py
pinned: false
---

# Tokopedia Review Insights

NLP topic modeling on Indonesian Tokopedia product reviews (PRDECT-ID). The app surfaces
**what customers praise and complain about** - not just sentiment, but the theme behind it.

Pages:
- **EDA** - sentiment balance, themes, emotions, categories.
- **Predict Theme** - paste a review, get its predicted theme (praise vs complaint).
- **Submit a Review** - save a new review to the database (Supabase).

## How prediction works
A review is embedded with `paraphrase-multilingual-MiniLM-L12-v2` and cosine-matched to the
exported topic vectors (`artifacts/topic_index.npz`). No BERTopic/UMAP/HDBSCAN are needed at
runtime, so the Space stays light.

## Run locally
```bash
pip install -r requirements.txt
streamlit run src/app.py
```

## Deploy to Hugging Face Spaces
1. Create a new Space -> **SDK: Streamlit**.
2. Upload these files/folders (NOT the notebook, raw dataset, or BERTopic models):
   - `src/`
   - `artifacts/topic_index.npz`, `artifacts/topic_index.json`, `artifacts/dashboard_data.csv`
   - `colloquial-indonesian-lexicon.csv`
   - `requirements.txt`, `README.md`
3. Set the database credentials under **Space -> Settings -> Secrets** (do NOT commit `secrets.toml`).
   Add a secret named `secrets.toml`-style connection, or set the `[connections.supabase]` values
   via the Secrets UI.

## Security
`.streamlit/secrets.toml` holds DB credentials and is gitignored. Use
`.streamlit/secrets.toml.example` as a template. Never commit real credentials to a public repo.

## Project
Hacktiv8 FTDS-040-HCK - Final Project - Group 001.
