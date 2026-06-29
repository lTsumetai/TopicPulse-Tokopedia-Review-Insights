import streamlit as st

def get_connection():
    return st.connection("supabase", type="sql")