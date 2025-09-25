import numpy as np
import pandas as pd
import streamlit as st

def prep_epda(cleaned_file , distname , year , month):
    try:
        prepared_file = cleaned_file.rename(columns={
            "item code": "item_code",
            "item name": "item_name",
            "client name": "client_name",
            "client code": "client_code",
            "sales Units": "sales_units",
            
        })   [[ "item_code", "item_name", "client_name", "client_code", "sales_units" ]]

        prepared_file["territory_name"] = prepared_file["client_name"].apply(lambda x: (
                            x.split("-", 1)[1].strip() if "-" in x and x.split("-", 1)[1].strip() != "" else
                            (x.split("-", 1)[0].strip() if "-" in x and x.split("-", 1)[0].strip() != "" else x.strip())
                        )
                    )
       
        return prepared_file , distname , year , month

        
    except Exception as e:
        st.error(f"Error : {e}")