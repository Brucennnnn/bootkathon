import streamlit as st
import pandas as pd
import plotly.express as px
import os
from rag_chatbot import get_ai_response

def clean_data_summary(df):
    # Clean column names by removing special characters and extra spaces
    df.columns = df.columns.str.replace(r'[^a-zA-Z0-9_]', '', regex=True).str.strip()
    
    # Rename columns for easier access
    df = df.rename(columns={
        'BALANCE_AS_OF_DATE': 'Date',
        'PLANT_NAME': 'Plant',
        'MATERIAL_NAME': 'Material',
        'UNRESRICTED_STOCK': 'Unrestricted_Stock',
        'STOCK_SELL_VALUE': 'Stock_Sell_Value',
        'SHELF_LIFE_IN_MONTH': 'Shelf_Life_Months',
        'IS_OVER_SHELFLIFE': 'Is_Over_Shelf_Life',
        'LOSS_VALUE': 'Loss_Value' # Assuming the first LOSS_VALUE is the relevant one
    })

    # Convert 'Date' to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Convert numeric columns, handling commas and errors
    numeric_cols = ['Unrestricted_Stock', 'Stock_Sell_Value', 'Loss_Value']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convert 'Is_Over_Shelf_Life' to boolean
    if 'Is_Over_Shelf_Life' in df.columns:
        df['Is_Over_Shelf_Life'] = df['Is_Over_Shelf_Life'].astype(str).str.strip().str.upper() == 'YES'

    # Drop rows with NaN in critical columns
    df.dropna(subset=['Date', 'Plant', 'Material', 'Unrestricted_Stock', 'Stock_Sell_Value'], inplace=True)
    
    return df

def main():
    st.set_page_config(layout="wide")
    page = st.sidebar.radio("Navigation", ["Inventory Dashboard", "Inventory Recommendations", "Chatbot"])

    file_path = os.path.join(os.getcwd(), 'Data_Analysis(Inventory Summary).csv')
    
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        st.stop()

    try:
        df = pd.read_csv(file_path)
        df = clean_data_summary(df)
    except Exception as e:
        st.error(f"Error loading or cleaning data: {e}")
        st.stop()

    if page == "Inventory Dashboard":
        st.title("Inventory Management Dashboard")

        st.sidebar.header("Filters")

        # Date Range Filter
        min_date = df['Date'].min().to_pydatetime()
        max_date = df['Date'].max().to_pydatetime()
        date_range = st.sidebar.date_input("Select Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

        if len(date_range) == 2:
            start_date, end_date = date_range
            df_filtered = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
        else:
            df_filtered = df.copy()

        # Plant Filter
        all_plants = ['All'] + sorted(df_filtered['Plant'].unique().tolist())
        selected_plants = st.sidebar.multiselect("Select Plant(s)", all_plants, default=['All'])
        if 'All' not in selected_plants:
            df_filtered = df_filtered[df_filtered['Plant'].isin(selected_plants)]

        # Material Filter
        all_materials = ['All'] + sorted(df_filtered['Material'].unique().tolist())
        selected_materials = st.sidebar.multiselect("Select Material(s)", all_materials, default=['All'])
        if 'All' not in selected_materials:
            df_filtered = df_filtered[df_filtered['Material'].isin(selected_materials)]

        if df_filtered.empty:
            st.warning("No data available for the selected filters.")
            return

        st.header("Key Performance Indicators")
        col1, col2, col3 = st.columns(3)
        
        total_stock = df_filtered['Unrestricted_Stock'].sum()
        total_sell_value = df_filtered['Stock_Sell_Value'].sum()
        total_loss_value = df_filtered['Loss_Value'].sum()

        col1.metric("Total Unrestricted Stock", f"{total_stock:,.0f}")
        col2.metric("Total Stock Sell Value", f"${total_sell_value:,.2f}")
        col3.metric("Total Loss Value (Over Shelf Life)", f"${total_loss_value:,.2f}")

        st.header("Inventory Trends Over Time")
        
        # Aggregate data for time series plot
        df_time_series = df_filtered.groupby('Date').agg(
            Total_Stock=('Unrestricted_Stock', 'sum'),
            Total_Sell_Value=('Stock_Sell_Value', 'sum'),
            Total_Loss_Value=('Loss_Value', 'sum')
        ).reset_index()

        fig_stock_trend = px.line(df_time_series, x='Date', y='Total_Stock', title='Total Unrestricted Stock Over Time')
        st.plotly_chart(fig_stock_trend, use_container_width=True)

        fig_value_trend = px.line(df_time_series, x='Date', y='Total_Sell_Value', title='Total Stock Sell Value Over Time')
        st.plotly_chart(fig_value_trend, use_container_width=True)

        st.header("Inventory Distribution")
        
        # Stock by Plant
        stock_by_plant = df_filtered.groupby('Plant')['Unrestricted_Stock'].sum().reset_index().sort_values(by='Unrestricted_Stock', ascending=False)
        fig_stock_plant = px.bar(stock_by_plant, x='Plant', y='Unrestricted_Stock', title='Unrestricted Stock by Plant')
        st.plotly_chart(fig_stock_plant, use_container_width=True)

        # Stock by Material (Top N)
        stock_by_material = df_filtered.groupby('Material')['Unrestricted_Stock'].sum().reset_index().sort_values(by='Unrestricted_Stock', ascending=False)
        fig_stock_material = px.bar(stock_by_material.head(10), x='Material', y='Unrestricted_Stock', title='Top 10 Unrestricted Stock by Material')
        st.plotly_chart(fig_stock_material, use_container_width=True)

        st.header("Loss Analysis")
        
        # Loss by Plant
        loss_by_plant = df_filtered.groupby('Plant')['Loss_Value'].sum().reset_index().sort_values(by='Loss_Value', ascending=False)
        fig_loss_plant = px.bar(loss_by_plant, x='Plant', y='Loss_Value', title='Loss Value by Plant')
        st.plotly_chart(fig_loss_plant, use_container_width=True)

        # Loss by Material (Top N)
        loss_by_material = df_filtered.groupby('Material')['Loss_Value'].sum().reset_index().sort_values(by='Loss_Value', ascending=False)
        fig_loss_material = px.bar(loss_by_material.head(10), x='Material', y='Loss_Value', title='Top 10 Loss Value by Material')
        st.plotly_chart(fig_loss_material, use_container_width=True)

        st.header("Detailed Data")
        st.dataframe(df_filtered)

    elif page == "Inventory Recommendations":
        recommendations_page()
    elif page == "Chatbot":
        chatbot_page(df)

def recommendations_page():
    st.title("Inventory Recommendations")
    file_path = os.path.join(os.getcwd(), 'inventory_recommendations.csv')
    
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        st.stop()

    try:
        df_reco = pd.read_csv(file_path)
        st.dataframe(df_reco)
    except Exception as e:
        st.error(f"Error loading inventory recommendations data: {e}")
        st.stop()

from rag_chatbot import get_ai_response

def chatbot_page(df):
    st.title("Inventory Chatbot (AI Powered)")
    st.write("Ask me questions about the inventory data. For example: 'What is the stock for MAT-0001?' or 'Show me details about Plant A'.")

    user_query = st.text_input("Your question:")

    if user_query:
        with st.spinner("Thinking..."):
            response = get_ai_response(user_query, df)
            st.write(f"**Chatbot:** {response}")

if __name__ == '__main__':
    main()