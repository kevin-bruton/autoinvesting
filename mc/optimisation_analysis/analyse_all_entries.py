#%%
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

entries_dir = './entries/'
results_file = 'entry_analysis_results.csv'

#get all files in the entries directory
entry_files = os.listdir(entries_dir)

results_str = 'Entry,SuccessPct,MeanNetProfit\n'

for entry_file in entry_files:
  # file format = entry_1.csv
  entry_num = entry_file.split('_')[1].split('.')[0]
  df = pd.read_csv(entries_dir + entry_file)

  # Calculate the percentage of Net Profits greater than 0
  percentage_positive_profits = f'{(df['Net Profit'] > 0).mean() * 100:.2f}'
  # Calculate the mean Net Profit
  mean_net_profit = f'{df['Net Profit'].mean():.2f}'
  results_str += f'{entry_num},{percentage_positive_profits},{mean_net_profit}\n'

# write results to file
with open(results_file, 'w') as f:
  f.write(results_str)
print('Results written to:', results_file)

