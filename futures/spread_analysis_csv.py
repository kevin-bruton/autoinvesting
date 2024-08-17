#%% Start
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

csv_file = 'C:/_StrategyDev/Data/SqxExported/@GC.txt'

rates_start_dt = datetime(2024, 1, 1)

# Read the CSV file into a DataFrame
rates_df = pd.read_csv(csv_file, dayfirst=True, header=None, names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'])

rates_df['datetime'] = pd.to_datetime(rates_df['date'] + ' ' + rates_df['time'], format='%m/%d/%Y %H:%M:%S')

# Sort the DataFrame by the 'DateTime' column (datetime) in descending order
rates_df = rates_df.sort_values(by='datetime', ascending=False)

# Extract the hour component
rates_df['hour'] = rates_df['datetime'].dt.hour

# Group data by hour and sum the total volume for each hour
hourly_data = rates_df.groupby('hour')['volume'].sum()

# Plot the histogram
plt.bar(hourly_data.index, hourly_data.values)
plt.xlabel('Hour of the Day')
plt.ylabel('Total Volume')
plt.title('Total Volume vs. Hour of the Day')
plt.xticks(range(24))  # Display all 24 hours
plt.show()


# %%
