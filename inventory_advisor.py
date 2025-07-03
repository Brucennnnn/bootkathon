
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def clean_inventory_data(file_path):
    with open(file_path, 'r') as f:
        header = f.readline().strip()
        
    # A more robust way to clean the header
    header_columns = [h.strip() for h in header.split(',') if '?' not in h and h.strip()]
    
    # Load the data, skipping the problematic header
    df = pd.read_csv(file_path, skiprows=1, header=None)
    
    # Keep only the columns we need and assign names
    df = df.iloc[:, [0, 3, 4]]
    df.columns = ['DATE', 'MATERIAL_NAME', 'STOCK']
    
    # Convert date column to datetime
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    # Clean and convert STOCK to numeric
    df['STOCK'] = pd.to_numeric(df['STOCK'].astype(str).str.replace(',', ''), errors='coerce')
    df.dropna(subset=['STOCK'], inplace=True)

    # Get the most recent stock for each material
    df = df.sort_values('DATE').drop_duplicates('MATERIAL_NAME', keep='last')
    
    return df

    # Convert date column to datetime
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    # Clean and convert STOCK to numeric, handling non-numeric values
    df['STOCK'] = pd.to_numeric(df['STOCK'].astype(str).str.replace(',', ''), errors='coerce')
    df.dropna(subset=['STOCK'], inplace=True)

    # Get the most recent stock for each material
    df = df.sort_values('DATE').drop_duplicates('MATERIAL_NAME', keep='last')
    
    return df

def analyze_inventory(inventory_df, forecast_df):
    # Aggregate forecast data
    forecast_summary = forecast_df.groupby('MATERIAL_NAME').agg(
        total_forecast=('FORECASTED_QUANTITY_MT', 'sum'),
        trend_slope=('TREND_SLOPE', 'first')
    ).reset_index()

    # Merge inventory and forecast data
    merged_df = pd.merge(inventory_df, forecast_summary, on='MATERIAL_NAME')

    # Calculate stock-to-forecast ratio
    merged_df['stock_to_forecast_ratio'] = merged_df['STOCK'] / merged_df['total_forecast']
    
    # Handle infinite ratios by replacing them with a large number for plotting
    merged_df['stock_to_forecast_ratio'].replace([np.inf, -np.inf], 10, inplace=True)

    # Categorize materials
    def get_recommendation(row):
        if row['trend_slope'] > 0.5 and row['stock_to_forecast_ratio'] < 1:
            return 'Buy More'
        elif row['trend_slope'] < -0.5 and row['stock_to_forecast_ratio'] > 1.5:
            return 'Buy Less'
        else:
            return 'Monitor'
            
    merged_df['recommendation'] = merged_df.apply(get_recommendation, axis=1)
    
    return merged_df

def plot_recommendations(df, output_path):
    plt.figure(figsize=(12, 8))
    
    colors = {'Buy More': 'green', 'Buy Less': 'red', 'Monitor': 'blue'}
    
    for category, color in colors.items():
        subset = df[df['recommendation'] == category]
        plt.scatter(subset['stock_to_forecast_ratio'], subset['trend_slope'], 
                    c=color, label=category, alpha=0.7, s=100)

    plt.axvline(1.0, color='gray', linestyle='--', lw=1)
    plt.axhline(0.0, color='gray', linestyle='--', lw=1)
    
    plt.xscale('log')
    plt.xlabel('Stock-to-Forecast Ratio (Log Scale)')
    plt.ylabel('Trend Slope')
    plt.title('Inventory Purchase Recommendations')
    plt.legend()
    plt.grid(True, which="both", ls="--")
    
    plt.savefig(output_path)
    print(f"Recommendation plot saved to {output_path}")

def main():
    # Define file paths
    inventory_file = os.path.join(os.getcwd(), 'Data_Analysis(Inventory Summary).csv')
    forecast_file = os.path.join(os.getcwd(), 'material_monthly_forecast.csv')
    
    # Clean and process data
    inventory_df = clean_inventory_data(inventory_file)
    forecast_df = pd.read_csv(forecast_file)
    
    # Analyze and get recommendations
    recommendations_df = analyze_inventory(inventory_df, forecast_df)
    
    # Save detailed recommendations to CSV
    recommendations_output_path = os.path.join(os.getcwd(), 'inventory_recommendations.csv')
    recommendations_df.to_csv(recommendations_output_path, index=False)
    print(f"Detailed recommendations saved to {recommendations_output_path}")
    
    # Plot and save the diagram
    plot_output_path = os.path.join(os.getcwd(), 'inventory_recommendation.png')
    plot_recommendations(recommendations_df, plot_output_path)

if __name__ == '__main__':
    main()
