import streamlit as st

st.set_page_config(
    page_title="NLP",
    page_icon="📋",
    layout="wide"
)

page = st.sidebar.selectbox(
    'Select Page',
    ['EDA', 'User','Prediction']
)

if page == 'EDA':
    import eda
    eda.run()
elif page == 'User':
    import utils.testInput as testInput
    testInput.run()
else:
    import prediction
    prediction.run()