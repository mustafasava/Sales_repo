import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import datetime
from github import Github

# --- GitHub setup ---
GITHUB_TOKEN = st.secrets["github_token"]
REPO_NAME = "your_repo_name"
MAPPING_PRODUCTS_FILE = "mapping/main_lists.xlsx"
DIST_NAME = "your_dist_name"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# --- Load data ---
try:
    products_list = pd.read_excel("./mapping/main_lists.xlsx", sheet_name="products")[["product", "barcode"]]
except Exception as e:
    st.error(f"Error reading main list: {e}")
    st.stop()

# Create readable selectbox options
name_to_code = dict(zip(products_list["product"], products_list["barcode"]))

# Simulate missed products (replace with your actual df)
missed_products = pd.read_excel("./mapping/missed_products.xlsx")[["item_code", "item_name"]]
missed_products.rename(columns={"item_name": "item"}, inplace=True)

if not missed_products.empty:
    disabled_cols = [col for col in missed_products.columns if col != "item"]

    st.write("### Enter missing Product mappings")

    # Editable table for user to select correct product name
    edited = st.data_editor(
        missed_products,
        column_config={
            "item": st.column_config.SelectboxColumn(
                "item", options=list(name_to_code.keys()), required=True
            )
        },
        disabled=disabled_cols,
        hide_index=True,
        key="products_editor"
    )

    # --- Handle Save ---
    if st.button("💾 Save Products"):
        try:
            df = pd.DataFrame(edited)
            df = df.drop_duplicates(subset=["item_code"])
            df = df.dropna(subset=["item"], how="all")

            # Convert selected name → barcode
            df["barcode"] = df["item"].map(name_to_code)

            df = df.rename(columns={"item_code": "dist_itemcode", "barcode": "item"})
            df["added_by"] = st.session_state.get("username", "guest")
            df["date_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            df = df[["dist_itemcode", "item", "added_by", "date_time"]]

            # --- Append to repo data ---
            existing_products = pd.read_excel("./mapping/main_lists.xlsx", sheet_name="products")
            new_mapped_products = pd.concat([existing_products, df], ignore_index=True).drop_duplicates(
                subset=["dist_itemcode"]
            )

            # Save to buffer
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                new_mapped_products.to_excel(writer, index=False, sheet_name="products")
            buffer.seek(0)

            # Upload to GitHub
            contents = repo.get_contents(MAPPING_PRODUCTS_FILE)
            repo.update_file(
                MAPPING_PRODUCTS_FILE,
                f"Update map_{DIST_NAME}_products.xlsx",
                buffer.read(),
                contents.sha,
            )

            st.success("✅ Product mappings saved successfully!")

        except Exception as e:
            st.error(f"⚠️ Unexpected error: {e}")
