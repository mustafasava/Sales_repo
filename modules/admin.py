from upload import upload
import streamlit as st

def admin():

    upload(st.file_uploader("Upload Excel file", type=["xlsx", "xls"]))
