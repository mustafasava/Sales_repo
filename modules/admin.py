from upload import upload
import streamlit as st
from info import dist_list



def admin():

    result = upload(st.file_uploader("Upload Excel file", type=["xlsx", "xls"]))
    if result is not None:
        
        dist_list[result[1]](result[0], result[1], result[2], result[3])

