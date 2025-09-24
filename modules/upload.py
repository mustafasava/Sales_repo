import streamlit as st
import pandas as pd
import re

def upload(uploaded_file):
    

    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        pattern = r"^([a-zA-Z]+)_(\d{4})_(0?[1-9]|1[0-2])\.(xlsx|xls)$"
        match = re.match(pattern,uploaded_file.name)
        if  match != None:
            st.success(f"Validation Done !, File is accepted.")
            distname , year , month , ext = match.groups()
            try:
                df = pd.read_excel(uploaded_file)
            except Exception as e:
                st.error(f"❌ Error reading Excel file: {e}")
                return None, None, None, None
            return df,distname , year , month
        
        else:
            st.markdown(
                        """
                        <div style="background-color:#f8d7da; color:#721c24; padding:10px; border-radius:5px; border:1px solid #f5c6cb;">
                            ❌ The naming pattern is wrong.<br>
                            Please name like: distname_year_month  ,<br>
                            Example   : ibs_2025_7
                        </div>
                        """,
                        unsafe_allow_html=True
                    )