import streamlit as st
import numpy as np

st.title("Practice Row-Operation Interface")

rows = st.text_input("Enter the number of rows for Matrix A:", "4")
cols = st.text_input("Enter the number of columns for Matrix A:", "3")

if st.button("Run Operation"):
    st.write("Matrix tool running...")
