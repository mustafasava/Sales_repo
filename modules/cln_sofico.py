import pandas as pd
from io import BytesIO
import streamlit as st

def cln_sofico(uploaded_file , distname , year , month):
    
    try:
        df = pd.read_excel(BytesIO(uploaded_file.getbuffer()),engine="xlrd")

        required_cols = ['VENDOR', 'VendorName', 'InventSiteID', 'ItemID', 'ItemName',        
                            'PrimaryVendorID', 'OrderAccount', 'Name', 'ADDRESS', 'CustGroup',   
                            'CUSTGROUPNAME', 'State', 'statename', 'ZipCode', 'INVOICEID',       
                            'INVOICEDATE', 'SALESPRICE', 'LINEAMOUNT', 'ZipCodeName', 'SalesQty',
                            'BonusQty', 'ReturnQty', 'ReturnBonus', 'NET SALES', 'من المدة',     
                            'الى المدة']
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
            cleaned_file = cleaned_file.dropna(subset = ['ItemID', 'ItemName','PrimaryVendorID','OrderAccount'], how="all")
            cleaned_file['dist_name'] = distname
            cleaned_file['year'] = year
            cleaned_file['month'] = month
            cleaned_file.reset_index(drop=True, inplace=True)

            if df.empty:
                st.error("❌ SOFICO ERROR: No valid data after cleaning (empty table).")
            else:
                return cleaned_file , distname , year , month
            
    except Exception as e:
        st.error(f"❌ SOFICO ERROR: Unexpected error: {str(e)}")
