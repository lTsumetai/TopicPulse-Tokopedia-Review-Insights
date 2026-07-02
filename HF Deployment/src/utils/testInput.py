import streamlit as st
from sqlalchemy import text

from utils.db_connection import get_connection
from utils.inference import predict_theme


def _insert(product, rating, review, sentiment, theme):
    conn = get_connection()
    with conn.session as session:
        session.execute(
            text("INSERT INTO user_input (product, rating, review, sentiment, theme) "
                 "VALUES (:product, :rating, :review, :sentiment, :theme)"),
            {"product": product, "rating": rating, "review": review,
             "sentiment": sentiment, "theme": theme},
        )
        session.commit()


def run():
    st.header("📝 Submit a Review")
    st.write("Add a new customer review to the database. The app predicts its theme on the way "
             "in, so the dashboard sees new reviews already categorized.")

    with st.form("review_form"):
        product = st.text_input("Product")
        rating = st.slider("Rating", min_value=1, max_value=5, value=5)
        review = st.text_area("Review")
        submit = st.form_submit_button("Submit", type="primary")

    if submit:
        if not product.strip() or not review.strip():
            st.warning("Please complete all fields.")
            return

        # Predict the theme on the way in (best-effort: still save the review if this fails).
        sentiment, theme = None, None
        try:
            _, ranked = predict_theme(review.strip())
            if ranked:
                sentiment, theme = ranked[0][0], ranked[0][1]
        except Exception:
            pass

        try:
            _insert(product.strip(), rating, review.strip(), sentiment, theme)
            if theme:
                st.success(f"Saved! Predicted theme: **{theme}**  ({sentiment.lower()} review)")
            else:
                st.success("Review saved. (Theme will be assigned later.)")
        except Exception as e:
            st.error("Could not save to the database - check the Supabase connection / secrets.")
            st.caption(f"Details: {e}")
