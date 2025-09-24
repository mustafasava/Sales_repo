import streamlit as st

# --- Auth dictionary ---
auth = {
    "user1": ["admin", "1234", "all"],
    "user2": ["sales", "1234", "ALEX"],
    "user3": ["sales", "1234", "Cairo"]
}

# --- Initialize session state ---
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


# --- App Layout ---
st.title("🔐 IBS Cleaning Portal")

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
        st.experimental_rerun()

    # --- Role-based app content ---
    if st.session_state.role == "admin":
        st.header("👑 Admin Dashboard")
        st.write("Here the admin can:")
        st.markdown("- Upload and clean **any distributor** file")
        st.markdown("- View consolidated reports across all areas")
        st.markdown("- Manage users")
        # 👉 place your admin cleaning app logic here
        # e.g., distributor selector, advanced reports, etc.

    elif st.session_state.role == "sales":
        st.header(f"📊 Sales Dashboard – {st.session_state.area}")
        st.write("Here the sales user can:")
        st.markdown(f"- Upload and clean files **only for {st.session_state.area}**")
        st.markdown("- See their own sales KPIs")
        # 👉 place your sales app logic here
        # e.g., restrict uploads, filter reports by st.session_state.area
