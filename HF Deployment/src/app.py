import os

import streamlit as st

from utils.paths import LOGO

st.set_page_config(
    page_title="Topic Pulse | Tokopedia Review Insight",
    page_icon="🛒",
    layout="wide",
)

st.sidebar.title("Topic Pulse")
st.sidebar.caption("Tokopedia Review Insight - NLP topic modeling")
page = st.sidebar.radio("Navigate", ["Home", "Methodology", "EDA", "Predict Theme", "Submit a Review"])
st.sidebar.markdown("---")
st.sidebar.caption("FTDS-040-HCK - Group 001")


def home():
    # Centered logo (place "Topic Pulse.png" in the repo root)
    if os.path.exists(LOGO):
        _, mid, _ = st.columns([1, 1, 1])
        with mid:
            st.image(LOGO, use_column_width=True)

    st.markdown(
        "<h1 style='text-align:center; margin-bottom:0;'>Topic Pulse</h1>"
        "<p style='text-align:center; color:#2e7d32; font-size:1.15rem; margin-top:0.2rem;'>"
        "Tokopedia Review Insight</p>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
Understand **what customers actually praise and complain about** in Indonesian Tokopedia
reviews - not just whether a review is good or bad, but the *topic* behind it.

This app accompanies our topic-modeling project (BERTopic on the PRDECT-ID dataset):

- **Methodology** - how the model works, end to end.
- **EDA** - an interactive dashboard: themes, emotions, ratings, price, geography, priorities.
- **Predict Theme** - paste any review and get its predicted theme (praise vs complaint).
- **Submit a Review** - add a new review to our live database (it is themed on the way in).
        """
    )

    c1, c2 = st.columns(2)
    c1.info("Praise themes: product quality, packaging, seller service, fast delivery, value, ...")
    c2.warning("Complaint themes: item not as described, poor quality, slow delivery, defective, ...")
    st.caption("Use the sidebar to navigate. Try **Predict Theme** for a quick demo, or **EDA** for the dashboard.")


if page == "Home":
    home()
elif page == "Methodology":
    import methodology
    methodology.run()
elif page == "EDA":
    import eda
    eda.run()
elif page == "Predict Theme":
    import prediction
    prediction.run()
else:
    import utils.testInput as testInput
    testInput.run()
