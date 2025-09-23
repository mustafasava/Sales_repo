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

# --- Test Database Connection ---
def test_database_connection():
    """Test database connection and show available tables"""
    try:
        result = client.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in result]
        st.sidebar.success("✅ Database connection successful")
        st.sidebar.write("📊 Available tables:", tables)
        return True
    except Exception as e:
        st.sidebar.error(f"❌ Database connection failed: {e}")
        return False

# --- Clean DataFrame for SQL Insertion ---
def clean_dataframe(df):
    """Prepare DataFrame for SQL insertion"""
    # Replace NaN with None for SQL compatibility
    df = df.where(pd.notnull(df), None)
    
    # Convert all columns to string to avoid data type issues
    for col in df.columns:
        df[col] = df[col].astype(str)
    
    return df

# --- Export to native table ---
def export_to_native(table, df, month, year):
    """Insert cleaned data into native_<distributor> table"""
    try:
        # Clean the DataFrame
        df_cleaned = clean_dataframe(df.copy())
        
        # Delete old rows
        try:
            delete_result = client.execute(
                f"DELETE FROM {table} WHERE Month = ? AND Year = ?", 
                [month, year]
            )
            st.info(f"🗑️ Old rows deleted from {table}")
        except Exception as e:
            st.error(f"❌ Failed to delete old rows: {str(e)}")
            return False

        rows = df_cleaned.to_dict(orient="records")
        if not rows:
            st.info("ℹ️ No rows to insert")
            return True

        # Debug: Show data structure
        with st.expander("🔍 Debug Information"):
            st.write("📋 First row sample:", rows[0])
            st.write("📊 DataFrame shape:", df_cleaned.shape)
            st.write("🏷️ DataFrame columns:", list(df_cleaned.columns))
            
            # Get table schema
            try:
                schema_result = client.execute(f"PRAGMA table_info({table})")
                db_columns = [(row[1], row[2]) for row in schema_result]  # name, type
                st.write("🗃️ Database table schema:", db_columns)
            except Exception as e:
                st.warning(f"Could not get table schema: {e}")

        # Insert rows with detailed error handling
        success_count = 0
        cols = list(rows[0].keys())
        placeholders = ",".join("?" for _ in cols)
        sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})"
        
        st.write(f"🚀 Inserting {len(rows)} rows into {table}...")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, row in enumerate(rows):
            try:
                values = [row[c] for c in cols]
                
                # Debug first few rows
                if i < 3:  # Show details for first 3 rows
                    with st.expander(f"🔧 Row {i+1} Details"):
                        st.write("📝 SQL:", sql)
                        st.write("📦 Values:", values)
                
                client.execute(sql, values)
                success_count += 1
                
                # Update progress
                progress = (i + 1) / len(rows)
                progress_bar.progress(progress)
                status_text.text(f"Inserted {i+1}/{len(rows)} rows...")
                
            except Exception as e:
                st.error(f"❌ Failed to insert row {i+1}: {str(e)}")
                st.write("💥 Problematic row data:", row)
                
                # Try to identify the problematic column
                for col_name, value in row.items():
                    try:
                        test_sql = f"INSERT INTO {table} ({col_name}) VALUES (?)"
                        client.execute(test_sql, [value])
                    except Exception as col_error:
                        st.error(f"❌ Problem with column '{col_name}', value: '{value}'")
                        st.error(f"Column error: {col_error}")
                
                return False

        progress_bar.empty()
        status_text.empty()
        st.success(f"✅ Successfully exported {success_count} rows to {table}")
        return True
        
    except Exception as e:
        st.error(f"💥 Unexpected error in export_to_native: {str(e)}")
        return False

# --- Run prep query ---
def run_prep(distributor, month, year):
    """Execute preparation query for the distributor"""
    query_file = f"queries/{distributor.lower()}_prep.sql"
    if not os.path.exists(query_file):
        st.error(f"❌ Prep query not found: {query_file}")
        return False

    with open(query_file, "r", encoding="utf-8") as f:
        sql = f.read()

    prep_table = f"prep_{distributor.lower()}"

    # Delete old rows
    try:
        client.execute(f"DELETE FROM {prep_table} WHERE Month = ? AND Year = ?", [month, year])
        st.info(f"🗑️ Old rows deleted from {prep_table}")
    except Exception as e:
        st.error(f"❌ Failed to delete old rows from prep table: {str(e)}")
        return False

    # Replace placeholders if exist
    sql = sql.replace("{month}", str(month)).replace("{year}", str(year))

    try:
        client.execute(sql)
        st.success(f"✅ Prep query executed successfully for {prep_table}")
        return True
    except Exception as e:
        st.error(f"❌ Prep query failed: {str(e)}")
        st.code(sql)  # Show the SQL for debugging
        return False

