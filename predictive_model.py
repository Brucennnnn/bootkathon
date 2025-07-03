
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
import os

# Get the absolute path of the current working directory
current_dir = os.getcwd()

# Load the dataset
file_path = os.path.join(current_dir, 'Outbound_cleaned.csv')
df = pd.read_csv(file_path)

# Convert 'OUTBOUND_DATE' to datetime objects
df['OUTBOUND_DATE'] = pd.to_datetime(df['OUTBOUND_DATE'])

# Aggregate data by date
df.set_index('OUTBOUND_DATE', inplace=True)
daily_quantity = df['NET_QUANTITY_MT'].resample('D').sum()

# Split data into training and test sets
train_data = daily_quantity[daily_quantity.index < '2024-06-01']
test_data = daily_quantity[daily_quantity.index >= '2024-06-01']

# SARIMA model training
# Define model parameters
p, d, q = 1, 1, 1
P, D, Q, s = 1, 1, 1, 7  # Seasonal parameters for weekly seasonality

# Create and train the SARIMA model
model = SARIMAX(train_data, order=(p, d, q), seasonal_order=(P, D, Q, s))
results = model.fit(disp=False)

# Make predictions
forecast_steps = len(test_data)
predictions = results.get_forecast(steps=forecast_steps)
predicted_means = predictions.predicted_mean

# Combine historical and forecasted data
forecast_df = pd.DataFrame({
    'OUTBOUND_DATE': predicted_means.index,
    'PREDICTED_QUANTITY_MT': predicted_means.values
})

# Save the forecast to a new CSV file
forecast_output_path = os.path.join(current_dir, 'forecasted_outbound.csv')
forecast_df.to_csv(forecast_output_path, index=False)

print(f"Forecasted data has been saved to '{forecast_output_path}'")
