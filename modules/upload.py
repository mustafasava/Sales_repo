import streamlit as st


def upload():
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        st.write("File details:")
        st.write(f"- Type: {uploaded_file.type}")
        st.write(f"- Size: {uploaded_file.size} bytes")