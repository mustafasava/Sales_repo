import os
import base64
import requests
import pandas as pd
import streamlit as st


x = None  # holder for dataframe or message
y = None  # holder for type (1 = df, 0 = message)


def save_to_github(df: pd.DataFrame, filename: str):
    """
    Save cleaned DataFrame as Excel to GitHub repo (cleaned_src/).
    """
    token = st.secrets["GITHUB_TOKEN"]
    repo = st.secrets["GITHUB_REPO"]
    user = st.secrets["GITHUB_USER"]

    # GitHub API endpoint for file
    url = f"https://api.github.com/repos/{repo}/contents/cleaned_src/{filename}"

    # Save DataFrame locally (Streamlit Cloud tmp space)
    out_path = f"/tmp/{filename}"
    df.to_excel(out_path, index=False)

    # Read file and encode to base64
    with open(out_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    # Prepare payload
    payload = {
        "message": f"Add cleaned IBS file {filename}",
        "content": content,
        "branch": "main"  # adjust if repo uses another branch
    }

    headers = {"Authorization": f"token {token}"}
    r = requests.put(url, json=payload, headers=headers)

    if r.status_code in [200, 201]:
        return f"✅ File {filename} saved to GitHub."
    else:
        return f"❌ GitHub push failed: {r.json()}"


def ibs_cln(sheet_path: str):
    global x, y
    try:
        # --- Extract Year & Month from filename ---
        try:
            date = (sheet_path.split(" ")[-1]).split(".")[0]
            year, month = date.split("-")
            year, month = int(year), int(month)
        except Exception:
            x = f"ibs_cln ERROR: Filename must contain date in 'YYYY-MM' format: {sheet_path}"
            y = 0
            return x, y

        # --- Read Excel ---
        try:
            df = pd.read_excel(io=sheet_path, skiprows=1)
        except FileNotFoundError:
            x = f"ibs_cln ERROR: File not found: {sheet_path}"
            y = 0
            return x, y
        except Exception as e:
            x = f"ibs_cln ERROR: Error reading Excel file {sheet_path}: {e}"
            y = 0
            return x, y

        # --- Validate required columns ---
        required_cols = [
            "Date", "Supp. Code", "Supp. Name", "Item Code", "Item Name", "Brick",
            "Governorate Name", "Territory Name", "Unnamed: 8", "Brick Name",
            "QTY", "FU", "Total Qty"
        ]
        expected = required_cols
        actual = list(df.columns)

        if expected != actual:
            missing = [col for col in expected if col not in actual]
            extra = [col for col in actual if col not in expected]
            order_issue = (set(expected) == set(actual)) and (expected != actual)

            msg = "ERROR: Columns do not match exactly.\n"
            if missing:
                msg += f"Missing columns: {missing} /////"
            if extra:
                msg += f"Unexpected columns: {extra} /////"
            if order_issue:
                msg += f"Order mismatch. : Expected order: {expected} ////// Found order: {actual}"

            x = msg
            y = 0
            return x, y

        # --- Drop rows with null ---
        drop_conditions_cols = ["Supp. Code", "Supp. Name", "Item Code", "Item Name"]
        df = df.dropna(subset=drop_conditions_cols, how="all")
        df = df.drop(columns=["Unnamed: 8"])

        # --- Add Year & Month ---
        df["Year"] = year
        df["Month"] = month

        # --- Return dataframe if not empty ---
        if df.empty:
            x = f"ibs_cln ERROR: No valid data after cleaning-Empty table. {sheet_path}"
            y = 0
            return x, y
        else:
            # --- Save cleaned file to GitHub ---
            base_name = os.path.basename(sheet_path)
            out_name = base_name.lower().replace(".xlsx", "_cleaned.xlsx")
            msg = save_to_github(df, out_name)

            x = df
            y = 1
            return x, y, month, year, msg

    except Exception as e:
        x = f"ibs_cln ERROR: Unexpected error in ibs_cln(): {e}"
        y = 0
        return x, y
