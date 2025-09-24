import streamlit as st
import re
from modules.cln_ibs import cln_ibs

# --- filename validation ---
def validate_filename(filename: str, distname: str) -> bool:
    """
    Validate filename format: distname_YYYY_MM.xlsx
    """
    pattern = rf"^{distname}_(\d{{4}})_(\d{{2}})\.xlsx$"
    return bool(re.match(pattern, filename))


st.title("📊 Sales Data Processing App")

# Select distributor
distributors = ["ibs", "pos", "sofico", "epda"]  # extend later
dist_choice = st.selectbox("Select Distributor", distributors)

# Upload file
uploaded_file = st.file_uploader("Upload file", type=["xlsx"])

if uploaded_file is not None:
    if validate_filename(uploaded_file.name, dist_choice):
        st.success("✅ Valid filename detected")
        
        if dist_choice == "ibs":
            message, status = cln_ibs(uploaded_file)  # returns (msg, status)
            if status == 1:
                st.success(message)
            else:
                st.error(message)

        # TODO: add other distributors (pos, sofico, epda)
    
    else:
        st.error(f"❌ Invalid filename. Expected: {dist_choice}_YYYY_MM.xlsx")
