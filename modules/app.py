import streamlit as st
import pandas as pd

from cln_ibs import cln_ibs
from prep_ibs import prep_ibs

st.title("IBS Cleaning App")

uploaded_file = st.file_uploader("Upload IBS Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Read directly from uploaded file (BytesIO)
        df = pd.read_excel(uploaded_file)

        st.write("📊 Raw Data Preview:")
        st.dataframe(df.head())

        # Run cleaning function (now accepts dataframe)
        cleaned_df = cln_ibs(df)

        st.success("✅ Cleaning successful!")

        # Show preview
        st.write("🧹 Cleaned Data Preview:")
        st.dataframe(cleaned_df.head())

        # Allow download of cleaned file
        cleaned_excel = cleaned_df.to_excel(index=False, engine="xlsxwriter")
        st.download_button(
            label="Download Cleaned File",
            data=cleaned_df.to_csv(index=False).encode("utf-8"),  # or to_excel via BytesIO
            file_name="cleaned_ibs.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error during cleaning: {e}")
