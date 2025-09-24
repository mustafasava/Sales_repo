import streamlit as st
from auth import login, logout
from cln_ibs import cln_ibs
from prep_ibs import prep_ibs
import re

# ------------------- LOGIN -------------------
if not login():
    st.stop()

st.sidebar.success(f"Welcome {st.session_state.username} ({st.session_state.role})")
if st.sidebar.button("Logout"):
    logout()

# ------------------- Helper: Validate filename -------------------
def validate_filename(filename):
    """
    Validate distributor filename: distname_year_month.xlsx
    Example: ibs_2025_09.xlsx
    """
    pattern = r"^([a-zA-Z]+)_(\d{4})_(0[1-9]|1[0-2])\.xlsx$"
    match = re.match(pattern, filename.lower())
    if not match:
        return None, None, None
    distname, year, month = match.groups()
    return distname, int(year), int(month)

# ------------------- ROLE ROUTING -------------------
if st.session_state.role == "admin":
    st.header("📊 Admin Dashboard")
    st.write("Here admin can manage cleaning & preparing for all distributors")

    uploaded_file = st.file_uploader("Upload distributor Excel file", type=["xlsx"])
    if uploaded_file:
        distname, year, month = validate_filename(uploaded_file.name)
        if not distname:
            st.error("❌ Invalid filename. Use format: distname_YYYY_MM.xlsx")
        else:
            msg, status, df, _, _ = cln_ibs(uploaded_file)  # only cleaning
            st.write(msg)
            if status:
                st.dataframe(df.head())

            if st.button("Run Preparing"):
                save_path = "cleaned_src/" + uploaded_file.name.lower()
                msg = prep_ibs(save_path)  # prepping uses saved path
                st.write(msg)

elif st.session_state.role == "sales":
    st.header(f"🧾 Sales Dashboard - {st.session_state.area}")
    st.write("Sales users see only limited uploads/reports")

    uploaded_file = st.file_uploader("Upload distributor Excel file", type=["xlsx"])
    if uploaded_file:
        distname, year, month = validate_filename(uploaded_file.name)
        if not distname:
            st.error("❌ Invalid filename. Use format: distname_YYYY_MM.xlsx")
        else:
            msg, status, df, _, _ = cln_ibs(uploaded_file)
            st.write(msg)
            if status:
                st.dataframe(df.head())

else:
    st.error("Unknown role — check auth setup.")
