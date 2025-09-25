import streamlit as st
import pandas as pd
import re
from info import dist_list

def upload(uploaded_file):
    

    if uploaded_file is not None:
        pattern = r"^([a-zA-Z]+)_(\d{4})_(0?[1-9]|1[0-2])\.(xlsx|xls)$"
        match = re.match(pattern,uploaded_file.name)

        if  match != None:
            distname , year , month , ext = match.groups()

            if distname in dist_list:
                year = int(year)
                month = int(month)

                try:
                    return uploaded_file , distname , year , month    #---------------- RETURNED ITEMS -------------#
                
                except Exception as e:
                    st.error(f"❌ Error reading Excel file: {e}")
                    
            else:
                st.error(f"❌ The distributor you provided is not in distributors list : {dist_list.keys()}")
                
        else:
            st.error(f"❌ The naming pattern is wrong. Please name like: distname_year_month , 💡  Example   : ibs_2025_7   ")

