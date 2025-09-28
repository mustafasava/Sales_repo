import streamlit as st
from auth import login, logout
from admin import admin
from info import dist_list
# ------------------- LOGIN -------------------
if not login():
    st.stop()

st.sidebar.success(f"Welcome {st.session_state.username} ({st.session_state.role})")
if st.sidebar.button("Logout"):
    logout()

if st.session_state.role == "admin":
    try:
        admin()
        distname = st.selectbox("Select Distributor", dist_list)

        # 2️⃣ Button to trigger the process
        if st.button("Run Mapping Process"):
            if not distname:
                st.error("Please select a distributor first.")
    except Exception as e:
        pass
