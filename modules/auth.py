import streamlit as st

# --- Auth dictionary ---
auth = {
    "user1": ["admin", "1234", "all"],
    "user2": ["sales", "1234", "ALEX"],
    "user3": ["sales", "1234", "Cairo"]
}

def init_auth():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.area = None

def login(username, password):
    if username in auth:
        role, pw, area = auth[username]
        if password == pw:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.session_state.area = area
            return True
    return False

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.area = None
