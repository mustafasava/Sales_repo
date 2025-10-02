import pandas as pd
from info import dist_list,products_list
# from download import download
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

        missed_products = merged_products[merged_products["dist_itemcode"].isna()][["item_code","item_name","item"]].drop_duplicates()

        if not missed_products.empty:
            disabled_colsp = [col for col in missed_products.columns if col != "item"]
            st.write("### Enter missing Products mappings")
            st.data_editor(missed_products,column_config={"item": st.column_config.SelectboxColumn("item",options=products_list,
            required=True)}, disabled=disabled_colsp ,hide_index=True)
        else:
            st.success("No missing products")

        
        merged_bricks = prep_df.merge(
            bricks,
            left_on="brick_code",
            right_on="dist_brickcode",
            how="left"
        )

        missed_bricks = merged_bricks[merged_bricks["dist_brickcode"].isna()][dist_list[dist_name][2]+["brick"]].drop_duplicates()

        if not missed_bricks.empty:

            disabled_colsb = [col for col in missed_bricks.columns if col != "brick"]
            st.write("### Enter missing Bricks mappings")
            st.data_editor(missed_bricks,column_config={"brick": st.column_config.SelectboxColumn("brick",options=products_list,
            required=True)},disabled=disabled_colsb,hide_index=True)
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



# def map_append(mapsheet,dist_name,year,month,user,date_time):
        
#         uploadedmap = pd.read_excel(BytesIO(mapsheet.getbuffer()))
    
#         mapping_file = f"./mapping/map_{dist_name}.xlsx"

#         products = pd.read_excel(mapping_file, sheet_name="products")
#         bricks = pd.read_excel(mapping_file, sheet_name="bricks", dtype={"dist_brickcode":str})


#         if "item_code" in mapsheet.columns and "dist_itemcode" in mapsheet.columns:
#             mapsheet

