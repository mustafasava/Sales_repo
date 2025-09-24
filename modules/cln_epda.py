import pandas as pd
import numpy as np



x = None #--- A global variable holder for messages or returned DataFrame --
y = None #--- A global variable holder for identifying the returned x is a df or text --

def cln_epda(uploaded_file , distname , year , month):
    global x
    global y
    try:
        
# --- Extract Year & Month ---
        try:
            date = (uploaded_file.split(" ")[-1]).split(".")[0]
            year, month = date.split("-")
            year, month = int(year), int(month)
        except Exception  :
            x = f"epda_cln ERROR: Filename must contain date in 'YYYY-MM' format: {uploaded_file}"
            y = 0
            return x ,y
# --- Read Excel ---
        try:
            df = pd.read_excel(io=uploaded_file, skiprows=10 , engine="xlrd")
        except FileNotFoundError:
            x = f"epda_cln ERROR: File not found: {uploaded_file}"
            y = 0
            return x ,y
        except Exception as e:
            x = f"epda_cln ERROR: Error reading Excel file {uploaded_file}: {e}"
           
            y = 0
            return x ,y
        
# --- Validate required columns ---
        required_cols = ['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'النسبة', 'Unnamed: 4',       
                        'الكمية المباعة', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8',
                        'Unnamed: 9', 'القيمة', 'Unnamed: 11', 'الصنف', 'Unnamed: 13',
                        'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17',
                        'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21',
                        'Unnamed: 22', 'Unnamed: 23', 'Unnamed: 24', 'Unnamed: 25',
                        'Unnamed: 26', 'كود الصنف', 'Unnamed: 28', 'Unnamed: 29', 'Unnamed: 30',
                        'Unnamed: 31', 'Unnamed: 32', 'Unnamed: 33', 'Unnamed: 34',
                        'Unnamed: 35', 'Unnamed: 36', 'Unnamed: 37']
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
            
# --- cleaning ---
        df = df.rename(columns={'Unnamed: 15':'client name','Unnamed: 28':'client code','الكمية المباعة':'sales Units','القيمة':'sales Value','الصنف':'item name','كود الصنف':'item code'})
        selected_cols = ['client code','client name','item name','item code','sales Units','sales Value']
        df = df[selected_cols]
        df["client name"] = df["client name"].replace("بيوتك فارما", np.nan)
        df[['client code','client name','sales Units']] = df[['client code','client name','sales Units']].ffill()
        df = df[df['item code'].notna()]
        
# --- Add Year & Month ---
        df["Year"] = year
        df["Month"] = month



       # --- returning dataframe if it is not empty ---
        if df.empty:
            x = f"epda_cln ERROR: No valid data after cleaning-Empty table.  {uploaded_file}"

            y = 0
            return x ,y
        else:
            
            x = df
            y = 1
            return x ,y,month,year
        
    except Exception as e:
        x = f"epda_cln ERROR: Unexpected error in epda_cln(): {e}"
       
        y = 0
        return x ,y
    


