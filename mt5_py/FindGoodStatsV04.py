# CopyRight 2023 Coensio.com. 
# All Rigths Reserved.
# DO NOT DISTRIBUTE!

#%%

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

# Strategies in True OOS are considered OK when RatingParameter > RatingThreshold
# Strategies in True OOS are considered NOT OK when RatingParameter <= RatingThreshold

# Rating parameter and threshold is the criteria to determine what is an acceptable strategy for the OOS period
# RatingParameter = 'Net profit'
# RatingThreshold = 0
RatingParameter = 'CAGR/Max DD %'
RatingThreshold = 1

# Selection parameter and threshold is the criteria to filter the strategies
#SelectionParameter = 'Ret/DD Ratio'
#SelectionThreshold = 13  # Strategy selected if equal or above this threshold
#SelectionParameter = 'CAGR/Max DD % (MC retest, Conf. level 95%)'
#SelectionThreshold = 0.7  # Strategy selected if equal or above this threshold
SelectionParameter = 'CAGR/Max DD %'
SelectionThreshold = 1.5  # Strategy selected if equal or above this threshold

""" 
# Define the command-line arguments
parser = argparse.ArgumentParser(description='Analyze and compare two CSV files containing backtest data.')
parser.add_argument('file1', type=str, help='Path to the MC Databank CSV file')
parser.add_argument('file2', type=str, help='Path to the True OOS CSV file')
args = parser.parse_args()

# Read the two CSV files into dataframes
file1 = args.file1
file2 = args.file2
 """
file1 = './MC_Databank.csv'
file2 = './TrueOOS_Databank.csv'

df1 = pd.read_csv(file1, sep=";")
df2 = pd.read_csv(file2, sep=";")

# Filter profitable strategies from the second backtest
profitable_strategies_df2 = df2[df2[RatingParameter] > RatingThreshold]
non_profitable_strategies_df2 = df2[df2[RatingParameter] <= RatingThreshold]

# Extract the names of profitable strategies in the second backtest
profitable_strategy_names = profitable_strategies_df2['Strategy Name'].tolist()
non_profitable_strategy_names = non_profitable_strategies_df2['Strategy Name'].tolist()

# Filter the first backtest data for the strategies that were profitable in the second backtest
profitable_strategies_df1 = df1[df1['Strategy Name'].isin(profitable_strategy_names)]
non_profitable_strategies_df1 = df1[df1['Strategy Name'].isin(non_profitable_strategy_names)]

# Calculate the number and percentage of profitable strategies in profitable_strategies_df2 compared to df1
num_profitable_strategies_df2 = len(profitable_strategies_df2)
percentage_profitable_df2_vs_df1 = (num_profitable_strategies_df2 / len(df1)) * 100

# Selecting strategies
selected_strategies_df1 = df1[df1[SelectionParameter] >= SelectionThreshold]

# Match selected_strategies_df1 in df2 and calculate how many of the selected strategies from df1 are profitable in df2
selected_strategies_df2 = df2[df2['Strategy Name'].isin(selected_strategies_df1['Strategy Name'])]

# Filter the selected strategies from df2 to find profitable ones
selected_profitable_strategies_df2 = selected_strategies_df2[selected_strategies_df2[RatingParameter] > RatingThreshold]

# Calculate the number and percentage of selected strategies in selected_strategies_df2 compared to selected_strategies_df1
num_selected_strategies_df1 = len(selected_strategies_df1)
num_selected_profitable_strategies_df2 = len(selected_profitable_strategies_df2)

# Calculate success rate
percentage_selected_profitable_df2_vs_df1 = (num_selected_profitable_strategies_df2 / num_selected_strategies_df1) * 100

