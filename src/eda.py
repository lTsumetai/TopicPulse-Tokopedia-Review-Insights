from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------------------
# getting eda.py to read from artifact directory
ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"

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
# loading dashboard_data.csv from artifacts directory
@st.cache_data
def load_data():
    df = pd.read_csv(ARTIFACTS_DIR / "dashboard_data.csv")
    return df


reviews = load_data()
# getting data with each categories without duplicates for filtering
ALL_CATEGORIES = sorted(reviews["Category"].unique())
ALL_SENTIMENTS = sorted(reviews["Sentiment"].unique())
ALL_EMOTIONS = sorted(reviews["Emotion"].unique())
ALL_LOCATIONS = sorted(reviews["Location"].unique())

# --------------------------------------------------------------------------------------
# Sidebar filters
# --------------------------------------------------------------------------------------
# adding filter options on sidebars
st.sidebar.title("Filters")
st.sidebar.caption("Filters apply to every section below.")

# the current filters from the sidebar are 
# sentiment, product category, and emotions
sel_sentiment = st.sidebar.multiselect(
    "Sentiment", ALL_SENTIMENTS, default=ALL_SENTIMENTS
)
sel_category = st.sidebar.multiselect(
    "Product category", ALL_CATEGORIES, default=[]
)
sel_emotion = st.sidebar.multiselect(
    "Emotion", ALL_EMOTIONS, default=[]
)

# Applying filters on the sidebar based on the variables above
df = reviews.copy()
if sel_sentiment:
    df = df[df["Sentiment"].isin(sel_sentiment)]
if sel_category:
    df = df[df["Category"].isin(sel_category)]
if sel_emotion:
    df = df[df["Emotion"].isin(sel_emotion)]
 
# if filters are empty returns this warning, just in case
if df.empty:
    st.warning("No reviews match the current filters. Try widening your selection in the sidebar.")
    st.stop()

df_pos = df[df["Sentiment"] == "Positive"]
df_neg = df[df["Sentiment"] == "Negative"]


# function to summarize how many reviews fall into each theme
def theme_summary(d):
    if d.empty:
        return pd.DataFrame(columns=["theme", "reviews", "pct"])
    s = d.groupby("theme").size().sort_values(ascending=False).rename("reviews").reset_index()
    s["pct"] = (100 * s["reviews"] / len(d)).round(1)
    return s

# function to create a shortcut to show a blue box under every visualizations
def conclusion(text):
    """docstring to show blue takeaway box for every visualizations"""
    st.info(f"**Takeaway:** {text}")


summ_pos = theme_summary(df_pos[df_pos["theme"] != "Other"])
summ_neg = theme_summary(df_neg[df_neg["theme"] != "Other"])

# --------------------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------------------
# header of the dashboard
st.title("Tokopedia Review Insights")
st.caption(
    "What do customers actually praise and complain about, and what should the business do about it?"
)

