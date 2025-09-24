import streamlit as st
from auth import init_auth, login, logout

# Import cleaning + prep functions
from cln_ibs import cln_ibs
from prep_ibs import prep_ibs
# ... import others when needed

# --- Initialize auth ---
init_auth()

st.title("🔐 Distributor Cleaning & Preparing Portal")

if not st.session_state.logged_in:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if login(username, password):
            st.success(f"Welcome {st.session_state.username} ({st.session_state.role}, {st.session_state.area})")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

else:
    st.sidebar.success(f"✅ Logged in as {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()

    # --- Role-based content ---
    if st.session_state.role == "admin":
        st.header("👑 Admin Dashboard")
        # Example IBS section
        st.subheader("IBS Cleaning")
        uploaded_file = st.file_uploader("Upload IBS Excel file", type=["xlsx"])
        if uploaded_file is not None:
            msg = cln_ibs(uploaded_file)   # cleaning returns message
            st.write(msg)

        st.subheader("IBS Preparing")
        repo_path = st.text_input("Enter IBS repo file path")
        if st.button("Run IBS Prep"):
            msg = prep_ibs(repo_path)      # preparing returns message
            st.write(msg)

    elif st.session_state.role == "sales":
        st.header(f"📊 Sales Dashboard – {st.session_state.area}")
        st.write("Restricted view for sales users.")
        # Here you can show limited distributors
