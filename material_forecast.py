
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import os
import numpy as np

# Create a directory for the plots if it doesn't exist
output_plot_dir = 'material_forecast_plots'
if not os.path.exists(output_plot_dir):
    os.makedirs(output_plot_dir)

# Load the dataset
file_path = 'Outbound_cleaned.csv'
df = pd.read_csv(file_path)

# Convert 'OUTBOUND_DATE' to datetime objects
df['OUTBOUND_DATE'] = pd.to_datetime(df['OUTBOUND_DATE'])
df.set_index('OUTBOUND_DATE', inplace=True)

# Get unique material names
materials = df['MATERIAL_NAME'].unique()

all_forecasts = []

for material in materials:
    print(f"Processing material: {material}")
    
    # Filter data for the current material
    material_df = df[df['MATERIAL_NAME'] == material]
    
    # Resample to monthly frequency
    monthly_data = material_df['NET_QUANTITY_MT'].resample('MS').sum()
    
    # Check if there is enough data to train the model (e.g., at least 2 years)
    if len(monthly_data) < 3:
        print(f"Skipping {material} due to insufficient data.")
        continue

    try:
        # ARIMA model training (non-seasonal)
        model = SARIMAX(monthly_data, order=(1, 1, 1))
        results = model.fit(disp=False)
        
        # Forecast for the next 12 months
        forecast = results.get_forecast(steps=12)
        forecast_index = forecast.predicted_mean.index
        forecast_values = forecast.predicted_mean.values
        
        # Trend and Slope Calculation using Linear Regression
        X = np.arange(len(forecast_values)).reshape(-1, 1)
        y = forecast_values
        
        lin_reg = LinearRegression()
        lin_reg.fit(X, y)
        
        slope = lin_reg.coef_[0]
        trend_line = lin_reg.predict(X)
        
        # Store the forecast
        forecast_df = pd.DataFrame({
            'MATERIAL_NAME': material,
            'MONTH': forecast_index,
            'FORECASTED_QUANTITY_MT': forecast_values,
            'TREND_SLOPE': slope
        })
        all_forecasts.append(forecast_df)
        
        # Plotting
        plt.figure(figsize=(12, 6))
        plt.plot(monthly_data.index, monthly_data, label='Historical Monthly Sales')
        plt.plot(forecast_index, forecast_values, label='Forecasted Sales')
        plt.plot(forecast_index, trend_line, label=f'Trend (slope: {slope:.2f})', linestyle='--')
        plt.title(f'Monthly Sales Forecast for {material}')
        plt.xlabel('Date')
        plt.ylabel('Net Quantity (MT)')
        plt.legend()
        plt.grid(True)
        
        # Save the plot
        plot_filename = os.path.join(output_plot_dir, f'{material}_forecast.png')
        plt.savefig(plot_filename)
        plt.close()

    except Exception as e:
        print(f"Could not process {material}. Reason: {e}")

# Combine all forecasts into a single DataFrame
if all_forecasts:
    final_forecast_df = pd.concat(all_forecasts, ignore_index=True)
    # Save the combined forecast data to a CSV file
    final_forecast_df.to_csv('material_monthly_forecast.csv', index=False)
    print("Forecasting complete. Results saved to 'material_monthly_forecast.csv' and plots saved in 'material_forecast_plots' directory.")
else:
    print("No materials had sufficient data for forecasting.")
