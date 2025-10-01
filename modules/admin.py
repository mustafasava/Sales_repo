from upload import upload
import streamlit as st
from info import dist_list
from save import save
from mapping import mapping


def admin():

    try:
        uploaded = upload(st.file_uploader("Upload Excel file", type=["xlsx", "xls"]))

        if uploaded is not None:
            
            cleaned = dist_list[uploaded[1]][0](uploaded[0], uploaded[1], uploaded[2], uploaded[3])
        
            if cleaned is not None:
                
                prepared = dist_list[cleaned[1]][1](cleaned[0], cleaned[1], cleaned[2], cleaned[3])
                
                # if prepared is not None:
                #     mapped = mapping(prepared[0],prepared[1],prepared[2],prepared[3])
                    
                #     if mapped is not None:

                #         save(cleaned[0], cleaned[1], cleaned[2], cleaned[3],"cleaned")
                #         save(mapped[0], mapped[1], mapped[2], mapped[3],"prep")
                #         st.success(f"( {mapped[1]} ) sheet has been uploaded, cleaned, prepared, mapped and saved successfully !")

        
    except Exception as e:
        st.error(f"{e}")
