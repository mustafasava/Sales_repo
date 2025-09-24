import streamlit as st
import pandas as pd
import re

def upload(uploaded_file):
    

    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        pattern = r"^([a-zA-Z]+)_(\d{4})_(0?[1-9]|1[0-2])\.(xlsx|xls)$"
        match = re.match(pattern,uploaded_file.name)
        if  match != None:
            st.success(f"Naming Validation Done !, File is accepted.")
            distname , year , month , ext = match.groups()
            try:
                df = pd.read_excel(uploaded_file)
                st.success(f"File is read successfully !")
                return df,distname , year , month
            except Exception as e:
                st.error(f"❌ Error reading Excel file: {e}")
                return None, None, None, None
            
        
        else:

            st.error(f"❌ The naming pattern is wrong. Please name like: distname_year_month , 💡  Example   : ibs_2025_7   ")
            