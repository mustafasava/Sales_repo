import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO
from datetime import datetime
import os
from github import Github
from info import dist_list

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "mustafasava/Sales_repo"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)


def _ensure_df(obj, name="object"):
    """
    Convert whatever Streamlit data_editor returns into a proper pandas DataFrame.
    Handles dicts-of-lists, list-of-dicts, or nested dicts.
    """
    import pandas as pd

    if isinstance(obj, pd.DataFrame):
        return obj

    # Sometimes it's a list of dicts
    if isinstance(obj, list):
        if all(isinstance(x, dict) for x in obj):
            return pd.DataFrame(obj)
        else:
            return pd.DataFrame(obj)

    # Sometimes it's a dict of columns -> lists
    if isinstance(obj, dict):
        try:
            # If dict values are also dicts, flatten them
            if all(isinstance(v, dict) for v in obj.values()):
                # Flatten nested dicts to DataFrame
                rows = []
                for k, v in obj.items():
                    if isinstance(v, dict):
                        v["__index__"] = k
                        rows.append(v)
                return pd.DataFrame(rows)
            # If it's a dict of lists
            elif all(isinstance(v, (list, tuple)) for v in obj.values()):
                return pd.DataFrame({k: list(v) for k, v in obj.items()})
            else:
                # Try one more generic attempt
                return pd.json_normalize(obj)
        except Exception as e:
            raise TypeError(f"Cannot convert dict '{name}' to DataFrame: {e}")

    raise TypeError(f"Unsupported type for '{name}': {type(obj)}")



