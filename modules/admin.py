from upload import upload
import streamlit as st
from info import dist_list



def admin():

    uploaded = upload(st.file_uploader("Upload Excel file", type=["xlsx", "xls"]))

    if uploaded is not None:
        
        cleaned = dist_list[uploaded[1]](uploaded[0], uploaded[1], uploaded[2], uploaded[3])
        

    

