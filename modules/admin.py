from upload import upload
import streamlit as st
from info import dist_list



def admin():

    result = upload(st.file_uploader("Upload Excel file", type=["xlsx", "xls"]))
    uploaded_file, distname, year, month = result
    dist_list[distname](uploaded_file, distname, year, month)

