import streamlit as st
import os

# --------------------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------------------
# Page configurations
st.set_page_config(
    page_title="Tokopedia Review Insights",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Get current directory path to prevent "File Not Found" errors
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------------------
# Home page content function
# --------------------------------------------------------------------------------------
# main homepage, about the project and the dashboard
def home_content():
    st.title("Tokopedia Review Insights")

    # Create two clean tabs to "overview" and "about this dashboard"
    tab1, tab2 = st.tabs(["Overview", "About This Dashboard"])

    with tab1:
        st.markdown(
            """
            Understand **what customers actually praise and complain about** in Indonesian
            Tokopedia reviews — not just whether a review is good or bad, but the *topic*
            behind it.

            This app accompanies our topic-modeling project (BERTopic on the PRDECT-ID dataset).
            
            - 📊 **EDA** — explore the reviews: sentiment balance, themes, emotions, categories.
            """
        )

        st.subheader("How It Works")
        st.markdown(
            """
            Each review is turned into a numerical vector with a multilingual language model,
            then matched to the closest of the themes our model discovered — 8 themes customers
            praise and 9 they complain about.
            """
        )

        col1, col2 = st.columns(2)
        with col1:
            st.info(
                "**Praise Themes:** product quality, packaging, seller service, fast delivery, value, ..."
            )
        with col2:
            st.warning(
                "**Complaint Themes:** item not as described, poor quality, slow delivery, defective, ..."
            )

    with tab2:
        st.markdown("Pipeline & Modeling")
        st.markdown(
            """
            Built on top of a topic modeling pipeline:
            * **BERTopic** (sentence embeddings + UMAP + HDBSCAN) for the primary themes.
            * **LDA and K-Means** baselines for comparison.
            * Reviews are modeled separately for positive and negative sentiment.
            """
        )
        
        st.markdown("---")
        
        st.markdown("Dataset")
        st.markdown(
            """
            * **[PRDECT-ID](https://github.com/crush7/PRDECT-ID)** Product Reviews Dataset for Emotions Classification Tasks - Indonesian.
            * **[Kamus Alay](https://github.com/nasalsabila/kamus-alay/blob/master/colloquial-indonesian-lexicon.csv)** lexicon for text normalization of Indonesian colloquial words. A total of 3,592 unique colloquial words—also known as *"bahasa alay"*—and manually annotated them with the normalized form.
            """
        )


# --------------------------------------------------------------------------------------
# Sidebar Branding & Custom Navigation
# --------------------------------------------------------------------------------------
# sidebar navigation for home and EDA
st.sidebar.markdown("Tokopedia Review Insights")
st.sidebar.caption("NLP topic modeling on Indonesian product reviews")
st.sidebar.write("")  # adding spacing

# radio selection navigation type
page_selection = st.sidebar.radio(
    "Navigate",
    ["Home", "EDA"]
    # adding this lists later ["Methodology", "Predict Theme", "Submit a Review"]
)

# Sidebar footer
st.sidebar.divider()
st.sidebar.caption("FTDS-040-HCK - Group 001")


# --------------------------------------------------------------------------------------
# Page Router Control
# --------------------------------------------------------------------------------------
# adding page selection by doing router control
if page_selection == "Home":
    home_content()

# uncomment methodology page when such file exists on src
# elif page_selection == "Methodology":
#     st.title("Methodology")
#     st.write("Your detailed methodology content goes here.")

elif page_selection == "EDA":
    eda_path = os.path.join(CURRENT_DIR, "eda.py")
    try:
        with open(eda_path, encoding="utf-8") as f:
            exec(f.read(), globals())
    except FileNotFoundError:
        st.error(f"Could not find eda.py at: {eda_path}")

# uncomment predict theme page when such file exists on src
# elif page_selection == "Predict Theme":
#     pred_path = os.path.join(CURRENT_DIR, "prediction.py")
#     try:
#         with open(pred_path, encoding="utf-8") as f:
#             exec(f.read(), globals())
#     except FileNotFoundError:
#         st.error(f"Could not find prediction.py at: {pred_path}")

# uncomment submit a review page when such file exists on src
# elif page_selection == "Submit a Review":
#     st.title("Submit a Review")
#     st.write(" user submission form goes here.")
