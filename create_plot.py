
import pandas as pd
import matplotlib.pyplot as plt
import os

# Get the absolute path of the current working directory
current_dir = os.getcwd()

# Load the historical and forecasted data
historical_data_path = os.path.join(current_dir, 'Outbound_cleaned.csv')
forecasted_data_path = os.path.join(current_dir, 'forecasted_outbound.csv')

historical_df = pd.read_csv(historical_data_path)
forecasted_df = pd.read_csv(forecasted_data_path)

# Convert date columns to datetime objects
historical_df['OUTBOUND_DATE'] = pd.to_datetime(historical_df['OUTBOUND_DATE'])
forecasted_df['OUTBOUND_DATE'] = pd.to_datetime(forecasted_df['OUTBOUND_DATE'])

# Aggregate historical data by date
historical_daily = historical_df.groupby('OUTBOUND_DATE')['NET_QUANTITY_MT'].sum().reset_index()

# Create the plot
plt.figure(figsize=(14, 7))
plt.plot(historical_daily['OUTBOUND_DATE'], historical_daily['NET_QUANTITY_MT'], label='Historical Data')
plt.plot(forecasted_df['OUTBOUND_DATE'], forecasted_df['PREDICTED_QUANTITY_MT'], label='Forecasted Data', linestyle='--')

# Add titles and labels
plt.title('Outbound Quantity Forecast')
plt.xlabel('Date')
plt.ylabel('Net Quantity (MT)')
plt.legend()
plt.grid(True)

# Save the plot to a file
plot_output_path = os.path.join(current_dir, 'forecast_plot.png')
plt.savefig(plot_output_path)

print(f"Forecast plot has been saved to '{plot_output_path}'")
