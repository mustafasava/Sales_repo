import streamlit as st

# Hardcoded users: name: [role, password, area]
auth = {
    "user1": ["admin", "1234", "all"],
    "user2": ["sales", "1234", "ALEX"],
    "user3": ["sales", "1234", "Cairo"]
}


def login():
    """Render login form and store user info in session state."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.area = None

    if st.session_state.logged_in:
        return True

    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in auth and password == auth[username][1]:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = auth[username][0]
            st.session_state.area = auth[username][2]
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

    return st.session_state.logged_in


def logout():
    """Clear login session."""
    for key in ["logged_in", "username", "role", "area"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
