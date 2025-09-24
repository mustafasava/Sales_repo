import streamlit as st
import re

def upload(uploaded_file):
    

    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        pattern = r"^([a-zA-Z]+)_(\d{4})_(0?[1-9]|1[0-2])\.(xlsx|xls)$"
        if re.match(pattern,uploaded_file.name) == None:
            st.error(st.write("❌ The naming pattern is wrong.\nPlease name like: distname_year_month\nExample: ibs_2025_7"))


        else:
            st.success(f"Validation Done !, File is accepted.")