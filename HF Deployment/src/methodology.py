import streamlit as st


def run():
    st.header("🧪 Methodology")
    st.write("How we turned ~5,400 Tokopedia reviews into actionable themes.")

    st.markdown("#### The Pipeline")
    st.markdown("`Reviews  ->  Clean text  ->  Embeddings  ->  Cluster (BERTopic)  ->  Themes`")
    st.markdown(
        """
1. **Data** - PRDECT-ID: ~5,400 Indonesian product reviews, each labeled Positive/Negative plus an emotion.
2. **Preprocessing** - lowercase, strip URLs/symbols, normalize slang (`gak` -> `tidak`); Indonesian
   stopwords are removed only when extracting the topic keywords.
3. **Embeddings** - each review becomes a 384-dim vector using a multilingual language model
   (paraphrase-multilingual-MiniLM-L12-v2).
4. **Clustering** - reviews are split by sentiment, then BERTopic (UMAP + HDBSCAN) groups similar
   vectors into topics, separately for positive and negative reviews.
5. **Themes** - the many micro-topics are grouped into **8 praise** and **9 complaint** business themes.
        """
    )

    st.markdown("#### Why BERTopic?")
    c1, c2, c3 = st.columns(3)
    c1.markdown("**K-Means**\n\nSimple, but needs the number of clusters up front and gave coarse, "
                "mixed groups.")
    c2.markdown("**LDA**\n\nClassic bag-of-words baseline; broad topics that ignore word context.")
    c3.markdown("**BERTopic (chosen)**\n\nEmbeddings + density clustering. Best coherence and "
                "diversity, and the finest themes.")

    st.markdown("#### The Key Decision")
    st.info(
        "BERTopic's default clustering (HDBSCAN 'eom') collapsed **89% of complaints into one "
        "cluster**. Switching to 'leaf' separated them into 9 clean themes - our single most "
        "important tuning choice."
    )

    st.markdown("#### How This App Predicts")
    st.markdown(
        "Your review goes through the **same cleaning**, becomes an embedding, and is matched by "
        "**cosine similarity** to the learned topic vectors. The nearest theme - and whether it "
        "reads as praise or a complaint - is returned, with no retraining needed."
    )
