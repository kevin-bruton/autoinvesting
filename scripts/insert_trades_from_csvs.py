import os
import csv
from db.trades import trade_exists, Trade

from db.trades import trade_exists

# Directory containing the CSV files
data_dir = './data'

def insert_trades_from_csvs():
  # Process each file in the data directory
  # The filename of each CSV file must contain the strategy ID and strategy run ID, separated by an underscore, eg. '1_1_trades.csv'
  for filename in os.listdir(data_dir):
    if filename.endswith('.csv'):
      strategy_id, strategy_run_id = filename.split('_')[:2]
      if strategy_id == '0': continue
      file_path = os.path.join(data_dir, filename)
      
      with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
          order_id = row['orderId']
          trade_details = str(row)
          trade = Trade(**row)
          if not trade_exists(order_id):
            #save_trade()
            print(f"Saved trade: {trade_details}")
