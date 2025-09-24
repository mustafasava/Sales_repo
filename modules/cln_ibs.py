import pandas as pd
import io

def cln_ibs(file) -> tuple[str, int]:
    """
    Cleans IBS file.
    Input: binary file object (from Streamlit uploader)
    Returns: (message, status) where status = 1 success, 0 failure
    """
    try:
        # Read file into DataFrame
        df = pd.read_excel(io.BytesIO(file.getbuffer()))

        # --- Example cleaning (replace with your real steps) ---
        if df.empty:
            return ("IBS file is empty.", 0)

        # Drop duplicates
        df.drop_duplicates(inplace=True)

        # Save cleaned file to repo (you can adjust path)
        save_path = "cleaned_data/ibs_cleaned.xlsx"
        df.to_excel(save_path, index=False)

        return (f"IBS file cleaned successfully and saved to {save_path}", 1)

    except Exception as e:
        return (f"Error during cleaning: {e}", 0)
