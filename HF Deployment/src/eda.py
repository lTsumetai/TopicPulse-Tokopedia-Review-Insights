import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.paths import ARTIFACTS

POS_COLOR = "#2e7d32"
NEG_COLOR = "#c62828"
ACCENT = "#1565c0"


@st.cache_data
def load_data():
    return pd.read_csv(os.path.join(ARTIFACTS, "dashboard_data.csv"))


def theme_summary(d):
    """How many reviews fall into each theme."""
    if d.empty:
        return pd.DataFrame(columns=["theme", "reviews", "pct"])
    s = d.groupby("theme").size().sort_values(ascending=False).rename("reviews").reset_index()
    s["pct"] = (100 * s["reviews"] / len(d)).round(1)
    return s


def conclusion(text):
    """Blue takeaway box shown under each visualization."""
    st.info(f"**Takeaway:** {text}")


# ---------------- Individual analysis sections ----------------
# Each function renders ONE section. Only the section the user selects is
# executed/rendered, so the page never mounts ~13 Plotly charts at once
# (which is what made the EDA page churn / never settle on the Space).

def section_themes(df, df_pos, df_neg, summ_pos, summ_neg):
    st.header("What Customers Praise vs. Complain About")
    st.caption("Each bar is a recurring topic found in the reviews, and how often it shows up.")
    tcol1, tcol2 = st.columns(2)
    with tcol1:
        st.subheader("Positive themes")
        if summ_pos.empty:
            st.info("No positive reviews in the current filter selection.")
        else:
            fig = px.bar(summ_pos.sort_values("reviews"), x="reviews", y="theme", orientation="h",
                         text="pct", color_discrete_sequence=[POS_COLOR])
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10),
                              xaxis_title="Reviews", yaxis_title="", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            conclusion(f"**{summ_pos.iloc[0]['theme']}** is what customers love the most, "
                       f"making up {summ_pos.iloc[0]['pct']}% of positive reviews.")
    with tcol2:
        st.subheader("Negative Themes")
        if summ_neg.empty:
            st.info("No negative reviews in the current filter selection.")
        else:
            fig = px.bar(summ_neg.sort_values("reviews"), x="reviews", y="theme", orientation="h",
                         text="pct", color_discrete_sequence=[NEG_COLOR])
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10),
                              xaxis_title="Reviews", yaxis_title="", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            conclusion(f"**{summ_neg.iloc[0]['theme']}** is the top complaint, making up "
                       f"{summ_neg.iloc[0]['pct']}% of negative reviews. This is the first thing to fix.")


def section_ratings(df, df_pos, df_neg, summ_pos, summ_neg):
    st.header("How Are Customers Actually Rating Their Experience?")
    st.caption("A closer look using the actual 1-5 star score, instead of just good/bad.")
    rcol1, rcol2 = st.columns([1, 1.3])
    with rcol1:
        st.subheader("Star Rating Distribution")
        rating_counts = df["Customer Rating"].value_counts().sort_index()
        fig = px.bar(x=rating_counts.index, y=rating_counts.values, color=rating_counts.index,
                     color_continuous_scale=["#c62828", "#ef6c00", "#fbc02d", "#7cb342", "#2e7d32"])
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis_title="Star rating", yaxis_title="Reviews",
                          showlegend=False, coloraxis_showscale=False, xaxis=dict(tickmode="linear"))
        st.plotly_chart(fig, use_container_width=True)
        most_common_rating = rating_counts.idxmax()
        one_star_pct = 100 * rating_counts.get(1, 0) / rating_counts.sum()
        conclusion(f"Ratings are split: **{most_common_rating}-star** is the most common score, but "
                   f"**{one_star_pct:.0f}%** of all reviews are 1-star, showing a clear group of unhappy customers.")
    with rcol2:
        st.subheader("Star Rating by Category")
        cat_rating = df.groupby("Category")["Customer Rating"].agg(["mean", "count"])
        cat_rating = cat_rating[cat_rating["count"] >= 10].sort_values("mean")
        fig = px.bar(cat_rating.tail(15), x="mean", orientation="h", color="mean",
                     color_continuous_scale="RdYlGn", range_color=[1, 5])
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis_title="Average star rating", yaxis_title="",
                          showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        best_cat = cat_rating["mean"].idxmax()
        worst_cat = cat_rating["mean"].idxmin()
        conclusion(f"**{best_cat}** has the happiest customers ({cat_rating.loc[best_cat, 'mean']:.2f}/5), "
                   f"while **{worst_cat}** has the lowest average rating ({cat_rating.loc[worst_cat, 'mean']:.2f}/5).")


