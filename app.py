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
            values_list = [list(row.values()) for row in batch]
            for values in values_list:
                client.execute(sql, values)
        except Exception as e:
            st.error(f"Failed to insert rows {start+1}-{start+len(batch)}: {e}")
            return False

    st.success(f"Exported {total_rows} rows to {table}")
    return True

# --- Run prep query ---
def run_prep(distributor, month, year):
    query_file = f"queries/{distributor.lower()}_prep.sql"
    if not os.path.exists(query_file):
        st.error(f"Prep query not found: {query_file}")
        return False

    with open(query_file, "r", encoding="utf-8") as f:
        sql = f.read()

    prep_table = f"prep_{distributor.lower()}"

    # Delete old rows
    try:
        client.execute(f"DELETE FROM {prep_table} WHERE Month = ? AND Year = ?", [month, year])
        st.info(f"Old rows deleted from {prep_table}")
    except Exception as e:
        st.error(f"Failed to delete old rows from prep table: {e}")
        return False

    # Execute prep query with parameters
    try:
        client.execute(sql, [month, year])
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

    # Clean up temporary file
    try:
        os.remove(temp_path)
    except:
        pass
