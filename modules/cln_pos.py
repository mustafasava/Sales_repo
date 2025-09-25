import pandas as pd
from io import BytesIO
import streamlit as st

def cln_pos(uploaded_file , distname , year , month):
    
    try:
        df = pd.read_excel(BytesIO(uploaded_file.getbuffer()), skiprows=1,engine="xlrd")

        required_cols = ['English Name', 'Product Code', 'Product Name', 'Territory Code',  
       'Territory Name', 'Sales Value', 'Credit Value', 'Net Sales Value','Sales', 'Bonus']
        expected = required_cols
        actual = list(df.columns)

        if expected != actual:
            
            missing = [col for col in expected if col not in actual]
            extra = [col for col in actual if col not in expected]
            order_issue = (set(expected) == set(actual)) and (expected != actual)
            if missing:
                st.error(f"Missing columns: {missing} ")
            if extra:
                st.error(f"Unexpected columns: {extra}")
            if order_issue:
                st.error(f"Order mismatch. : Expected order: {expected}")
                st.error(f"Order mismatch. : Found order: {actual}")
            
        else:    
            cleaned_file = df[df["English Name"] != "English Name"]
            cleaned_file = cleaned_file.dropna(subset = ['Product Code', 'Product Name', 'Territory Code'], how="all")
            cleaned_file["English Name"] = cleaned_file["English Name"].ffill()
            cleaned_file['dist_name'] = distname
            cleaned_file['year'] = year
            cleaned_file['month'] = month
            cleaned_file.reset_index(drop=True, inplace=True)

            if df.empty:
                st.error("❌ POS ERROR: No valid data after cleaning (empty table).")
            else:
                return cleaned_file , distname , year , month
            
    except Exception as e:
        st.error(f"❌ POS ERROR: Unexpected error: {str(e)}")
