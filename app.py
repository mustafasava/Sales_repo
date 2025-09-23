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
    
    # Convert numeric columns to appropriate types
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            # Convert numeric columns to proper Python types
            df[col] = df[col].astype(object)  # Convert to Python objects
            df[col] = df[col].where(pd.notnull(df[col]), None)
        else:
            # Convert string columns, handling NaN
            df[col] = df[col].astype(str)
            df[col] = df[col].replace('nan', None).replace('None', None)
    
    return df

# --- Export to native table ---
def export_to_native(table, df, month, year):
    """Insert cleaned data into native_<distributor> table"""
    try:
        # Clean the DataFrame
        df_cleaned = clean_dataframe(df.copy())
        
        # Delete old rows
        try:
            result = client.execute(
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
                
                # Debug first row
                if i == 0:
                    with st.expander("🔧 First Row Details"):
                        st.write("📝 SQL:", sql)
                        st.write("📦 Values:", values)
                        st.write("📦 Values types:", [type(v) for v in values])
                
                # Execute the query - LibSQL client returns a result object
                result = client.execute(sql, values)
                
                # If we get here, the query executed successfully
                success_count += 1
                
                # Update progress
                progress = (i + 1) / len(rows)
                progress_bar.progress(progress)
                status_text.text(f"Inserted {i+1}/{len(rows)} rows...")
                
            except Exception as e:
                st.error(f"❌ Failed to insert row {i+1}: {str(e)}")
                st.write("💥 Problematic row data:", row)
                
                # More detailed error analysis
                st.write("🔍 Detailed error analysis:")
                for col_name, value in row.items():
                    st.write(f"   {col_name}: '{value}' (type: {type(value)})")
                
                return False

        progress_bar.empty()
        status_text.empty()
        st.success(f"✅ Successfully exported {success_count} rows to {table}")
        return True
        
    except Exception as e:
        st.error(f"💥 Unexpected error in export_to_native: {str(e)}")
        import traceback
        st.write("📋 Full traceback:")
        st.code(traceback.format_exc())
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
        result = client.execute(f"DELETE FROM {prep_table} WHERE Month = ? AND Year = ?", [month, year])
        st.info(f"🗑️ Old rows deleted from {prep_table}")
    except Exception as e:
        st.error(f"❌ Failed to delete old rows from prep table: {str(e)}")
        return False

    # Replace placeholders if exist
    sql = sql.replace("{month}", str(month)).replace("{year}", str(year))

    try:
        result = client.execute(sql)
        st.success(f"✅ Prep query executed successfully for {prep_table}")
        return True
    except Exception as e:
        st.error(f"❌ Prep query failed: {str(e)}")
        st.code(sql)  # Show the SQL for debugging
        return False

# --- Alternative batch insertion method ---
def export_to_native_batch(table, df, month, year):
    """Alternative method using batch insertion"""
    try:
        # Clean the DataFrame
        df_cleaned = clean_dataframe(df.copy())
        
        # Delete old rows
        try:
            result = client.execute(
                f"DELETE FROM {table} WHERE Month = ? AND Year = ?", 
                [month, year]
            )
            st.info(f"🗑️ Old rows deleted from {table}")
        except Exception as e:
            st.error(f"❌ Failed to delete old rows: {str(e)}")
            return False

        # Convert to list of tuples for batch insertion
        data_tuples = [tuple(row) for row in df_cleaned.itertuples(index=False)]
        cols = df_cleaned.columns.tolist()
        placeholders = ",".join("?" for _ in cols)
        
        sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})"
        
        st.write(f"🚀 Batch inserting {len(data_tuples)} rows into {table}...")
        
        # Try batch execution
        success_count = 0
        for i, row_tuple in enumerate(data_tuples):
            try:
                result = client.execute(sql, list(row_tuple))
                success_count += 1
            except Exception as e:
                st.error(f"❌ Failed to insert row {i+1}: {str(e)}")
                st.write("💥 Problematic row:", row_tuple)
                return False
        
        st.success(f"✅ Successfully exported {success_count} rows to {table}")
        return True
        
    except Exception as e:
        st.error(f"💥 Unexpected error in batch export: {str(e)}")
        return False

