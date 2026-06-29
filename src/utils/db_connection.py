import streamlit as st

def get_connection():
    return st.connection("postgresql", type="sql")