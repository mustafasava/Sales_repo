import streamlit as st
import pandas as pd
import os


# --- Import your cleaning functions ---
from modules.cleaning.IBS_cln import ibs_cln

# (when you add more: from modules.EPDA_cln import epda_cln, etc.)

# --- Turso connection ---
from libsql_client import create_client_sync

db_url = st.secrets["TURSO_URL"]
db_token = st.secrets["TURSO_AUTH_TOKEN"]
client = create_client_sync(url=db_url, auth_token=db_token)

# --- Export to native table ---
def export_to_native(table, df, month, year):
    client.execute(f"DELETE FROM {table} WHERE Month = ? AND Year = ?", (month, year))
    rows = df.to_dict(orient="records")
    for row in rows:
        cols = list(row.keys())
        placeholders = ",".join("?" * len(cols))
        sql = f'INSERT INTO {table} ({",".join(cols)}) VALUES ({placeholders})'
        client.execute(sql, tuple(row.values()))


# --- Run prep query ---
def run_prep(distributor, month, year):
    query_file = f"queries/{distributor.lower()}_prep.sql"
    if not os.path.exists(query_file):
        st.error(f"Prep query not found: {query_file}")
        return False

    with open(query_file, "r", encoding="utf-8") as f:
        sql = f.read()

    prep_table = f"prep_{distributor.lower()}"
    client.execute(f"DELETE FROM {prep_table} WHERE Month = ? AND Year = ?", (month, year))
    client.execute(sql, (month, year))
    return True


# --- Streamlit UI ---
st.title("Data Cleaning & Prep Pipeline")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file:
    temp_path = "temp_upload.xlsx"
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
        st.error("Cleaning function not implemented yet for this distributor.")
        result = None

    if result:
        if len(result) == 4:
            x, y, month, year = result
        else:
            x, y = result
            month, year = None, None

        if y == 1:
            st.success(f"Cleaned {distributor} data for {month}-{year}")
            st.dataframe(x.head(20))

            try:
                # Export to native
                export_to_native(f"native_{distributor.lower()}", x, month, year)
                st.success(f"Exported to native_{distributor.lower()}")

                # Run prep
                if run_prep(distributor, month, year):
                    st.success(f"Prep done into prep_{distributor.lower()}")
                else:
                    st.error("Prep failed.")

            except Exception as e:
                st.error(f"Error during export/prep: {e}")

        else:
            st.error(x)

    # Clean up
    try:
        os.remove(temp_path)
    except:
        pass
