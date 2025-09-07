# Streamlit Sales Dashboard (Starter)

A minimal Streamlit app that reads **data/sales.xlsx** and shows charts by manager and product.

## Quickstart (Windows / PowerShell)

```powershell
# 1) Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run locally
streamlit run app.py
```

Put your real Excel file at `data/sales.xlsx` (with columns like: Date, Manager, Product, Sales).

## Git & GitHub

```powershell
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## Deploy on Streamlit Community Cloud

1. Go to https://streamlit.io/cloud and sign in with GitHub.
2. Click **New app** → choose this repo, the `main` branch, and `app.py` as the file.
3. Deploy. Every time you **push** updates (including changes to `data/sales.xlsx`) the app will refresh.

## Later: Authentication

- Add `streamlit-authenticator` and store creds in `.streamlit/secrets.toml`.
- Use role-based filtering to show each manager only their data.
