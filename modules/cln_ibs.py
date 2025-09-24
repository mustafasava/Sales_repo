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
    
    Parameters
    ----------
    data : str | BytesIO | pd.DataFrame
        - str : local path to Excel file
        - BytesIO : uploaded file object (e.g., from Streamlit)
        - pd.DataFrame : already-loaded DataFrame

    Returns
    -------
    tuple(message:str, status:int, df:pd.DataFrame, month:int|None, year:int|None)
    """
    try:
        # -------- Handle input & extract date --------
        df, file_name, year, month = _load_input(data)

        # -------- Validate required columns --------
        required_cols = [
            'Date', 'Supp. Code', 'Supp. Name', 'Item Code', 'Item Name', 'Brick',
            'Governorate Name', 'Territory Name', 'Unnamed: 8',
            'Brick Name', 'QTY', 'FU', 'Total Qty'
        ]
        if list(df.columns) != required_cols:
            return (
                f"❌ IBS ERROR: Columns mismatch.\n"
                f"Expected: {required_cols}\n"
                f"Found: {list(df.columns)}",
                0, None, None, None
            )

        # -------- Clean --------
        df = df.dropna(
            subset=['Supp. Code', 'Supp. Name', 'Item Code', 'Item Name'],
            how="all"
        ).drop(columns=['Unnamed: 8'])

        if year and month:
            df["Year"] = year
            df["Month"] = month

        if df.empty:
            return "❌ IBS ERROR: No valid data after cleaning (empty table).", 0, None, None, None

        # -------- Save cleaned file to GitHub --------
        save_path = _save_to_github(df, file_name)

        return f"✅ SUCCESS: Cleaned file saved to GitHub at {save_path}", 1, df, month, year

    except Exception as e:
        return f"❌ IBS ERROR: Unexpected error: {e}", 0, None, None, None


# ================= Helpers =================
def _load_input(data):
    """Read Excel from path, BytesIO, or DataFrame and extract date."""
    if isinstance(data, str):  # File path
        file_name = os.path.basename(data).lower().replace(" ", "_")
        df = pd.read_excel(data, skiprows=1)

    elif isinstance(data, BytesIO):  # Uploaded file
        file_name = getattr(data, "name", "uploaded.xlsx").lower().replace(" ", "_")
        df = pd.read_excel(data, skiprows=1)

    elif isinstance(data, pd.DataFrame):
        file_name = "dataframe_input.xlsx"
        df = data.copy()
        return df, file_name, None, None

    else:
        raise TypeError("Unsupported input type for cln_ibs")

    # Extract year & month from file name
    try:
        date = (file_name.split(" ")[-1]).split(".")[0]
        year, month = map(int, date.split("-"))
    except Exception:
        raise ValueError("Filename must contain date in 'YYYY-MM' format.")

    return df, file_name, year, month


def _save_to_github(df, file_name):
    """Save DataFrame as Excel to GitHub."""
    save_path = f"{SAVE_FOLDER}/{file_name}"

    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    content = buffer.getvalue()  # ✅ safer than reusing .read()

    try:
        contents = repo.get_contents(save_path)
        repo.update_file(save_path, f"Update cleaned file {file_name}", content, contents.sha)
    except Exception:
        repo.create_file(save_path, f"Add cleaned file {file_name}", content)

    return save_path