# --- Streamlit UI ---
st.set_page_config(page_title="Data Cleaning Pipeline", layout="wide")
st.title("📊 Data Cleaning & Prep Pipeline")

# Test database connection
test_database_connection()

# File upload section
st.header("📁 Upload Data")
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"], help="Upload your distributor data file")

# Initialize session state to preserve cleaned data
if 'cleaned_data' not in st.session_state:
    st.session_state.cleaned_data = None
if 'distributor' not in st.session_state:
    st.session_state.distributor = None
if 'month' not in st.session_state:
    st.session_state.month = None
if 'year' not in st.session_state:
    st.session_state.year = None

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
    
    if st.button("🚀 Start Cleaning Process", type="primary", key="clean_btn"):
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
                # Store results in session state
                st.session_state.cleaned_data = df_cleaned
                st.session_state.distributor = distributor
                st.session_state.month = month
                st.session_state.year = year
                
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
                
                # Show data types
                with st.expander("🔍 Data Types Info"):
                    st.write("DataFrame dtypes:")
                    st.write(df_cleaned.dtypes)
            else:
                st.error(f"❌ Cleaning failed: {df_cleaned}")

    # Clean up temporary file
    try:
        os.remove(temp_path)
    except:
        pass

    # Show export section only if we have cleaned data
    if st.session_state.cleaned_data is not None:
        st.header("📤 Export to Database")
        
        # Display current state info
        st.info(f"Ready to export: {st.session_state.distributor} data for {st.session_state.month}-{st.session_state.year}")
        
        # Let user choose insertion method
        insertion_method = st.radio(
            "Insertion Method:",
            ["Standard", "Batch"],
            help="Try Batch method if Standard fails"
        )
        
        if st.button("💾 Export to Database", type="secondary", key="export_btn"):
            if st.session_state.month and st.session_state.year:
                with st.spinner("Exporting to database..."):
                    if insertion_method == "Standard":
                        success = export_to_native(
                            f"native_{st.session_state.distributor.lower()}", 
                            st.session_state.cleaned_data, 
                            st.session_state.month, 
                            st.session_state.year
                        )
                    else:
                        success = export_to_native_batch(
                            f"native_{st.session_state.distributor.lower()}", 
                            st.session_state.cleaned_data, 
                            st.session_state.month, 
                            st.session_state.year
                        )
                    
                    if success:
                        st.success("✅ Data exported successfully!")
                        
                        # Run prep query
                        st.header("⚙️ Running Preparation Query")
                        with st.spinner("Running preparation query..."):
                            if run_prep(st.session_state.distributor, st.session_state.month, st.session_state.year):
                                st.success("🎉 Pipeline completed successfully!")
                            else:
                                st.error("❌ Preparation query failed")
                    else:
                        st.error("❌ Data export failed")
            else:
                st.error("❌ Month and year information missing from cleaned data")

else:
    st.info("👆 Please upload an Excel file to begin")
    
    # Clear session state when no file is uploaded
    if st.session_state.cleaned_data is not None:
        st.session_state.cleaned_data = None
        st.session_state.distributor = None
        st.session_state.month = None
        st.session_state.year = None

# Instructions section
with st.expander("📖 How to use this app"):
    st.markdown("""
    ### Usage Instructions:
    1. **Upload** your Excel file using the file uploader
    2. **Select** the appropriate distributor from the dropdown
    3. **Click** "Start Cleaning Process" to clean the data
    4. **Review** the cleaned data preview
    5. **Choose** insertion method (Standard or Batch)
    6. **Click** "Export to Database" to save to Turso database

    ### Troubleshooting:
    - If Standard method fails, try Batch method
    - Check the debug information for data type issues
    - Verify your table schema matches the data
    """)

# Footer
st.markdown("---")
st.markdown("*Data Cleaning Pipeline v2.1 - Fixed LibSQL client handling*")