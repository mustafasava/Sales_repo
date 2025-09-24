import pandas as pd




x = None #--- A global variable holder for messages or returned DataFrame --
y = None #--- A global variable holder for identifying the returned x is a df or text --

def cln_pos(uploaded_file , distname , year , month):
    global x
    global y
    try:

# --- Extract Year & Month ---
        try:
            date = (uploaded_file.split(" ")[-1]).split(".")[0]
            year, month = date.split("-")
            year, month = int(year), int(month)
        except Exception  :
            x = f"pos_cln ERROR: Filename must contain date in 'YYYY-MM' format: {uploaded_file}"
            y = 0
            return x ,y
# --- Read old excel format ---
        try:
            df = pd.read_excel(io=uploaded_file, engine="xlrd")
        except FileNotFoundError:
            x = f"pos_cln ERROR: File not found: {uploaded_file}"
            y = 0
            return x ,y
        except Exception as e:
            x = f"pos_cln ERROR: Error reading Excel file {uploaded_file}: {e}"
            y = 0
            return x ,y
        
# --- Validate required columns ---
        required_cols = ['English Name', 'Product Code', 'Product Name', 'Territory Code',  
       'Territory Name', 'Sales Value', 'Credit Value', 'Net Sales Value','Sales', 'Bonus']
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
            
# --- Drop reapeted headers rows& fill down first column ---

        df = df[df["English Name"] != "English Name"]
        drop_conditions_cols = ['Product Code', 'Product Name', 'Territory Code']
        df = df.dropna(subset = drop_conditions_cols, how="all")
        df["English Name"] = df["English Name"].ffill()
       
# --- Add Year & Month ---
        df["Year"]  =  year
        df["Month"] =  month


# --- returning dataframe if it is not empty ---
        if df.empty:
            x = f"pos_cln ERROR: No valid data after cleaning-Empty table.  {uploaded_file}"

            y = 0
            return x ,y
        else:
            
            x = df
            y = 1
            return x ,y,month,year

    except Exception as e:
        x = f"pos_cln ERROR: Unexpected error in pos_cln(): {e}"
        y = 0
        return x ,y
    





