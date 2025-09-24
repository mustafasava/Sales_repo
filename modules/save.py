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
    folder = "cleaned_src" if sheettype == "cln" else "prepared_src"
    file_name = f"{sheettype}_{distname}_{year}_{month}.xlsx"
    save_path = f"{folder}/{file_name}"

    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    try:
        contents = repo.get_contents(save_path)
        repo.update_file(save_path, f"Update {file_name}", buffer.read(), contents.sha)
        st.success("great")
    except:
        buffer.seek(0)
        repo.create_file(save_path, f"Add {file_name}", buffer.read())
        st.success("great")