
#%% Start
import MetaTrader5 as mt
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

rates_start_dt = datetime(2024, 1, 1)
num_bars = 1000
symbol = "UK100"

# Connect to MetaTrader
if not mt.initialize():
    print("initialize() failed, error code =",mt.last_error())
    quit()
 
# display data on MetaTrader 5 version
print('\nConnected! MT5 version info: ', mt.version())
 
rates = mt.copy_rates_from(symbol, mt.TIMEFRAME_H1, rates_start_dt, num_bars)

# shut down connection to the MetaTrader 5 terminal
mt.shutdown()
if rates is None:
    print("Could not retrieve rates from MetaTrader 5. Please check the symbol is available in the logged in account.")
    print("Current symbol: ", symbol, "Number of bars to retrieve: ", num_bars)
    quit()
print(f'Got {len(rates)} rates. Closed MT5 connection.')

rates_df = pd.DataFrame(rates)

# convert time in seconds into the datetime format
rates_df['time'] = pd.to_datetime(rates_df['time'], unit='s')

# Sort the DataFrame by the 'DateTime' column (datetime) in descending order
rates_df = rates_df.sort_values(by='time', ascending=False)

# Extract the hour component
rates_df['hour'] = rates_df['time'].dt.hour

# Group data by hour and sum the total volume for each hour
hourly_data = rates_df.groupby('hour')['tick_volume'].sum()

spread_data = rates_df.groupby('hour')['spread'].sum()

# Plot the histogram
plt.bar(hourly_data.index, hourly_data.values)
plt.xlabel('Hour of the Day')
plt.ylabel('Total Volume')
plt.title('Total Volume vs. Hour of the Day')
plt.xticks(range(24))  # Display all 24 hours
plt.show()

# Plot the histogram
plt.bar(spread_data.index, spread_data.values)
plt.xlabel('Hour of the Day')
plt.ylabel('Avg Spread')
plt.title('Avg Spread vs. Hour of the Day')
plt.xticks(range(24))  # Display all 24 hours
plt.show()

# %%
