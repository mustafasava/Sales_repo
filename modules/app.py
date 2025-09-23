from cln_egydrug import *
from cln_epda import *
from cln_ibs import cln_ibs
from cln_pos import *
from cln_sofico import *

from prep_egydrug import *
from prep_epda import *
from prep_ibs import *
from prep_pos import *
from prep_sofico import *

import streamlit as st
import pandas as pd
import sys
import os

import streamlit as st
import os


st.title("IBS Cleaning App")

uploaded_file = st.file_uploader("Upload IBS Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Use the original uploaded file name
    original_name = uploaded_file.name
    save_path = os.path.join(".", original_name)

    # Save uploaded file locally
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write(f"✅ File saved as: {save_path}")

    try:
        # Run cleaning function
        cleaned_path = cln_ibs(save_path)

        st.success(f"Cleaning successful! Cleaned file saved at: {cleaned_path}")
        st.download_button(
            label="Download Cleaned File",
            data=open(cleaned_path, "rb"),
            file_name=os.path.basename(cleaned_path),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error during cleaning: {e}")
