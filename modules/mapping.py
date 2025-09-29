import pandas as pd
from info import dist_list
from download import download
import streamlit as st

def mapping(prep_df,dist_name,year,month):
    
    mapping_file = f"./mapping/map_{dist_name}.xlsx"

    products = pd.read_excel(mapping_file, sheet_name="products")
    bricks = pd.read_excel(mapping_file, sheet_name="bricks")

    
    merged_products = prep_df.merge(
        products,
        left_on="item_code",
        right_on="dist_itemcode",
        how="left"
    )
    
    missed_products = merged_products[merged_products["dist_itemcode"].isna()][["item_code","item_name","dist_itemcode"]]

    if not missed_products.empty:
        download(missed_products, filename=f"missed_products_{dist_name}_{year}_{month}.xlsx")
    else:
        st.success("No missing products")

    


    merged_bricks = prep_df.merge(
        bricks,
        left_on="brick_code",
        right_on="dist_brickcode",
        how="left"
    )
    
    missed_bricks = merged_bricks[merged_bricks["dist_brickcode"].isna()][dist_list[dist_name][2]]

    if not missed_bricks.empty:
        download(missed_bricks, filename=f"missed_bricks_{dist_name}_{year}_{month}.xlsx")
    else:
        st.success("No missing bricks")

    
    if missed_bricks.empty and missed_products.empty:
        final_merged = prep_df.merge(
            products,
            left_on="item_code",
            right_on="dist_itemcode",
            how="left"
        ).merge(
            bricks,
            left_on="brick_code",
            right_on="dist_brickcode",
            how="left"
        )
        
        return final_merged , dist_name, year ,month
        