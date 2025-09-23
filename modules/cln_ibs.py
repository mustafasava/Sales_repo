import pandas as pd
import os

def ibs_cln(sheet_path: str):
    """
    Cleans an IBS Excel sheet.
    Returns:
        (df, 1, month, year) if successful
        (error_message, 0) if failed
    """
    try:
        # --- Extract Year & Month from filename ---
        try:
            date = (sheet_path.split(" ")[-1]).split(".")[0]
            year, month = date.split("-")
            year, month = int(year), int(month)
        except Exception:
            return f"ibs_cln ERROR: Filename must contain date in 'YYYY-MM' format: {sheet_path}", 0

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
            'Governorate Name', 'Territory Name', 'Unnamed: 8', 'Brick Name', 'QTY', 'FU', 'Total Qty'
        ]
        expected = required_cols
        actual = list(df.columns)

        if expected != actual:
            missing = [col for col in expected if col not in actual]
            extra = [col for col in actual if col not in expected]
            order_issue = (set(expected) == set(actual)) and (expected != actual)

            msg = "ibs_cln ERROR: Columns do not match exactly.\n"
            if missing:
                msg += f"Missing: {missing} /////"
            if extra:
                msg += f"Unexpected: {extra} /////"
            if order_issue:
                msg += f"Order mismatch. Expected order: {expected} ////// Found order: {actual}"
            return msg, 0

        # --- Drop rows with nulls ---
        drop_conditions_cols = ['Supp. Code', 'Supp. Name', 'Item Code', 'Item Name']
        df = df.dropna(subset=drop_conditions_cols, how="all")
        df = df.drop(columns=['Unnamed: 8'])

        # --- Add Year & Month ---
        df["Year"] = year
        df["Month"] = month

        # --- Return dataframe ---
        if df.empty:
            return f"ibs_cln ERROR: No valid data after cleaning (empty table) - {sheet_path}", 0
        else:
            return df, 1, month, year

    except Exception as e:
        return f"ibs_cln ERROR: Unexpected error in ibs_cln(): {e}", 0
