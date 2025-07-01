
import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(layout="wide")

# Load data
@st.cache_data
def load_data():
    inbound = pd.read_csv('Inbound_cleaned.csv')
    outbound = pd.read_csv('Outbound_cleaned.csv')
    inventory = pd.read_csv('Inventory.csv')
    material_master = pd.read_csv('MaterialMaster.csv')
    return inbound, outbound, inventory, material_master

inbound, outbound, inventory, material_master = load_data()

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Inventory Overview", "Inbound vs. Outbound", "Material Master"])

if page == "Inventory Overview":
    st.title("Inventory Overview")

    # KPIs
    total_inventory_value = inventory['STOCK_SELL_VALUE'].sum()
    num_skus = inventory['MATERIAL_NAME'].nunique()
    total_quantity = inventory['UNRESRICTED_STOCK'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Inventory Value", f"${total_inventory_value:,.2f}")
    col2.metric("Number of SKUs", num_skus)
    col3.metric("Total Quantity on Hand", f"{total_quantity:,}")

    # Inventory Distribution
    st.subheader("Inventory Distribution by Material")
    inventory_dist = inventory.groupby('MATERIAL_NAME')['UNRESRICTED_STOCK'].sum().reset_index()
    inventory_dist = inventory_dist.merge(material_master[['MATERIAL_NAME', 'POLYMER_TYPE']], on='MATERIAL_NAME')
    fig_dist = px.bar(inventory_dist, x='MATERIAL_NAME', y='UNRESRICTED_STOCK', title="Inventory Quantity by Material")
    st.plotly_chart(fig_dist, use_container_width=True)

    # Inventory Value Analysis
    st.subheader("Inventory Value Analysis")
    inventory_value = inventory.copy()
    inventory_value['Value'] = inventory_value['STOCK_SELL_VALUE']
    inventory_value = inventory_value.merge(material_master[['MATERIAL_NAME', 'POLYMER_TYPE']], on='MATERIAL_NAME')
    fig_value = px.pie(inventory_value, values='Value', names='MATERIAL_NAME', title="Inventory Value by Material")
    st.plotly_chart(fig_value, use_container_width=True)


elif page == "Inbound vs. Outbound":
    st.title("Inbound vs. Outbound Flow")

    # Trend Analysis
    st.subheader("Inbound and Outbound Quantities Over Time")
    inbound['INBOUND_DATE'] = pd.to_datetime(inbound['INBOUND_DATE'])
    outbound['OUTBOUND_DATE'] = pd.to_datetime(outbound['OUTBOUND_DATE'])
    inbound_ts = inbound.groupby('INBOUND_DATE')['NET_QUANTITY_MT'].sum().reset_index().rename(columns={'NET_QUANTITY_MT':'Inbound Quantity'})
    outbound_ts = outbound.groupby('OUTBOUND_DATE')['NET_QUANTITY_MT'].sum().reset_index().rename(columns={'NET_QUANTITY_MT':'Outbound Quantity'})
    ts_data = pd.merge(inbound_ts, outbound_ts, left_on='INBOUND_DATE', right_on='OUTBOUND_DATE', how='outer').fillna(0)
    ts_data['Date'] = ts_data['INBOUND_DATE'].fillna(ts_data['OUTBOUND_DATE'])
    ts_data = ts_data.melt(id_vars=['Date'], value_vars=['Inbound Quantity', 'Outbound Quantity'], var_name='Flow', value_name='NET_QUANTITY_MT')
    fig_ts = px.line(ts_data, x='Date', y='NET_QUANTITY_MT', color='Flow', title="Inbound vs. Outbound Quantity Over Time")
    st.plotly_chart(fig_ts, use_container_width=True)

    # Material-Level Flow
    st.subheader("Inbound vs. Outbound by Material")
    inbound_agg = inbound.groupby('MATERIAL_NAME')['NET_QUANTITY_MT'].sum().reset_index().rename(columns={'NET_QUANTITY_MT':'Inbound'})
    outbound_agg = outbound.groupby('MATERIAL_NAME')['NET_QUANTITY_MT'].sum().reset_index().rename(columns={'NET_QUANTITY_MT':'Outbound'})
    flow_agg = pd.merge(inbound_agg, outbound_agg, on='MATERIAL_NAME', how='outer').fillna(0)
    flow_agg = flow_agg.merge(material_master[['MATERIAL_NAME', 'POLYMER_TYPE']], on='MATERIAL_NAME')
    flow_agg = flow_agg.melt(id_vars=['MATERIAL_NAME'], value_vars=['Inbound', 'Outbound'], var_name='Flow', value_name='NET_QUANTITY_MT')
    fig_agg = px.bar(flow_agg, x='MATERIAL_NAME', y='NET_QUANTITY_MT', color='Flow', barmode='group', title="Inbound vs. Outbound Quantity by Material")
    st.plotly_chart(fig_agg, use_container_width=True)

elif page == "Material Master":
    st.title("Material Master Details")
    st.dataframe(material_master)
