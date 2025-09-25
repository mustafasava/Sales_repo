import os
from io import BytesIO
import pandas as pd
from github import Github
import streamlit as st
# GitHub setup
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "mustafasava/Sales_repo"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)

def save(df, distname, year, month, sheettype):
    if sheettype == "cleaned":
        folder = "cleaned_src"
    else :
        folder = "prepared_src"
    file_name = f"{sheettype}_{distname}_{year}_{month}.xlsx"
    save_path = f"{folder}/{file_name}"

    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    try:
        files = repo.get_contents(folder)  # list of files in the folder
        existing_files = [f.path for f in files]
    except:
        st.error(f"Can't find a folder for {sheettype}, please inform Admin")

    if save_path in existing_files:
        try:
            contents = repo.get_contents(save_path)
            repo.update_file(
                save_path,
                f"Update {file_name}",
                buffer.read(),
                contents.sha
            )
            st.info(f"while saving in {folder} I found a sheet with same name, I updated it.")
        except Exception as e:
            st.error(f"{e}")
            
    else:
        try:
            buffer.seek(0)
            repo.create_file(
                save_path,
                f"Add {file_name}",
                buffer.read()
            )
        except Exception as e:
            st.error(f"{e}")