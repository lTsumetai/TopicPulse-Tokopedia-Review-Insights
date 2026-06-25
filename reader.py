from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Score CSV Viewer", layout="wide")

st.title("Score CSV Viewer")
st.write("Select a CSV file from the scores folder and view its contents.")

scores_dir = Path(__file__).parent / "scores"
csv_files = sorted(scores_dir.glob("*.csv"))

if not csv_files:
    st.warning("No CSV files found in the scores folder.")
else:
    selected_file = st.selectbox(
        "Select a CSV file",
        options=csv_files,
        format_func=lambda path: path.name,
    )

    try:
        df = pd.read_csv(selected_file)
    except Exception as exc:
        st.error(f"Failed to read {selected_file.name}: {exc}")
    else:
        st.subheader(selected_file.name)
        st.dataframe(df, use_container_width=True)