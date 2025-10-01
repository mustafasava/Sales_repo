import numpy as np
import pandas as pd
import streamlit as st

def prep_sofico(cleaned_file , distname , year , month):
    try:
        prepared_file = cleaned_file.rename(columns={
        "ItemID": "item_code",
        "ItemName": "item_name",
        "ZipCodeName": "territory_name",
        "ADDRESS": "address"
    })
        
        prepared_file["brick_code"] = prepared_file.apply(
            lambda row: 99009900 if row["ZipCode"] == 1101 and (
                "تجمع" in str(row["address"]) or "مدينت" in str(row["address"])
            )
            else row["OrderAccount"] if row["ZipCode"] == 1102
            else row["ZipCode"],
            axis=1
        ).astype(str)

        prepared_file["sales_units"] = prepared_file["SalesQty"] + prepared_file["ReturnQty"]
        prepared_file["bonus_units"] = prepared_file["BonusQty"] + prepared_file["ReturnBonus"]

        
            
        prepared_file = prepared_file[[
            "item_code", "item_name", "territory_name","brick_code", "address",
            "sales_units", "bonus_units", "dist_name","year","month"]]
        return prepared_file , distname , year , month

        
    except Exception as e:
        st.error(f"Error : {e}")