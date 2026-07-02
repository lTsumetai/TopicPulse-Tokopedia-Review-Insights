# TopicPulse - Tokopedia Review Insights

**NLP topic modeling on Indonesian Tokopedia product reviews.**
Understand not just *whether* a review is good or bad, but the *theme* behind it —
what customers actually praise, and what they actually complain about.

🔗 **Live app:** [Hugging Face]([https://topicpulse.streamlit.app/](https://huggingface.co/spaces/dahutapea/Topic-Modeling-Tokopedia-Reviews))

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

## How it works 
