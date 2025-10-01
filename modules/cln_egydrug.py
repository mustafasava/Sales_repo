import pandas as pd
from io import BytesIO
import streamlit as st

def cln_egydrug(uploaded_file , distname , year , month):
    
    try:
        df_branches = pd.read_excel(BytesIO(uploaded_file.getbuffer()),sheet_name="Branches Sales",dtype={"BRANCH_CODE":str,"CUSTOMER_CODE":str})
        df_pharmacies = pd.read_excel(BytesIO(uploaded_file.getbuffer()),sheet_name="Pharmacy Sales",dtype={"BRANCH_CODE":str,"CUSTOMER_CODE":str})
        df_return = pd.read_excel(BytesIO(uploaded_file.getbuffer()),sheet_name="Branch Sales Return",dtype={"BRANCH_CODE":str,"CUSTOMER_CODE":str})
        df_transfer = pd.read_excel(BytesIO(uploaded_file.getbuffer()),sheet_name="Transfer")
        df_trnsreturn = pd.read_excel(BytesIO(uploaded_file.getbuffer()),sheet_name="Transfer Return ")
        df_stocks = pd.read_excel(BytesIO(uploaded_file.getbuffer()),sheet_name="Monthly Stocks")
        
        branches_rcols =['CR_TIME', 'INVOICE_SER', 'INVOICE_NO', 'INVOICE_DATE', 'ITEM_CODE',   
        'ITEM_NAME', 'SUPPLIER_CODE', 'SUPPLIER_NAME', 'STATUS', 'STATUS_NAME','ITEM_OUT_STATUS', 'STATUS_DESC', 'QTY_INVOICE', 'RETURN_QTY',
        'QTY_PACK', 'QTY_UNIT', 'TOTAL_VALUE_INVOICE', 'BASE_PRICE','PHARMAIST_PRICE', 'COMMUNITY_PRICE', 'EXPIRE_DATE', 'BATCH_NO','CUSTOMER_CODE', 'CUSTOMER_NAME', 'CUSTOMER_ADDRESS',
        'CUSTOMER_TYPE_CODE', 'EGYDRUG_CUSTOMER_TYPE', 'CUST_FAMILY','BRANCH_CODE', 'BRANCH_NAME', 'PROVINCE_CODE', 'PROVINCE_NAME','MRKZ_C', 'MRKZ_N']

        pharmacies_rcols =['CR_TIME', 'INVOICE_SER', 'INVOICE_NO', 'INVOICE_DATE', 'ITEM_CODE',
        'ITEM_NAME', 'SUPPLIER_CODE', 'SUPPLIER_NAME', 'STATUS', 'STATUS_NAME',
        'ITEM_OUT_STATUS', 'STATUS_DESC', 'QTY_INVOICE', 'RETURN_QTY','QTY_PACK', 'QTY_UNIT', 'TOTAL_VALUE_INVOICE', 'BASE_PRICE',
        'PHARMAIST_PRICE', 'COMMUNITY_PRICE', 'EXPIRE_DATE', 'BATCH_NO','CUSTOMER_CODE', 'CUSTOMER_NAME', 'CUSTOMER_ADDRESS',
        'CUSTOMER_TYPE_CODE', 'EGYDRUG_CUSTOMER_TYPE', 'CUST_FAMILY','BRANCH_CODE', 'BRANCH_NAME', 'PROVINCE_CODE', 'PROVINCE_NAME','MRKZ_C', 'MRKZ_N']

        sales_return_rcols =['CR_TIME', 'INVOICE_SER', 'INVOICE_NO', 'INVOICE_DATE', 'ITEM_CODE',
        'ITEM_NAME', 'SUPPLIER_CODE', 'SUPPLIER_NAME', 'STATUS', 'STATUS_NAME','ITEM_OUT_STATUS', 'STATUS_DESC', 'QTY_INVOICE', 'RETURN_QTY',
        'QTY_PACK', 'QTY_UNIT', 'VALUE', 'BASE_PRICE', 'PHARMAIST_PRICE','COMMUNITY_PRICE', 'EXPIRE_DATE', 'BATCH_NO', 'CUSTOMER_CODE','CUSTOMER_NAME', 'CUSTOMER_ADDRESS',
        'CUSTOMER_TYPE_CODE','EGYDRUG_CUSTOMER_TYPE', 'CUST_FAMILY', 'BRANCH_CODE', 'BRANCH_NAME','PROVINCE_CODE', 'PROVINCE_NAME', 'MRKZ_C', 'MRKZ_N']

        transfer_rcols =['TRANSFER_ORDER_INVOICE_SER', 'CARD_DATE', 'ITEM_CODE', 'ITEM_NAME_ENG',
        'STOCK_TYPE_CODE', 'SUPPLIER_CODE', 'TO_COMPANY_ENTITY_CODE',
        'TO_COMPANY_ENTITY_NAME', 'FROM_COMPANY_ENTITY_CODE',
        'FROM_COMPANY_ENTITY_NAME', 'GOV_NAME', 'QTY', 'RETURN_QTY',
        'EXPIRE_DATE', 'BATCH_NO', 'VALUE']

        trnsreturn_rcols =['TRANS_SERIAL', 'CARD_DATE', 'ITEM_CODE', 'ITEM_NAME_ENG',
        'STOCK_TYPE_CODE', 'SUPPLIER_CODE', 'TO_COMPANY_ENTITY_CODE',
        'TO_COMPANY_ENTITY_NAME', 'FROM_COMPANY_ENTITY_CODE',
        'FROM_COMPANY_ENTITY_NAME', 'GOV_NAME', 'SALES_QTY', 'RETURN_QTY',
        'EXPIRE_DATE', 'BATCH_NO', 'VALUE']

        stocks_rcols =['ITEM_CODE', 'ITEM_NAME_ENG', 'ITEM_STOCK', 'ITEM_STATUS_CODE',
        'ITEM_STATUS_NAME', 'STOCK_TYPE_CODE', 'STOCK_TYPE_NAME', 'EXPIRE_DATE',
        'BATCH_NO', 'TOTAL_BASE_PRICE', 'TOTAL_PHARMAIST_PRICE',
        'TOTAL_COMMUNITY_PRICE', 'COMPANY_ENTITY_CODE', 'COMPANY_ENTITY_NAME',
        'STORE_DEPT_CODE', 'STORE_DEPT_NAME']

        df_map = {
        "Branches Sales": (df_branches, branches_rcols),
        "Pharmacy Sales": (df_pharmacies, pharmacies_rcols),
        "Sales Return": (df_return, sales_return_rcols),
        "Transfer": (df_transfer, transfer_rcols),
        "Transfer Return": (df_trnsreturn, trnsreturn_rcols),
        "Monthly Stocks": (df_stocks, stocks_rcols)}
        for sheet_name, (df, expected) in df_map.items():
            actual = list(df.columns)
            if expected != actual:
                
                missing = [col for col in expected if col not in actual]
                extra = [col for col in actual if col not in expected]
                order_issue = (set(expected) == set(actual)) and (expected != actual)
                if missing:
                    st.error(f"Error in {sheet_name}: Missing columns: {missing} ")
                if extra:
                    st.error(f"Error in {sheet_name}: Unexpected columns: {extra}")
                if order_issue:
                    st.error(f"Error in {sheet_name}: Order mismatch. : Expected order: {expected}")
                    st.error(f"Error in {sheet_name}: Order mismatch. : Found order: {actual}")
                return 0
                
                
        df_return= df_return.rename(columns={"VALUE":"TOTAL_VALUE_INVOICE"})
        df_transfer= df_transfer.rename(columns={"TRANSFER_ORDER_INVOICE_SER":"TRANS_SERIAL","QTY":"SALES_QTY"})
        df_branches["sheet_src"] = "Br"
        df_pharmacies["sheet_src"] = "Ph"
        df_return["sheet_src"] = "Rt"
        df_transfer["sheet_src"] = "Tr"
        df_trnsreturn["sheet_src"] = "Tr_Rt"
        sales_df = pd.concat([df_branches, df_pharmacies, df_return], ignore_index=True)
        transfer_df = pd.concat([df_transfer, df_trnsreturn], ignore_index=True)
        dfs = [sales_df,transfer_df,df_stocks]
        
        for i in dfs:
            i["year"] = year
            i["month"] = month
            i["dist_name"] = distname

        dfs = {
        "egydrug_sales": sales_df,
        "egydrug_transfer": transfer_df,
        "egydrug_stock": df_stocks}

        if all(df.empty for df in dfs.values()) or sales_df.empty:
            st.error("❌ EGYDRUG ERROR: No valid data after cleaning (empty table).")
        else:
            return dfs , distname , year , month
            
    except Exception as e:
        st.error(f"❌ EGYDRUG ERROR: Unexpected error: {e}")
