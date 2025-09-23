import os
import pandas as pd
from github import Github

# -------- GitHub Setup --------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # stored in Streamlit secrets
GITHUB_REPO = "your-username/your-repo"   # change to your repo
SAVE_FOLDER = "cleaned_src"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)


def cln_ibs(sheet_path: str):
    try:
        # --- Extract Year & Month from filename ---
        try:
            date = (sheet_path.split(" ")[-1]).split(".")[0]
            year, month = date.split("-")
            year, month = int(year), int(month)
        except Exception:
            return "ibs_cln ERROR: Filename must contain date in 'YYYY-MM' format.", 0

        # --- Read Excel ---
        try:
            df = pd.read_excel(io=sheet_path, skiprows=1)
        except FileNotFoundError:
            return f"ibs_cln ERROR: File not found: {sheet_path}", 0
        except Exception as e:
            return f"ibs_cln ERROR: Error reading Excel file {sheet_path}: {e}", 0

        # --- Validate required columns ---
        required_cols = [
            'Date', 'Supp. Code', 'Supp. Name', 'Item Code', 'Item Name', 'Brick',
            'Governorate Name', 'Territory Name', 'Unnamed: 8',
            'Brick Name', 'QTY', 'FU', 'Total Qty'
        ]
        if list(df.columns) != required_cols:
            return f"ibs_cln ERROR: Columns mismatch.\nExpected: {required_cols}\nFound: {list(df.columns)}", 0

        # --- Drop invalid rows and columns ---
        df = df.dropna(subset=['Supp. Code', 'Supp. Name', 'Item Code', 'Item Name'], how="all")
        df = df.drop(columns=['Unnamed: 8'])

        # --- Add Year & Month ---
        df["Year"] = year
        df["Month"] = month

        if df.empty:
            return f"ibs_cln ERROR: No valid data after cleaning - Empty table.", 0

        # --- Save to GitHub ---
        file_name = os.path.basename(sheet_path).lower().replace(" ", "_")
        save_path = f"{SAVE_FOLDER}/{file_name}"

        # Convert dataframe to Excel bytes
        from io import BytesIO
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)

        # Push to GitHub (create or update)
        try:
            contents = repo.get_contents(save_path)
            repo.update_file(
                save_path, f"Update cleaned file {file_name}", buffer.read(), contents.sha
            )
        except Exception:
            repo.create_file(
                save_path, f"Add cleaned file {file_name}", buffer.read()
            )

        return f"SUCCESS: Cleaned file saved to GitHub at {save_path}", 1, df, month, year

    except Exception as e:
        return f"ibs_cln ERROR: Unexpected error in ibs_cln(): {e}", 0
