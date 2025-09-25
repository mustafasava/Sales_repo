import pandas as pd
from io import BytesIO
import streamlit as st
import numpy as np

def cln_epda(uploaded_file , distname , year , month):
    
    try:
        df = pd.read_excel(BytesIO(uploaded_file.getbuffer()), engine="xlrd",skiprows=10)

        required_cols = ['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'النسبة', 'Unnamed: 4',       
                        'الكمية المباعة', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8',
                        'Unnamed: 9', 'القيمة', 'Unnamed: 11', 'الصنف', 'Unnamed: 13',
                        'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17',
                        'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21',
                        'Unnamed: 22', 'Unnamed: 23', 'Unnamed: 24', 'Unnamed: 25',
                        'Unnamed: 26', 'كود الصنف', 'Unnamed: 28', 'Unnamed: 29', 'Unnamed: 30',
                        'Unnamed: 31', 'Unnamed: 32', 'Unnamed: 33', 'Unnamed: 34',
                        'Unnamed: 35', 'Unnamed: 36', 'Unnamed: 37']
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
            cleaned_file = df.rename(columns={'Unnamed: 15':'client name','Unnamed: 28':'client code','الكمية المباعة':'sales Units','القيمة':'sales Value','الصنف':'item name','كود الصنف':'item code'})
            selected_cols = ['client code','client name','item name','item code','sales Units','sales Value']
            cleaned_file = cleaned_file[selected_cols]
            cleaned_file["client name"] = cleaned_file["client name"].replace("بيوتك فارما", np.nan)
            cleaned_file[['client code','client name','sales Units']] = cleaned_file[['client code','client name','sales Units']].ffill()
            cleaned_file = cleaned_file[cleaned_file['item code'].notna()]
            cleaned_file['dist_name'] = distname
            cleaned_file['year'] = year
            cleaned_file['month'] = month
            cleaned_file.reset_index(drop=True, inplace=True)

            if df.empty:
                st.error("❌ EPDA ERROR: No valid data after cleaning (empty table).")
            else:
                return cleaned_file , distname , year , month
            
    except Exception as e:
        st.error(f"❌ EPDA ERROR: Unexpected error: {str(e)}")
