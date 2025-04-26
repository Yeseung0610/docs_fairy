import os
import shutil
import streamlit as st

# Clear Streamlit cache
if os.path.exists(".streamlit/cache"):
    shutil.rmtree(".streamlit/cache")

st.write("Cache cleared. Please refresh your browser.")
