from upload import upload
import streamlit as st
from info import dist_list
from save import save


def admin():

    try:
        uploaded = upload(st.file_uploader("Upload Excel file", type=["xlsx", "xls"]))

        if uploaded is not None:
            
            cleaned = dist_list[uploaded[1]][0](uploaded[0], uploaded[1], uploaded[2], uploaded[3])
            save(cleaned[0], cleaned[1], cleaned[2], cleaned[3],"cleaned")
            
            if cleaned is not None:
                
                prepared = dist_list[cleaned[1]][1](cleaned[0], cleaned[1], cleaned[2], cleaned[3])
                save(prepared[0], prepared[1], prepared[2], prepared[3],"prepared")
                

                if prepared is not None:
                    
                    st.success(f"( {prepared[1]} ) sheet has been uploaded, cleaned, prepared and saved successfully !")

        
    except Exception as e:
        st.error(f"{e}")
