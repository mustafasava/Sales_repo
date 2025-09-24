import pandas as pd
from io import BytesIO

def cln_ibs(uploaded_file , distname , year , month):
    """
    Cleans IBS Excel file from Streamlit uploader.

    Parameters
    ----------
    uploaded_file : UploadedFile
        Streamlit uploaded file.

    Returns
    -------
    tuple
        (message:str, status:int, df:DataFrame, month:int|None, year:int|None)
    """
    try:
        # --- Load Excel from uploaded file ---
        df = pd.read_excel(BytesIO(uploaded_file.getbuffer()), skiprows=1)

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
        df['Dist_Name'] = distname
        df.reset_index(drop=True, inplace=True)

        if df.empty:
            return "❌ IBS ERROR: No valid data after cleaning (empty table).", 0, None, None, None

        # --- Placeholders for month/year (from filename in app.py) ---
        month, year = None, None

        return "✅ IBS file cleaned successfully.", 1, df, month, year

    except Exception as e:
        return f"❌ IBS ERROR: Unexpected error: {str(e)}", 0, None, None, None
