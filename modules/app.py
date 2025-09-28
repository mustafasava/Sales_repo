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
        options = [""] + dist_list
        distname = st.selectbox("Select Distributor", options, placeholder="choose distributor")

        if st.button("Run Mapping Process"):
            if not distname:
                st.error("Please select a distributor first.")
            else:
                pass
    except Exception as e:
        pass
