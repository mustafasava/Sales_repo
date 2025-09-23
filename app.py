import streamlit as st
import pandas as pd
import os
from libsql_client import create_client_sync

# --- Import cleaning functions ---
from modules.cleaning.IBS_cln import ibs_cln
# from modules.cleaning.EPDA_cln import epda_cln, etc.

# --- Turso client ---
client = create_client_sync(
    url=st.secrets["TURSO_URL"],
    auth_token=st.secrets["TURSO_AUTH_TOKEN"]
)

# --- Export to native table with batch insert ---
def export_to_native(table, df, month, year, batch_size=100):
    """Insert cleaned data into native_<distributor> table in batches"""
    try:
        client.execute(f"DELETE FROM {table} WHERE Month = ? AND Year = ?", [month, year])
        st.info(f"Old rows deleted from {table}")
    except Exception as e:
        st.error(f"Failed to delete old rows: {e}")
        return False

    rows = df.to_dict(orient="records")
    if not rows:
        st.info("No rows to insert")
        return True

    # Batch insert
    total_rows = len(rows)
    for start in range(0, total_rows, batch_size):
        batch = rows[start:start+batch_size]
        cols = [f"[{c}]" for c in batch[0].keys()]  # wrap column names in []
        placeholders = ",".join("?" for _ in cols)
        sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})"
        try:
            for row in batch:
                client.execute(sql, list(row.values()))
        except Exception as e:
            st.error(f"Failed to insert rows {start+1}-{start+len(batch)}: {e}")
            return False

    st.success(f"Exported {total_rows} rows to {table}")
    return True

# --- Run prep query with hardcoded SQL ---
def run_prep(distributor, month, year):
    prep_table = f"prep_{distributor.lower()}"

    try:
        client.execute(f"DELETE FROM {prep_table} WHERE Month = ? AND Year = ?", [month, year])
        st.info(f"Old rows deleted from {prep_table}")
    except Exception as e:
        st.error(f"Failed to delete old rows from prep table: {e}")
        return False

    # Execute prep SQL directly
    try:
        client.execute(client.execute(f"INSERT INTO prep_ibs (Year,Month,Item_Code,Item_Name,Brick,Territory_Name,Governorate_Name,Sales_Units,Bonus_Units,Dist_name) "
               f"SELECT Year,Month,[Item Code] AS Item_Code,[Item Name] AS Item_Name,Brick,CASE WHEN [Territory Name]='Template District                       ' THEN [Brick Name] "
               f"WHEN [Territory Name]='QENA I /RED SEA RED SEA                 ' THEN [Governorate Name] "
               f"WHEN [Territory Name]='NASR CITY NASR CITY                     ' AND ([Governorate Name]='القاهره الجديده     ' OR [Governorate Name] LIKE '%عاصم%') THEN 'القاهره الجديده     ' "
               f"ELSE [Territory Name] END AS Territory_Name,[Governorate Name] AS Governorate_Name,QTY AS Sales_Units,FU AS Bonus_Units,'IBS' AS Dist_name "
               f"FROM native_ibs WHERE Month=? AND Year=?;", [month, year]))
        st.success(f"Prep query executed for {prep_table}")
        return True
    except Exception as e:
        st.error(f"Prep query failed: {e}")
        return False


# --- Streamlit UI ---
st.title("Data Cleaning & Prep Pipeline")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file:
    temp_path = uploaded_file.name
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    distributor = st.selectbox(
        "Select distributor",
        ["IBS", "EPDA", "POS", "Sofico", "Egydrug_Sales"]
    )

    # Run cleaning
    if distributor == "IBS":
        result = ibs_cln(temp_path)
    else:
        st.error(f"Cleaning function not implemented yet for {distributor}")
        result = None

    if result:
        if len(result) == 4:
            df_cleaned, y, month, year = result
        else:
            df_cleaned, y = result
            month, year = None, None

        if y == 1:
            st.success(f"Cleaned {distributor} data for {month}-{year}")
            st.dataframe(df_cleaned.head(20))

            if export_to_native(f"native_{distributor.lower()}", df_cleaned, month, year):
                run_prep(distributor, month, year)
        else:
            st.error(df_cleaned)

    try:
        os.remove(temp_path)
    except:
        pass
