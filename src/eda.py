import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

def run():
    st.header("📊 Exploratory Data Analysis")
    st.subheader('Dataset Overview')
    
    @st.cache_data
    def load_data(path):
        return pd.read_csv(path)
    
    df = load_data(os.path.join("data/PRDECT-ID Dataset.csv"))
    st.dataframe(df)
    
    st.subheader('Distribution Class')
    