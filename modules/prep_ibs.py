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

        prepared_file["territory_name"] = np.where(prepared_file["territory_name"] == "Template District                       ",prepared_file["brick_name"],
                                        np.where(prepared_file["territory_name"] == "QENA I /RED SEA RED SEA                 ", prepared_file["governorate_name"],
                                        np.where((prepared_file["territory_name"] == "NASR CITY NASR CITY                     ") 
                                                &(
                                                    (prepared_file["governorate_name"] == "القاهره الجديده     ") |
                                                    (prepared_file["governorate_name"].str.contains("عاصم", na=False))
                                                    ),"القاهره الجديده     ",prepared_file["territory_name"])))
        
        prepared_file = prepared_file[[
            "item_code", "item_name", "brick_name", "governorate_name",
            "territory_name", "sales_units", "bonus_units", "dist_name","year","month"]]
        st.success(f"✅ IBS file prepared successfuly !")
        return prepared_file , distname , year , month

        
    except Exception as e:
        st.error(f"Error : {e}")