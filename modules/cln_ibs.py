# modules/cln_ibs.py

import pandas as pd
from io import BytesIO

def cln_ibs(file_binary):
    """
    Cleans IBS Excel file from Streamlit uploader.

    Parameters
    ----------
    file_binary : UploadedFile (binary content)

    Returns
    -------
    tuple
        (message:str, status:int, df:DataFrame, month:int|None, year:int|None)
    """
    try:
        # --- Load Excel ---
        df = pd.read_excel(BytesIO(file_binary), skiprows=1)

        # --- Validate required columns ---
        required_cols = [
            'Date', 'Supp. Code', 'Supp. Name', 'Item Code', 'Item Name', 'Brick',
            'Governorate Name', 'Territory Name', 'Unnamed: 8',
            'Brick Name', 'QTY', 'FU', 'Total Qty'
        ]
        if list(df.columns) != required_cols:
            return (
                f"❌ IBS ERROR: Columns mismatch.\nExpected: {required_cols}\nFound: {list(df.columns)}",
                0, None, None, None
            )

        # --- Cleaning steps ---
        df = df.dropna(subset=['Supp. Code', 'Supp. Name', 'Item Code', 'Item Name'], how="all")
        df = df.drop(columns=['Unnamed: 8'])
        df.reset_index(drop=True, inplace=True)

        if df.empty:
            return "❌ IBS ERROR: No valid data after cleaning (empty table).", 0, None, None, None

        # --- Optional: Add placeholders for month/year ---
        month, year = None, None  # extracted from filename in app.py

        return "✅ IBS file cleaned successfully.", 1, df, month, year

    except Exception as e:
        return f"❌ IBS ERROR: Unexpected error: {str(e)}", 0, None, None, None