# --------------------------------------------------------------------------------------
# Section 1: KPI row
# --------------------------------------------------------------------------------------
# Main Key performance indicator. summarazing the whole dataset 
total = len(df)
pct_pos = 100 * len(df_pos) / total if total else 0
pct_neg = 100 * len(df_neg) / total if total else 0
top_complaint = summ_neg.iloc[0]["theme"] if not summ_neg.empty else "—"
avg_price = df["Price"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total reviews", f"{total:,}")
c2.metric("Positive", f"{len(df_pos):,}", f"{pct_pos:.0f}% of total")
c3.metric("Negative", f"{len(df_neg):,}", f"{pct_neg:.0f}% of total", delta_color="inverse")
c4.metric("Avg. customer rating", f"{df['Customer Rating'].mean():.2f} / 5")
c5.metric("Top complaint", top_complaint if len(top_complaint) < 22 else top_complaint[:20] + "…")

st.divider()

# --------------------------------------------------------------------------------------
# Section 2: Theme breakdown
# --------------------------------------------------------------------------------------
# theme data exploration using bar chart
st.header("What customers praise vs. complain about")
st.caption("Each bar is a recurring topic found in the reviews, and how often it shows up.")

tcol1, tcol2 = st.columns(2)

# positive themes
with tcol1:
    st.subheader("Positive themes")
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
        conclusion(
            f"**{summ_pos.iloc[0]['theme']}** is what customers loves the most, "
            f"making up {summ_pos.iloc[0]['pct']}% of positive reviews."
        )

# negative themes
with tcol2:
    st.subheader("Negative themes")
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
        conclusion(
            f"**{summ_neg.iloc[0]['theme']}** is the top complaint, "
            f"making up {summ_neg.iloc[0]['pct']}% of negative reviews. This is the first thing to fix."
        )

st.divider()

# --------------------------------------------------------------------------------------
# Section 3: Star rating distribution 
# --------------------------------------------------------------------------------------
# data exploration on star scores based on costumer experience using another bar chart
st.header("How are customers actually rating their experience?")
st.caption("A closer look using the actual 1-5 star score, instead of just good/bad.")

rcol1, rcol2 = st.columns([1, 1.3])

# star rating distribution
with rcol1:
    st.subheader("Star rating distribution")
    rating_counts = df["Customer Rating"].value_counts().sort_index()
    fig = px.bar(
        x=rating_counts.index, y=rating_counts.values,
        color=rating_counts.index,
        color_continuous_scale=["#c62828", "#ef6c00", "#fbc02d", "#7cb342", "#2e7d32"],
    )
    fig.update_layout(
        height=380, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Star rating", yaxis_title="Reviews",
        showlegend=False, coloraxis_showscale=False,
        xaxis=dict(tickmode="linear"),
    )
    st.plotly_chart(fig, use_container_width=True)
    most_common_rating = rating_counts.idxmax() # common star var
    one_star_pct = 100 * rating_counts.get(1, 0) / rating_counts.sum() # calculates what percentage of all reviews have a 1-star rating
    conclusion(
        f"Ratings are split **{most_common_rating}-star** is the most common score, but "
        f"**{one_star_pct:.0f}%** of all reviews are 1-star, showing a clear group of unhappy customers."
    )

# star rating category
with rcol2:
    st.subheader("Star rating by category")
    cat_rating = df.groupby("Category")["Customer Rating"].agg(["mean", "count"])
    cat_rating = cat_rating[cat_rating["count"] >= 10].sort_values("mean")
    fig = px.bar(
        cat_rating.tail(15),
        x="mean", orientation="h",
        color="mean", color_continuous_scale="RdYlGn",
        range_color=[1, 5],
    )
    fig.update_layout(
        height=380, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Average star rating", yaxis_title="",
        showlegend=False, coloraxis_showscale=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    # defining categories
    best_cat = cat_rating["mean"].idxmax()
    worst_cat = cat_rating["mean"].idxmin()
    conclusion(
        f"**{best_cat}** has the happiest customers ({cat_rating.loc[best_cat, 'mean']:.2f}/5), "
        f"while **{worst_cat}** has the lowest average rating ({cat_rating.loc[worst_cat, 'mean']:.2f}/5)."
    )

st.divider()

# --------------------------------------------------------------------------------------
# Section 4: Emotion signature per theme
# --------------------------------------------------------------------------------------
# dataexploration using heatmaps to show how many themes based by emotions
# im also using plotly.express.imshow by copy and paste from documentation
st.header("How do these themes make customers feel?")
st.caption("Each row adds up to 100%, showing which emotion dominates that topic.")

ecol1, ecol2 = st.columns(2)

# positive themes heatmap
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
        dominant_emotion = ct_pct.mean().idxmax()
        conclusion(
            f"**{dominant_emotion}** is the dominant emotion across most positive themes. "
            f"customers aren't just satisfied, they're emotionally engaged."
        )

# negative themes heatmap
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
        dominant_emotion = ct_pct.mean().idxmax()
        conclusion(
            f"**{dominant_emotion}** dominates negative reviews, knowing the emotion helps "
            f"decide how customer service should respond (calm down anger vs. reassure fear)."
        )

st.divider()

# --------------------------------------------------------------------------------------
# Section 5: Price vs satisfaction 
# --------------------------------------------------------------------------------------
# data exploration on price statisfaction using plotly 
# on the left is boxplot, on the right is bar chart 
st.header("Does price predict satisfaction?")
st.caption("Products are split into 4 equal-sized price groups, from cheapest to most expensive.")

pcol1, pcol2 = st.columns(2)

df_price = df.copy()
try:
    df_price["price_bracket"] = pd.qcut(
        df_price["Price"], q=4,
        labels=["Budget", "Mid-low", "Mid-high", "Premium"],
        duplicates="drop",
    )
except ValueError:
    df_price["price_bracket"] = pd.cut(df_price["Price"], bins=4)

# rating distribution based on price 
with pcol1:
    st.subheader("Rating distribution by price bracket")
    fig = px.box(
        df_price, x="price_bracket", y="Customer Rating",
        color="price_bracket",
        category_orders={"price_bracket": ["Budget", "Mid-low", "Mid-high", "Premium"]},
    )
    fig.update_layout(
        height=400, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Price bracket", yaxis_title="Customer rating",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    # defining two medians, one for inexpensive, one for expensive.
    median_by_bracket = df_price.groupby("price_bracket", observed=True)["Customer Rating"].median()
    cheapest_median = median_by_bracket.get("Budget", median_by_bracket.iloc[0])
    priciest_median = median_by_bracket.get("Premium", median_by_bracket.iloc[-1])
    # making conditionals if both median are different.
    if priciest_median > cheapest_median:
        conclusion(
            f"The typical (median) rating rises with price **Budget** items median "
            f"{cheapest_median:.0f}/5 stars vs. **Premium** items at {priciest_median:.0f}/5."
        )
    else:
        conclusion(
            f"Median ratings don't rise consistently with price **Budget** sits at "
            f"{cheapest_median:.0f}/5 and **Premium** at {priciest_median:.0f}/5."
        )

# negative review rate based on price  
with pcol2:
    st.subheader("Negative review rate by price bracket")
    neg_rate = (
        df_price.assign(is_neg=df_price["Sentiment"].eq("Negative"))
        .groupby("price_bracket", observed=True)["is_neg"].mean().mul(100)
    )
    fig = px.bar(
        neg_rate, color_discrete_sequence=[NEG_COLOR],
        category_orders={"price_bracket": ["Budget", "Mid-low", "Mid-high", "Premium"]},
    )
    fig.update_layout(
        height=400, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Price bracket", yaxis_title="% negative reviews",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    # same as before, making variables for each price
    cheapest_rate = neg_rate.get("Budget", neg_rate.iloc[0])
    priciest_rate = neg_rate.get("Premium", neg_rate.iloc[-1])
    # making conditionals if prices are different
    if cheapest_rate > priciest_rate:
        conclusion(
            f"Cheaper products complain more **Budget** items have a {cheapest_rate:.0f}% negative rate "
            f"vs. only {priciest_rate:.0f}% for **Premium** items. Price may signal quality expectations."
        )
    else:
        conclusion(
            f"Price doesn't clearly predict complaints **Premium** items actually have a higher "
            f"negative rate ({priciest_rate:.0f}%) than **Budget** items ({cheapest_rate:.0f}%)."
        )

st.divider()

# --------------------------------------------------------------------------------------
# Section 6: Geography 
# --------------------------------------------------------------------------------------
# making another bar chart to see where are the reviews comes from
st.header("Where are customers reviewing from?")
st.caption("Top 15 cities by number of reviews, and how each one feels about their purchase.")

gcol1, gcol2 = st.columns(2)

top_locations = df["Location"].value_counts().head(15)

# review volumne based on locations
with gcol1:
    st.subheader("Review volume by location")
    fig = px.bar(
        top_locations.sort_values(),
        orientation="h", color_discrete_sequence=[ACCENT],
    )
    fig.update_layout(
        height=450, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Reviews", yaxis_title="",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    conclusion(
        f"**{top_locations.idxmax()}** sends in the most reviews ({top_locations.max():,}), "
        f"making it the biggest customer base worth prioritizing."
    )

# negative review rates based on locations
with gcol2:
    st.subheader("Negative review rate by location")
    loc_counts = df.groupby("Location").size()
    loc_neg_rate = (
        df.assign(is_neg=df["Sentiment"].eq("Negative"))
        .groupby("Location")["is_neg"].mean().mul(100)
    )
    loc_neg_rate = loc_neg_rate[loc_counts[loc_neg_rate.index] >= 10]
    loc_neg_rate = loc_neg_rate.loc[loc_neg_rate.index.intersection(top_locations.index)]
    fig = px.bar(
        loc_neg_rate.sort_values(),
        orientation="h", color_discrete_sequence=[NEG_COLOR],
    )
    fig.add_vline(x=loc_neg_rate.mean(), line_dash="dash", line_color="gray")
    fig.update_layout(
        height=450, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="% negative reviews", yaxis_title="",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    worst_loc = loc_neg_rate.idxmax()
    conclusion(
        f"**{worst_loc}** has the highest share of negative reviews ({loc_neg_rate.max():.0f}%), "
        f"possibly pointing to local delivery or logistics issues."
    )

st.divider()

# --------------------------------------------------------------------------------------
# Section 7: Category performance 
# --------------------------------------------------------------------------------------
# using bubble chart (almost the same as bar chart) using plotly 
# using this formula : volume vs rating, bubble = review count 
st.header("Which categories sell a lot but satisfy little?")
st.caption("Each bubble is a category. Bigger bubble = more reviews.")

cat_perf = df.groupby("Category").agg(
    avg_sold=("Number Sold", "mean"),
    avg_rating=("Overall Rating", "mean"),
    review_count=("Customer Rating", "count"),
).reset_index()
cat_perf = cat_perf[cat_perf["review_count"] >= 10]

fig = px.scatter(
    cat_perf, x="avg_sold", y="avg_rating",
    size="review_count", color="avg_rating",
    color_continuous_scale="RdYlGn", range_color=[4, 5],
    hover_name="Category", size_max=45,
)
fig.update_layout(
    height=480, margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="Average units sold", yaxis_title="Average overall rating",
    coloraxis_showscale=False,
)
st.plotly_chart(fig, use_container_width=True)
risk_cat = cat_perf.sort_values(["avg_sold", "avg_rating"], ascending=[False, True]).iloc[0]
conclusion(
    f"**{risk_cat['Category']}** sells the most but isn't the highest rated "
    f"({risk_cat['avg_rating']:.2f}/5 average). worth a closer look since it affects the most customers."
)

st.divider()

# --------------------------------------------------------------------------------------
# Section 8: Priority matrix
# --------------------------------------------------------------------------------------
# trying using scatter plot to make a priority matrix
st.header("Which complaints should the business fix first?")
st.caption("X-axis = how often it happens. Y-axis = how angry/scared it makes customers. Top-right = fix first.")

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
        yaxis_title="Urgency (Percentage of Anger + Fear)",
    )
    st.plotly_chart(fig, use_container_width=True)
    top_priority = (prio["volume"].rank(pct=True) + prio["urgency"].rank(pct=True)).idxmax()
    conclusion(
        f"**{top_priority}** scores highest on both volume and urgency, this is the single "
        f"biggest opportunity to reduce complaints."
    )

st.divider()

# --------------------------------------------------------------------------------------
# Section 9: Top / bottom products 
# --------------------------------------------------------------------------------------
# showing simple dataframe using pandas to show the top rated vs lowest rated
st.header("Best and worst rated products")
st.caption("Only products with 5+ reviews are shown, so one angry buyer can't skew the list.")

prod_stats = df.groupby(["Product Name", "Category"]).agg(
    avg_rating=("Customer Rating", "mean"),
    reviews=("Customer Rating", "count"),
    price=("Price", "mean"),
).reset_index()
prod_stats = prod_stats[prod_stats["reviews"] >= 5]

bcol1, bcol2 = st.columns(2)

with bcol1:
    st.subheader("Top rated")
    top_prod = prod_stats.sort_values(["avg_rating", "reviews"], ascending=[False, False]).head(10)
    st.dataframe(
        top_prod.assign(avg_rating=top_prod["avg_rating"].round(2)).reset_index(drop=True),
        use_container_width=True, height=380,
    )

with bcol2:
    st.subheader("Lowest rated")
    bottom_prod = prod_stats.sort_values(["avg_rating", "reviews"], ascending=[True, False]).head(10)
    st.dataframe(
        bottom_prod.assign(avg_rating=bottom_prod["avg_rating"].round(2)).reset_index(drop=True),
        use_container_width=True, height=380,
    )

if not bottom_prod.empty:
    conclusion(
        f"The lowest-rated qualifying product is **{bottom_prod.iloc[0]['Product Name']}** "
        f"at {bottom_prod.iloc[0]['avg_rating']:.2f}/5 a candidate for delisting or seller follow-up."
    )

st.divider()

# --------------------------------------------------------------------------------------
# Section 10: Review explorer
# --------------------------------------------------------------------------------------
# using dataframe to search for some reviews
st.header("Review explorer")
st.caption("Pick a theme or search a keyword to read the actual reviews behind the numbers.")

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
st.caption("footer testing")