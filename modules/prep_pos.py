import numpy as np
import pandas as pd
import streamlit as st

def prep_pos(cleaned_file , distname , year , month):
    try:
        prepared_file = cleaned_file.rename(columns={
                "Product Code": "item_code",
                "Product Name": "item_name",
                "Territory Code": "territory_code",
                "Territory Name": "territory_name",
                "Sales": "sales_units",
                "Bonus": "bonus_units"
        })

        prepared_file["sales_units"] = prepared_file["sales_units"].astype(float)
        prepared_file["bonus_units"] = prepared_file["bonus_units"].astype(float)

        split_codes = ['280C6','406C6','407C6','M0009']
        mask = prepared_file["territory_code"].isin(split_codes)

        df_half = prepared_file.loc[mask].copy()
        df_half["sales_units"] = df_half["sales_units"] / 2
        df_half["bonus_units"] = df_half["bonus_units"] / 2
        df_new = df_half.copy()
        df_new["territory_code"] = "N9999999"
        df_new["territory_name"] = "القاهرة الجديدة"

        prepared_file = pd.concat([df_half, df_new, prepared_file.loc[~mask]], ignore_index=True)

        prepared_file = prepared_file[[
            "item_code", "item_name", "territory_code", "territory_name","sales_units", "bonus_units", "dist_name","year","month"]]
        
        return prepared_file , distname , year , month

        
    except Exception as e:
        st.error(f"Error : {e}")