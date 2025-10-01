import numpy as np
import pandas as pd
import streamlit as st

def prep_egydrug(cleaned_file , distname , year , month):
    try:
        prepared_file = cleaned_file["egydrug_sales"]

        prepared_file = prepared_file.rename(columns={
                            "ITEM_CODE": "item_code",
                            "ITEM_NAME": "item_name",
                            "CUSTOMER_NAME": "customer_name",
                            "CUSTOMER_ADDRESS": "customer_address",
                            "BRANCH_NAME": "branch_name"
                            
                        })
        

        prepared_file["BRANCH_CODE"] = prepared_file["BRANCH_CODE"].astype(str)
        prepared_file["brick_code"] = np.where(
                                    prepared_file["BRANCH_CODE"].str.startswith("06"),
                                    prepared_file["BRANCH_CODE"], 
                                    prepared_file["CUSTOMER_CODE"] 
                                ).astype(str)
        
        
        
        prepared_file["sales_units"] = prepared_file.apply(
                        lambda x: x["QTY_INVOICE"] + x["RETURN_QTY"]
                        if ("بونص" not in str(x["STATUS_NAME"])) and ("بونص" not in str(x["STATUS_DESC"]))
                        else 0,
                        axis=1)


        prepared_file["bonus_units"] = prepared_file.apply(
                        lambda x: x["QTY_INVOICE"] + x["RETURN_QTY"]
                        if ("بونص" in str(x["STATUS_NAME"])) or ("بونص" in str(x["STATUS_DESC"]))
                        else 0,
                        axis=1)
        
        prepared_file = prepared_file[[
            "item_code", "item_name", "brick_code", "customer_name",
            "customer_address", "branch_name", "sales_units","bonus_units", "dist_name","year","month"]]
        return prepared_file , distname , year , month

        
    except Exception as e:
        st.error(f"Error : {e}")