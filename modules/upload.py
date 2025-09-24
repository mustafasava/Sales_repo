import streamlit as st


def upload():
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    