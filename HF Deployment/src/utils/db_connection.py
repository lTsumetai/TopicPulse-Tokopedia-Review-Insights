import os
import streamlit as st


def get_connection():
    """Supabase Postgres connection.

    - On Hugging Face: set a Space Secret named SUPABASE_DB_URL (a full SQLAlchemy URL,
      e.g. postgresql+psycopg2://USER:PASSWORD@HOST:5432/postgres). It is read here as an
      environment variable, so the password never lives in the repo.
    - Locally: if SUPABASE_DB_URL is not set, this falls back to the [connections.supabase]
      block in .streamlit/secrets.toml (gitignored).
    """
    url = os.environ.get("SUPABASE_DB_URL")
    if url:
        return st.connection("supabase", type="sql", url=url)
    return st.connection("supabase", type="sql")
