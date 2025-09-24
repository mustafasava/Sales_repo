import pandas as pd
from io import BytesIO
import streamlit as st

def cln_ibs(uploaded_file , distname , year , month):
    
    try:
        df = pd.read_excel(BytesIO(uploaded_file.getbuffer()), skiprows=1)

        required_cols = ['Date', 'Supp. Code', 'Supp. Name', 'Item Code', 'Item Name', 'Brick',
       'Governorate Name', 'Territory Name', 'Unnamed: 8','Brick Name', 'QTY', 'FU','Total Qty']
        expected = required_cols
        actual = list(df.columns)

        if expected != actual:
            
            missing = [col for col in expected if col not in actual]
            extra = [col for col in actual if col not in expected]
            order_issue = (set(expected) == set(actual)) and (expected != actual)

            msg = "ERROR: Columns do not match exactly.\n"
            if missing:
                st.error(f"Missing columns: {missing} ")
                
            if extra:
                st.error(f"Unexpected columns: {extra}")
                
            if order_issue:
                st.error(f"Order mismatch. : Expected order: {expected}")
                st.error(f"Order mismatch. : Found order: {actual}")
            

        else:    
            cleaned_file = df.dropna(subset=['Supp. Code', 'Supp. Name', 'Item Code', 'Item Name'], how="all")
            cleaned_file = cleaned_file.drop(columns=['Unnamed: 8'])
            cleaned_file['Dist_Name'] = distname
            cleaned_file['year'] = year
            cleaned_file['month'] = month
            cleaned_file.reset_index(drop=True, inplace=True)

            if df.empty:
                st.error("❌ IBS ERROR: No valid data after cleaning (empty table).")
            else:
                st.success("✅ IBS file cleaned successfully.")
                return cleaned_file , distname , year , month
            

    except Exception as e:
        st.error(f"❌ IBS ERROR: Unexpected error: {str(e)}")
