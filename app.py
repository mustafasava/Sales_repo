
import os
from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Sales Dashboard", page_icon="📈", layout="wide")

SALES_FILE = Path("data/sales.xlsx")

@st.cache_data(show_spinner=False)
def _load_data_impl(xlsx_path: str, mtime: float) -> pd.DataFrame:
    df = pd.read_excel(xlsx_path, engine="openpyxl")
    # Normalize columns (rename if your sheet uses different names)
    rename_map = {
        "manager": "Manager",
        "date": "Date",
        "product": "Product",
        "sales": "Sales",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    # Basic parsing
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
    if "Sales" in df.columns:
        df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce").fillna(0)
    return df

def load_data(xlsx_path: str) -> pd.DataFrame:
    # Bust cache when the Excel file changes by including its mtime in the key
    mtime = os.path.getmtime(xlsx_path)
    return _load_data_impl(xlsx_path, mtime)

st.title("📈 Sales Dashboard")
st.caption("Data source: **data/sales.xlsx** in this GitHub repo. Push an updated file to refresh.")

if not SALES_FILE.exists():
    st.error(f"Couldn't find {SALES_FILE}. Please add your Excel file and push again.")
    st.stop()

df = load_data(str(SALES_FILE))

if df.empty:
    st.warning("Your sales file has no data rows.")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    managers = ["All"] + sorted([m for m in df["Manager"].dropna().astype(str).unique()])
    selected_manager = st.selectbox("Manager", managers, index=0)
    date_min, date_max = df["Date"].min(), df["Date"].max()
    date_range = st.date_input("Date range", (date_min, date_max), min_value=date_min, max_value=date_max)

# Apply filters
f = df.copy()
if selected_manager != "All":
    f = f[f["Manager"].astype(str) == selected_manager]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    f = f[(f["Date"] >= start) & (f["Date"] <= end)]

# KPIs
total_sales = float(f["Sales"].sum()) if "Sales" in f.columns else 0.0
days = max(1, (f["Date"].max() - f["Date"].min()).days or 1) if "Date" in f.columns and not f.empty else 1
avg_daily = total_sales / days

left, mid, right = st.columns(3)
left.metric("Total Sales", f"{total_sales:,.0f}")
mid.metric("Avg / Day", f"{avg_daily:,.0f}")
right.metric("Records", f"{len(f):,}")

# Charts
if not f.empty:
    # Sales over time
    sales_over_time = (
        f.groupby("Date", as_index=False)["Sales"].sum()
        .sort_values("Date")
    )
    c1 = alt.Chart(sales_over_time).mark_line(point=True).encode(
        x="Date:T",
        y=alt.Y("Sales:Q", title="Sales"),
        tooltip=["Date:T", "Sales:Q"]
    ).properties(height=300, title="Sales Over Time")
    st.altair_chart(c1, use_container_width=True)

    col1, col2 = st.columns(2)
    # Sales by Product
    by_product = f.groupby("Product", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
    c2 = alt.Chart(by_product).mark_bar().encode(
        x=alt.X("Sales:Q", title="Sales"),
        y=alt.Y("Product:N", sort="-x"),
        tooltip=["Product:N", "Sales:Q"]
    ).properties(height=300, title="Sales by Product")
    col1.altair_chart(c2, use_container_width=True)

    # Sales by Manager (only when All managers selected)
    if selected_manager == "All":
        by_manager = df.groupby("Manager", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
        c3 = alt.Chart(by_manager).mark_bar().encode(
            x=alt.X("Sales:Q", title="Sales"),
            y=alt.Y("Manager:N", sort="-x"),
            tooltip=["Manager:N", "Sales:Q"]
        ).properties(height=300, title="Sales by Manager")
        col2.altair_chart(c3, use_container_width=True)

st.divider()
st.info(
    "🔐 Authentication is not enabled yet. Later, you can add role-based access with "
    "`streamlit-authenticator` and `st.secrets`."
)
