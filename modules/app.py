import streamlit as st
from auth import login, logout
from admin import admin , sales


# ------------------- LOGIN -------------------
if not login():
    st.stop()

st.sidebar.success(f"Welcome {st.session_state.username} ({st.session_state.role})")
if st.sidebar.button("Logout"):
    logout()

if st.session_state.role == "admin":
    try:
        admin()
       
    except Exception as e:
        st.error(f"{e}")


    