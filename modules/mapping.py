import pandas as pd
from info import dist_list
from download import download
import streamlit as st
from io import BytesIO

def check_missing(prep_df,dist_name,year,month):
    try:
        mapping_file = f"./mapping/map_{dist_name}.xlsx"

        products = pd.read_excel(mapping_file, sheet_name="products")
        bricks = pd.read_excel(mapping_file, sheet_name="bricks", dtype={"dist_brickcode":str})

        merged_products = prep_df.merge(
            products,
            left_on="item_code",
            right_on="dist_itemcode",
            how="left"
        )

        missed_products = merged_products[merged_products["dist_itemcode"].isna()][["item_code","item_name","dist_itemcode"]].drop_duplicates()

        if not missed_products.empty:
            st.write("### Enter missing mappings")
            product_edited_df = st.data_editor(missed_products, num_rows="fixed")
        else:
            st.success("No missing products")

        
        merged_bricks = prep_df.merge(
            bricks,
            left_on="brick_code",
            right_on="dist_brickcode",
            how="left"
        )

        missed_bricks = merged_bricks[merged_bricks["dist_brickcode"].isna()][dist_list[dist_name][2]+["dist_brickcode"]].drop_duplicates()

        if not missed_bricks.empty:
            brick_edited_df = st.data_editor(missed_bricks, num_rows="fixed")
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
        
        else:
            return 
    except Exception as e:
        st.error(f"{e}")   


def map_append(mapsheet,dist_name,year,month,user,date_time):
        
        uploadedmap = pd.read_excel(BytesIO(mapsheet.getbuffer()))
    
        mapping_file = f"./mapping/map_{dist_name}.xlsx"

        products = pd.read_excel(mapping_file, sheet_name="products")
        bricks = pd.read_excel(mapping_file, sheet_name="bricks", dtype={"dist_brickcode":str})


        if "item_code" in mapsheet.columns and "dist_itemcode" in mapsheet.columns:
            mapsheet

