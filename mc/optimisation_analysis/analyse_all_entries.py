#%%
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

opt_results_dir = './es_60_long_tf_var0_10/'
results_file = 'es_60_long_tf_var0_10_analysis_results.csv'

#get all files in the results directory
results_files = os.listdir(opt_results_dir)

results_str = 'Value,SuccessPct,MeanNetProfit,MeanRetDd,MeanKRatio\n'

for result_file in results_files:
  # file format = entry_1.csv
  result_num = result_file.split('_')[1].split('.')[0]
  df = pd.read_csv(opt_results_dir + result_file)

  # Calculate the percentage of Net Profits greater than 0
  percentage_positive_profits = f'{(df['Net Profit'] > 0).mean() * 100:.2f}'
  # Calculate the mean Net Profit
  mean_net_profit = f'{df['Net Profit'].mean():.2f}'
  # Calculate the mean return / drawdown ratio
  mean_return_drawdown_ratio = f'{df['ret_dd'].mean():.2f}'
  mean_k_ratio = f'{df['k_ratio'].mean():.2f}'
  results_str += f'{result_num},{percentage_positive_profits},{mean_net_profit},{mean_return_drawdown_ratio},{mean_k_ratio}\n'

# write results to file
with open(results_file, 'w') as f:
  f.write(results_str)
print('Results written to:', results_file)

