import pandas as pd
from info import dist_list
import streamlit as st
from io import BytesIO
import numpy as np
from datetime import datetime
import os
from github import Github


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "mustafasava/Sales_repo"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)


def check_missing(prep_df,dist_name,year,month):
    try:
        mapping_products_file = f"./mapping/map_{dist_name}_products.xlsx"
        mapping_bricks_file = f"./mapping/map_{dist_name}_bricks.xlsx"

        products = pd.read_excel(mapping_products_file, sheet_name="products")
        bricks = pd.read_excel(mapping_bricks_file, sheet_name="bricks", dtype={"dist_brickcode":str})

        merged_products = prep_df.merge(
            products,
            left_on="item_code",
            right_on="dist_itemcode",
            how="left"
        )

        missed_products = merged_products[merged_products["dist_itemcode"].isna()][["item_code","item_name","item"]].drop_duplicates()

        if not missed_products.empty:

            products_list = pd.read_excel("./mapping/main_lists.xlsx",sheet_name="products")[["product","barcode"]]
            name_to_code = dict(zip(products_list["product"], products_list["barcode"]))
            disabled_colsp = [col for col in missed_products.columns if col != "item"]

            st.write("### Enter missing Products mappings")
            missing_products = st.data_editor(missed_products,column_config={"item": st.column_config.SelectboxColumn("item",options=list(name_to_code.keys()),
            required=True)}, disabled=disabled_colsp ,hide_index=True)

            if st.button("Save Products"):
                missing_products = missing_products.drop_duplicates(subset=["item_code"])
                missing_products = missing_products.dropna(subset=["item"],how = "all")
                missing_products = missing_products.rename(columns={"item_code":"dist_itemcode"})
                missing_products["item"] = missing_products["item"].map(name_to_code)
                missing_products["added_by"] = st.session_state.get("username")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                missing_products["date_time"] =  timestamp

                missing_products = missing_products[["dist_itemcode","item","added_by","date_time"]]
                new_mapped_products = pd.concat([products, missing_products], ignore_index=True).drop_duplicates(subset=["dist_itemcode"])
                buffer = BytesIO()
                new_mapped_products.to_excel(buffer, index=False, sheet_name="products")
                buffer.seek(0)
                try:
                    contents = repo.get_contents(mapping_products_file)
                    repo.update_file(
                        mapping_products_file,
                        f"Update map_{dist_name}_products.xlsx",
                        buffer.read(),
                        contents.sha
                    )
                    st.info(f"saved")
                
                except Exception as e:
                    st.error(f"Error happened while updating. Not saved. details: {e}")           
            
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

            bricks_list = pd.read_excel("./mapping/main_lists.xlsx",sheet_name="bricks")
            

            disabled_colsb = [col for col in missed_bricks.columns if col != "brick"]
            st.write("### Enter missing Bricks mappings")

            missing_bricks = st.data_editor(missed_bricks,column_config={"brick": st.column_config.SelectboxColumn("brick",options=[""]+bricks_list["bricks"].tolist(),
                                required=True)},disabled=disabled_colsb,hide_index=True)


            if st.button("Save Bricks"):
                missing_bricks = missing_bricks.drop_duplicates(subset=["brick_code"])
                missing_bricks = missing_bricks.dropna(subset=["brick"],how = "all")
                missing_bricks = missing_bricks.rename(columns={"brick_code":"dist_brickcode"})
                missing_bricks["added_by"] = st.session_state.get("username")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                missing_bricks["date_time"] =  timestamp

                missing_bricks = missing_bricks[["dist_brickcode","brick","added_by","date_time"]]
                new_mapped_bricks = pd.concat([bricks, missing_bricks], ignore_index=True).drop_duplicates(subset=["dist_brickcode"])
                buffer = BytesIO()
                new_mapped_bricks.to_excel(buffer, index=False, sheet_name="bricks")
                buffer.seek(0)
                try:
                    contents = repo.get_contents(mapping_bricks_file)
                    repo.update_file(
                        mapping_bricks_file,
                        f"Update map_{dist_name}_bricks.xlsx",
                        buffer.read(),
                        contents.sha
                    )
                    st.info(f"saved")
                
                except Exception as e:
                    st.error(f"Error happened while updating. Not saved. details: {e}")
            
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



