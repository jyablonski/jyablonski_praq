import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Generate fake daily sales data for the last 2 years
np.random.seed(0)  # For reproducibility

start_date = "2022-01-01"
end_date = "2023-12-31"
dates = pd.date_range(start=start_date, end=end_date, freq="D")
num_days = len(dates)

# Generate random walk data with noise
sales_data = np.cumsum(np.random.randn(num_days)) + 100

# Create a DataFrame with date index and sales data
sales_df = pd.DataFrame({"Date": dates, "Sales": sales_data})
sales_df.set_index("Date", inplace=True)

# Perform basic forecasting using a simple moving average
window_size = 30  # Moving average window size (e.g., 30 days)
sales_df["Forecast"] = sales_df["Sales"].rolling(window=window_size).mean()

# Visualize the results
plt.figure(figsize=(10, 6))
plt.plot(sales_df.index, sales_df["Sales"], label="Actual Sales", color="blue")
plt.plot(
    sales_df.index,
    sales_df["Forecast"],
    label=f"Forecast ({window_size}-Day Moving Average)",
    color="red",
    linestyle="--",
)
plt.title("Daily Sales Forecasting")
plt.xlabel("Date")
plt.ylabel("Sales")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
