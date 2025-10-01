import numpy as np
import pandas as pd
import streamlit as st

def prep_ibs(cleaned_file , distname , year , month):
    try:
        prepared_file = cleaned_file.rename(columns={
            "Item Code": "item_code",
            "Item Name": "item_name",
            "Governorate Name": "governorate_name",
            "Territory Name": "territory_name",
            "Brick Name": "brick_name",
            "QTY": "sales_units",
            "FU": "bonus_units"
        })

        prepared_file["brick_code"] = np.where(prepared_file["territory_name"] == "Template District                       ",prepared_file["brick_name"],
                                        np.where(prepared_file["territory_name"] == "QENA I /RED SEA RED SEA                 ", prepared_file["governorate_name"],
                                        np.where((prepared_file["territory_name"] == "NASR CITY NASR CITY                     ") 
                                                &(
                                                    (prepared_file["governorate_name"] == "القاهره الجديده     ") |
                                                    (prepared_file["governorate_name"].str.contains("عاصم", na=False))
                                                    ),"القاهره الجديده     ",prepared_file["territory_name"]))).astype(str)
        
        prepared_file = prepared_file[[
            "item_code", "item_name", "brick_name", "governorate_name",
            "brick_code", "sales_units", "bonus_units", "dist_name","year","month"]]
        return prepared_file , distname , year , month

        
    except Exception as e:
        st.error(f"Error : {e}")