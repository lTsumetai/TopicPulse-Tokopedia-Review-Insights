from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------------------
# app.py reads from artifacts directory
ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"

# --------------------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------------------
# page configurations : tab title, icon, wide layout, sidebar
st.set_page_config(
    page_title="Tokopedia Review Insights",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

POS_COLOR = "#2e7d32"
NEG_COLOR = "#c62828"
ACCENT = "#1565c0"

EMOTION_COLORS = {
    "Happy": "#2e7d32",
    "Love": "#43a047",
    "Sadness": "#1565c0",
    "Anger": "#c62828",
    "Fear": "#6a1b9a",
}


# --------------------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------------------
# data loading from the artifacts directory
# i didn't add topics_csv because it doesn't contain any specific topics
@st.cache_data
def load_data():
    reviews = pd.read_csv(ARTIFACTS_DIR / "reviews_with_themes.csv")
    themes_pos = pd.read_csv(ARTIFACTS_DIR / "themes_positive.csv")
    themes_neg = pd.read_csv(ARTIFACTS_DIR / "themes_negative.csv")
    return reviews, themes_pos, themes_neg


reviews, themes_pos_full, themes_neg_full = load_data()

ALL_CATEGORIES = sorted(reviews["Category"].unique())
ALL_SENTIMENTS = sorted(reviews["Sentiment"].unique())
ALL_EMOTIONS = sorted(reviews["Emotion"].unique())

# --------------------------------------------------------------------------------------
# Sidebar filters
# --------------------------------------------------------------------------------------
# filtering through sidebars
st.sidebar.title(" Filters")
# applying sidebar filters
st.sidebar.caption("Filters apply to every section below.")

#filters for positive and negative reviews
sel_sentiment = st.sidebar.multiselect(
    "Sentiment", ALL_SENTIMENTS, default=ALL_SENTIMENTS
)
#filters for product categories 
sel_category = st.sidebar.multiselect(
    "Product category", ALL_CATEGORIES, default=[]
)
#filters for emotions based on reviews_with_themes.csv
sel_emotion = st.sidebar.multiselect(
    "Emotion", ALL_EMOTIONS, default=[]
)

# sidebar dashboard descriptions
st.sidebar.divider()
st.sidebar.markdown(
    """
**About this dashboard**

Built on top of a topic modeling pipeline:
- **BERTopic** (sentence embeddings + UMAP + HDBSCAN) for the primary themes
- **LDA** and **K-Means** baselines for comparison
- Reviews are modeled separately for positive and negative sentiment

Dataset: 
- [PRDECT-ID](https://data.mendeley.com/datasets/574v66hf2v/1) Product Reviews Dataset for Emotions Classification Tasks - Indonesian
- [Kamus Alay](https://github.com/nasalsabila/kamus-alay) lexicon for text normalization of Indonesian colloquial words. a total of 3,592 unique colloquial words-also known as “bahasa alay” -and manually annotated them with the normalized form.
"""
)

# Apply filters
df = reviews.copy()
if sel_sentiment:
    df = df[df["Sentiment"].isin(sel_sentiment)]
if sel_category:
    df = df[df["Category"].isin(sel_category)]
if sel_emotion:
    df = df[df["Emotion"].isin(sel_emotion)]

if df.empty:
    st.warning("No reviews match the current filters. Try widening your selection in the sidebar.")
    st.stop()

df_pos = df[df["Sentiment"] == "Positive"]
df_neg = df[df["Sentiment"] == "Negative"]


def theme_summary(d):
    if d.empty:
        return pd.DataFrame(columns=["theme", "reviews", "pct"])
    s = d.groupby("theme").size().sort_values(ascending=False).rename("reviews").reset_index()
    s["pct"] = (100 * s["reviews"] / len(d)).round(1)
    return s


summ_pos = theme_summary(df_pos[df_pos["theme"] != "Other"])
summ_neg = theme_summary(df_neg[df_neg["theme"] != "Other"])

# --------------------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------------------
# header for the streamlit page
st.title("Tokopedia Review Insights")
st.caption(
    "What do customers actually praise and complain about and what should the business do about it?"
)

# --------------------------------------------------------------------------------------
# KPI row
# --------------------------------------------------------------------------------------
# top-line numbers on the top of the dashboard
total = len(df)
pct_pos = 100 * len(df_pos) / total if total else 0
pct_neg = 100 * len(df_neg) / total if total else 0
top_complaint = summ_neg.iloc[0]["theme"] if not summ_neg.empty else "—"
top_praise = summ_pos.iloc[0]["theme"] if not summ_pos.empty else "—"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total reviews", f"{total:,}")
c2.metric("Positive", f"{len(df_pos):,}", f"{pct_pos:.0f}% of total")
c3.metric("Negative", f"{len(df_neg):,}", f"{pct_neg:.0f}% of total", delta_color="inverse")
c4.metric("Top complaint", top_complaint if len(top_complaint) < 22 else top_complaint[:20] + "…")

st.divider()

# --------------------------------------------------------------------------------------
# Section: Theme breakdown (the core of the project)
# --------------------------------------------------------------------------------------
# side by side bar charts. possitive on the left, negative on the right 
st.header("What customers praise vs. complain about")
st.caption("Themes were derived from BERTopic clustering, then mapped to human-readable business labels.")

tcol1, tcol2 = st.columns(2)

with tcol1:
    st.subheader(" Positive themes")
    if summ_pos.empty:
        st.info("No positive reviews in the current filter selection.")
    else:
        fig = px.bar(
            summ_pos.sort_values("reviews"),
            x="reviews", y="theme", orientation="h",
            text="pct", color_discrete_sequence=[POS_COLOR],
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(
            height=420, margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Reviews", yaxis_title="",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

with tcol2:
    st.subheader(" Negative themes")
    if summ_neg.empty:
        st.info("No negative reviews in the current filter selection.")
    else:
        fig = px.bar(
            summ_neg.sort_values("reviews"),
            x="reviews", y="theme", orientation="h",
            text="pct", color_discrete_sequence=[NEG_COLOR],
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(
            height=420, margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Reviews", yaxis_title="",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------------------
# Section: Emotion signature per theme
# --------------------------------------------------------------------------------------
# using heatmaps to show which emotion dominates each theme
st.header("How do these themes make customers feel?")
st.caption("Each row is normalized to 100%, showing the emotional signature of each theme.")

ecol1, ecol2 = st.columns(2)

with ecol1:
    st.subheader("Positive themes by emotion")
    d = df_pos[df_pos["theme"] != "Other"]
    if d.empty:
        st.info("No data for the current filters.")
    else:
        ct = pd.crosstab(d["theme"], d["Emotion"])
        ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
        ct_pct = ct_pct.loc[d["theme"].value_counts().index]
        fig = px.imshow(
            ct_pct, text_auto=".0f", aspect="auto",
            color_continuous_scale="Greens",
            labels=dict(color="% within theme"),
        )
        fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

with ecol2:
    st.subheader("Negative themes by emotion")
    d = df_neg[df_neg["theme"] != "Other"]
    if d.empty:
        st.info("No data for the current filters.")
    else:
        ct = pd.crosstab(d["theme"], d["Emotion"])
        ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
        ct_pct = ct_pct.loc[d["theme"].value_counts().index]
        fig = px.imshow(
            ct_pct, text_auto=".0f", aspect="auto",
            color_continuous_scale="Reds",
            labels=dict(color="% within theme"),
        )
        fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------------------
# Section: Category deep-dive
# --------------------------------------------------------------------------------------
# which product categories get the most complaint (left)
# which complaints that exists on each categories (right)
st.header("Where are the problems concentrated?")

ccol1, ccol2 = st.columns([1, 1.3])

# left
with ccol1:
    st.subheader("Complaint rate by category")
    cat_rate = (
        df.assign(is_neg=df["Sentiment"].eq("Negative"))
        .groupby("Category")["is_neg"].mean().mul(100).sort_values(ascending=False)
    )
    cat_counts = df.groupby("Category").size()
    # Avoid noisy rates from tiny categories when filters narrow the data
    cat_rate = cat_rate[cat_counts[cat_rate.index] >= 5]
    fig = px.bar(
        cat_rate.head(15).sort_values(),
        orientation="h", color_discrete_sequence=[NEG_COLOR],
    )
    fig.add_vline(x=50, line_dash="dash", line_color="gray")
    fig.update_layout(
        height=480, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="% negative reviews", yaxis_title="",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

# right
with ccol2:
    st.subheader("What each category complains about")
    d = df_neg[df_neg["theme"] != "Other"]
    if d.empty or d["Category"].nunique() < 1:
        st.info("No negative reviews for the current filters.")
    else:
        ctc = pd.crosstab(d["Category"], d["theme"])
        ctc_pct = ctc.div(ctc.sum(axis=1), axis=0) * 100
        ctc_pct = ctc_pct.loc[d["Category"].value_counts().index]
        fig = px.imshow(
            ctc_pct, aspect="auto",
            color_continuous_scale="Sunsetdark",
            labels=dict(color="% of category's complaints"),
        )
        fig.update_layout(height=480, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------------------
# Section: Priority matrix
# --------------------------------------------------------------------------------------
# using scatter plot to find how many complaints dominates on the data. 
# (if the data goes more to the right, means it was the most dominant)
st.header("Which complaints should the business fix first?")
st.caption(
    "Volume (how many reviews) vs. urgency (share of Anger + Fear, the activating emotions). "
    "Top-right = frequent and emotionally charged = fix first."
)

d = df_neg[df_neg["theme"] != "Other"]
if d.empty:
    st.info("No negative reviews for the current filters.")
else:
    em = pd.crosstab(d["theme"], d["Emotion"])
    for col in ["Anger", "Fear"]:
        if col not in em.columns:
            em[col] = 0
    em_pct = em.div(em.sum(axis=1), axis=0) * 100
    prio = pd.DataFrame({
        "volume": d["theme"].value_counts(),
        "urgency": em_pct["Anger"] + em_pct["Fear"],
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=prio["volume"], y=prio["urgency"],
        mode="markers+text",
        text=prio.index, textposition="top center",
        marker=dict(size=14, color=NEG_COLOR),
        textfont=dict(size=10),
    ))
    fig.update_layout(
        height=500, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Volume (number of reviews)",
        yaxis_title="Urgency (% Anger + Fear)",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------------------
# Section: Review explorer
# --------------------------------------------------------------------------------------
# filterable table to find the actual reviews based on themes
st.header("Review explorer")
st.caption("Read the actual reviews behind any theme.")

theme_options = sorted(df["theme"].unique())
sel_theme = st.multiselect("Filter by theme", theme_options, default=[])

explorer_df = df.copy()
if sel_theme:
    explorer_df = explorer_df[explorer_df["theme"].isin(sel_theme)]

search = st.text_input("Search review text (optional)", "")
if search:
    explorer_df = explorer_df[explorer_df["Customer Review"].str.contains(search, case=False, na=False)]

st.dataframe(
    explorer_df[["Category", "Product Name", "Sentiment", "Emotion", "theme", "Customer Review"]]
    .reset_index(drop=True),
    use_container_width=True,
    height=400,
)
st.caption(f"Showing {len(explorer_df):,} of {len(df):,} filtered reviews.")

# --------------------------------------------------------------------------------------
# Footer
# --------------------------------------------------------------------------------------
st.divider()
st.caption(
  "footer testing"
)
