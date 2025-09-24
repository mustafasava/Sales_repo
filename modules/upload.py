import streamlit as st
import re

def upload():
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        return uploaded_file.name
    else:
        return "no file uploaded yet"
    
def validate(filename):
    pattern = r"^([a-zA-Z]+)_(\d{4})_(0?[1-9]|1[0-2])\.(xlsx|xls)$"
    if re.match(pattern,filename) == None:
        st.error(f"The naming pattern is wrong please name like : distname_year_month ,\
                  example: ibs_2025_7")