# --- Streamlit UI ---
st.set_page_config(page_title="Data Cleaning Pipeline", layout="wide")
st.title("📊 Data Cleaning & Prep Pipeline")

# Test database connection
test_database_connection()

# File upload section
st.header("📁 Upload Data")
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"], help="Upload your distributor data file")

if uploaded_file:
    # Save uploaded file temporarily
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"✅ File uploaded: {uploaded_file.name}")

    # Distributor selection
    distributor = st.selectbox(
        "Select distributor",
        ["IBS", "EPDA", "POS", "Sofico", "Egydrug_Sales"],
        help="Select the distributor for the uploaded data"
    )

    # Run cleaning process
    st.header("🔧 Data Cleaning")
    if st.button("🚀 Start Cleaning Process", type="primary"):
        with st.spinner("Cleaning data..."):
            if distributor == "IBS":
                result = ibs_cln(temp_path)
            else:
                st.error(f"❌ Cleaning function not implemented yet for {distributor}")
                result = None

        if result:
            # Handle different return formats from cleaning functions
            if len(result) == 4:
                df_cleaned, y, month, year = result
            else:
                df_cleaned, y = result
                month, year = None, None

            if y == 1:
                st.success(f"✅ Cleaned {distributor} data for {month}-{year}")
                
                # Show cleaned data preview
                st.subheader("📋 Cleaned Data Preview")
                st.dataframe(df_cleaned.head(20), use_container_width=True)
                
                # Data statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rows", df_cleaned.shape[0])
                with col2:
                    st.metric("Columns", df_cleaned.shape[1])
                with col3:
                    st.metric("Period", f"{month}-{year}" if month and year else "N/A")

                # Export and Prep section
                st.header("📤 Export to Database")
                if st.button("💾 Export to Database", type="secondary"):
                    if month and year:
                        with st.spinner("Exporting to database..."):
                            if export_to_native(f"native_{distributor.lower()}", df_cleaned, month, year):
                                st.success("✅ Data exported successfully!")
                                
                                # Run prep query
                                st.header("⚙️ Running Preparation Query")
                                with st.spinner("Running preparation query..."):
                                    if run_prep(distributor, month, year):
                                        st.success("🎉 Pipeline completed successfully!")
                                    else:
                                        st.error("❌ Preparation query failed")
                            else:
                                st.error("❌ Data export failed")
                    else:
                        st.error("❌ Month and year information missing from cleaned data")
            else:
                st.error(f"❌ Cleaning failed: {df_cleaned}")

    # Clean up temporary file
    try:
        os.remove(temp_path)
    except:
        pass

else:
    st.info("👆 Please upload an Excel file to begin")

# Instructions section
with st.expander("📖 How to use this app"):
    st.markdown("""
    ### Usage Instructions:
    1. **Upload** your Excel file using the file uploader
    2. **Select** the appropriate distributor from the dropdown
    3. **Click** "Start Cleaning Process" to clean the data
    4. **Review** the cleaned data preview
    5. **Click** "Export to Database" to save to Turso database
    6. **Monitor** the progress and debug information

    ### Supported Distributors:
    - ✅ IBS (Implemented)
    - ❌ EPDA (Coming soon)
    - ❌ POS (Coming soon)
    - ❌ Sofico (Coming soon)
    - ❌ Egydrug_Sales (Coming soon)

    ### Features:
    - 🔍 Detailed debugging information
    - 📊 Data preview and statistics
    - 🗑️ Automatic cleanup of old data
    - ✅ Comprehensive error handling
    - 📈 Progress tracking
    """)

# Footer
st.markdown("---")
st.markdown("*Data Cleaning Pipeline v2.0 - Enhanced with better error handling*")