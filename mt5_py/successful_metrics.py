#%%

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Strategies in True OOS are considered OK when RatingParameter > RatingThreshold
# Strategies in True OOS are considered NOT OK when RatingParameter <= RatingThreshold
# Rating parameter and threshold is the criteria to determine what is an acceptable strategy for the OOS period

# RatingParameter = 'Net profit'
# RatingThreshold = 0
RatingParameter = 'Profit factor'
RatingThreshold = 1

is_file = './IS_Databank.csv'
oos_file = './OOS_Databank.csv'

is_df = pd.read_csv(is_file, sep=";")
oos_df = pd.read_csv(oos_file, sep=";")

# Filter profitable strategies from the second backtest
oos_successful_strategies_df = oos_df[oos_df[RatingParameter] > RatingThreshold]
oos_failed_strategies_df = oos_df[oos_df[RatingParameter] <= RatingThreshold]

# Extract the names of profitable strategies in the second backtest
oos_successful_strategy_names = oos_successful_strategies_df['Strategy Name'].tolist()
oos_failed_strategy_names = oos_failed_strategies_df['Strategy Name'].tolist()

# Filter the first backtest data for the strategies that were profitable in the second backtest
is_successful_strategies_df = is_df[is_df['Strategy Name'].isin(oos_successful_strategy_names)]
is_failed_strategies_df = is_df[is_df['Strategy Name'].isin(oos_failed_strategy_names)]

# Create histograms for all specified headers
plt.figure(figsize=(15, 10))
headers_to_plot = ['Complexity', '# of trades', 'Net profit', 'Ret/DD Ratio', 'Avg. Trade', 'Stability', 'Stagnation', 'CAGR/Max DD %', 'CAGR/Max DD % (MC retest, Conf. level 95%)']

for i, header in enumerate(headers_to_plot):
    plt.subplot(3, 3, i+1)
    sns.histplot(data=is_successful_strategies_df, x=header, bins=20, kde=True, color='blue', alpha=0.5, label='Profitable')
    sns.histplot(data=is_failed_strategies_df, x=header, bins=20, kde=True, color='red', alpha=0.5, label='Non-Profitable')
    #plt.title(f'Histogram of {header}')

plt.legend()
plt.tight_layout()
plt.show()

# %%