def section_emotions(df, df_pos, df_neg, summ_pos, summ_neg):
    st.header("How Do These Themes Make Customers Feel?")
    st.caption("Each row adds up to 100%, showing which emotion dominates that topic.")
    ecol1, ecol2 = st.columns(2)
    with ecol1:
        st.subheader("Positive Themes by Emotion")
        d = df_pos[df_pos["theme"] != "Other"]
        if d.empty:
            st.info("No data for the current filters.")
        else:
            ct = pd.crosstab(d["theme"], d["Emotion"])
            ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
            ct_pct = ct_pct.loc[d["theme"].value_counts().index]
            fig = px.imshow(ct_pct, text_auto=".0f", aspect="auto", color_continuous_scale="Greens",
                            labels=dict(color="% within theme"))
            fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            conclusion(f"**{ct_pct.mean().idxmax()}** is the dominant emotion across most positive themes - "
                       f"customers aren't just satisfied, they're emotionally engaged.")
    with ecol2:
        st.subheader("Negative Themes by Emotion")
        d = df_neg[df_neg["theme"] != "Other"]
        if d.empty:
            st.info("No data for the current filters.")
        else:
            ct = pd.crosstab(d["theme"], d["Emotion"])
            ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
            ct_pct = ct_pct.loc[d["theme"].value_counts().index]
            fig = px.imshow(ct_pct, text_auto=".0f", aspect="auto", color_continuous_scale="Reds",
                            labels=dict(color="% within theme"))
            fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            conclusion(f"**{ct_pct.mean().idxmax()}** dominates negative reviews; knowing the emotion helps "
                       f"decide how customer service should respond (calm anger vs. reassure fear).")


def section_price(df, df_pos, df_neg, summ_pos, summ_neg):
    st.header("Does Price Predict Satisfaction?")
    st.caption("Products are split into 4 equal-sized price groups, from cheapest to most expensive.")
    pcol1, pcol2 = st.columns(2)
    df_price = df.copy()
    try:
        df_price["price_bracket"] = pd.qcut(df_price["Price"], q=4,
                                            labels=["Budget", "Mid-low", "Mid-high", "Premium"],
                                            duplicates="drop")
    except ValueError:
        df_price["price_bracket"] = pd.cut(df_price["Price"], bins=4)
    with pcol1:
        st.subheader("Rating Distribution by Price Bracket")
        fig = px.box(df_price, x="price_bracket", y="Customer Rating", color="price_bracket",
                     category_orders={"price_bracket": ["Budget", "Mid-low", "Mid-high", "Premium"]})
        fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis_title="Price bracket", yaxis_title="Customer rating", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        median_by_bracket = df_price.groupby("price_bracket", observed=True)["Customer Rating"].median()
        cheapest_median = median_by_bracket.get("Budget", median_by_bracket.iloc[0])
        priciest_median = median_by_bracket.get("Premium", median_by_bracket.iloc[-1])
        if priciest_median > cheapest_median:
            conclusion(f"The typical (median) rating rises with price: **Budget** items median "
                       f"{cheapest_median:.0f}/5 vs. **Premium** items at {priciest_median:.0f}/5.")
        else:
            conclusion(f"Median ratings don't rise consistently with price: **Budget** sits at "
                       f"{cheapest_median:.0f}/5 and **Premium** at {priciest_median:.0f}/5.")
    with pcol2:
        st.subheader("Negative Review Rate by Price Bracket")
        neg_rate = (df_price.assign(is_neg=df_price["Sentiment"].eq("Negative"))
                    .groupby("price_bracket", observed=True)["is_neg"].mean().mul(100))
        fig = px.bar(neg_rate, color_discrete_sequence=[NEG_COLOR],
                     category_orders={"price_bracket": ["Budget", "Mid-low", "Mid-high", "Premium"]})
        fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis_title="Price bracket", yaxis_title="% negative reviews", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        cheapest_rate = neg_rate.get("Budget", neg_rate.iloc[0])
        priciest_rate = neg_rate.get("Premium", neg_rate.iloc[-1])
        if cheapest_rate > priciest_rate:
            conclusion(f"Cheaper products complain more: **Budget** items have a {cheapest_rate:.0f}% negative "
                       f"rate vs. only {priciest_rate:.0f}% for **Premium**. Price may signal quality expectations.")
        else:
            conclusion(f"Price doesn't clearly predict complaints: **Premium** items actually have a higher "
                       f"negative rate ({priciest_rate:.0f}%) than **Budget** items ({cheapest_rate:.0f}%).")


