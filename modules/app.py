import streamlit as st
from auth import login, logout
from cln_ibs import cln_ibs
from prep_ibs import prep_ibs

# ------------------- LOGIN -------------------
if not login():
    st.stop()

st.sidebar.success(f"Welcome {st.session_state.username} ({st.session_state.role})")
if st.sidebar.button("Logout"):
    logout()

# ------------------- ROLE ROUTING -------------------
if st.session_state.role == "admin":
    st.header("📊 Admin Dashboard")
    st.write("Here admin can manage cleaning & preparing for all distributors")

    uploaded_file = st.file_uploader("Upload IBS Excel file", type=["xlsx"])
    if uploaded_file:
        msg, status, df, month, year = cln_ibs(uploaded_file)
        st.write(msg)
        if status:
            st.dataframe(df.head())

        if st.button("Run Preparing"):
            msg = prep_ibs("cleaned_src/" + uploaded_file.name.lower().replace(" ", "_"))
            st.write(msg)

elif st.session_state.role == "sales":
    st.header(f"🧾 Sales Dashboard - {st.session_state.area}")
    st.write("Sales users see only limited reports or uploads here.")

    uploaded_file = st.file_uploader("Upload IBS Excel file", type=["xlsx"])
    if uploaded_file:
        msg, status, df, month, year = cln_ibs(uploaded_file)
        st.write(msg)
        if status:
            st.dataframe(df.head())

else:
    st.error("Unknown role — check auth setup.")
