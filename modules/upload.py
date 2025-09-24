import streamlit as st
import re

def upload(uploaded_file):
    

    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        pattern = r"^([a-zA-Z]+)_(\d{4})_(0?[1-9]|1[0-2])\.(xlsx|xls)$"
        if re.match(pattern,uploaded_file.name) == None:
            st.markdown(
                        """
                        <div style="background-color:#f8d7da; color:#721c24; padding:10px; border-radius:5px; border:1px solid #f5c6cb;">
                            ❌ The naming pattern is wrong.<br>
                            Please name like: distname_year_month<br>
                            <h1>Example</h1>: ibs_2025_7
                        </div>
                        """,
                        unsafe_allow_html=True
                    )



        else:
            st.success(f"Validation Done !, File is accepted.")