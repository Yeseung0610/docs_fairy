import os
import shutil
import streamlit as st

# Clear Streamlit cache
if os.path.exists(".streamlit/cache"):
    shutil.rmtree(".streamlit/cache")

# Clear browser cachefdsafsd
st.write("Cache cleared. Please refresh your browser.")