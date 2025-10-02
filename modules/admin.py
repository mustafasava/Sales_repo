from upload import upload
import streamlit as st
from info import dist_list
from save import save
from mapping import check_missing
import pandas as pd
import plotly.express as px


def admin():

    try:
        st.sidebar.file_uploader("Upload Mapping file", type=["xlsx", "xls"])
        uploaded = upload(st.file_uploader("Upload Excel file", type=["xlsx", "xls"]))

        if uploaded is not None:
            
            cleaned = dist_list[uploaded[1]][0](uploaded[0], uploaded[1], uploaded[2], uploaded[3])
        
            if cleaned is not None:
                
                prepared = dist_list[cleaned[1]][1](cleaned[0], cleaned[1], cleaned[2], cleaned[3])
                
                if prepared is not None:
                    mapped = check_missing(prepared[0],prepared[1],prepared[2],prepared[3])
                    
                    
                    if mapped is not None:

                        save(cleaned[0], cleaned[1], cleaned[2], cleaned[3],"cleaned")
                        save(mapped[0], mapped[1], mapped[2], mapped[3],"prep")
                        st.success(f"( {mapped[1]} ) sheet has been uploaded, cleaned, prepared, mapped and saved successfully !")

        
    except Exception as e:
        st.error(f"{e}")


def sales():
    df = pd.read_excel("./prepared_src/prep_egydrug_2025_7.xlsx")
    
    

    # Load your dataframe
    

    st.set_page_config(page_title="Sales Dashboard", layout="wide")

    # --- Sidebar filters
    st.sidebar.header("Filters")
    year = st.sidebar.multiselect("Year", options=df["year"].unique(), default=df["year"].unique())
    month = st.sidebar.multiselect("Month", options=df["month"].unique(), default=df["month"].unique())
    dist = st.sidebar.multiselect("Distributor", options=df["dist_name"].unique(), default=df["dist_name"].unique())
    product = st.sidebar.multiselect("Product", options=df["item_name"].unique())

    # Apply filters
    df_filtered = df.query("year in @year and month in @month and dist_name in @dist")
    if product:
        df_filtered = df_filtered[df_filtered["item_name"].isin(product)]

    # --- KPIs
    total_sales = df_filtered["sales_units"].sum()
    total_bonus = df_filtered["bonus_units"].sum()
    unique_customers = df_filtered["customer_name"].nunique()
    unique_products = df_filtered["item_name"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales Units", f"{total_sales:,}")
    col2.metric("Total Bonus Units", f"{total_bonus:,}")
    col3.metric("Unique Customers", unique_customers)
    col4.metric("Unique Products", unique_products)

    # --- Charts
    st.subheader("Sales Trend Over Time")
    trend = df_filtered.groupby(["year","month"])["sales_units"].sum().reset_index()
    fig_trend = px.line(trend, x="month", y="sales_units", color="year", markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Products")
        top_products = df_filtered.groupby("item_name")["sales_units"].sum().nlargest(10).reset_index()
        fig_top = px.bar(top_products, x="item_name", y="sales_units")
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.subheader("Sales by Distributor")
        dist_sales = df_filtered.groupby("dist_name")["sales_units"].sum().reset_index()
        fig_dist = px.bar(dist_sales, x="dist_name", y="sales_units")
        st.plotly_chart(fig_dist, use_container_width=True)

    st.subheader("Detailed Data")
    st.dataframe(df_filtered)

