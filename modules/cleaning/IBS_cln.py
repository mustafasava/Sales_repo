import pandas as pd




x = None #--- A global variable holder for messages or returned DataFrame --
y = None #--- A global variable holder for identifying the returned x is a df or text --

def ibs_cln(sheet_path: str):
    global x
    global y
    try:

# --- Extract Year & Month ---
        try:
            date = (sheet_path.split(" ")[-1]).split(".")[0]
            year, month = date.split("-")
            year, month = int(year), int(month)
        except Exception  :
            x = f"ibs_cln ERROR: Filename must contain date in 'YYYY-MM' format: {sheet_path}"
            y = 0
            return x ,y
# --- Read Excel ---
        try:
            df = pd.read_excel(io=sheet_path, skiprows=1)
        except FileNotFoundError:
            x = f"ibs_cln ERROR: File not found: {sheet_path}"
            y = 0
            return x ,y
        except Exception as e:
            x = f"ibs_cln ERROR: Error reading Excel file {sheet_path}: {e}"
            y = 0
            return x ,y
        
# --- Validate required columns ---
        required_cols = ['Date', 'Supp. Code', 'Supp. Name', 'Item Code', 'Item Name', 'Brick',
       'Governorate Name', 'Territory Name', 'Unnamed: 8','Brick Name', 'QTY', 'FU','Total Qty']
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
            return x ,y
            
# --- Drop rows with null ---
        drop_conditions_cols = ['Supp. Code', 'Supp. Name', 'Item Code', 'Item Name']
        df = df.dropna(subset = drop_conditions_cols, how="all")
        df = df.drop(columns=['Unnamed: 8'])
# --- Add Year & Month ---
        df["Year"] = year
        df["Month"] = month

# --- returning dataframe if it is not empty ---
        if df.empty:
            x = f"ibs_cln ERROR: No valid data after cleaning-Empty table.  {sheet_path}"

            y = 0
            return x ,y
        else:
            
            x = df
            y = 1
            return x ,y,month,year
                

    except Exception as e:
        x = f"ibs_cln ERROR: Unexpected error in ibs_cln(): {e}"
        
        y = 0
        return x ,y
    

