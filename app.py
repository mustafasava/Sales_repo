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
def run_prep_batch(distributor, month, year, batch_size=100):
    prep_table = f"prep_{distributor.lower()}"

    # Delete old rows
    try:
        client.execute(f"DELETE FROM {prep_table} WHERE Month=? AND Year=?", [month, year])
        st.info(f"Old rows deleted from {prep_table}")
    except Exception as e:
        st.error(f"Failed to delete old rows from prep table: {e}")
        return False

    # Fetch rows from native table
    try:
        rows = client.execute(f"SELECT * FROM native_{distributor.lower()} WHERE Month=? AND Year=?", [month, year])
        rows = rows.fetchall()  # get list of rows
    except Exception as e:
        st.error(f"Failed to fetch rows from native table: {e}")
        return False

    if not rows:
        st.info("No rows to insert into prep table")
        return True

    # Transform rows for prep logic (Territory_Name mapping)
    prep_rows = []
    for r in rows:
        # Map Territory_Name according to your rules
        territory = r["Territory Name"]
        governorate = r["Governorate Name"]
        if territory == "Template District                       ":
            territory = r["Brick Name"]
        elif territory == "QENA I /RED SEA RED SEA                 ":
            territory = governorate
        elif territory == "NASR CITY NASR CITY                     " and ("القاهره الجديده     " in governorate or "عاصم" in governorate):
            territory = "القاهره الجديده     "

        prep_rows.append({
            "Year": r["Year"],
            "Month": r["Month"],
            "Item_Code": r["Item Code"],
            "Item_Name": r["Item Name"],
            "Brick": r["Brick"],
            "Territory_Name": territory,
            "Governorate_Name": governorate,
            "Sales_Units": r["QTY"],
            "Bonus_Units": r["FU"],
            "Dist_name": distributor.upper()
        })

    # Batch insert
    total_rows = len(prep_rows)
    for start in range(0, total_rows, batch_size):
        batch = prep_rows[start:start+batch_size]
        cols = [f"[{c}]" for c in batch[0].keys()]
        placeholders = ",".join("?" for _ in cols)
        sql = f"INSERT INTO {prep_table} ({','.join(cols)}) VALUES ({placeholders})"
        try:
            for row in batch:
                client.execute(sql, list(row.values()))
        except Exception as e:
            st.error(f"Failed to insert prep rows {start+1}-{start+len(batch)}: {e}")
            return False

    st.success(f"Inserted {total_rows} rows into {prep_table}")
    return True



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