print(f"Total in [MC]: {len(df1):.0f}")
print(f"OK in [True OOS] when: {RatingParameter} > {RatingThreshold:.0f}")
print(f"OK in [True OOS] (no selection): {num_profitable_strategies_df2:.0f}")
print(f"% OK in [True OOS] (no selection): {percentage_profitable_df2_vs_df1:.2f}% ({num_profitable_strategies_df2:.0f}/{len(df1):.0f})")
print()
print(f"Total in [MC]: {len(df1):.0f}")
print(f"Selected from [MC] when: {SelectionParameter} >= {SelectionThreshold:.0f}")
print(f"Selected from [MC]: {num_selected_strategies_df1:.0f}")
print(f"OK in [True OOS] when: {RatingParameter} > {RatingThreshold:.0f}")
print(f"OK in [True OOS] (after selection): {num_selected_profitable_strategies_df2:.0f}")
print(f"% OK in [True OOS] (after selection): {percentage_selected_profitable_df2_vs_df1:.2f}% ({num_selected_profitable_strategies_df2:.0f}/{num_selected_strategies_df1:.0f})")
print()

# Now, you can analyze and compare the statistics of profitable strategies in the first backtest
# Include 80% and 90% levels in the describe() method
common_statistics_profitable = profitable_strategies_df1.describe(percentiles=[0.75, 0.9])

# Print the common statistics for profitable strategies
print("Common Statistical Numbers/Figures for Profitable Strategies in the First Backtest:")
print(common_statistics_profitable)

# Now, you can analyze and compare the statistics of non-profitable strategies in the first backtest
# Include 80% and 90% levels in the describe() method
common_statistics_non_profitable = non_profitable_strategies_df1.describe(percentiles=[0.75, 0.9])

# Print the common statistics for non-profitable strategies
print("Common Statistical Numbers/Figures for Non-Profitable Strategies in the First Backtest:")
print(common_statistics_non_profitable)

# Print statistics of "Price indicators" - Unique combinations with occurrences
# price_indicators_stats = profitable_strategies_df1['Price indicators'].value_counts()
price_indicators_split = profitable_strategies_df1['Price indicators'].str.split(',', expand=True)
price_indicators_stats = price_indicators_split.apply(pd.Series.value_counts).fillna(0).sum(axis=1).astype(int).sort_values(ascending=False)
print("Statistics of profitable Price Indicators:")
print(price_indicators_stats)

# Print statistics of "Entry indicators" - Unique combinations with occurrences
#entry_indicators = profitable_strategies_df1['Entry indicators'].value_counts()
entry_indicators_split = profitable_strategies_df1['Entry indicators'].str.split(',', expand=True)
entry_indicators_counts = entry_indicators_split.apply(pd.Series.value_counts).fillna(0).sum(axis=1).astype(int).sort_values(ascending=False)
print("Statistics of profitable Entry Indicators:")
print(entry_indicators_counts)

# Print statistics of "Exit indicators" - Unique combinations with occurrences
# exit_indicators = profitable_strategies_df1['Exit indicators'].value_counts()
exit_indicators_split = profitable_strategies_df1['Exit indicators'].str.split(',', expand=True)
exit_indicators_counts = exit_indicators_split.apply(pd.Series.value_counts).fillna(0).sum(axis=1).astype(int).sort_values(ascending=False)
print("Statistics of profitable Exit Indicators:")
print(exit_indicators_counts)

print("TRADE FORMULA = IF(Entry Indicators==TRUE) THEN (Price Indicator2 + Frac * Price Indicator1)")

# Create histograms for all specified headers
plt.figure(figsize=(15, 10))
headers_to_plot = ['Complexity', '# of trades', 'Net profit', 'Ret/DD Ratio', 'Avg. Trade', 'Stability', 'Stagnation', 'CAGR/Max DD %', 'CAGR/Max DD % (MC retest, Conf. level 95%)']

for i, header in enumerate(headers_to_plot):
    plt.subplot(3, 3, i+1)
    sns.histplot(data=profitable_strategies_df1, x=header, bins=20, kde=True, color='blue', alpha=0.5, label='Profitable')
    sns.histplot(data=non_profitable_strategies_df1, x=header, bins=20, kde=True, color='red', alpha=0.5, label='Non-Profitable')
    #plt.title(f'Histogram of {header}')

plt.legend()
plt.tight_layout()
plt.show()

# %%
