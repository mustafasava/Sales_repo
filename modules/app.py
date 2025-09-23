from cln_egydrug import *
from cln_epda import *
from cln_ibs import *
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

# --- Add cleaned_src to Python path ---
sys.path.append(os.path.abspath("cleaned_src"))

# --- Import cleaning function ---
from cln_ibs import ibs_cln   # make sure file is named cln_ibs.py inside cleaned_src

st.set_page_config(page_title="IBS Cleaning Test", layout="wide")
st.title("🧹 IBS Cleaning Test")

# File uploader
uploaded_file = st.file_uploader("Upload your IBS Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    st.success("✅ File uploaded successfully")

    try:
        # Save file temporarily because ibs_cln expects a path
        temp_path = "temp_uploaded.xlsx"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Run cleaning
        result = ibs_cln(temp_path)

        if isinstance(result, tuple) and len(result) >= 2:
            df_or_msg, y = result[0], result[1]

            if y == 1 and isinstance(df_or_msg, pd.DataFrame):
                st.write("Preview of Cleaned Data:")
                st.dataframe(df_or_msg.head(20))

                # Option to download cleaned file
                csv = df_or_msg.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Cleaned Data as CSV",
                    data=csv,
                    file_name="ibs_cleaned.csv",
                    mime="text/csv",
                )
            else:
                st.error(df_or_msg)

        else:
            st.error("❌ Unexpected return format from ibs_cln")

    except Exception as e:
        st.error(f"❌ Error during cleaning: {e}")

else:
    st.info("👆 Please upload an Excel file to test.")
