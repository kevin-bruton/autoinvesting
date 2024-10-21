#%%
import os
import pandas as pd
import xml.etree.ElementTree as ET
import zipfile

bb_src_file = 'base_building_blocks.xml'
bb_file = 'config.xml'
bb_compressed_filename = "BlockSettings.sqb"

# Strategies in True OOS are considered OK when RatingParameter > RatingThreshold
# Strategies in True OOS are considered NOT OK when RatingParameter <= RatingThreshold

# Rating parameter and threshold is the criteria to determine what is an acceptable strategy for the OOS period
# RatingParameter = 'Net profit'
# RatingThreshold = 0
RatingParameter = 'CAGR/Max DD %'
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

# Print statistics of "Price indicators" - Unique combinations with occurrences
price_indicators_split = is_successful_strategies_df['Price indicators'].str.split(',', expand=True)
price_indicators_stats = price_indicators_split.apply(pd.Series.value_counts).fillna(0).sum(axis=1).astype(int).sort_values(ascending=False)
print("\nStatistics of profitable Price Indicators:")
print(price_indicators_stats)

# Print statistics of "Entry indicators" - Unique combinations with occurrences
entry_indicators_split = is_successful_strategies_df['Entry indicators'].str.split(',', expand=True)
entry_indicators_counts = entry_indicators_split.apply(pd.Series.value_counts).fillna(0).sum(axis=1).astype(int).sort_values(ascending=False)
print("\nStatistics of profitable Entry Indicators:")
print(entry_indicators_counts)

# Print statistics of "Exit indicators" - Unique combinations with occurrences
exit_indicators_split = is_successful_strategies_df['Exit indicators'].str.split(',', expand=True)
exit_indicators_counts = exit_indicators_split.apply(pd.Series.value_counts).fillna(0).sum(axis=1).astype(int).sort_values(ascending=False)
print("\nStatistics of profitable Exit Indicators:")
print(exit_indicators_counts)

price_indicators_list = price_indicators_stats.index.tolist()
entry_indicators_list = entry_indicators_counts.index.tolist()

# Write successful building blocks to bulding block config file

# Read the base building blocks file to a string
xmlTree = ET.parse(bb_src_file)
root = xmlTree.getroot()  

for indicator_name in price_indicators_list:
  indicator_el = root.find('.//Block[@key="Stop/Limit Price Levels.' + indicator_name + '"]')
  if indicator_el is None:
    indicator_el = root.find('.//Block[@key="Stop/Limit Price Ranges.' + indicator_name + '"]')
  if indicator_el is not None:
    indicator_el.attrib['use'] = 'true'

for indicator_name in entry_indicators_list:
  indicator_el = root.find('.//Block[@key="' + indicator_name + '"]')
  if indicator_el is None:
    indicator_el = root.find('.//Block[@key="Indicators.' + indicator_name + '"]')
  if indicator_el is None:
    indicator_el = root.find('.//Block[@key="Prices.' + indicator_name + '"]')
  if indicator_el is not None:
    indicator_el.attrib['use'] = 'true'  

xmlTree.write(bb_file)

zip = zipfile.ZipFile(bb_compressed_filename, "w", zipfile.ZIP_DEFLATED)
zip.write(bb_file)
zip.close()
os.remove(bb_file)

print("\nBuilding block config file " + bb_compressed_filename + " has been created successfully!")