def check_missing(prep_df, dist_name, year, month):
    try:
        mapping_products_file = f"./mapping/map_{dist_name}_products.xlsx"
        mapping_bricks_file = f"./mapping/map_{dist_name}_bricks.xlsx"

        products = pd.read_excel(mapping_products_file, sheet_name="products")
        bricks = pd.read_excel(mapping_bricks_file, sheet_name="bricks", dtype={"dist_brickcode": str})

        # --- PRODUCTS ---
        merged_products = prep_df.merge(
            products,
            left_on="item_code",
            right_on="dist_itemcode",
            how="left"
        )

        missed_products = merged_products[
            merged_products["dist_itemcode"].isna()
        ][["item_code", "item_name", "item"]].drop_duplicates()

        if not missed_products.empty:
            products_list = pd.read_excel("./mapping/main_lists.xlsx", sheet_name="products")[["product", "barcode"]]
            name_to_code = dict(zip(products_list["product"], products_list["barcode"]))
            disabled_colsp = [col for col in missed_products.columns if col != "item"]

            st.write("### 🧩 Enter missing Products mappings")

            # use a stable key
            prod_key = "missing_products_editor"

            # Render editor
            st.data_editor(
                missed_products,
                key=prod_key,
                column_config={
                    "item": st.column_config.SelectboxColumn(
                        "item",
                        options=list(name_to_code.keys()),
                        required=True
                    )
                },
                disabled=disabled_colsp,
                hide_index=True
            )

            if st.button("Save Products"):
                # get editor content safely
                editor_val = st.session_state.get(prod_key, None)
                if editor_val is None:
                    # fallback: use the original missed_products (no edits were committed)
                    st.warning("No edits detected in the Products editor — using original values.")
                    missing_products = missed_products.copy()
                else:
                    try:
                        missing_products = _ensure_df(editor_val, name=prod_key)
                    except TypeError as e:
                        st.error(f"Could not read edited products: {e}")
                        return

                # Validate columns exist
                expected_cols = {"item_code", "item"}
                if not expected_cols.issubset(set(missing_products.columns)):
                    st.error(f"Edited products is missing required columns. Found: {list(missing_products.columns)}")
                    return

                # proceed with cleaning and saving
                missing_products = missing_products.drop_duplicates(subset=["item_code"])
                missing_products = missing_products.dropna(subset=["item"], how="all")
                missing_products = missing_products.rename(columns={"item_code": "dist_itemcode"})

                # Optional mapping: uncomment if you want barcode in item column
                # missing_products["item"] = missing_products["item"].map(name_to_code)

                missing_products["added_by"] = st.session_state.get("username", "unknown")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                missing_products["date_time"] = timestamp

                missing_products = missing_products[["dist_itemcode", "item", "added_by", "date_time"]]

                new_mapped_products = pd.concat([products, missing_products], ignore_index=True).drop_duplicates(subset=["dist_itemcode"])

                buffer = BytesIO()
                new_mapped_products.to_excel(buffer, index=False, sheet_name="products")
                buffer.seek(0)
                data = buffer.getvalue()

                try:
                    contents = repo.get_contents(mapping_products_file)
                    repo.update_file(
                        mapping_products_file,
                        f"Update map_{dist_name}_products.xlsx",
                        data,
                        contents.sha
                    )
                    st.success("✅ Products mapping saved successfully!")
                except Exception as e:
                    st.error(f"❌ Error while updating product file: {e}")

        else:
            st.success("✅ No missing products found.")

        # --- BRICKS ---
        merged_bricks = prep_df.merge(
            bricks,
            left_on="brick_code",
            right_on="dist_brickcode",
            how="left"
        )

        missed_bricks = merged_bricks[
            merged_bricks["dist_brickcode"].isna()
        ][dist_list[dist_name][2] + ["brick"]].drop_duplicates()

        if not missed_bricks.empty:
            bricks_list = pd.read_excel("./mapping/main_lists.xlsx", sheet_name="bricks")
            disabled_colsb = [col for col in missed_bricks.columns if col != "brick"]

            st.write("### 🧱 Enter missing Bricks mappings")

            brick_key = "missing_bricks_editor"

            st.data_editor(
                missed_bricks,
                key=brick_key,
                column_config={
                    "brick": st.column_config.SelectboxColumn(
                        "brick",
                        options=[""] + bricks_list["bricks"].tolist(),
                        required=True
                    )
                },
                disabled=disabled_colsb,
                hide_index=True
            )

            if st.button("Save Bricks"):
                editor_val = st.session_state.get(brick_key, None)
                if editor_val is None:
                    st.warning("No edits detected in the Bricks editor — using original values.")
                    missing_bricks = missed_bricks.copy()
                else:
                    try:
                        missing_bricks = _ensure_df(editor_val, name=brick_key)
                    except TypeError as e:
                        st.error(f"Could not read edited bricks: {e}")
                        return

                expected_brick_cols = {"brick_code", "brick"}
                if not expected_brick_cols.issubset(set(missing_bricks.columns)):
                    st.error(f"Edited bricks is missing required columns. Found: {list(missing_bricks.columns)}")
                    return

                missing_bricks = missing_bricks.drop_duplicates(subset=["brick_code"])
                missing_bricks = missing_bricks.dropna(subset=["brick"], how="all")
                missing_bricks = missing_bricks.rename(columns={"brick_code": "dist_brickcode"})
                missing_bricks["added_by"] = st.session_state.get("username", "unknown")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                missing_bricks["date_time"] = timestamp

                missing_bricks = missing_bricks[["dist_brickcode", "brick", "added_by", "date_time"]]

                new_mapped_bricks = pd.concat([bricks, missing_bricks], ignore_index=True).drop_duplicates(subset=["dist_brickcode"])

                buffer = BytesIO()
                new_mapped_bricks.to_excel(buffer, index=False, sheet_name="bricks")
                buffer.seek(0)
                data = buffer.getvalue()

                try:
                    contents = repo.get_contents(mapping_bricks_file)
                    repo.update_file(
                        mapping_bricks_file,
                        f"Update map_{dist_name}_bricks.xlsx",
                        data,
                        contents.sha
                    )
                    st.success("✅ Bricks mapping saved successfully!")
                except Exception as e:
                    st.error(f"❌ Error while updating bricks file: {e}")
        else:
            st.success("✅ No missing bricks found.")

        # --- final merged return if no misses ---
        if missed_bricks.empty and missed_products.empty:
            final_merged = (
                prep_df.merge(products, left_on="item_code", right_on="dist_itemcode", how="left")
                .merge(bricks, left_on="brick_code", right_on="dist_brickcode", how="left")
            )
            return final_merged, dist_name, year, month
        else:
            return None

    except Exception as e:
        st.error(f"⚠️ Unexpected error: {e}")