def section_geography(df, df_pos, df_neg, summ_pos, summ_neg):
    st.header("Where Are Customers Reviewing From?")
    st.caption("Top 15 cities by number of reviews, and how each one feels about their purchase.")
    gcol1, gcol2 = st.columns(2)
    top_locations = df["Location"].value_counts().head(15)
    with gcol1:
        st.subheader("Review Volume by Location")
        fig = px.bar(top_locations.sort_values(), orientation="h", color_discrete_sequence=[ACCENT])
        fig.update_layout(height=450, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis_title="Reviews", yaxis_title="", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        conclusion(f"**{top_locations.idxmax()}** sends in the most reviews ({top_locations.max():,}), "
                   f"making it the biggest customer base worth prioritizing.")
    with gcol2:
        st.subheader("Negative Review Rate by Location")
        loc_counts = df.groupby("Location").size()
        loc_neg_rate = (df.assign(is_neg=df["Sentiment"].eq("Negative"))
                        .groupby("Location")["is_neg"].mean().mul(100))
        loc_neg_rate = loc_neg_rate[loc_counts[loc_neg_rate.index] >= 10]
        loc_neg_rate = loc_neg_rate.loc[loc_neg_rate.index.intersection(top_locations.index)]
        fig = px.bar(loc_neg_rate.sort_values(), orientation="h", color_discrete_sequence=[NEG_COLOR])
        fig.add_vline(x=loc_neg_rate.mean(), line_dash="dash", line_color="gray")
        fig.update_layout(height=450, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis_title="% negative reviews", yaxis_title="", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        conclusion(f"**{loc_neg_rate.idxmax()}** has the highest share of negative reviews "
                   f"({loc_neg_rate.max():.0f}%), possibly pointing to local delivery or logistics issues.")


def section_category(df, df_pos, df_neg, summ_pos, summ_neg):
    st.header("Which Categories Sell a Lot but Satisfy Little?")
    st.caption("Each bubble is a category. Bigger bubble = more reviews.")
    cat_perf = df.groupby("Category").agg(
        avg_sold=("Number Sold", "mean"),
        avg_rating=("Overall Rating", "mean"),
        review_count=("Customer Rating", "count"),
    ).reset_index()
    cat_perf = cat_perf[cat_perf["review_count"] >= 10]
    fig = px.scatter(cat_perf, x="avg_sold", y="avg_rating", size="review_count", color="avg_rating",
                     color_continuous_scale="RdYlGn", range_color=[4, 5], hover_name="Category", size_max=45)
    fig.update_layout(height=480, margin=dict(l=10, r=10, t=10, b=10),
                      xaxis_title="Average units sold", yaxis_title="Average overall rating",
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    risk_cat = cat_perf.sort_values(["avg_sold", "avg_rating"], ascending=[False, True]).iloc[0]
    conclusion(f"**{risk_cat['Category']}** sells the most but isn't the highest rated "
               f"({risk_cat['avg_rating']:.2f}/5 average) - worth a closer look since it affects the most customers.")


def section_priority(df, df_pos, df_neg, summ_pos, summ_neg):
    st.header("Which Complaints Should The Business Fix First?")
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
        prio = pd.DataFrame({"volume": d["theme"].value_counts(),
                             "urgency": em_pct["Anger"] + em_pct["Fear"]})
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prio["volume"], y=prio["urgency"], mode="markers+text",
                                 text=prio.index, textposition="top center",
                                 marker=dict(size=14, color=NEG_COLOR), textfont=dict(size=10)))
        fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis_title="Volume (number of reviews)",
                          yaxis_title="Urgency (% Anger + Fear)")
        st.plotly_chart(fig, use_container_width=True)
        top_priority = (prio["volume"].rank(pct=True) + prio["urgency"].rank(pct=True)).idxmax()
        conclusion(f"**{top_priority}** scores highest on both volume and urgency - the single biggest "
                   f"opportunity to reduce complaints.")


