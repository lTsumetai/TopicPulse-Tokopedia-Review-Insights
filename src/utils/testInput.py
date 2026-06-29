import streamlit as st
import psycopg2

from utils.db_connection import get_connection
from sqlalchemy import text

def run():    
    st.subheader('Input User')
    def insert_data(product, rating, review):
        # akses database
        conn = get_connection()
        
        # create session
        with conn.session as session:
            session.execute(
                text("""
                    INSERT INTO user_input
                    (product, rating, review)

                    VALUES
                    (:product, :rating, :review)
                """),
                {
                    "product": product,
                    "rating": rating,
                    "review": review
                }
            )

            session.commit()
    
    with st.form("review_form"):

        product = st.text_input("Product")

        rating = st.slider(
            "Rating",
            min_value=1,
            max_value=5,
            value=5
        )

        review = st.text_area("Review")

        submit = st.form_submit_button("Submit")

    if submit:

        if product == "" or review == "":
            st.warning("Please complete all fields.")

        else:

            insert_data(
                product,
                rating,
                review
            )

            st.success("Review successfully saved!")