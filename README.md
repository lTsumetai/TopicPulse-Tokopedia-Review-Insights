# TopicPulse - Tokopedia Review Insights

**NLP topic modeling on Indonesian Tokopedia product reviews.**
Understand not just *whether* a review is good or bad, but the *theme* behind it. 
what customers actually praise, and what they actually complain about.

🔗 **Live app:** [Hugging Face](https://huggingface.co/spaces/dahutapea/Topic-Modeling-Tokopedia-Reviews)

> Hacktiv8 Data Science Bootcamp — Final Project (FTDS-040-HCK, Group 001)



## About
This Project turns raw tokopedia product reviews into structured, exploreable insight. rather than collections of plain positive/negative sentiment score, each review is matched to one of several data-driven **themes** or topics (e.g. *packaging*, *fast deliverey*, *unresponsive seller*, *item not as describe*) discovered through topic modelling. 

Built based on **[PRDECT-ID](https://github.com/crush7/PRDECT-ID)** dataset and with text normalization dataset **[Kamus Alay](https://github.com/nasalsabila/kamus-alay)** colloquial Indonesian Lexicon

## Features

- **Home** topic modelling project description
- **Methodology** Model pipeline alongside model selection, and how does the model predicts
- **Interactive EDA dashboard** filter by sentiment, product category, emotion, and data exploration. lists of features inside dashboard :
  - Praise vs. complaint theme breakdowns
  - Star rating distribution, overall and by category
  - Theme-to-emotion heatmaps
  - Price bracket vs. satisfaction analysis
  - Geographic breakdown of review volume and negative rate
  - A category "bubble chart" (volume vs. satisfaction) to spot high-sell/low-satisfaction     categories
  - A complaint priority matrix to flag what the business should fix first
  - Best/worst rated products and a raw review explorer
- **Theme Prediction** Model Inferencing. paste any Indonesian product review and get its predicted theme (praise or complaint)
- **Review submission** form for submitting a new review, wired to supabase database.

## Project Pipeline 
1. **Topic modeling** (`Topic Modeling - DS Role.ipynb`): 
2. **Artifact export**: 
3. **Prediction at inference time**: 
4. **Dashboard**: `src/eda.py` reads the exported artifacts and renders the full analytics
   experience with Plotly.

## Tech Stack
| Layer | Tools |
|---|---|
| Language | Python |
| App / UI | Streamlit |
| NLP / Modeling | BERTopic,...|
| Data | pandas, numpy |
| Visualization | Plotly, Altair, Matplotlib |
| Database | Supabase, psycopg2 |
| Deployment | Docker, Docker Compose, Hugging Face Spaces, Streamlit |

## Project structure

```
.
├── src/
│   ├── app.py              # Page router (Home / EDA / ...)
│   ├── eda.py               # EDA dashboard
│   ├── prediction.py        # Theme prediction page
│   └── utils/
│       ├── db_connection.py # Supabase connection helper
│       └── ...
├── artifacts/               # Exported model outputs used by the app at runtime
│   ├── dashboard_data.csv
│   ├── reviews_with_themes.csv
│   ├── themes_positive.csv / themes_negative.csv
│   └── topics_positive.csv / topics_negative.csv
├── models/                   # Saved BERTopic / LDA models 
├── data/                     # Raw source data (PRDECT-ID, Kamus Alay lexicon)
├── HF Deployment/            
├── Topic Modeling - DS Role.ipynb   
├── csv_reads.ipynb
├── Dockerfile
├── docker-compose.yaml
└── requirements.txt
```

## Team
This project was built by a three-person team. covering the Data Engineer -> Data Scientist -> Data analyst Pipeline:
- **Data Engineer [Derida Falahian](https://github.com/Derida21)** — data ingestion & pipeline
- **Data Scientist [Daffa Hutapea](https://github.com/daphutapea)** — topic modeling (BERTopic/LDA/K-Means) and artifact export
- **Data Analyst [Fauzi Maulana](https://github.com/lTsumetai)** — EDA dashboard, prediction page, and review submission UI (this repo's Streamlit app)

## Reference
- [PRDECT-ID Dataset](https://github.com/crush7/PRDECT-ID) — Product Reviews Dataset for Emotions Classification Tasks (Indonesian)
- [Kamus Alay](https://github.com/nasalsabila/kamus-alay) — colloquial Indonesian lexicon for text normalization