def section_products(df, df_pos, df_neg, summ_pos, summ_neg):
    st.header("Best and Worst Rated Products")
    st.caption("Only products with 5+ reviews are shown, so one angry buyer can't skew the list.")
    prod_stats = df.groupby(["Product Name", "Category"]).agg(
        avg_rating=("Customer Rating", "mean"),
        reviews=("Customer Rating", "count"),
        price=("Price", "mean"),
    ).reset_index()
    prod_stats = prod_stats[prod_stats["reviews"] >= 5]
    bcol1, bcol2 = st.columns(2)
    with bcol1:
        st.subheader("Top Rated")
        top_prod = prod_stats.sort_values(["avg_rating", "reviews"], ascending=[False, False]).head(10)
        st.dataframe(top_prod.assign(avg_rating=top_prod["avg_rating"].round(2)).reset_index(drop=True),
                     use_container_width=True, height=380)
    with bcol2:
        st.subheader("Lowest Rated")
        bottom_prod = prod_stats.sort_values(["avg_rating", "reviews"], ascending=[True, False]).head(10)
        st.dataframe(bottom_prod.assign(avg_rating=bottom_prod["avg_rating"].round(2)).reset_index(drop=True),
                     use_container_width=True, height=380)
    if not bottom_prod.empty:
        conclusion(f"The lowest-rated qualifying product is **{bottom_prod.iloc[0]['Product Name']}** "
                   f"at {bottom_prod.iloc[0]['avg_rating']:.2f}/5 - a candidate for delisting or seller follow-up.")


def section_explorer(df, df_pos, df_neg, summ_pos, summ_neg):
    st.header("Review Explorer")
    st.caption("Pick a theme or search a keyword to read the actual reviews behind the numbers.")
    sel_theme = st.multiselect("Filter by theme", sorted(df["theme"].unique()), default=[])
    explorer_df = df.copy()
    if sel_theme:
        explorer_df = explorer_df[explorer_df["theme"].isin(sel_theme)]
    search = st.text_input("Search review text (optional)", "")
    if search:
        explorer_df = explorer_df[explorer_df["Customer Review"].str.contains(search, case=False, na=False)]
    st.dataframe(
        explorer_df[["Category", "Product Name", "Sentiment", "Emotion", "theme", "Customer Review"]]
        .reset_index(drop=True),
        use_container_width=True, height=400,
    )
    st.caption(f"Showing {len(explorer_df):,} of {len(df):,} filtered reviews.")


# Ordered registry of sections: label -> render function.
SECTIONS = {
    "Praise vs Complaints": section_themes,
    "Star Ratings": section_ratings,
    "Emotions by Theme": section_emotions,
    "Price vs Satisfaction": section_price,
    "Geography": section_geography,
    "Category Performance": section_category,
    "Priority Matrix": section_priority,
    "Best & Worst Products": section_products,
    "Review Explorer": section_explorer,
}


def run():
    reviews = load_data()
    ALL_CATEGORIES = sorted(reviews["Category"].unique())
    ALL_SENTIMENTS = sorted(reviews["Sentiment"].unique())
    ALL_EMOTIONS = sorted(reviews["Emotion"].unique())

    # ---------------- Sidebar filters ----------------
    st.sidebar.title("Filters")
    st.sidebar.caption("Filters apply to every section below.")
    sel_sentiment = st.sidebar.multiselect("Sentiment", ALL_SENTIMENTS, default=ALL_SENTIMENTS)
    sel_category = st.sidebar.multiselect("Product category", ALL_CATEGORIES, default=[])
    sel_emotion = st.sidebar.multiselect("Emotion", ALL_EMOTIONS, default=[])

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
    summ_pos = theme_summary(df_pos[df_pos["theme"] != "Other"])
    summ_neg = theme_summary(df_neg[df_neg["theme"] != "Other"])

    # ---------------- Header ----------------
    st.title("Tokopedia Review Insights")
    st.caption("What do customers actually praise and complain about, and what should the business do about it?")

    # ---------------- KPI row (always shown, lightweight) ----------------
    total = len(df)
    pct_pos = 100 * len(df_pos) / total if total else 0
    pct_neg = 100 * len(df_neg) / total if total else 0
    top_complaint = summ_neg.iloc[0]["theme"] if not summ_neg.empty else "-"
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total reviews", f"{total:,}")
    c2.metric("Positive", f"{len(df_pos):,}", f"{pct_pos:.0f}% of total")
    c3.metric("Negative", f"{len(df_neg):,}", f"{pct_neg:.0f}% of total", delta_color="inverse")
    c4.metric("Avg. customer rating", f"{df['Customer Rating'].mean():.2f} / 5")
    c5.metric("Top complaint", top_complaint if len(top_complaint) < 22 else top_complaint[:20] + "...")
    st.divider()

    # ---------------- Section selector ----------------
    # Only the chosen section's charts are built/rendered. This keeps the page
    # light enough to settle reliably on the Space (instead of churning while it
    # tries to mount every chart at once).
    choice = st.radio("Choose an analysis", list(SECTIONS.keys()), horizontal=True)
    st.divider()
    SECTIONS[choice](df, df_pos, df_neg, summ_pos, summ_neg)

    st.divider()
    st.caption("Topic Pulse | Tokopedia Review Insight  -  FTDS-040-HCK Group 001")
