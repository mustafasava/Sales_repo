import os
import pandas as pd
from github import Github
from io import BytesIO

# -------- GitHub Setup --------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # stored in Streamlit secrets
GITHUB_REPO = "mustafasava/Sales_repo"   # change to your repo
SAVE_FOLDER = "cleaned_src"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)


def cln_ibs(data):
    """
    Clean IBS data.
    Accepts either:
      - str : path to Excel file
      - BytesIO : uploaded file object from Streamlit
      - pd.DataFrame : already-loaded dataframe
    Returns: (message, status, df, month, year)
    """

    try:
        # --- Determine input type ---
        if isinstance(data, str):  # File path
            sheet_path = data
            # Extract date from filename
            try:
                date = (sheet_path.split(" ")[-1]).split(".")[0]
                year, month = map(int, date.split("-"))
            except Exception:
                return "ibs_cln ERROR: Filename must contain date in 'YYYY-MM' format.", 0, None, None, None

            df = pd.read_excel(sheet_path, skiprows=1)

            file_name = os.path.basename(sheet_path).lower().replace(" ", "_")

        elif isinstance(data, BytesIO):  # Uploaded file
            # Get name if available (Streamlit provides .name attr)
            file_name = getattr(data, "name", "uploaded.xlsx").lower().replace(" ", "_")
            try:
                date = (file_name.split(" ")[-1]).split(".")[0]
                year, month = map(int, date.split("-"))
            except Exception:
                return "ibs_cln ERROR: Filename must contain date in 'YYYY-MM' format.", 0, None, None, None

            df = pd.read_excel(data, skiprows=1)

        elif isinstance(data, pd.DataFrame):  # Already a DataFrame
            df = data.copy()
            # If DataFrame, you’ll need to pass month/year separately or skip this check
            year, month = None, None
            file_name = "dataframe_input.xlsx"
        else:
            return "ibs_cln ERROR: Unsupported input type", 0, None, None, None

        # --- Validate required columns ---
        required_cols = [
            'Date', 'Supp. Code', 'Supp. Name', 'Item Code', 'Item Name', 'Brick',
            'Governorate Name', 'Territory Name', 'Unnamed: 8',
            'Brick Name', 'QTY', 'FU', 'Total Qty'
        ]
        if list(df.columns) != required_cols:
            return f"ibs_cln ERROR: Columns mismatch.\nExpected: {required_cols}\nFound: {list(df.columns)}", 0, None, None, None

        # --- Drop invalid rows and columns ---
        df = df.dropna(subset=['Supp. Code', 'Supp. Name', 'Item Code', 'Item Name'], how="all")
        df = df.drop(columns=['Unnamed: 8'])

        # --- Add Year & Month if available ---
        if year and month:
            df["Year"] = year
            df["Month"] = month

        if df.empty:
            return f"ibs_cln ERROR: No valid data after cleaning - Empty table.", 0, None, None, None

        # --- Save to GitHub ---
        save_path = f"{SAVE_FOLDER}/{file_name}"
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)

        try:
            contents = repo.get_contents(save_path)
            repo.update_file(
                save_path, f"Update cleaned file {file_name}", buffer.read(), contents.sha
            )
        except Exception:
            buffer.seek(0)  # reset pointer before re-reading
            repo.create_file(
                save_path, f"Add cleaned file {file_name}", buffer.read()
            )

        return f"SUCCESS: Cleaned file saved to GitHub at {save_path}", 1, df, month, year

    except Exception as e:
        return f"ibs_cln ERROR: Unexpected error in ibs_cln(): {e}", 0, None, None, None
