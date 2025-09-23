import streamlit as st
import pandas as pd
import os
from libsql_client import create_client_sync

# --- Import your cleaning functions ---
from modules.cleaning.IBS_cln import ibs_cln
# from modules.cleaning.EPDA_cln import epda_cln, etc.

# --- Turso connection ---
db_url = st.secrets["TURSO_URL"]
db_token = st.secrets["TURSO_AUTH_TOKEN"]
client = create_client_sync(url=db_url, auth_token=db_token)


# --- Helper to escape values ---
def escape_value(v):
    if v is None:
        return "NULL"
    if isinstance(v, str):
        return f"'{v.replace('\'','\'\'')}'"  # escape single quotes
    return str(v)


# --- Export to native table ---
def export_to_native(table, df, month, year):
    """Insert cleaned data into native_<distributor> table"""
    try:
        client.execute(f"DELETE FROM {table} WHERE Month = {month} AND Year = {year}")
        st.info(f"Old rows deleted from {table}")
    except Exception as e:
        st.error(f"Failed to delete old rows: {e}")
        return False

    rows = df.to_dict(orient="records")
    for i, row in enumerate(rows):
        cols = list(row.keys())
        values = [escape_value(row[c]) for c in cols]
        sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(values)})"
        try:
            client.execute(sql)
        except Exception as e:
            st.error(f"Failed to insert row {i+1}: {e}")
            return False

    st.success(f"Exported {len(rows)} rows to {table}")
    return True


# --- Run prep query ---
def run_prep(distributor, month, year):
    """Run the prep SQL query to populate prep_<distributor>"""
    query_file = f"queries/{distributor.lower()}_prep.sql"
    if not os.path.exists(query_file):
        st.error(f"Prep query not found: {query_file}")
        return False

    with open(query_file, "r", encoding="utf-8") as f:
        sql = f.read()

    prep_table = f"prep_{distributor.lower()}"

    try:
        client.execute(f"DELETE FROM {prep_table} WHERE Month = {month} AND Year = {year}")
        st.info(f"Old rows deleted from {prep_table}")
    except Exception as e:
        st.error(f"Failed to delete old rows from prep table: {e}")
        return False

    # Inline month/year in SQL if needed
    sql = sql.replace("{month}", str(month)).replace("{year}", str(year))

    try:
        client.execute(sql)
        st.success(f"Prep query executed for {prep_table}")
        return True
    except Exception as e:
        st.error(f"Prep query failed: {e}")
        return False


# --- Streamlit UI ---
st.title("Data Cleaning & Prep Pipeline")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file:
    # Save temporary file
    temp_path = uploaded_file.name
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Select distributor
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

            # Export to native table
            if export_to_native(f"native_{distributor.lower()}", df_cleaned, month, year):
                # Run prep
                run_prep(distributor, month, year)

        else:
            st.error(df_cleaned)

    # Clean up temporary file
    try:
        os.remove(temp_path)
    except:
        pass
