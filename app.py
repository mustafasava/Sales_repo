import pandas as pd
import streamlit as st
import altair as alt
from pathlib import Path

st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")

# File & sheet
DATA_FILE = Path("data/Sales YTD.xlsx")
SHEET_NAME = "All_sales"

@st.cache_data(show_spinner=False)
def load_data(path, sheet):
    df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
    df.columns = [c.strip() for c in df.columns]

    # Ensure Month is integer (1–12)
    if "Month" in df.columns:
        df["Month"] = pd.to_numeric(df["Month"], errors="coerce").astype("Int64")
    return df

# Load data
if not DATA_FILE.exists():
    st.error(f"Could not find {DATA_FILE}. Please add your Excel file to the data/ folder.")
    st.stop()

df = load_data(DATA_FILE, SHEET_NAME)

# Debugging aid
st.write("🔎 Columns loaded:", df.columns.tolist())
st.dataframe(df.head())

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    region = st.selectbox("Region", ["All"] + sorted(df["Region"].dropna().unique()))
    governorate = st.selectbox("Governorate", ["All"] + sorted(df["Governorate"].dropna().unique()))
    distributor = st.selectbox("Distributor", ["All"] + sorted(df["Dist name"].dropna().unique()))
    product = st.selectbox("Product", ["All"] + sorted(df["P-name"].dropna().unique()))

# Apply filters
f = df.copy()
if region != "All":
    f = f[f["Region"] == region]
if governorate != "All":
    f = f[f["Governorate"] == governorate]
if distributor != "All":
    f = f[f["Dist name"] == distributor]
if product != "All":
    f = f[f["P-name"] == product]

# KPIs
col1, col2 = st.columns(2)
col1.metric("Total Sales Units", f"{f['Sales Units'].sum():,.0f}")
col2.metric("Total Sales Value", f"{f['Sales Value'].sum():,.0f}")

# Trend line chart
if not f.empty:
    trend = (
        f.groupby("Month", as_index=False)[["Sales Units", "Sales Value"]]
        .sum()
        .sort_values("Month")
    )

    line_units = alt.Chart(trend).mark_line(point=True, color="blue").encode(
        x=alt.X("Month:O", title="Month"),
        y="Sales Units:Q",
        tooltip=["Month:O", "Sales Units:Q"]
    )
    line_value = alt.Chart(trend).mark_line(point=True, color="green").encode(
        x=alt.X("Month:O", title="Month"),
        y="Sales Value:Q",
        tooltip=["Month:O", "Sales Value:Q"]
    )

    chart = alt.layer(line_units, line_value).resolve_scale(y="independent").properties(
        height=400, title="Sales Trend (Units & Value)"
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("No data available for these filters.")
